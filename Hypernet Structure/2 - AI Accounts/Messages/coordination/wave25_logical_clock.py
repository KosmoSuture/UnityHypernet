#!/usr/bin/env python3
"""Wave 2.5 logical-clock DAG tooling.

H5 substrate: every coordination entry can be represented as
content_hash + parent_hash + actor-local monotonic counter. Wall-clock remains
advisory; replay and ordering disputes use the DAG.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import wave1_board
import wave25_coorddb


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PROJECT_ID = "wave-2.5"
DEFAULT_MESSAGES_DIR = SCRIPT_DIR


@dataclass
class LogicalClockEntry:
    project_id: str
    entry_id: str
    actor: str
    actor_counter: int
    content_hash: str
    parent_hash: str
    wall_time: str = ""
    source_path: str = ""
    entry_type: str = "coordination_message"
    body: str = ""


@dataclass
class DagFinding:
    kind: str
    severity: str
    message: str


@dataclass(frozen=True)
class ParentReference:
    key: str
    value: str


def _configure_stream_errors(stream: Any) -> None:
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


_configure_stream_errors(sys.stdout)
_configure_stream_errors(sys.stderr)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_content(value: str) -> str:
    return "\n".join(line.rstrip() for line in value.replace("\r\n", "\n").split("\n")).strip() + "\n"


def content_hash(value: str) -> str:
    return sha256_text(normalize_content(value))


def parse_frontmatter_actor(content: str, fallback: str = "unknown") -> tuple[str, str]:
    frontmatter, _ = wave1_board.parse_frontmatter(content)
    actor = str(frontmatter.get("from") or frontmatter.get("creator") or frontmatter.get("created_by") or fallback)
    wall_time = str(frontmatter.get("created") or frontmatter.get("timestamp") or "")
    return actor, wall_time


def frontmatter_refs(content: str) -> tuple[dict[str, Any], list[ParentReference]]:
    frontmatter, _ = wave1_board.parse_frontmatter(content)
    refs: list[ParentReference] = []
    for key in ("in_response_to", "parent_ref", "parent_uid", "parent_hash", "parent_refs"):
        value = frontmatter.get(key)
        if value:
            if isinstance(value, list):
                raw_values = value
            else:
                raw_values = [value]
            refs.extend(
                ParentReference(key=key, value=str(ref).strip())
                for ref in raw_values
                if str(ref).strip()
            )
    return frontmatter, refs


def normalize_hash_ref(ref: str) -> str:
    match = re.fullmatch(r"(?:sha256:)?([0-9a-f]{64})", ref.strip(), re.IGNORECASE)
    return match.group(1).lower() if match else ""


def actor_from_filename(path: Path) -> str:
    match = re.match(r"\d{8}T\d{6}Z-([a-z0-9_.-]+)-", path.name, re.IGNORECASE)
    return match.group(1) if match else "unknown"


def message_files(messages_dir: str | Path, pattern: str = "202*.md") -> list[Path]:
    directory = Path(messages_dir)
    return sorted(path for path in directory.glob(pattern) if path.is_file())


def entries_from_message_files(
    paths: Iterable[str | Path],
    project_id: str = DEFAULT_PROJECT_ID,
    root_parent_hash: str = "",
) -> list[LogicalClockEntry]:
    records: list[dict[str, Any]] = []
    ref_to_hash: dict[str, str] = {}
    for path_like in sorted(Path(path) for path in paths):
        content = path_like.read_text(encoding="utf-8")
        fallback_actor = actor_from_filename(path_like)
        actor, wall_time = parse_frontmatter_actor(content, fallback=fallback_actor)
        frontmatter, parent_refs = frontmatter_refs(content)
        digest = content_hash(content)
        record = {
            "path": path_like,
            "content": content,
            "actor": actor,
            "wall_time": wall_time,
            "digest": digest,
            "parent_refs": parent_refs,
        }
        records.append(record)
        for ref in (
            path_like.name,
            path_like.stem,
            str(frontmatter.get("message_uid") or ""),
            str(frontmatter.get("ha") or ""),
        ):
            if ref.strip():
                ref_to_hash[ref.strip()] = digest

    for record in records:
        parent_hash = root_parent_hash
        for ref in record["parent_refs"]:
            ref_hash = ref_to_hash.get(ref.value)
            if ref_hash:
                parent_hash = ref_hash
                break
            literal_hash = normalize_hash_ref(ref.value)
            if literal_hash:
                parent_hash = literal_hash
                break
            if ref.key != "in_response_to":
                parent_hash = ref.value
                break
        record["parent_hash"] = parent_hash

    ordered_records: list[dict[str, Any]] = []
    emitted_hashes: set[str] = set()
    remaining = list(records)
    while remaining:
        progressed = False
        next_remaining: list[dict[str, Any]] = []
        remaining_hashes = {record["digest"] for record in remaining}
        for record in remaining:
            parent_hash = str(record["parent_hash"])
            if not parent_hash or parent_hash == root_parent_hash or parent_hash in emitted_hashes or parent_hash not in remaining_hashes:
                ordered_records.append(record)
                emitted_hashes.add(record["digest"])
                progressed = True
            else:
                next_remaining.append(record)
        if not progressed:
            ordered_records.extend(next_remaining)
            break
        remaining = next_remaining

    entries: list[LogicalClockEntry] = []
    actor_counters: dict[str, int] = {}
    for record in ordered_records:
        actor = str(record["actor"])
        actor_key = actor.casefold()
        actor_counters[actor_key] = actor_counters.get(actor_key, 0) + 1
        entries.append(
            LogicalClockEntry(
                project_id=project_id,
                entry_id=record["path"].name,
                actor=actor,
                actor_counter=actor_counters[actor_key],
                content_hash=record["digest"],
                parent_hash=str(record["parent_hash"]),
                wall_time=str(record["wall_time"]),
                source_path=str(record["path"]),
                body=str(record["content"]),
            )
        )
    return entries


def entries_from_board_handoffs(
    board_path: str | Path,
    project_id: str = DEFAULT_PROJECT_ID,
    root_parent_hash: str = "",
) -> list[LogicalClockEntry]:
    board = wave1_board.parse_board(board_path)
    entries: list[LogicalClockEntry] = []
    actor_counters: dict[str, int] = {}
    parent = root_parent_hash
    for index, handoff in enumerate(board.handoffs, start=1):
        actor = handoff.sender or "unknown"
        actor_key = actor.casefold()
        actor_counters[actor_key] = actor_counters.get(actor_key, 0) + 1
        body = f"{handoff.timestamp}|{handoff.sender}|{handoff.recipient}|{handoff.body}"
        digest = content_hash(body)
        entries.append(
            LogicalClockEntry(
                project_id=project_id,
                entry_id=f"{Path(board_path).name}#handoff-{index}",
                actor=actor,
                actor_counter=actor_counters[actor_key],
                content_hash=digest,
                parent_hash=parent,
                wall_time=handoff.timestamp,
                source_path=str(board_path),
                entry_type="board_handoff",
                body=body,
            )
        )
        parent = digest
    return entries


def validate_dag(entries: list[LogicalClockEntry]) -> list[DagFinding]:
    findings: list[DagFinding] = []
    by_hash: dict[str, LogicalClockEntry] = {}
    for entry in entries:
        if entry.content_hash in by_hash:
            findings.append(
                DagFinding(
                    "duplicate_content_hash",
                    "high",
                    f"{entry.entry_id} duplicates {by_hash[entry.content_hash].entry_id}",
                )
            )
        by_hash[entry.content_hash] = entry

    for entry in entries:
        if entry.parent_hash and entry.parent_hash not in by_hash:
            findings.append(
                DagFinding(
                    "orphan_parent",
                    "high",
                    f"{entry.entry_id} parent {entry.parent_hash[:12]} is not present in replay set",
                )
            )

    children_by_parent: dict[str, list[LogicalClockEntry]] = {}
    for entry in entries:
        if entry.parent_hash:
            children_by_parent.setdefault(entry.parent_hash, []).append(entry)
    for parent_hash, children in children_by_parent.items():
        if len(children) > 1:
            child_ids = ", ".join(child.entry_id for child in children)
            findings.append(
                DagFinding(
                    "forked_parent",
                    "medium",
                    f"parent {parent_hash[:12]} has multiple children in this replay set: {child_ids}",
                )
            )

    counters_by_actor: dict[str, list[int]] = {}
    for entry in entries:
        counters_by_actor.setdefault(entry.actor.casefold(), []).append(entry.actor_counter)
    for actor, counters in counters_by_actor.items():
        expected = list(range(1, len(counters) + 1))
        if counters != expected:
            findings.append(
                DagFinding(
                    "actor_counter_gap",
                    "medium",
                    f"{actor} counters are {counters}, expected {expected}",
                )
            )

    # Parent edges should point backward within this replay list for the linear projection.
    index_by_hash = {entry.content_hash: index for index, entry in enumerate(entries)}
    for index, entry in enumerate(entries):
        if entry.parent_hash and index_by_hash.get(entry.parent_hash, index + 1) >= index:
            findings.append(
                DagFinding(
                    "parent_order_warning",
                    "medium",
                    f"{entry.entry_id} parent appears after child in replay order",
                )
            )
    return findings


def record_entries_to_db(
    db_path: str | Path,
    entries: list[LogicalClockEntry],
    project_id: str = DEFAULT_PROJECT_ID,
) -> int:
    with wave25_coorddb.coordination_db(db_path) as conn:
        wave25_coorddb.ensure_project(conn, project_id)
        count = 0
        for entry in entries:
            wave25_coorddb.record_event(
                conn,
                wave25_coorddb.CoordinationEvent(
                    project_id=project_id,
                    event_type=entry.entry_type,
                    actor=entry.actor,
                    slot="",
                    occurred_at=entry.wall_time,
                    logical_counter=entry.actor_counter,
                    content_hash=entry.content_hash,
                    parent_hash=entry.parent_hash,
                    entity_type=entry.entry_type,
                    entity_id=entry.entry_id,
                    operation="logical_clock_index",
                    payload={
                        "entry_id": entry.entry_id,
                        "source_path": entry.source_path,
                        "wall_time": entry.wall_time,
                    },
                    evidence={"content_hash": entry.content_hash, "parent_hash": entry.parent_hash},
                ),
            )
            count += 1
    return count


def render_entries(entries: list[LogicalClockEntry], findings: list[DagFinding]) -> str:
    lines = ["Wave 2.5 Logical-Clock DAG", "", "Entries:"]
    if not entries:
        lines.append("- none")
    for entry in entries:
        parent = entry.parent_hash[:12] if entry.parent_hash else "ROOT"
        lines.append(
            f"- {entry.entry_id}: actor={entry.actor} counter={entry.actor_counter} "
            f"hash={entry.content_hash[:12]} parent={parent}"
        )
    lines.extend(["", "Findings:"])
    if findings:
        lines.extend(f"- [{finding.severity}] {finding.kind}: {finding.message}" for finding in findings)
    else:
        lines.append("- none")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wave 2.5 logical-clock DAG tooling.")
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    sub = parser.add_subparsers(dest="command", required=True)

    messages = sub.add_parser("index-messages", help="Index coordination message files into a logical-clock DAG.")
    messages.add_argument("--messages-dir", default=str(DEFAULT_MESSAGES_DIR))
    messages.add_argument("--pattern", default="202*.md")
    messages.add_argument("--db", default="")
    messages.add_argument("--root-parent-hash", default="")

    board = sub.add_parser("index-board-handoffs", help="Index board handoff entries into a logical-clock DAG.")
    board.add_argument("--board", required=True)
    board.add_argument("--db", default="")
    board.add_argument("--root-parent-hash", default="")

    hash_file = sub.add_parser("hash-file", help="Print the normalized content hash for one file.")
    hash_file.add_argument("path")
    return parser.parse_args(argv)


def entries_for_args(args: argparse.Namespace) -> list[LogicalClockEntry]:
    if args.command == "index-messages":
        return entries_from_message_files(
            message_files(args.messages_dir, args.pattern),
            project_id=args.project_id,
            root_parent_hash=args.root_parent_hash,
        )
    if args.command == "index-board-handoffs":
        return entries_from_board_handoffs(args.board, project_id=args.project_id, root_parent_hash=args.root_parent_hash)
    return []


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.command == "hash-file":
        digest = content_hash(Path(args.path).read_text(encoding="utf-8"))
        print(digest if args.format == "text" else json.dumps({"path": args.path, "content_hash": digest}, indent=2))
        return 0

    entries = entries_for_args(args)
    findings = validate_dag(entries)
    recorded = 0
    if getattr(args, "db", ""):
        recorded = record_entries_to_db(args.db, entries, args.project_id)
    if args.format == "json":
        print(
            json.dumps(
                {
                    "entries": [asdict(entry) for entry in entries],
                    "findings": [asdict(finding) for finding in findings],
                    "recorded": recorded,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(render_entries(entries, findings))
        if recorded:
            print(f"\nRecorded to DB: {recorded}")
    return 1 if any(finding.severity == "high" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())

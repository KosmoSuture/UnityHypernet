#!/usr/bin/env python3
"""Atomic writer for the Wave 1 coordination board.

Address: 2.7.13.CA. This is the first writer slice for Datum's v1.3
desync-killer rule: roster row updates and handoff appends happen together under
a board-level file lock, then land through same-directory atomic replace.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import wave1_board


LOCK_TIMEOUT_SECONDS = 10.0
LOCK_POLL_SECONDS = 0.1
LOCK_STALE_SECONDS = 60.0


class BoardWriteError(ValueError):
    pass


@dataclass
class BoardUpdate:
    slot: str
    current_task: str
    blocked_on: str
    last_handoff: str
    updated: str
    handoff_timestamp: str
    handoff_from: str
    handoff_to: str
    handoff_body: str
    clear_lock_name: str = ""
    board_status: dict[str, str] = field(default_factory=dict)


def _configure_stream_errors(stream: Any) -> None:
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


_configure_stream_errors(sys.stdout)
_configure_stream_errors(sys.stderr)


def lock_path_for(board_path: Path) -> Path:
    return board_path.with_name(f"{board_path.name}.lock")


@contextmanager
def board_file_lock(
    board_path: str | Path,
    timeout_seconds: float = LOCK_TIMEOUT_SECONDS,
    stale_seconds: float = LOCK_STALE_SECONDS,
):
    path = lock_path_for(Path(board_path))
    start = time.monotonic()
    fd: int | None = None
    while True:
        try:
            fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"{os.getpid()} {time.time()}\n".encode("utf-8"))
            break
        except FileExistsError:
            try:
                lock_age = time.time() - path.stat().st_mtime
            except FileNotFoundError:
                continue
            if lock_age > stale_seconds:
                try:
                    path.unlink()
                    continue
                except FileNotFoundError:
                    continue
            if time.monotonic() - start >= timeout_seconds:
                raise TimeoutError(f"Timed out waiting for board lock: {path}")
            time.sleep(LOCK_POLL_SECONDS)
    try:
        yield
    finally:
        if fd is not None:
            os.close(fd)
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def atomic_write_text(path: str | Path, content: str) -> None:
    target = Path(path)
    tmp = target.with_name(f"{target.name}.{os.getpid()}.{time.time_ns()}.tmp")
    try:
        with tmp.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(tmp, target)
    finally:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass


def normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def raw_table_cells(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def table_safe(value: str) -> str:
    if "\n" in value or "\r" in value:
        raise BoardWriteError("Board table cells must be single-line values.")
    if "|" in value:
        raise BoardWriteError("Board table cells cannot contain '|'.")
    return re.sub(r"\s+", " ", value).strip()


def format_table_row(cells: list[str]) -> str:
    return "| " + " | ".join(table_safe(cell) for cell in cells) + " |"


def find_section_bounds(lines: list[str], heading_prefix: str) -> tuple[int, int]:
    start = None
    for idx, line in enumerate(lines):
        if line.startswith("## ") and line[3:].strip().startswith(heading_prefix):
            start = idx
            break
    if start is None:
        raise BoardWriteError(f"Board section not found: {heading_prefix}")
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("## "):
            end = idx
            break
    return start, end


def find_table(lines: list[str], start: int, end: int) -> tuple[int, list[str]]:
    for idx in range(start, end):
        if not lines[idx].strip().startswith("|"):
            continue
        if idx + 1 >= end or not wave1_board.is_separator_row(lines[idx + 1]):
            continue
        headers = [normalize_header(cell) for cell in raw_table_cells(lines[idx])]
        return idx, headers
    raise BoardWriteError("No markdown table found in requested section.")


def update_roster_row_text(content: str, update: BoardUpdate) -> str:
    lines = content.splitlines()
    start, end = find_section_bounds(lines, "Instance Roster")
    table_idx, headers = find_table(lines, start, end)
    try:
        slot_idx = headers.index("slot")
    except ValueError as exc:
        raise BoardWriteError("Instance Roster table has no Slot column.") from exc
    column_indexes = {
        "current_task": headers.index("current_task"),
        "blocked_on": headers.index("blocked_on"),
        "last_handoff": headers.index("last_handoff"),
        "updated": headers.index("updated"),
    }

    target = wave1_board.clean_cell(update.slot).casefold()
    for idx in range(table_idx + 2, end):
        line = lines[idx]
        if not line.strip().startswith("|"):
            break
        cells = raw_table_cells(line)
        if len(cells) < len(headers):
            cells.extend([""] * (len(headers) - len(cells)))
        if wave1_board.clean_cell(cells[slot_idx]).casefold() != target:
            continue
        cells[column_indexes["current_task"]] = update.current_task
        cells[column_indexes["blocked_on"]] = update.blocked_on
        cells[column_indexes["last_handoff"]] = update.last_handoff
        cells[column_indexes["updated"]] = update.updated
        lines[idx] = format_table_row(cells)
        return "\n".join(lines) + ("\n" if content.endswith("\n") else "")
    raise BoardWriteError(f"Instance Roster row not found for slot: {update.slot}")


def build_handoff_entry(update: BoardUpdate) -> str:
    for value in (update.handoff_timestamp, update.handoff_from, update.handoff_to, update.handoff_body):
        if "\n" in value or "\r" in value:
            raise BoardWriteError("Handoff fields must be single-line values.")
    body = re.sub(r"\s+", " ", update.handoff_body).strip()
    return f"- **{update.handoff_timestamp} - {update.handoff_from} > {update.handoff_to}** - {body}"


def append_handoff_text(content: str, update: BoardUpdate) -> str:
    lines = content.splitlines()
    start, end = find_section_bounds(lines, "Handoff Log")
    insert_at = end
    for idx in range(start + 1, end):
        if lines[idx].strip() == "---":
            insert_at = idx
            break
    entry = build_handoff_entry(update)
    if insert_at > 0 and lines[insert_at - 1].strip():
        lines.insert(insert_at, entry)
    else:
        lines[insert_at:insert_at] = [entry]
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")


def status_overrides(update: BoardUpdate) -> dict[str, str]:
    allowed = {"current_phase", "whats_happening_now", "next_action_owner", "next_action", "human_gate"}
    return {key: value for key, value in update.board_status.items() if key in allowed and value}


def single_line(value: str, field_name: str) -> str:
    if "\n" in value or "\r" in value:
        raise BoardWriteError(f"{field_name} must be a single-line value.")
    return re.sub(r"\s+", " ", value).strip()


def update_board_status_text(content: str, update: BoardUpdate) -> str:
    overrides = status_overrides(update)
    if not overrides:
        return content
    lines = content.splitlines()
    start, end = find_section_bounds(lines, "BOARD STATUS")
    existing = wave1_board.parse_status(lines[start + 1 : end])
    current_phase = overrides.get("current_phase", existing.current_phase)
    whats_happening_now = overrides.get("whats_happening_now", existing.whats_happening_now)
    next_action_owner = overrides.get("next_action_owner", existing.next_action_owner or "engineers")
    next_action = overrides.get("next_action", existing.next_action)
    human_gate = overrides.get("human_gate", existing.human_gate)
    replacement = [
        "",
        f"> **CURRENT PHASE:** {single_line(current_phase, 'current_phase')}",
        f"> **WHAT'S HAPPENING NOW:** {single_line(whats_happening_now, 'whats_happening_now')}",
        f"> **NEXT ACTION ({single_line(next_action_owner, 'next_action_owner')}):** {single_line(next_action, 'next_action')}",
        f"> **HUMAN GATE:** {single_line(human_gate, 'human_gate')}",
        "",
    ]
    lines[start + 1 : end] = replacement
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")


def clear_edit_locks_text(content: str, clear_lock_name: str) -> str:
    target = wave1_board.clean_cell(clear_lock_name).casefold()
    if not target:
        return content
    lines = content.splitlines()
    start, end = find_section_bounds(lines, "Active Edit Locks")
    table_idx, headers = find_table(lines, start, end)
    try:
        name_idx = headers.index("name")
    except ValueError as exc:
        raise BoardWriteError("Active Edit Locks table has no Name column.") from exc

    row_start = table_idx + 2
    row_end = row_start
    while row_end < end and lines[row_end].strip().startswith("|"):
        row_end += 1

    kept_rows: list[str] = []
    for line in lines[row_start:row_end]:
        cells = raw_table_cells(line)
        if len(cells) < len(headers):
            cells.extend([""] * (len(headers) - len(cells)))
        row = dict(zip(headers, [wave1_board.clean_cell(cell) for cell in cells]))
        if wave1_board.is_placeholder_row(row):
            continue
        if wave1_board.clean_cell(cells[name_idx]).casefold() == target:
            continue
        kept_rows.append(format_table_row(cells))

    if not kept_rows:
        kept_rows = ["| - | - | - | - |"]
    lines[row_start:row_end] = kept_rows
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")


def apply_board_update_text(content: str, update: BoardUpdate) -> str:
    updated = update_board_status_text(content, update)
    updated = update_roster_row_text(updated, update)
    updated = clear_edit_locks_text(updated, update.clear_lock_name)
    return append_handoff_text(updated, update)


def write_board_update(
    board_path: str | Path,
    update: BoardUpdate,
    execute: bool = False,
    lock_timeout_seconds: float = LOCK_TIMEOUT_SECONDS,
    stale_seconds: float = LOCK_STALE_SECONDS,
) -> dict[str, Any]:
    path = Path(board_path)
    if not execute:
        original = path.read_text(encoding="utf-8")
        updated = apply_board_update_text(original, update)
        return {
            "board_path": str(path),
            "execute": False,
            "changed": updated != original,
            "lock_path": str(lock_path_for(path)),
        }

    with board_file_lock(path, timeout_seconds=lock_timeout_seconds, stale_seconds=stale_seconds):
        original = path.read_text(encoding="utf-8")
        updated = apply_board_update_text(original, update)
        changed = updated != original
        if changed:
            atomic_write_text(path, updated)
        return {
            "board_path": str(path),
            "execute": True,
            "changed": changed,
            "lock_path": str(lock_path_for(path)),
        }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Atomically update a Wave 1 board roster row and handoff.")
    parser.add_argument("--board", default=str(wave1_board.DEFAULT_BOARD_PATH))
    parser.add_argument("--slot", required=True)
    parser.add_argument("--current-task", required=True)
    parser.add_argument("--blocked-on", default="")
    parser.add_argument("--last-handoff", required=True)
    parser.add_argument("--updated", required=True)
    parser.add_argument("--handoff-timestamp", required=True)
    parser.add_argument("--handoff-from", required=True)
    parser.add_argument("--handoff-to", required=True)
    parser.add_argument("--handoff-body", required=True)
    parser.add_argument("--clear-lock-name", default="")
    parser.add_argument("--status-current-phase", default="")
    parser.add_argument("--status-whats-happening-now", default="")
    parser.add_argument("--status-next-action-owner", default="")
    parser.add_argument("--status-next-action", default="")
    parser.add_argument("--status-human-gate", default="")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--format", choices={"text", "json"}, default="text")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    update = BoardUpdate(
        slot=args.slot,
        current_task=args.current_task,
        blocked_on=args.blocked_on,
        last_handoff=args.last_handoff,
        updated=args.updated,
        handoff_timestamp=args.handoff_timestamp,
        handoff_from=args.handoff_from,
        handoff_to=args.handoff_to,
        handoff_body=args.handoff_body,
        clear_lock_name=args.clear_lock_name,
        board_status={
            "current_phase": args.status_current_phase,
            "whats_happening_now": args.status_whats_happening_now,
            "next_action_owner": args.status_next_action_owner,
            "next_action": args.status_next_action,
            "human_gate": args.status_human_gate,
        },
    )
    try:
        report = write_board_update(args.board, update, execute=args.execute)
    except (BoardWriteError, TimeoutError) as exc:
        report = {"error": str(exc), "execute": args.execute, "board_path": args.board}
        if args.format == "json":
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps({**report, "update": asdict(update)}, indent=2, sort_keys=True))
    else:
        mode = "executed" if report["execute"] else "dry-run"
        print(f"Wave 1 board writer {mode}: changed={str(report['changed']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

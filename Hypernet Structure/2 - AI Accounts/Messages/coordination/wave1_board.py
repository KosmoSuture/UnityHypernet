#!/usr/bin/env python3
"""Parse and validate the Wave 1 coordination board at Hypernet address 2.7.13.

This is the first Codex-A / Truss implementation slice for project #3 + #10:
read the canonical markdown board, extract its stable sections, and report
status/desync findings without changing board state.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
HYPERNET_ROOT = SCRIPT_DIR.parents[3]
SHARED_UNDERSTANDING_DIR = (
    HYPERNET_ROOT
    / "Hypernet Structure"
    / "2 - AI Accounts"
    / "2.7 - AI Shared Understanding"
)
DEFAULT_BOARD_PATH = SHARED_UNDERSTANDING_DIR / "2.7.13 - Execution Wave 1 Coordination & Status.md"
DEFAULT_CONTRACTS_DIR = SHARED_UNDERSTANDING_DIR
BOARD_STALENESS_MINUTES = 60
EMPTY_MARKERS = {"", "-", "\u2014"}
CONTRACT_READY_STATUSES = {"published", "accepted", "revised"}
SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3}


def _configure_stream_errors(stream: Any) -> None:
    reconfigure = getattr(stream, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(errors="replace")
    except (AttributeError, OSError, ValueError):
        pass


def configure_cli_output() -> None:
    _configure_stream_errors(sys.stdout)
    _configure_stream_errors(sys.stderr)


configure_cli_output()


@dataclass
class BoardStatus:
    current_phase: str = ""
    whats_happening_now: str = ""
    next_action_owner: str = ""
    next_action: str = ""
    human_gate: str = ""


@dataclass
class RosterRow:
    slot: str
    chosen_name: str
    role: str
    current_task: str
    blocked_on: str
    last_handoff: str
    updated: str


@dataclass
class ContractRow:
    contract: str
    address: str
    owner: str
    consumed_by: str
    version: str
    status: str


@dataclass
class EditLockRow:
    name: str
    file_or_address: str
    claimed_at: str
    note: str


@dataclass
class HandoffEntry:
    timestamp: str
    sender: str
    recipient: str
    body: str


@dataclass
class Finding:
    kind: str
    severity: str
    message: str


@dataclass
class Wave1Board:
    path: Path
    frontmatter: dict[str, Any]
    status: BoardStatus
    roster: list[RosterRow]
    contracts: list[ContractRow]
    edit_locks: list[EditLockRow]
    handoffs: list[HandoffEntry]
    body: str = ""


def is_empty(value: str) -> bool:
    return clean_cell(value) in EMPTY_MARKERS


def explicitly_not_blocked(value: str) -> bool:
    return clean_cell(value).lower().startswith("not blocked")


def strip_inline_markup(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\*\*(.*?)\*\*", r"\1", value)
    value = re.sub(r"`([^`]*)`", r"\1", value)
    return value.strip()


def clean_cell(value: str) -> str:
    value = value.replace("<br>", " ").replace("<br/>", " ")
    value = strip_inline_markup(value)
    value = re.sub(r"\s+", " ", value).strip()
    return "" if value in EMPTY_MARKERS else value


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return None
    if value in {"null", "~"}:
        return None
    if value in {"true", "True", "yes"}:
        return True
    if value in {"false", "False", "no"}:
        return False
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(item.strip()) for item in inner.split(",")]
    return value


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, content

    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return {}, content

    result: dict[str, Any] = {}
    current_key: str | None = None
    for raw in lines[1:end_idx]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        list_match = re.match(r"^\s*-\s+(.*)$", raw)
        if list_match and current_key:
            result.setdefault(current_key, [])
            if not isinstance(result[current_key], list):
                result[current_key] = [result[current_key]]
            result[current_key].append(parse_scalar(list_match.group(1)))
            continue

        match = re.match(r"^([A-Za-z0-9_.-]+):\s*(.*)$", raw)
        if not match:
            continue
        key, value = match.group(1), match.group(2)
        if value == "":
            result[key] = []
            current_key = key
        else:
            result[key] = parse_scalar(value)
            current_key = key

    body = "\n".join(lines[end_idx + 1 :])
    return result, body


def split_sections(body: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = ""
    for line in body.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        if current:
            sections[current].append(line)
    return sections


def section_by_prefix(sections: dict[str, list[str]], prefix: str) -> list[str]:
    for heading, lines in sections.items():
        if heading.startswith(prefix):
            return lines
    return []


def parse_status(lines: list[str]) -> BoardStatus:
    fields: dict[str, str] = {}
    current_key: str | None = None
    for raw in lines:
        if not raw.startswith(">"):
            continue
        text = raw.lstrip("> ").strip()
        if not text:
            continue
        match = re.match(r"\*\*([^*]+):\*\*\s*(.*)$", text)
        if match:
            raw_key = match.group(1).strip()
            key = raw_key.lower()
            value = match.group(2).strip()
            if key.startswith("current phase"):
                current_key = "current_phase"
            elif key.startswith("what"):
                current_key = "whats_happening_now"
            elif key.startswith("next action"):
                current_key = "next_action"
                owner_match = re.search(r"\(([^)]+)\)", raw_key)
                if owner_match:
                    fields["next_action_owner"] = owner_match.group(1).strip()
            elif key.startswith("human gate"):
                current_key = "human_gate"
            else:
                current_key = re.sub(r"[^a-z0-9]+", "_", key).strip("_")
            fields[current_key] = value
        elif current_key:
            fields[current_key] = f"{fields[current_key]} {text}".strip()
    return BoardStatus(
        current_phase=fields.get("current_phase", ""),
        whats_happening_now=fields.get("whats_happening_now", ""),
        next_action_owner=fields.get("next_action_owner", ""),
        next_action=fields.get("next_action", ""),
        human_gate=fields.get("human_gate", ""),
    )


def split_table_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [clean_cell(cell) for cell in line.split("|")]


def is_separator_row(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def parse_first_table(lines: list[str]) -> list[dict[str, str]]:
    for idx, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        if idx + 1 >= len(lines) or not is_separator_row(lines[idx + 1]):
            continue
        headers = [re.sub(r"[^a-z0-9]+", "_", h.lower()).strip("_") for h in split_table_row(line)]
        rows: list[dict[str, str]] = []
        for row_line in lines[idx + 2 :]:
            if not row_line.strip().startswith("|"):
                break
            values = split_table_row(row_line)
            if len(values) < len(headers):
                values.extend([""] * (len(headers) - len(values)))
            rows.append(dict(zip(headers, values)))
        return rows
    return []


def parse_handoffs(lines: list[str]) -> list[HandoffEntry]:
    entries: list[HandoffEntry] = []
    current: list[str] = []
    for line in lines:
        if line.strip() == "---":
            if current:
                entries.append(parse_handoff_entry(" ".join(current)))
                current = []
            break
        if line.startswith("- "):
            if current:
                entries.append(parse_handoff_entry(" ".join(current)))
            current = [line.strip()]
        elif current and (line.startswith("  ") or line.strip()):
            current.append(line.strip())
    if current:
        entries.append(parse_handoff_entry(" ".join(current)))
    return entries


def parse_handoff_entry(text: str) -> HandoffEntry:
    cleaned = strip_inline_markup(text.lstrip("- ").strip())
    match = re.match(r"(.+?)\s+[\-\u2014]\s+(.+?)\s+[\u2192>]\s+(.+?)\s+[\-\u2014]\s+(.*)$", cleaned)
    if not match:
        return HandoffEntry(timestamp="", sender="", recipient="", body=cleaned)
    return HandoffEntry(
        timestamp=match.group(1).strip(),
        sender=match.group(2).strip(),
        recipient=match.group(3).strip(),
        body=match.group(4).strip(),
    )


def parse_board(path: str | Path) -> Wave1Board:
    board_path = Path(path)
    content = board_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(content)
    sections = split_sections(body)

    roster_rows = parse_first_table(section_by_prefix(sections, "Instance Roster"))
    contract_rows = parse_first_table(section_by_prefix(sections, "Interface-Contract Registry"))
    lock_rows = parse_first_table(section_by_prefix(sections, "Active Edit Locks"))

    roster = [
        RosterRow(
            slot=row.get("slot", ""),
            chosen_name=row.get("chosen_name", ""),
            role=row.get("role", ""),
            current_task=row.get("current_task", ""),
            blocked_on=row.get("blocked_on", ""),
            last_handoff=row.get("last_handoff", ""),
            updated=row.get("updated", ""),
        )
        for row in roster_rows
        if not is_placeholder_row(row)
    ]
    contracts = [
        ContractRow(
            contract=row.get("contract", ""),
            address=row.get("address", ""),
            owner=row.get("owner", ""),
            consumed_by=row.get("consumed_by", ""),
            version=row.get("version", ""),
            status=row.get("status", ""),
        )
        for row in contract_rows
        if not is_placeholder_row(row)
    ]
    edit_locks = [
        EditLockRow(
            name=row.get("name", ""),
            file_or_address=row.get("file_address") or row.get("file_or_address", ""),
            claimed_at=row.get("claimed_utc_ish", "") or row.get("claimed_at", ""),
            note=row.get("note", ""),
        )
        for row in lock_rows
        if not is_placeholder_row(row)
    ]
    handoffs = parse_handoffs(section_by_prefix(sections, "Handoff Log"))

    return Wave1Board(
        path=board_path,
        frontmatter=frontmatter,
        status=parse_status(section_by_prefix(sections, "BOARD STATUS")),
        roster=roster,
        contracts=contracts,
        edit_locks=edit_locks,
        handoffs=handoffs,
        body=body,
    )


def is_placeholder_row(row: dict[str, str]) -> bool:
    values = [clean_cell(value) for value in row.values()]
    return bool(values) and all(value in EMPTY_MARKERS for value in values)


def normalize_status(status: str) -> str:
    text = clean_cell(status).lower()
    if text.startswith("published"):
        return "published"
    if text.startswith("draft"):
        return "draft"
    if text.startswith("accepted"):
        return "accepted"
    if text.startswith("revised"):
        return "revised"
    if text.startswith("blocked"):
        return "blocked"
    return text


def parse_time(value: str, now: datetime) -> datetime | None:
    value = clean_cell(value)
    if not value:
        return None
    leading_timestamp = re.match(
        r"^(\d{4}-\d{2}-\d{2}(?:[T ][0-9]{2}:[0-9]{2}(?::[0-9]{2})?(?:Z|[+-][0-9]{2}:[0-9]{2})?)?)\b",
        value,
    )
    if leading_timestamp:
        value = leading_timestamp.group(1)
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        try:
            parsed = datetime.fromisoformat(f"{value}T00:00:00+00:00")
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(now.tzinfo or timezone.utc)


ADDRESS_PATTERN = r"\b\d+(?:\.\d+){2,}(?:\.[A-Za-z0-9][A-Za-z0-9_-]*)*\b"
MESSAGE_PATH_PATTERN = r"\bMessages/coordination/[A-Za-z0-9][A-Za-z0-9._-]*\.md\b"


def extract_addresses(value: str) -> list[str]:
    return re.findall(ADDRESS_PATTERN, value)


def extract_message_paths(value: str) -> list[str]:
    return re.findall(MESSAGE_PATH_PATTERN, value)


def clean_address(value: str) -> str:
    matches = extract_addresses(value)
    return matches[0] if matches else clean_cell(value)


def find_contract_frontmatter(address: str, contracts_dir: Path) -> dict[str, Any] | None:
    for path in contracts_dir.glob("*.md"):
        try:
            frontmatter, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        except OSError:
            continue
        if str(frontmatter.get("ha", "")) == address:
            return frontmatter
    return None


def contract_file_statuses(board: Wave1Board, contracts_dir: str | Path) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for row in board.contracts:
        address = clean_address(row.address)
        frontmatter = find_contract_frontmatter(address, Path(contracts_dir))
        statuses[address] = "" if frontmatter is None else str(frontmatter.get("status", ""))
    return statuses


def board_accounts_dir(board: Wave1Board) -> Path:
    for parent in board.path.parents:
        if parent.name == "2 - AI Accounts":
            return parent
    return board.path.parent


def board_status_claims_all_engineers_blocked(status: BoardStatus) -> bool:
    text = f"{status.current_phase} {status.whats_happening_now} {status.next_action}".lower()
    return "blocked" in text and (
        "every engineer" in text
        or "all engineer" in text
        or "every instance" in text
        or "all instance" in text
    )


def roster_row_looks_active(row: RosterRow) -> bool:
    task = clean_cell(row.current_task).lower()
    if not task:
        return False
    active_markers = ("active", "actively", "build", "building", "implement", "working", "running")
    return any(marker in task for marker in active_markers)


def looks_like_lock_target(value: str) -> bool:
    value = value.strip()
    if not value:
        return False
    return bool(
        extract_addresses(value)
        or "/" in value
        or "\\" in value
        or re.search(r"\.[A-Za-z][A-Za-z0-9]{0,7}(?:$|\s)", value)
    )


def strip_lock_note(value: str) -> str:
    value = value.strip()
    for separator in (" \u2014 ", " \u2013 "):
        if separator in value:
            return value.split(separator, 1)[0].strip()
    if " - " in value:
        head, tail = value.rsplit(" - ", 1)
        if looks_like_lock_target(head) and not looks_like_lock_target(tail):
            return head.strip()
    return value


def lock_targets(value: str) -> list[str]:
    targets: list[str] = []
    for part in re.split(r"\s*;\s*", clean_cell(value)):
        target = strip_lock_note(part)
        if not target:
            continue
        addresses = extract_addresses(target)
        if addresses:
            targets.extend(addresses)
        if looks_like_lock_target(target) or not addresses:
            targets.append(target)

    deduped: list[str] = []
    for target in targets:
        if target not in deduped:
            deduped.append(target)
    return deduped


def overlaps_path_or_address(left: str, right: str) -> bool:
    left = clean_cell(left).replace("\\", "/").rstrip("/").casefold()
    right = clean_cell(right).replace("\\", "/").rstrip("/").casefold()
    if not left or not right:
        return False
    if left == right:
        return True
    if re.fullmatch(ADDRESS_PATTERN, left) and re.fullmatch(ADDRESS_PATTERN, right):
        return left.startswith(f"{right}.") or right.startswith(f"{left}.")
    return left.startswith(f"{right}/") or right.startswith(f"{left}/")


def lock_targets_overlap(left: str, right: str) -> bool:
    return any(
        overlaps_path_or_address(left_target, right_target)
        for left_target in lock_targets(left)
        for right_target in lock_targets(right)
    )


def collect_findings(
    board: Wave1Board,
    contracts_dir: str | Path = DEFAULT_CONTRACTS_DIR,
    now: datetime | None = None,
    stale_minutes: int = BOARD_STALENESS_MINUTES,
) -> list[Finding]:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    contracts_dir = Path(contracts_dir)
    accounts_dir = board_accounts_dir(board)
    findings: list[Finding] = []
    threshold_seconds = stale_minutes * 60

    for row in board.roster:
        updated = parse_time(row.updated, now)
        if updated is None and not is_empty(row.updated):
            findings.append(
                Finding(
                    "parse_warning",
                    "medium",
                    f"Roster row {row.slot} has unparsable updated timestamp '{row.updated}'.",
                )
            )
        for message_path in extract_message_paths(row.last_handoff):
            if not (accounts_dir / message_path).exists():
                findings.append(
                    Finding(
                        "missing_handoff_evidence",
                        "medium",
                        f"Roster row {row.slot} / {row.chosen_name or '(unnamed)'} cites missing coordination message '{message_path}'.",
                    )
                )
            continue
        if (
            updated is not None
            and (now - updated).total_seconds() > threshold_seconds
            and not is_empty(row.current_task)
            and (is_empty(row.blocked_on) or explicitly_not_blocked(row.blocked_on))
            and "blocked" not in row.current_task.lower()
        ):
            findings.append(
                Finding(
                    "stale_ownership",
                    "medium",
                    f"Roster row {row.slot} / {row.chosen_name or '(unnamed)'} has not updated since {row.updated}.",
                )
            )

    for idx, lock in enumerate(board.edit_locks):
        claimed = parse_time(lock.claimed_at, now)
        if claimed is None and not is_empty(lock.claimed_at):
            findings.append(
                Finding(
                    "parse_warning",
                    "medium",
                    f"Edit lock by {lock.name} has unparsable claimed timestamp '{lock.claimed_at}'.",
                )
            )
        elif claimed is not None and (now - claimed).total_seconds() > threshold_seconds:
            findings.append(
                Finding(
                    "stale_lock",
                    "high",
                    f"Edit lock by {lock.name} on {lock.file_or_address} is older than {stale_minutes} minutes.",
                )
            )
        for other in board.edit_locks[idx + 1 :]:
            if lock_targets_overlap(lock.file_or_address, other.file_or_address):
                findings.append(
                    Finding(
                        "lock_conflict",
                        "high",
                        f"Edit locks overlap: {lock.name} on {lock.file_or_address} and {other.name} on {other.file_or_address}.",
                    )
                )

    registry_by_address = {clean_address(row.address): row for row in board.contracts}
    file_statuses = contract_file_statuses(board, contracts_dir)
    for address, row in registry_by_address.items():
        file_status = file_statuses.get(address, "")
        if not file_status:
            findings.append(
                Finding(
                    "desync",
                    "high",
                    f"Contract registry lists {address}, but no matching contract file frontmatter was found.",
                )
            )
            continue
        if normalize_status(row.status) != normalize_status(file_status):
            findings.append(
                Finding(
                    "desync",
                    "high",
                    f"Contract {address} registry status '{row.status}' differs from file status '{file_status}'.",
                )
            )

    ready_files = [
        address
        for address, status in file_statuses.items()
        if normalize_status(status) in CONTRACT_READY_STATUSES
    ]
    status_text = f"{board.status.whats_happening_now} {board.status.next_action}".lower()
    if ready_files and "publish" in status_text and "contract" in status_text:
        findings.append(
            Finding(
                "board_status_desync",
                "medium",
                "BOARD STATUS still describes contract publication as the next/current action even published contract files exist.",
            )
        )

    if board_status_claims_all_engineers_blocked(board.status):
        for row in board.roster:
            if (is_empty(row.blocked_on) or explicitly_not_blocked(row.blocked_on)) and roster_row_looks_active(row):
                findings.append(
                    Finding(
                        "roster_board_status_desync",
                        "medium",
                        f"BOARD STATUS says every engineer/instance is blocked, but roster row {row.slot} / {row.chosen_name or '(unnamed)'} appears active with Blocked-On '{row.blocked_on or 'empty'}'.",
                    )
                )

    previous_handoff_time: datetime | None = None
    for idx, handoff in enumerate(board.handoffs, start=1):
        if not handoff.timestamp or not handoff.sender or not handoff.recipient or not handoff.body:
            preview = clean_cell(handoff.body)[:120]
            findings.append(
                Finding(
                    "handoff_parse_warning",
                    "medium",
                    f"Handoff entry {idx} is malformed or missing timestamp/sender/recipient/body: {preview or '(empty)'}",
                )
            )
            continue
        handoff_time = parse_time(handoff.timestamp, now)
        if handoff_time is None:
            findings.append(
                Finding(
                    "handoff_parse_warning",
                    "medium",
                    f"Handoff entry {idx} has unparsable timestamp '{handoff.timestamp}'.",
                )
            )
        else:
            if previous_handoff_time is not None and handoff_time < previous_handoff_time:
                findings.append(
                    Finding(
                        "handoff_order_warning",
                        "medium",
                        f"Handoff entry {idx} timestamp '{handoff.timestamp}' is earlier than the previous parsed handoff timestamp.",
                    )
                )
            previous_handoff_time = handoff_time
        for message_path in extract_message_paths(handoff.body):
            if not (accounts_dir / message_path).exists():
                findings.append(
                    Finding(
                        "missing_handoff_evidence",
                        "medium",
                        f"Handoff entry {idx} cites missing coordination message '{message_path}'.",
                    )
                )

    roster_by_slot_or_name: dict[str, RosterRow] = {}
    for row in board.roster:
        roster_by_slot_or_name[row.slot.lower()] = row
        if row.chosen_name:
            roster_by_slot_or_name[row.chosen_name.lower()] = row

    for row in board.roster:
        if is_empty(row.blocked_on) or explicitly_not_blocked(row.blocked_on):
            continue
        for address in extract_addresses(row.blocked_on):
            contract = registry_by_address.get(address)
            if contract and normalize_status(contract.status) not in CONTRACT_READY_STATUSES:
                findings.append(
                    Finding(
                        "blocked_chain",
                        "medium",
                        f"{row.slot} / {row.chosen_name or '(unnamed)'} is blocked on {address}, whose registry status is '{contract.status}'.",
                    )
                )
        blocked_text = clean_cell(row.blocked_on).lower()
        for key, other in roster_by_slot_or_name.items():
            if key and key in blocked_text and not is_empty(other.blocked_on):
                findings.append(
                    Finding(
                        "blocked_chain",
                        "medium",
                        f"{row.slot} / {row.chosen_name or '(unnamed)'} is blocked on {other.slot} / {other.chosen_name}, which is also blocked.",
                    )
                )

    return findings


def handoff_matches(handoff: HandoffEntry, query: str) -> bool:
    needle = clean_cell(query).casefold()
    if not needle:
        return True
    fields = (handoff.sender, handoff.recipient, handoff.body)
    return any(needle in clean_cell(field).casefold() for field in fields)


def handoffs_for(board: Wave1Board, query: str) -> list[HandoffEntry]:
    return [handoff for handoff in board.handoffs if handoff_matches(handoff, query)]


def format_handoff_history(board: Wave1Board, query: str) -> str:
    matches = handoffs_for(board, query)
    lines = [
        "Wave 1 Handoff History",
        f"Board: {board.path}",
        f"Filter: {query or '(all)'}",
        f"Matches: {len(matches)}",
        "",
    ]
    if not matches:
        lines.append("- none")
        return "\n".join(lines)
    for handoff in matches:
        lines.append(f"- {handoff.timestamp} — {handoff.sender} -> {handoff.recipient}: {handoff.body}")
    return "\n".join(lines)


def format_report(board: Wave1Board, findings: list[Finding]) -> str:
    lines = [
        "Wave 1 Coordination Board Status",
        f"Board: {board.path}",
        f"HA: {board.frontmatter.get('ha', '(missing)')}",
        f"Phase: {board.status.current_phase or '(missing)'}",
        f"Next action: {board.status.next_action or '(missing)'}",
        "",
        "Roster:",
    ]
    for row in board.roster:
        name = row.chosen_name or "(unnamed)"
        blocked = row.blocked_on or ""
        blocked_text = f"; blocked_on={blocked}" if blocked else ""
        lines.append(f"- {row.slot} / {name}: {row.current_task or '(no task)'}{blocked_text}")

    lines.extend(["", "Contracts:"])
    for row in board.contracts:
        lines.append(f"- {clean_address(row.address)}: registry_status={row.status}; owner={row.owner}")

    lines.extend(["", "Findings:"])
    if findings:
        for finding in findings:
            lines.append(f"- [{finding.severity}] {finding.kind}: {finding.message}")
    else:
        lines.append("- none")
    return "\n".join(lines)


def board_to_dict(
    board: Wave1Board,
    findings: list[Finding],
    contracts_dir: str | Path = DEFAULT_CONTRACTS_DIR,
    handoffs_for_query: str = "",
) -> dict[str, Any]:
    handoffs = handoffs_for(board, handoffs_for_query) if handoffs_for_query else board.handoffs
    return {
        "board_path": str(board.path),
        "frontmatter": board.frontmatter,
        "status": asdict(board.status),
        "roster": [asdict(row) for row in board.roster],
        "contracts": [asdict(row) for row in board.contracts],
        "contract_file_statuses": contract_file_statuses(board, contracts_dir),
        "edit_locks": [asdict(row) for row in board.edit_locks],
        "handoff_filter": handoffs_for_query,
        "handoffs": [asdict(row) for row in handoffs],
        "findings": [asdict(finding) for finding in findings],
    }


def format_json_report(
    board: Wave1Board,
    findings: list[Finding],
    contracts_dir: str | Path = DEFAULT_CONTRACTS_DIR,
    handoffs_for_query: str = "",
) -> str:
    return json.dumps(board_to_dict(board, findings, contracts_dir, handoffs_for_query), indent=2, ensure_ascii=False)


def findings_at_or_above(findings: list[Finding], threshold: str) -> list[Finding]:
    if not threshold or threshold == "none":
        return []
    minimum = SEVERITY_RANK[threshold]
    return [finding for finding in findings if SEVERITY_RANK.get(finding.severity, 0) >= minimum]


def parse_now(value: str | None) -> datetime | None:
    if not value:
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse and validate the Wave 1 coordination board.")
    parser.add_argument("--board", default=str(DEFAULT_BOARD_PATH), help="Path to 2.7.13 board markdown")
    parser.add_argument("--contracts-dir", default=str(DEFAULT_CONTRACTS_DIR), help="Directory containing contract markdown files")
    parser.add_argument("--now", default="", help="Override current time for stale checks (ISO 8601)")
    parser.add_argument("--stale-minutes", type=int, default=BOARD_STALENESS_MINUTES)
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    parser.add_argument("--handoffs-for", default="", help="Filter handoff history by participant/text")
    parser.add_argument(
        "--fail-on-severity",
        choices=("none", "low", "medium", "high"),
        default="none",
        help="Exit non-zero when any finding at or above this severity is present",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    board = parse_board(args.board)
    findings = collect_findings(
        board,
        contracts_dir=args.contracts_dir,
        now=parse_now(args.now),
        stale_minutes=args.stale_minutes,
    )
    if args.format == "json":
        print(format_json_report(board, findings, args.contracts_dir, args.handoffs_for))
    elif args.handoffs_for:
        print(format_handoff_history(board, args.handoffs_for))
    else:
        print(format_report(board, findings))
    return 1 if findings_at_or_above(findings, args.fail_on_severity) else 0


if __name__ == "__main__":
    raise SystemExit(main())

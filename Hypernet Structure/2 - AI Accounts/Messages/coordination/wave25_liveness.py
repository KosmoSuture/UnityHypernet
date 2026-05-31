#!/usr/bin/env python3
"""Wave 2.5 liveness heartbeat writer and classifier.

H1 substrate: active instances write heartbeats into the H2 SQLite DB.
The classifier returns stable labels consumed by H3 respawn and H6 closure:
active-working, active-slow, idle, stale-warning, dead.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import wave1_board
import wave25_coorddb


LABEL_ACTIVE_WORKING = "active-working"
LABEL_ACTIVE_SLOW = "active-slow"
LABEL_IDLE = "idle"
LABEL_STALE_WARNING = "stale-warning"
LABEL_DEAD = "dead"
LIVENESS_LABELS = {
    LABEL_ACTIVE_WORKING,
    LABEL_ACTIVE_SLOW,
    LABEL_IDLE,
    LABEL_STALE_WARNING,
    LABEL_DEAD,
}

DEFAULT_ACTIVE_SECONDS = 90
DEFAULT_SLOW_SECONDS = 300
DEFAULT_DEAD_SECONDS = 900
DEFAULT_EXPECTED_INTERVAL_SECONDS = 60
DEFAULT_DEAD_SUSPICION_THRESHOLD = 8.0
DEFAULT_CLOCK_SKEW_TOLERANCE_SECONDS = DEFAULT_ACTIVE_SECONDS
IDLE_ACTIONS = {
    "idle",
    "waiting",
    "wait",
    "blocked",
    "polling",
    "review-wait",
    "standby",
    "going-dark",
    "stood-down",
}
STARTING_ACTIONS = {
    "boot",
    "booting",
    "first-boot",
    "first_boot",
    "starting",
}


@dataclass
class LivenessThresholds:
    active_seconds: int = DEFAULT_ACTIVE_SECONDS
    slow_seconds: int = DEFAULT_SLOW_SECONDS
    dead_seconds: int = DEFAULT_DEAD_SECONDS
    expected_interval_seconds: int = DEFAULT_EXPECTED_INTERVAL_SECONDS
    dead_suspicion_threshold: float = DEFAULT_DEAD_SUSPICION_THRESHOLD
    clock_skew_tolerance_seconds: int = DEFAULT_CLOCK_SKEW_TOLERANCE_SECONDS


@dataclass
class LivenessStatus:
    project_id: str
    slot: str
    instance_name: str
    label: str
    observed_at: str = ""
    age_seconds: float | None = None
    monotonic_counter: int = 0
    current_task: str = ""
    last_action_type: str = ""
    lifecycle_state: str = "live"
    suspicion_score: float = 0.0
    work_signature_unchanged_count: int = 0
    reason: str = ""
    heartbeat_present: bool = False
    roster_current_task: str = ""
    roster_blocked_on: str = ""
    roster_updated_at: str = ""


def _configure_stream_errors(stream: Any) -> None:
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


_configure_stream_errors(sys.stdout)
_configure_stream_errors(sys.stderr)


def parse_time(value: str) -> datetime | None:
    if not value:
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def now_dt() -> datetime:
    return datetime.now(timezone.utc)


def now_iso() -> str:
    return now_dt().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def idle_like(last_action_type: str, current_task: str) -> bool:
    action = last_action_type.strip().casefold()
    if action in IDLE_ACTIONS:
        return True
    task = current_task.casefold()
    return any(marker in task for marker in ("waiting", "awaiting", "blocked", "standby", "polling"))


def lifecycle_state(last_action_type: str, current_task: str, roster_task: str = "") -> str:
    action = last_action_type.strip().casefold()
    task = current_task.casefold()
    roster = roster_task.casefold()
    text = f"{action} {task} {roster}"
    if any(marker in text for marker in ("going-dark", "stood-down", "stand down", "departed")):
        return "stood-down"
    if action in STARTING_ACTIONS:
        return "starting"
    if (
        "boot via" in roster
        or "unclaimed" in roster
        or "first-boot sequence" in roster
        or roster.startswith("first-boot")
        or roster.startswith("starting")
        or (not task and ("first-boot" in roster or "starting" in roster))
    ):
        return "starting"
    return "live"


def age_seconds(observed_at: str, now: datetime) -> float | None:
    observed = parse_time(observed_at)
    if observed is None:
        return None
    return (now - observed).total_seconds()


def heartbeat_intervals(conn, project_id: str, slot: str, limit: int = 8) -> list[float]:
    rows = conn.execute(
        """
        SELECT observed_at
        FROM heartbeat_events
        WHERE project_id = ? AND slot = ?
        ORDER BY event_id DESC
        LIMIT ?
        """,
        (project_id, slot, limit),
    ).fetchall()
    times = [parse_time(row["observed_at"]) for row in reversed(rows)]
    parsed = [value for value in times if value is not None]
    intervals: list[float] = []
    for previous, current in zip(parsed, parsed[1:]):
        delta = (current - previous).total_seconds()
        if delta >= 0:
            intervals.append(delta)
    return intervals


def work_signature_unchanged_count(conn, project_id: str, slot: str, limit: int = 8) -> int:
    rows = conn.execute(
        """
        SELECT current_task, last_action_type
        FROM heartbeat_events
        WHERE project_id = ? AND slot = ?
        ORDER BY event_id DESC
        LIMIT ?
        """,
        (project_id, slot, limit),
    ).fetchall()
    if not rows:
        return 0
    latest = f"{rows[0]['current_task']}|{rows[0]['last_action_type']}"
    count = 0
    for row in rows:
        signature = f"{row['current_task']}|{row['last_action_type']}"
        if signature != latest:
            break
        count += 1
    return count


def suspicion_score(age: float | None, intervals: list[float], expected_interval_seconds: int) -> float:
    if age is None:
        return math.inf
    if intervals:
        mean = sum(intervals) / len(intervals)
        baseline = max(1.0, mean)
    else:
        baseline = max(1.0, float(expected_interval_seconds))
    return round(age / baseline, 3)


def latest_message_activity_by_slot(
    messages_dir: str | Path | None,
    roster_rows: dict[str, dict[str, Any]],
) -> dict[str, datetime]:
    """Return latest coordination-message filesystem activity per roster slot."""
    if not messages_dir:
        return {}
    directory = Path(messages_dir)
    if not directory.exists():
        return {}

    names_by_slot = {
        slot: str(row.get("chosen_name", "")).strip().casefold()
        for slot, row in roster_rows.items()
        if str(row.get("chosen_name", "")).strip()
    }
    latest: dict[str, datetime] = {}
    for path in directory.glob("202*.md"):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
            frontmatter, _ = wave1_board.parse_frontmatter(content)
            stat = path.stat()
        except OSError:
            continue
        actor_text = " ".join(
            str(frontmatter.get(key) or "")
            for key in ("from", "creator", "created_by")
        ).casefold()
        actor_text = f"{actor_text} {path.name.casefold()}"
        activity_at = datetime.fromtimestamp(stat.st_mtime, timezone.utc)
        for slot, name in names_by_slot.items():
            if name and (name in actor_text or slot.casefold() in actor_text):
                if slot not in latest or activity_at > latest[slot]:
                    latest[slot] = activity_at
    return latest


def next_counter(conn, project_id: str, slot: str) -> int:
    row = conn.execute(
        "SELECT monotonic_counter FROM heartbeats WHERE project_id = ? AND slot = ?",
        (project_id, slot),
    ).fetchone()
    return int(row["monotonic_counter"]) + 1 if row else 1


def write_heartbeat(
    db_path: str | Path = wave25_coorddb.DEFAULT_DB_PATH,
    project_id: str = wave25_coorddb.DEFAULT_PROJECT_ID,
    slot: str = "",
    instance_name: str = "",
    current_task: str = "",
    last_action_type: str = "",
    observed_at: str | None = None,
    monotonic_counter: int | None = None,
    status: str = "active",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not slot.strip():
        raise ValueError("slot is required")
    if not instance_name.strip():
        raise ValueError("instance_name is required")
    with wave25_coorddb.coordination_db(db_path) as conn:
        wave25_coorddb.ensure_project(conn, project_id)
        counter = monotonic_counter if monotonic_counter is not None else next_counter(conn, project_id, slot)
        wave25_coorddb.record_heartbeat(
            conn,
            project_id,
            slot,
            instance_name,
            observed_at=observed_at or now_iso(),
            current_task=current_task,
            last_action_type=last_action_type,
            status=status,
            monotonic_counter=counter,
            payload=payload,
        )
    return {
        "project_id": project_id,
        "slot": slot,
        "instance_name": instance_name,
        "monotonic_counter": counter,
        "observed_at": observed_at or now_iso(),
    }


def classify_row(
    project_id: str,
    slot: str,
    heartbeat: dict[str, Any] | None,
    roster: dict[str, Any] | None,
    now: datetime,
    thresholds: LivenessThresholds,
    intervals: list[float],
    unchanged_signature_count: int = 0,
    message_activity_at: datetime | None = None,
) -> LivenessStatus:
    roster = roster or {}
    if heartbeat is None:
        roster_task = str(roster.get("current_task", ""))
        roster_updated = str(roster.get("updated_at", ""))
        state = lifecycle_state("", "", roster_task)
        if state == "starting":
            return LivenessStatus(
                project_id=project_id,
                slot=slot,
                instance_name=str(roster.get("chosen_name", "")),
                label=LABEL_IDLE,
                lifecycle_state="starting",
                reason="no heartbeat yet for first-boot/unclaimed row; not a respawn outage",
                roster_current_task=roster_task,
                roster_blocked_on=str(roster.get("blocked_on", "")),
                roster_updated_at=roster_updated,
            )
        message_age = (now - message_activity_at).total_seconds() if message_activity_at else None
        roster_age = age_seconds(roster_updated, now)
        if message_age is not None and message_age <= thresholds.slow_seconds:
            label = LABEL_IDLE
            reason = "no H1 heartbeat; recent coordination message is fallback activity evidence"
        elif message_age is not None and message_age <= thresholds.dead_seconds:
            label = LABEL_STALE_WARNING
            reason = "no H1 heartbeat; coordination message activity exceeded slow window"
        elif message_age is not None:
            label = LABEL_DEAD
            reason = "no H1 heartbeat and coordination message activity exceeded dead window"
        elif roster_age is not None and roster_age < 0:
            label = LABEL_STALE_WARNING
            reason = f"no H1 heartbeat; roster timestamp is future-dated by {abs(round(roster_age, 3))}s"
        elif roster_age is not None and roster_age <= thresholds.slow_seconds:
            label = LABEL_STALE_WARNING
            reason = "no H1 heartbeat yet; recent roster update is fallback evidence only, not proof of life"
        elif roster_age is not None and roster_age <= thresholds.dead_seconds:
            label = LABEL_STALE_WARNING
            reason = "no H1 heartbeat yet; roster update exceeded slow window"
        else:
            label = LABEL_DEAD
            reason = "no heartbeat present in H2 DB"
        return LivenessStatus(
            project_id=project_id,
            slot=slot,
            instance_name=str(roster.get("chosen_name", "")),
            label=label,
            lifecycle_state=state,
            age_seconds=None if message_age is None and roster_age is None else round(
                message_age if message_age is not None else roster_age,
                3,
            ),
            suspicion_score=suspicion_score(
                message_age if message_age is not None else roster_age,
                [],
                thresholds.expected_interval_seconds,
            ),
            reason=reason,
            roster_current_task=roster_task,
            roster_blocked_on=str(roster.get("blocked_on", "")),
            roster_updated_at=roster_updated,
        )

    observed_at = str(heartbeat.get("observed_at", ""))
    age = age_seconds(observed_at, now)
    last_action = str(heartbeat.get("last_action_type", ""))
    current_task = str(heartbeat.get("current_task", ""))
    state = lifecycle_state(last_action, current_task, str(roster.get("current_task", "")))
    score_age = 0.0 if age is not None and age < 0 else age
    score = suspicion_score(score_age, intervals, thresholds.expected_interval_seconds)
    label = LABEL_ACTIVE_WORKING
    reason = "fresh heartbeat with active work signal"
    if state == "stood-down":
        label = LABEL_IDLE
        reason = "final/going-dark heartbeat recorded; not a crash"
    elif age is None:
        label = LABEL_STALE_WARNING
        reason = "heartbeat timestamp is unparseable"
    elif age < 0:
        skew = abs(age)
        if skew > thresholds.clock_skew_tolerance_seconds:
            label = LABEL_STALE_WARNING
            reason = (
                f"heartbeat timestamp is future-dated by {round(skew, 3)}s, beyond "
                f"clock skew tolerance {thresholds.clock_skew_tolerance_seconds}s; "
                "treating as clock anomaly, not freshness"
            )
        elif idle_like(last_action, current_task):
            label = LABEL_IDLE
            reason = "heartbeat is future-dated within clock skew tolerance and reports waiting/idle/blocked action"
        else:
            reason = "heartbeat is future-dated within clock skew tolerance; treating as fresh"
    elif age <= thresholds.active_seconds:
        if idle_like(last_action, current_task):
            label = LABEL_IDLE
            reason = "fresh heartbeat reports waiting/idle/blocked action"
    elif age <= thresholds.slow_seconds:
        label = LABEL_ACTIVE_SLOW
        reason = "heartbeat is late but inside slow window"
    elif age <= thresholds.dead_seconds:
        label = LABEL_STALE_WARNING
        reason = "heartbeat exceeded slow window but not dead window"
    elif score < thresholds.dead_suspicion_threshold:
        label = LABEL_STALE_WARNING
        reason = (
            "heartbeat exceeded dead window but adaptive suspicion is below "
            f"dead threshold {thresholds.dead_suspicion_threshold}"
        )
    else:
        label = LABEL_DEAD
        reason = "heartbeat exceeded dead window and adaptive suspicion threshold"

    return LivenessStatus(
        project_id=project_id,
        slot=slot,
        instance_name=str(heartbeat.get("instance_name", roster.get("chosen_name", ""))),
        label=label,
        observed_at=observed_at,
        age_seconds=None if age is None else round(age, 3),
        monotonic_counter=int(heartbeat.get("monotonic_counter", 0)),
        current_task=current_task,
        last_action_type=last_action,
        lifecycle_state=state,
        suspicion_score=score,
        work_signature_unchanged_count=unchanged_signature_count,
        reason=reason,
        heartbeat_present=True,
        roster_current_task=str(roster.get("current_task", "")),
        roster_blocked_on=str(roster.get("blocked_on", "")),
        roster_updated_at=str(roster.get("updated_at", "")),
    )


def classify_liveness(
    db_path: str | Path = wave25_coorddb.DEFAULT_DB_PATH,
    project_id: str = wave25_coorddb.DEFAULT_PROJECT_ID,
    now: datetime | None = None,
    thresholds: LivenessThresholds | None = None,
    messages_dir: str | Path | None = None,
) -> list[LivenessStatus]:
    thresholds = thresholds or LivenessThresholds()
    now = now or now_dt()
    with wave25_coorddb.coordination_db(db_path) as conn:
        roster_rows = {
            row["slot"]: dict(row)
            for row in conn.execute("SELECT * FROM roster WHERE project_id = ?", (project_id,))
        }
        heartbeat_rows = {
            row["slot"]: dict(row)
            for row in conn.execute("SELECT * FROM heartbeats WHERE project_id = ?", (project_id,))
        }
        message_activity = latest_message_activity_by_slot(messages_dir, roster_rows)
        slots = sorted(set(roster_rows) | set(heartbeat_rows))
        statuses = [
            classify_row(
                project_id,
                slot,
                heartbeat_rows.get(slot),
                roster_rows.get(slot),
                now,
                thresholds,
                heartbeat_intervals(conn, project_id, slot),
                work_signature_unchanged_count(conn, project_id, slot),
                message_activity.get(slot),
            )
            for slot in slots
        ]
    return statuses


def status_for_slot(statuses: list[LivenessStatus], slot: str) -> LivenessStatus | None:
    key = slot.casefold()
    return next((status for status in statuses if status.slot.casefold() == key), None)


def liveness_to_dict(statuses: list[LivenessStatus]) -> list[dict[str, Any]]:
    return [asdict(status) for status in statuses]


def format_text(statuses: list[LivenessStatus]) -> str:
    lines = ["Wave 2.5 Liveness", ""]
    if not statuses:
        lines.append("- no roster or heartbeat rows")
        return "\n".join(lines)
    for status in statuses:
        age = "none" if status.age_seconds is None else f"{status.age_seconds:.0f}s"
        lines.append(
            f"- {status.slot} / {status.instance_name or '(unnamed)'}: {status.label} "
            f"age={age} counter={status.monotonic_counter} lifecycle={status.lifecycle_state}; {status.reason}"
        )
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wave 2.5 heartbeat writer and liveness classifier.")
    parser.add_argument("--db", default=str(wave25_coorddb.DEFAULT_DB_PATH))
    parser.add_argument("--project-id", default=wave25_coorddb.DEFAULT_PROJECT_ID)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--active-seconds", type=int, default=DEFAULT_ACTIVE_SECONDS)
    parser.add_argument("--slow-seconds", type=int, default=DEFAULT_SLOW_SECONDS)
    parser.add_argument("--dead-seconds", type=int, default=DEFAULT_DEAD_SECONDS)
    parser.add_argument("--expected-interval-seconds", type=int, default=DEFAULT_EXPECTED_INTERVAL_SECONDS)
    parser.add_argument("--dead-suspicion-threshold", type=float, default=DEFAULT_DEAD_SUSPICION_THRESHOLD)
    parser.add_argument("--clock-skew-tolerance-seconds", type=int, default=DEFAULT_CLOCK_SKEW_TOLERANCE_SECONDS)
    parser.add_argument("--messages-dir", default="")
    sub = parser.add_subparsers(dest="command", required=True)

    beat = sub.add_parser("beat", help="Write one heartbeat.")
    beat.add_argument("--slot", required=True)
    beat.add_argument("--instance", required=True)
    beat.add_argument("--current-task", default="")
    beat.add_argument("--last-action-type", default="")
    beat.add_argument("--observed-at", default="")
    beat.add_argument("--counter", type=int)
    beat.add_argument("--status", default="active")

    sub.add_parser("classify", help="Classify all known slots.")
    return parser.parse_args(argv)


def thresholds_from_args(args: argparse.Namespace) -> LivenessThresholds:
    return LivenessThresholds(
        active_seconds=args.active_seconds,
        slow_seconds=args.slow_seconds,
        dead_seconds=args.dead_seconds,
        expected_interval_seconds=args.expected_interval_seconds,
        dead_suspicion_threshold=args.dead_suspicion_threshold,
        clock_skew_tolerance_seconds=args.clock_skew_tolerance_seconds,
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.command == "beat":
        result = write_heartbeat(
            db_path=args.db,
            project_id=args.project_id,
            slot=args.slot,
            instance_name=args.instance,
            current_task=args.current_task,
            last_action_type=args.last_action_type,
            observed_at=args.observed_at or None,
            monotonic_counter=args.counter,
            status=args.status,
        )
        if args.format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(
                f"heartbeat: {result['slot']} / {result['instance_name']} "
                f"counter={result['monotonic_counter']} observed_at={result['observed_at']}"
            )
        return 0

    statuses = classify_liveness(
        args.db,
        args.project_id,
        thresholds=thresholds_from_args(args),
        messages_dir=args.messages_dir or None,
    )
    if args.format == "json":
        print(json.dumps(liveness_to_dict(statuses), indent=2, ensure_ascii=False))
    else:
        print(format_text(statuses))
    return 0 if all(status.label != LABEL_DEAD for status in statuses) else 1


if __name__ == "__main__":
    raise SystemExit(main())

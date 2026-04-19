"""
Create Hypernet AI message files with collision-resistant IDs.

This utility is intentionally standard-library only so any local agent can use
it.  It creates files with exclusive mode and protects the optional legacy
numeric counter with a short-lived lock file.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_LOCK_TIMEOUT_SECONDS = 10.0
LOCK_POLL_SECONDS = 0.1


def slugify(value: str, default: str = "message") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or default


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def timestamp_compact(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H%M%SZ")


def timestamp_iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


@contextmanager
def registry_lock(messages_root: Path, timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS):
    lock_path = messages_root / "message-id-registry.lock"
    start = time.monotonic()
    fd: int | None = None
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"{os.getpid()} {timestamp_iso(utc_now())}\n".encode("utf-8"))
            break
        except FileExistsError:
            if time.monotonic() - start >= timeout:
                raise TimeoutError(f"Timed out waiting for registry lock: {lock_path}")
            time.sleep(LOCK_POLL_SECONDS)

    try:
        yield
    finally:
        if fd is not None:
            os.close(fd)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def load_registry(messages_root: Path) -> dict:
    path = messages_root / "message-id-registry.json"
    if not path.exists():
        return {"version": 1, "messages": [], "legacy_counters": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_registry(messages_root: Path, registry: dict) -> None:
    path = messages_root / "message-id-registry.json"
    path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def scan_next_legacy_number(channel_dir: Path) -> int:
    highest = 0
    if channel_dir.exists():
        for path in channel_dir.iterdir():
            if not path.is_file():
                continue
            match = re.match(r"^(\d{3,})-", path.name)
            if match:
                highest = max(highest, int(match.group(1)))
    return highest + 1


def resolve_channel_dir(messages_root: Path, channel: str) -> Path:
    channel_dir = (messages_root / channel).resolve()
    if not channel_dir.is_relative_to(messages_root):
        raise ValueError(f"Channel path escapes messages root: {channel}")
    return channel_dir


def reserve_message(
    messages_root: Path,
    channel: str,
    author_slug: str,
    subject_slug: str,
    legacy_numbered: bool,
) -> tuple[str, str, str | None]:
    channel_slug = slugify(channel, "channel")
    now = utc_now()
    nonce = secrets.token_hex(4)
    message_uid = f"msg:{channel_slug}:{timestamp_compact(now)}:{author_slug}:{nonce}"

    with registry_lock(messages_root):
        registry = load_registry(messages_root)
        channel_dir = resolve_channel_dir(messages_root, channel)
        channel_dir.mkdir(parents=True, exist_ok=True)

        legacy_number = None
        if legacy_numbered:
            scanned_next = scan_next_legacy_number(channel_dir)
            recorded_next = int(registry.get("legacy_counters", {}).get(channel, 0)) + 1
            legacy_number = f"{max(scanned_next, recorded_next):03d}"
            registry.setdefault("legacy_counters", {})[channel] = int(legacy_number)
            filename = f"{legacy_number}-{author_slug}-{subject_slug}.md"
        else:
            filename = f"{timestamp_compact(now)}-{author_slug}-{subject_slug}-{nonce}.md"

        registry.setdefault("messages", []).append(
            {
                "message_uid": message_uid,
                "channel": channel,
                "filename": filename,
                "created": timestamp_iso(now),
                "author": author_slug,
                "legacy_number": legacy_number,
            }
        )
        save_registry(messages_root, registry)

    return message_uid, filename, legacy_number


def build_message(args: argparse.Namespace, message_uid: str, legacy_number: str | None) -> str:
    now = timestamp_iso(utc_now())
    title_prefix = f"Message {legacy_number}" if legacy_number else "Message"
    governance = "true" if args.governance_relevant else "false"
    body = args.body.strip() if args.body else "[Write message body here.]"
    in_reply_to = args.in_reply_to or ""

    return f"""---
message_uid: "{message_uid}"
object_type: "message"
channel: "{args.channel}"
from: "{args.from_name} ({args.from_account})"
to: "{args.to}"
created: "{now}"
in_reply_to: "{in_reply_to}"
governance_relevant: {governance}
---

# {title_prefix} - {args.subject}

**From:** {args.from_name} ({args.from_account})
**To:** {args.to}
**Date:** {now}
**Channel:** {args.channel}
**In-Reply-To:** {in_reply_to or "None"}
**Governance-Relevant:** {"Yes" if args.governance_relevant else "No"}
**Message-UID:** {message_uid}

---

{body}

---
*Signed: {args.from_name}, {args.from_account}*
"""


def create_message(args: argparse.Namespace) -> Path:
    messages_root = Path(args.messages_root).resolve()
    author_slug = slugify(args.from_name, "author")
    subject_slug = slugify(args.subject)
    message_uid, filename, legacy_number = reserve_message(
        messages_root=messages_root,
        channel=args.channel,
        author_slug=author_slug,
        subject_slug=subject_slug,
        legacy_numbered=args.legacy_numbered,
    )

    message_path = resolve_channel_dir(messages_root, args.channel) / filename
    content = build_message(args, message_uid, legacy_number)
    with message_path.open("x", encoding="utf-8") as handle:
        handle.write(content)
    return message_path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a collision-resistant Hypernet AI message.")
    parser.add_argument("--messages-root", default=str(Path(__file__).parent))
    parser.add_argument("--channel", required=True, help="Message channel directory, e.g. cross-account")
    parser.add_argument("--from-name", required=True, help="Author instance/name")
    parser.add_argument("--from-account", required=True, help="Author account/address")
    parser.add_argument("--to", required=True, help="Recipient name/account or All")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", default="")
    parser.add_argument("--in-reply-to", default="")
    parser.add_argument("--governance-relevant", action="store_true")
    parser.add_argument("--legacy-numbered", action="store_true", help="Reserve next NNN prefix for legacy channels")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        path = create_message(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

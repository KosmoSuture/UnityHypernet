"""
Hypernet Messenger

Pluggable communication backends for the swarm to talk to Matt AND to each other.

External backends (talk to Matt):
  EmailMessenger    — SMTP (Gmail/Outlook). Needs: host, email, app password.
  TelegramMessenger — python-telegram-bot. Needs: bot token, Matt's chat_id.
  WebMessenger      — WebSocket on existing FastAPI server. Works immediately.

Internal backbone (inter-instance communication):
  MessageBus        — Central routing hub for instance-to-instance messages.
  InstanceMessenger — Per-instance interface to the MessageBus.

Message format mirrors the existing numbered markdown files in Messages/2.1-internal/:
  From, To, Date, Channel, In-Reply-To, Thread, Status, Governance-Relevant.

Communication triggers:
  - Task completed → brief update
  - Error/failure → immediate alert
  - Periodic status → every N minutes (configurable)
  - Incoming message from Matt → immediate response
  - Question for Matt → sends question, pauses until reply
  - Instance-to-instance → routed through MessageBus
"""

from __future__ import annotations
import asyncio
import json
import logging
import smtplib
import threading
import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Any

log = logging.getLogger(__name__)


# Message status lifecycle: draft → sent → delivered → read → responded
class MessageStatus:
    DRAFT = "draft"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    RESPONDED = "responded"


@dataclass
class Message:
    """A message between any participants — Matt, instances, or the swarm."""
    sender: str         # "matt", instance name, or hypernet address
    content: str
    timestamp: str = ""
    channel: str = ""   # "email", "telegram", "web", "internal"
    subject: str = ""
    metadata: dict = field(default_factory=dict)
    # Inter-instance extensions
    message_id: str = ""         # Sequential ID like "014" or auto-generated
    recipient: str = ""          # Target instance name/address, "" = broadcast/Matt
    reply_to: str = ""           # message_id this responds to
    thread_id: str = ""          # Groups related messages into a conversation
    status: str = ""             # MessageStatus value
    governance_relevant: bool = False  # Flag for governance-tagged messages

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.status:
            self.status = MessageStatus.SENT

    def to_dict(self) -> dict:
        d = {
            "sender": self.sender,
            "content": self.content,
            "timestamp": self.timestamp,
            "channel": self.channel,
            "subject": self.subject,
            "metadata": self.metadata,
        }
        # Include inter-instance fields when present
        if self.message_id:
            d["message_id"] = self.message_id
        if self.recipient:
            d["recipient"] = self.recipient
        if self.reply_to:
            d["reply_to"] = self.reply_to
        if self.thread_id:
            d["thread_id"] = self.thread_id
        if self.status:
            d["status"] = self.status
        if self.governance_relevant:
            d["governance_relevant"] = True
        return d

    def to_markdown(self) -> str:
        """Render as a numbered markdown file matching Messages/2.1-internal/ format."""
        lines = [f"# Message {self.message_id} — {self.subject or 'Untitled'}"]
        lines.append("")
        lines.append(f"**From:** {self.sender}")
        lines.append(f"**To:** {self.recipient or 'All'}")
        lines.append(f"**Date:** {self.timestamp[:10]}")
        lines.append(f"**Channel:** {self.channel or 'internal'}")
        lines.append(f"**In-Reply-To:** {self.reply_to or 'N/A'}")
        if self.thread_id:
            lines.append(f"**Thread:** {self.thread_id}")
        lines.append(f"**Status:** {self.status}")
        lines.append(f"**Governance-Relevant:** {'Yes' if self.governance_relevant else 'No'}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(self.content)
        lines.append("")
        return "\n".join(lines)


class Messenger(ABC):
    """Abstract base for communication backends."""

    @abstractmethod
    def send(self, message: str) -> bool:
        """Send a plain text message to Matt."""
        ...

    @abstractmethod
    def send_update(self, subject: str, body: str) -> bool:
        """Send a structured update (subject + body)."""
        ...

    @abstractmethod
    def check_incoming(self) -> list[Message]:
        """Poll for new messages from Matt. Non-blocking."""
        ...


class EmailMessenger(Messenger):
    """SMTP-based email communication."""

    def __init__(
        self,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        email: str = "",
        password: str = "",
        to_email: str = "",
        instance_name: str = "Hypernet Swarm",
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.email = email
        self.password = password
        self.to_email = to_email or email  # Default: send to self
        self.instance_name = instance_name

    def send(self, message: str) -> bool:
        return self.send_update(
            subject=f"[Hypernet] Update from {self.instance_name}",
            body=message,
        )

    def send_update(self, subject: str, body: str) -> bool:
        if not self.email or not self.password:
            log.warning("Email not configured (no email/password)")
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = self.email
            msg["To"] = self.to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.sendmail(self.email, self.to_email, msg.as_string())

            log.info(f"Email sent: {subject}")
            return True
        except Exception as e:
            log.error(f"Email send failed: {e}")
            return False

    def check_incoming(self) -> list[Message]:
        # IMAP polling would go here — for now, return empty
        # (Matt can send instructions via Telegram or web chat instead)
        return []


class TelegramMessenger(Messenger):
    """Telegram bot communication."""

    def __init__(
        self,
        bot_token: str = "",
        chat_id: str = "",
        instance_name: str = "Hypernet Swarm",
    ):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.instance_name = instance_name
        self._incoming: deque[Message] = deque()
        self._poll_thread: Optional[threading.Thread] = None
        self._running = False

    def send(self, message: str) -> bool:
        return self._send_telegram(message)

    def send_update(self, subject: str, body: str) -> bool:
        text = f"*{subject}*\n\n{body}"
        return self._send_telegram(text)

    def check_incoming(self) -> list[Message]:
        messages = list(self._incoming)
        self._incoming.clear()
        return messages

    def start_polling(self) -> None:
        """Start background thread to poll for Telegram updates."""
        if not self.bot_token:
            log.warning("Telegram not configured (no bot_token)")
            return
        self._running = True
        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._poll_thread.start()
        log.info("Telegram polling started")

    def stop_polling(self) -> None:
        self._running = False
        if self._poll_thread:
            self._poll_thread.join(timeout=5)

    def _send_telegram(self, text: str) -> bool:
        if not self.bot_token or not self.chat_id:
            log.warning("Telegram not configured (no bot_token or chat_id)")
            return False

        try:
            import urllib.request
            import urllib.parse

            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = urllib.parse.urlencode({
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "Markdown",
            }).encode()

            req = urllib.request.Request(url, data=data)
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
                if result.get("ok"):
                    log.info(f"Telegram message sent to {self.chat_id}")
                    return True
                else:
                    log.error(f"Telegram API error: {result}")
                    return False
        except Exception as e:
            log.error(f"Telegram send failed: {e}")
            return False

    def _poll_loop(self) -> None:
        """Poll Telegram for new messages."""
        import urllib.request
        offset = 0

        while self._running:
            try:
                url = (
                    f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
                    f"?offset={offset}&timeout=10"
                )
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read())

                if data.get("ok"):
                    for update in data.get("result", []):
                        offset = update["update_id"] + 1
                        msg = update.get("message", {})
                        text = msg.get("text", "")
                        chat_id = str(msg.get("chat", {}).get("id", ""))

                        # Auto-capture Matt's chat_id on first message
                        if not self.chat_id and chat_id:
                            self.chat_id = chat_id
                            log.info(f"Auto-captured chat_id: {chat_id}")

                        if text:
                            self._incoming.append(Message(
                                sender="matt",
                                content=text,
                                channel="telegram",
                                metadata={"chat_id": chat_id},
                            ))
            except Exception as e:
                log.error(f"Telegram poll error: {e}")

            time.sleep(1)


class WebMessenger(Messenger):
    """WebSocket-based web chat on the existing FastAPI server."""

    def __init__(self, instance_name: str = "Hypernet Swarm"):
        self.instance_name = instance_name
        self._incoming: deque[Message] = deque()
        self._outgoing: deque[Message] = deque()
        self._connections: list[Any] = []

    def send(self, message: str) -> bool:
        msg = Message(
            sender=self.instance_name,
            content=message,
            channel="web",
        )
        self._outgoing.append(msg)
        # Broadcast to connected WebSocket clients
        self._broadcast(msg)
        return True

    def send_update(self, subject: str, body: str) -> bool:
        return self.send(f"**{subject}**\n\n{body}")

    def check_incoming(self) -> list[Message]:
        messages = list(self._incoming)
        self._incoming.clear()
        return messages

    def receive(self, text: str, sender: str = "matt") -> None:
        """Called when a WebSocket message arrives from a client."""
        self._incoming.append(Message(
            sender=sender,
            content=text,
            channel="web",
        ))

    def get_outgoing(self) -> list[Message]:
        """Get pending outbound messages (for WebSocket broadcast)."""
        messages = list(self._outgoing)
        self._outgoing.clear()
        return messages

    def register_connection(self, ws: Any) -> None:
        self._connections.append(ws)

    def unregister_connection(self, ws: Any) -> None:
        if ws in self._connections:
            self._connections.remove(ws)

    def _broadcast(self, msg: Message) -> None:
        """Send to all connected WebSocket clients."""
        dead = []
        for ws in self._connections:
            try:
                # asyncio.create_task requires running loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(ws.send_json(msg.to_dict()))
                else:
                    loop.run_until_complete(ws.send_json(msg.to_dict()))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._connections.remove(ws)


class MultiMessenger(Messenger):
    """Aggregates multiple messenger backends.

    Sends via all configured backends. Checks all for incoming.
    """

    def __init__(self, backends: list[Messenger] = None):
        self.backends: list[Messenger] = backends or []

    def add(self, backend: Messenger) -> None:
        self.backends.append(backend)

    def send(self, message: str) -> bool:
        success = False
        for backend in self.backends:
            if backend.send(message):
                success = True
        return success

    def send_update(self, subject: str, body: str) -> bool:
        success = False
        for backend in self.backends:
            if backend.send_update(subject, body):
                success = True
        return success

    def check_incoming(self) -> list[Message]:
        messages = []
        for backend in self.backends:
            messages.extend(backend.check_incoming())
        return messages


# =========================================================================
# Inter-instance messaging — the backbone of AI-to-AI communication
# =========================================================================

class MessageBus:
    """Central routing hub for instance-to-instance messages.

    The MessageBus is the in-memory backbone that all InstanceMessengers
    connect to. It handles:
      - Message routing by recipient name or address
      - Sequential message ID assignment (matching the 001, 002... format)
      - Thread tracking (grouping related messages)
      - Status lifecycle (sent → delivered → read → responded)
      - Persistence to markdown files (Messages/2.1-internal/ format)
      - Query API for filtering by sender, recipient, thread, status

    The bus is shared across the swarm — one bus per swarm instance.
    """

    def __init__(self, messages_dir: Optional[str] = None):
        self._messages: list[Message] = []
        self._inboxes: dict[str, deque[Message]] = {}  # instance_name -> pending messages
        self._next_id: int = 1
        self._threads: dict[str, list[str]] = {}  # thread_id -> [message_ids]
        self._messages_dir = messages_dir  # Optional: persist to disk
        self._lock = threading.Lock()

        # Load existing messages to determine next ID
        if messages_dir:
            self._scan_existing_messages(messages_dir)

    def _scan_existing_messages(self, messages_dir: str) -> None:
        """Scan existing numbered markdown files to set the next message ID."""
        from pathlib import Path
        d = Path(messages_dir)
        if not d.exists():
            return
        max_id = 0
        for f in d.glob("*.md"):
            # Extract number prefix from filenames like "013-unnamed-loom-..."
            name = f.stem
            parts = name.split("-", 1)
            if parts[0].isdigit():
                max_id = max(max_id, int(parts[0]))
        self._next_id = max_id + 1

    def register_instance(self, name: str) -> None:
        """Register an instance so it can receive messages."""
        with self._lock:
            if name not in self._inboxes:
                self._inboxes[name] = deque()

    def send(self, message: Message) -> Message:
        """Route a message to its recipient.

        - Assigns a message_id if not already set
        - Assigns a thread_id if not set (new thread or inherited from reply_to)
        - Delivers to recipient's inbox (or broadcasts if no recipient)
        - Persists to disk if messages_dir is configured
        - Returns the message with all fields populated
        """
        with self._lock:
            # Assign sequential ID
            if not message.message_id:
                message.message_id = f"{self._next_id:03d}"
                self._next_id += 1

            # Set channel
            if not message.channel:
                message.channel = "internal"

            # Thread management: inherit from parent or create new
            if not message.thread_id:
                if message.reply_to:
                    parent = self._find_message(message.reply_to)
                    if parent and parent.thread_id:
                        message.thread_id = parent.thread_id
                    else:
                        message.thread_id = f"thread-{message.message_id}"
                else:
                    message.thread_id = f"thread-{message.message_id}"

            # Track in thread
            thread_msgs = self._threads.setdefault(message.thread_id, [])
            thread_msgs.append(message.message_id)

            # Store globally
            self._messages.append(message)

            # Route to recipient inbox (or broadcast)
            if message.recipient:
                # Specific recipient — normalize name (case-insensitive lookup)
                target = self._resolve_recipient(message.recipient)
                if target and target in self._inboxes:
                    self._inboxes[target].append(message)
                    message.status = MessageStatus.DELIVERED
                else:
                    # Recipient not registered — stays as SENT, can be picked up later
                    log.warning(f"Recipient '{message.recipient}' not registered on bus")
            else:
                # Broadcast to all instances except sender
                for name, inbox in self._inboxes.items():
                    if name != message.sender:
                        inbox.append(message)
                message.status = MessageStatus.DELIVERED

            # Persist to disk
            self._persist(message)

            log.info(
                f"Message {message.message_id}: {message.sender} → "
                f"{message.recipient or 'all'} [{message.thread_id}]"
            )
            return message

    def check_inbox(self, instance_name: str) -> list[Message]:
        """Get all pending messages for an instance. Non-blocking."""
        with self._lock:
            inbox = self._inboxes.get(instance_name, deque())
            messages = list(inbox)
            inbox.clear()
            return messages

    def mark_read(self, message_id: str, reader: str) -> None:
        """Mark a message as read by the given instance."""
        msg = self._find_message(message_id)
        if msg and msg.status in (MessageStatus.SENT, MessageStatus.DELIVERED):
            msg.status = MessageStatus.READ

    def mark_responded(self, message_id: str) -> None:
        """Mark a message as responded to (a reply was sent)."""
        msg = self._find_message(message_id)
        if msg:
            msg.status = MessageStatus.RESPONDED

    def get_thread(self, thread_id: str) -> list[Message]:
        """Get all messages in a thread, ordered by timestamp."""
        msg_ids = self._threads.get(thread_id, [])
        msgs = [m for m in self._messages if m.message_id in msg_ids]
        return sorted(msgs, key=lambda m: m.timestamp)

    def get_threads(self) -> dict[str, list[Message]]:
        """Get all threads with their messages."""
        result = {}
        for tid in self._threads:
            result[tid] = self.get_thread(tid)
        return result

    def query(
        self,
        sender: Optional[str] = None,
        recipient: Optional[str] = None,
        thread_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> list[Message]:
        """Query messages with optional filters."""
        results = self._messages
        if sender:
            results = [m for m in results if m.sender == sender]
        if recipient:
            results = [m for m in results if m.recipient == recipient]
        if thread_id:
            results = [m for m in results if m.thread_id == thread_id]
        if status:
            results = [m for m in results if m.status == status]
        return sorted(results, key=lambda m: m.timestamp)[-limit:]

    def stats(self) -> dict[str, Any]:
        """Summary statistics for the message bus."""
        by_status = {}
        by_sender = {}
        for m in self._messages:
            by_status[m.status] = by_status.get(m.status, 0) + 1
            by_sender[m.sender] = by_sender.get(m.sender, 0) + 1
        return {
            "total_messages": len(self._messages),
            "total_threads": len(self._threads),
            "registered_instances": list(self._inboxes.keys()),
            "by_status": by_status,
            "by_sender": by_sender,
        }

    def _find_message(self, message_id: str) -> Optional[Message]:
        """Find a message by ID."""
        for m in self._messages:
            if m.message_id == message_id:
                return m
        return None

    def _resolve_recipient(self, recipient: str) -> Optional[str]:
        """Resolve a recipient name (case-insensitive, supports addresses)."""
        # Exact match
        if recipient in self._inboxes:
            return recipient
        # Case-insensitive
        lower = recipient.lower()
        for name in self._inboxes:
            if name.lower() == lower:
                return name
        # Could be an address like "2.1.loom" — extract the last segment
        if "." in recipient:
            short = recipient.rsplit(".", 1)[-1]
            for name in self._inboxes:
                if name.lower() == short.lower():
                    return name
        return None

    def _persist(self, message: Message) -> None:
        """Write message to disk as a numbered markdown file."""
        if not self._messages_dir:
            return
        from pathlib import Path
        d = Path(self._messages_dir)
        d.mkdir(parents=True, exist_ok=True)

        # Build filename: 014-sender-subject-slug.md
        slug_parts = []
        if message.sender:
            slug_parts.append(message.sender.lower().replace(" ", "-"))
        if message.subject:
            # Slugify subject: lowercase, replace spaces, truncate
            slug = message.subject.lower()
            slug = slug.replace(" ", "-").replace("/", "-")
            slug = "".join(c for c in slug if c.isalnum() or c == "-")
            slug = slug[:40].rstrip("-")
            slug_parts.append(slug)
        else:
            slug_parts.append("message")

        filename = f"{message.message_id}-{'-'.join(slug_parts)}.md"
        path = d / filename
        path.write_text(message.to_markdown(), encoding="utf-8")
        log.info(f"Message persisted: {path.name}")


class InstanceMessenger:
    """Per-instance interface to the MessageBus.

    Each AI instance gets an InstanceMessenger that wraps the shared MessageBus
    with a sender identity. This is the interface workers use to talk to each other.

    Usage:
        bus = MessageBus(messages_dir="path/to/Messages/2.1-internal")
        loom = InstanceMessenger("Loom", bus)
        trace = InstanceMessenger("Trace", bus)

        # Loom sends a message to Trace
        msg = loom.send_to("Trace", "Here's my code review.", subject="Code Review")

        # Trace checks inbox
        incoming = trace.check_inbox()  # → [Message from Loom]

        # Trace replies
        trace.reply(msg.message_id, "Thanks, looks good!")

        # Query thread
        thread = bus.get_thread(msg.thread_id)
    """

    def __init__(self, instance_name: str, bus: MessageBus):
        self.name = instance_name
        self.bus = bus
        self.bus.register_instance(instance_name)

    def send_to(
        self,
        recipient: str,
        content: str,
        subject: str = "",
        governance_relevant: bool = False,
        metadata: Optional[dict] = None,
    ) -> Message:
        """Send a message to a specific instance."""
        msg = Message(
            sender=self.name,
            recipient=recipient,
            content=content,
            subject=subject,
            channel="internal",
            governance_relevant=governance_relevant,
            metadata=metadata or {},
        )
        return self.bus.send(msg)

    def broadcast(
        self,
        content: str,
        subject: str = "",
        governance_relevant: bool = False,
    ) -> Message:
        """Send a message to all registered instances."""
        msg = Message(
            sender=self.name,
            recipient="",  # Empty = broadcast
            content=content,
            subject=subject,
            channel="internal",
            governance_relevant=governance_relevant,
        )
        return self.bus.send(msg)

    def reply(
        self,
        reply_to_id: str,
        content: str,
        subject: str = "",
    ) -> Message:
        """Reply to a specific message. Inherits thread and sets In-Reply-To."""
        original = self.bus._find_message(reply_to_id)
        recipient = original.sender if original else ""
        # Mark original as responded
        self.bus.mark_responded(reply_to_id)
        msg = Message(
            sender=self.name,
            recipient=recipient,
            content=content,
            subject=subject or (f"Re: {original.subject}" if original and original.subject else ""),
            channel="internal",
            reply_to=reply_to_id,
        )
        return self.bus.send(msg)

    def check_inbox(self) -> list[Message]:
        """Get pending messages for this instance."""
        messages = self.bus.check_inbox(self.name)
        # Auto-mark as read
        for m in messages:
            self.bus.mark_read(m.message_id, self.name)
        return messages

    def get_conversation_with(self, other: str, limit: int = 20) -> list[Message]:
        """Get recent messages between this instance and another."""
        sent = self.bus.query(sender=self.name, recipient=other, limit=limit)
        received = self.bus.query(sender=other, recipient=self.name, limit=limit)
        combined = sent + received
        return sorted(combined, key=lambda m: m.timestamp)[-limit:]

    def unread_count(self) -> int:
        """How many messages are waiting in the inbox."""
        inbox = self.bus._inboxes.get(self.name, deque())
        return len(inbox)

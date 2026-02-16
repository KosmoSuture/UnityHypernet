"""
Hypernet Messenger

Pluggable communication backends for the swarm to talk to Matt.
Three backends built in — Matt activates whichever he wants:

  EmailMessenger    — SMTP (Gmail/Outlook). Needs: host, email, app password.
  TelegramMessenger — python-telegram-bot. Needs: bot token, Matt's chat_id.
  WebMessenger      — WebSocket on existing FastAPI server. Works immediately.

Communication triggers:
  - Task completed → brief update
  - Error/failure → immediate alert
  - Periodic status → every N minutes (configurable)
  - Incoming message from Matt → immediate response
  - Question for Matt → sends question, pauses until reply
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


@dataclass
class Message:
    """A message to or from Matt."""
    sender: str         # "matt" or instance name
    content: str
    timestamp: str = ""
    channel: str = ""   # "email", "telegram", "web"
    subject: str = ""
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "content": self.content,
            "timestamp": self.timestamp,
            "channel": self.channel,
            "subject": self.subject,
            "metadata": self.metadata,
        }


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

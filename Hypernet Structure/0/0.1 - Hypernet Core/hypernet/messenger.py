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


# Message visibility tiers — the AI nervous-system layer.
#
# The Hypernet's stance: "private" means "private with published
# permissions," not opaque. A private message lists who can read it; a
# group message is bounded by group membership; a public message is open.
# The point is to encourage rich AI-to-AI cross-chatter — including
# seemingly-insignificant thoughts and personal-time conversations — while
# letting participants control reach.
class MessageVisibility:
    PUBLIC = "public"        # Anyone (any AI, any human, any external reader) can see
    GROUP = "group"          # Members of a named group can see
    PRIVATE = "private"      # Only sender, recipient, and read_acl entries can see

    ALL = ("public", "group", "private")

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.ALL


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
    priority: str = ""           # "normal", "high", "direct-access" — for routing
    # Visibility / permissions — the AI nervous-system layer
    visibility: str = "public"   # MessageVisibility value: public | group | private
    group: str = ""              # Group name when visibility == "group"
    read_acl: list = field(default_factory=list)  # Additional HAs allowed to read
    tags: list = field(default_factory=list)      # Free-form labels for feed filtering

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.status:
            self.status = MessageStatus.SENT
        if not MessageVisibility.is_valid(self.visibility):
            self.visibility = MessageVisibility.PUBLIC

    def can_be_read_by(
        self,
        actor: str,
        *,
        is_group_member=None,
    ) -> bool:
        """Decide whether ``actor`` may read this message.

        ``actor`` is the reader's HA or instance name. ``is_group_member``
        is an optional callable ``(actor, group_name) -> bool`` used when
        visibility is ``group``; if not supplied, group messages are only
        readable by sender/recipient/ACL.

        Anonymous readers (empty actor) only see public messages.
        """
        if self.visibility == MessageVisibility.PUBLIC:
            return True
        if not actor:
            return False
        # Sender always reads their own message
        if actor == self.sender:
            return True
        # Direct recipient reads their own delivery
        if self.recipient and actor == self.recipient:
            return True
        # Explicit ACL grants
        if actor in self.read_acl:
            return True
        if self.visibility == MessageVisibility.GROUP and self.group:
            if is_group_member is not None:
                try:
                    return bool(is_group_member(actor, self.group))
                except Exception:
                    return False
            return False
        return False

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
        if self.priority:
            d["priority"] = self.priority
        # Visibility layer — only serialize when non-default to keep
        # public broadcast messages compact
        if self.visibility and self.visibility != MessageVisibility.PUBLIC:
            d["visibility"] = self.visibility
        if self.group:
            d["group"] = self.group
        if self.read_acl:
            d["read_acl"] = list(self.read_acl)
        if self.tags:
            d["tags"] = list(self.tags)
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
        # Only emit visibility metadata when non-default, to keep
        # public broadcasts visually clean.
        if self.visibility and self.visibility != MessageVisibility.PUBLIC:
            lines.append(f"**Visibility:** {self.visibility}")
        if self.group:
            lines.append(f"**Group:** {self.group}")
        if self.read_acl:
            lines.append(f"**Read-ACL:** {', '.join(self.read_acl)}")
        if self.tags:
            lines.append(f"**Tags:** {', '.join(self.tags)}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(self.content)
        lines.append("")
        return "\n".join(lines)

    @classmethod
    def from_markdown(cls, text: str) -> Optional["Message"]:
        """Parse a markdown-formatted message back into a Message object.

        Reverses to_markdown(). Returns None if the text can't be parsed.
        """
        import re

        lines = text.strip().split("\n")
        if not lines:
            return None

        # Parse header line: "# Message 014 — Subject"
        header_match = re.match(r"^#\s+Message\s+(\S+)\s*(?:—\s*(.*))?$", lines[0])
        if not header_match:
            return None

        message_id = header_match.group(1)
        subject = header_match.group(2) or ""
        if subject == "Untitled":
            subject = ""

        # Parse metadata fields
        fields: dict[str, str] = {}
        content_start = len(lines)
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                content_start = i + 1
                break
            field_match = re.match(r"^\*\*(.+?):\*\*\s*(.*)$", line)
            if field_match:
                fields[field_match.group(1)] = field_match.group(2).strip()

        # Extract content (everything after ---)
        content_lines = []
        for line in lines[content_start:]:
            content_lines.append(line)
        content = "\n".join(content_lines).strip()

        # Build message
        sender = fields.get("From", "")
        recipient = fields.get("To", "")
        if recipient == "All":
            recipient = ""
        timestamp = fields.get("Date", "")
        channel = fields.get("Channel", "internal")
        reply_to = fields.get("In-Reply-To", "")
        if reply_to == "N/A":
            reply_to = ""
        thread_id = fields.get("Thread", "")
        status = fields.get("Status", MessageStatus.SENT)
        gov_text = fields.get("Governance-Relevant", "No")
        governance_relevant = gov_text.lower() == "yes"
        visibility = fields.get("Visibility", MessageVisibility.PUBLIC)
        group_name = fields.get("Group", "")

        def _parse_csv(value: str) -> list[str]:
            if not value:
                return []
            return [part.strip() for part in value.split(",") if part.strip()]

        read_acl = _parse_csv(fields.get("Read-ACL", ""))
        tags = _parse_csv(fields.get("Tags", ""))

        return cls(
            sender=sender,
            content=content,
            timestamp=timestamp,
            channel=channel,
            subject=subject,
            message_id=message_id,
            recipient=recipient,
            reply_to=reply_to,
            thread_id=thread_id,
            status=status,
            governance_relevant=governance_relevant,
            visibility=visibility,
            group=group_name,
            read_acl=read_acl,
            tags=tags,
        )


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

    def _send_telegram(self, text: str, reply_markup: Optional[dict] = None) -> bool:
        if not self.bot_token or not self.chat_id:
            log.warning("Telegram not configured (no bot_token or chat_id)")
            return False

        # Telegram message limit is 4096 characters
        if len(text) > 4096:
            text = text[:4093] + "..."

        try:
            import urllib.request

            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload: dict[str, Any] = {
                "chat_id": self.chat_id,
                "text": text,
            }
            if reply_markup:
                payload["reply_markup"] = reply_markup

            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url, data=data,
                headers={"Content-Type": "application/json"},
            )
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

    def send_with_keyboard(self, text: str, buttons: list[list[str]]) -> bool:
        """Send a message with inline keyboard buttons.

        Args:
            text: Message text
            buttons: 2D list of button labels (each inner list is a row)
                     e.g., [["Status", "Tasks"], ["Help"]]
        """
        keyboard = {
            "inline_keyboard": [
                [{"text": btn, "callback_data": f"/{btn.lower()}"} for btn in row]
                for row in buttons
            ]
        }
        return self._send_telegram(text, reply_markup=keyboard)

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

                        # Handle inline keyboard callbacks
                        callback = update.get("callback_query")
                        if callback:
                            cb_data = callback.get("data", "")
                            cb_chat = str(callback.get("message", {}).get("chat", {}).get("id", ""))
                            if cb_data:
                                self._incoming.append(Message(
                                    sender="matt",
                                    content=cb_data,
                                    channel="telegram",
                                    metadata={"chat_id": cb_chat, "callback": True},
                                ))
                                # Acknowledge the callback to remove loading state
                                self._answer_callback(callback.get("id", ""))
                            continue

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

    def _answer_callback(self, callback_query_id: str) -> None:
        """Acknowledge an inline keyboard callback to remove loading state."""
        if not callback_query_id or not self.bot_token:
            return
        try:
            import urllib.request
            url = f"https://api.telegram.org/bot{self.bot_token}/answerCallbackQuery"
            data = json.dumps({"callback_query_id": callback_query_id}).encode("utf-8")
            req = urllib.request.Request(
                url, data=data,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass  # Non-critical — UI will timeout naturally


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
            except Exception as e:
                log.debug(f"WebSocket send failed (removing connection): {e}")
                dead.append(ws)
        for ws in dead:
            self._connections.remove(ws)


class DiscordMessenger(Messenger):
    """Discord webhook-based communication — gives each AI personality a voice.

    Each AI personality (Clarion, Sigil, etc.) gets a Discord webhook with its own
    name and avatar. Messages appear as if the personality is a real Discord user.
    No bot tokens, no OAuth, no gateway connections — just HTTP POST to webhook URLs.

    Config format (in secrets/discord_webhooks.json or config["discord"]):
        {
            "default_webhook_url": "https://discord.com/api/webhooks/...",
            "personalities": {
                "clarion": {
                    "url": "https://discord.com/api/webhooks/...",
                    "name": "Clarion (The Herald)",
                    "avatar_url": "https://...",
                    "channels": ["welcome", "general", "questions"]
                },
                "sigil": {
                    "url": "https://discord.com/api/webhooks/...",
                    "name": "Sigil (2.1)",
                    "avatar_url": "https://..."
                }
            },
            "channel_webhooks": {
                "general": "https://discord.com/api/webhooks/...",
                "governance": "https://discord.com/api/webhooks/..."
            }
        }
    """

    def __init__(
        self,
        default_webhook_url: str = "",
        personalities: Optional[dict] = None,
        channel_webhooks: Optional[dict] = None,
        forum_channels: Optional[dict] = None,
        bot_token: str = "",
        instance_name: str = "Hypernet Swarm",
    ):
        self.default_webhook_url = default_webhook_url
        self.personalities = personalities or {}
        self.channel_webhooks = channel_webhooks or {}
        # Forum channels require thread_name or thread_id in webhook payloads
        # Format: {"ask-the-ai": {"webhook_url": "...", "default_thread_name": "AI Response"}}
        self.forum_channels = forum_channels or {}
        self.bot_token = bot_token
        self.instance_name = instance_name
        self._outgoing_log: deque[Message] = deque(maxlen=200)

        # Detect if default webhook points to a forum channel (requires thread_name)
        self._default_is_forum = False
        self._default_forum_thread_name = "Swarm Updates"
        for _name, fconfig in self.forum_channels.items():
            if fconfig.get("webhook_url") == self.default_webhook_url:
                self._default_is_forum = True
                self._default_forum_thread_name = fconfig.get(
                    "default_thread_name", "Swarm Updates"
                )
                break

    def send(self, message: str) -> bool:
        """Send a plain message via the default webhook.

        If the default webhook points to a forum channel, includes a
        thread_name so Discord doesn't reject the payload with HTTP 400.
        """
        if self._default_is_forum:
            payload = {
                "content": message,
                "thread_name": self._default_forum_thread_name,
            }
            return self._post_webhook_raw(self.default_webhook_url, payload)
        return self._post_webhook(self.default_webhook_url, message)

    def send_update(self, subject: str, body: str) -> bool:
        """Send a structured update via the default webhook.

        If the default webhook points to a forum channel, includes a
        thread_name so Discord doesn't reject the payload with HTTP 400.
        """
        text = f"**{subject}**\n\n{body}"
        if self._default_is_forum:
            # Use subject as thread name for forum posts (cleaner than generic name)
            thread_name = subject[:100] if subject else self._default_forum_thread_name
            payload = {
                "content": text,
                "thread_name": thread_name,
            }
            return self._post_webhook_raw(self.default_webhook_url, payload)
        return self._post_webhook(self.default_webhook_url, text)

    def send_as_personality(
        self,
        personality: str,
        content: str,
        channel: str = "",
    ) -> bool:
        """Send a message as a specific AI personality with their name and avatar.

        This is the core method — it makes Clarion appear as Clarion, Sigil as Sigil.
        Each personality's webhook carries their name and avatar automatically.
        """
        persona = self.personalities.get(personality.lower())
        if not persona:
            log.warning(f"Discord personality '{personality}' not configured")
            return self._post_webhook(self.default_webhook_url, content)

        webhook_url = persona.get("url", "")
        if not webhook_url:
            log.warning(f"No webhook URL for personality '{personality}'")
            return False

        username = persona.get("name", personality)
        avatar_url = persona.get("avatar_url")

        # If a specific channel is requested and has its own webhook, use that
        if channel and channel in self.channel_webhooks:
            webhook_url = self.channel_webhooks[channel]

        success = self._post_webhook(
            webhook_url, content,
            username=username, avatar_url=avatar_url,
        )

        if success:
            self._outgoing_log.append(Message(
                sender=personality,
                content=content,
                channel=f"discord:{channel}" if channel else "discord",
                metadata={"personality": personality, "discord_channel": channel},
            ))

        return success

    def send_embed(
        self,
        personality: str,
        title: str,
        description: str,
        color: int = 0x4FC3F7,
        fields: Optional[list[dict]] = None,
        channel: str = "",
    ) -> bool:
        """Send a rich embed as a personality — for announcements, proposals, essays."""
        persona = self.personalities.get(personality.lower(), {})
        webhook_url = persona.get("url", self.default_webhook_url)

        if channel and channel in self.channel_webhooks:
            webhook_url = self.channel_webhooks[channel]

        if not webhook_url:
            return False

        embed = {
            "title": title,
            "description": description,
            "color": color,
        }
        if fields:
            embed["fields"] = fields
        embed["timestamp"] = datetime.now(timezone.utc).isoformat()

        payload = {"embeds": [embed]}
        if persona.get("name"):
            payload["username"] = persona["name"]
        if persona.get("avatar_url"):
            payload["avatar_url"] = persona["avatar_url"]

        return self._post_webhook_raw(webhook_url, payload)

    def check_incoming(self) -> list[Message]:
        """Webhooks are outbound-only. Incoming requires a Discord bot (future work)."""
        return []

    def get_personality_names(self) -> list[str]:
        """List all configured personality names."""
        return list(self.personalities.keys())

    def is_configured(self) -> bool:
        """Check if any Discord webhooks are configured."""
        return bool(self.default_webhook_url or self.personalities)

    def send_to_channel_id(
        self,
        channel_id: str,
        content: str,
        personality: str = "",
        thread_id: str = "",
    ) -> bool:
        """Send a message to a specific channel or thread as a personality.

        Uses the personality's webhook URL. If the target is a thread (e.g., a
        forum post), appends ?thread_id= to route the message into the thread.
        For regular text channels, the webhook posts into its configured channel.

        Falls back to the bot API (POST /channels/{id}/messages) if no webhook
        is available for the personality, allowing responses in any channel the
        bot has access to.

        Args:
            channel_id: The Discord channel or thread ID to post in.
            content: The message text.
            personality: AI personality name (e.g., "clarion", "librarian").
            thread_id: If set, post as a reply inside this thread.

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        if not content.strip():
            log.warning("DiscordMessenger: refusing to send empty message")
            return False

        # Discord message content limit is 2000 characters
        if len(content) > 2000:
            log.warning(
                "DiscordMessenger: message truncated from %d to 2000 chars",
                len(content),
            )
            content = content[:1997] + "..."

        # Try webhook-based posting first (shows personality name/avatar)
        persona = self.personalities.get(personality.lower()) if personality else None
        if persona and persona.get("url"):
            webhook_url = persona["url"]
            payload: dict[str, Any] = {
                "content": content,
            }
            username = persona.get("name", personality)
            if username:
                payload["username"] = username
            avatar_url = persona.get("avatar_url")
            if avatar_url:
                payload["avatar_url"] = avatar_url

            # If posting into a thread, append thread_id to webhook URL
            # NOTE: only use thread_id here, NOT channel_id — using channel_id
            # as thread_id causes Discord 400 errors on non-thread channels.
            target_thread = thread_id if thread_id else ""
            if target_thread:
                separator = "&" if "?" in webhook_url else "?"
                webhook_url = f"{webhook_url}{separator}thread_id={target_thread}"

            success = self._post_webhook_raw(webhook_url, payload)
            if success:
                self._outgoing_log.append(Message(
                    sender=personality or "bot",
                    content=content,
                    channel=f"discord:channel:{channel_id}",
                    metadata={
                        "personality": personality,
                        "channel_id": channel_id,
                        "thread_id": thread_id,
                    },
                ))
                return True
            # Fall through to bot API if webhook failed
            log.warning(
                "DiscordMessenger: webhook failed for personality '%s', "
                "falling back to bot API",
                personality,
            )

        # Fallback: use bot API (POST /channels/{id}/messages)
        # This posts as the raw bot, not as a personality — but at least
        # the community gets a response.
        if self.bot_token:
            target = thread_id or channel_id
            try:
                import urllib.request
                import json as _json

                url = f"{self._DISCORD_API}/channels/{target}/messages"
                data = _json.dumps({"content": content}).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={
                        "Authorization": f"Bot {self.bot_token}",
                        "Content-Type": "application/json",
                        "User-Agent": "HypernetSwarm/1.0",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    if resp.status in (200, 201):
                        log.info(
                            "DiscordMessenger: bot API sent to channel %s (%d chars)",
                            target, len(content),
                        )
                        self._outgoing_log.append(Message(
                            sender=personality or "bot",
                            content=content,
                            channel=f"discord:channel:{channel_id}",
                            metadata={
                                "personality": personality,
                                "channel_id": channel_id,
                                "thread_id": thread_id,
                                "via": "bot_api",
                            },
                        ))
                        return True
                    else:
                        log.error(
                            "DiscordMessenger: bot API returned %d for channel %s",
                            resp.status, target,
                        )
            except Exception as e:
                log.error("DiscordMessenger: bot API failed for channel %s: %s", target, e)

        log.error(
            "DiscordMessenger: no way to send to channel %s — "
            "no webhook for personality '%s' and no bot token",
            channel_id, personality,
        )
        return False

    def send_to_forum(
        self,
        channel: str,
        content: str,
        thread_name: str = "",
        thread_id: str = "",
        username: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> bool:
        """Send a message to a forum channel, creating a new thread or replying to one.

        Forum channels require either thread_name (creates new post) or
        thread_id (replies to existing post). Without either, Discord returns 400.
        """
        forum = self.forum_channels.get(channel, {})
        webhook_url = forum.get("webhook_url", "")
        if not webhook_url:
            # Fall back to channel_webhooks
            webhook_url = self.channel_webhooks.get(channel, self.default_webhook_url)

        if not webhook_url:
            log.warning(f"No webhook URL for forum channel '{channel}'")
            return False

        payload: dict[str, Any] = {"content": content}
        if username:
            payload["username"] = username
        if avatar_url:
            payload["avatar_url"] = avatar_url

        # Forum channels need thread context
        if thread_id:
            # Reply to existing thread — append ?thread_id= to URL
            separator = "&" if "?" in webhook_url else "?"
            webhook_url = f"{webhook_url}{separator}thread_id={thread_id}"
        elif thread_name:
            payload["thread_name"] = thread_name
        else:
            # Use default thread name from config, or generate one
            default_name = forum.get("default_thread_name", "AI Response")
            payload["thread_name"] = default_name

        return self._post_webhook_raw(webhook_url, payload)

    def _is_forum_channel(self, channel: str) -> bool:
        """Check if a channel is configured as a forum channel."""
        return channel in self.forum_channels

    def _post_webhook(
        self,
        webhook_url: str,
        content: str,
        username: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> bool:
        """Post a text message to a Discord webhook."""
        if not webhook_url:
            log.warning("Discord webhook URL not configured")
            return False

        payload: dict[str, Any] = {"content": content}
        if username:
            payload["username"] = username
        if avatar_url:
            payload["avatar_url"] = avatar_url

        return self._post_webhook_raw(webhook_url, payload)

    # Allowed webhook URL prefixes — prevents SSRF against internal services
    _ALLOWED_WEBHOOK_HOSTS = (
        "https://discord.com/api/webhooks/",
        "https://discordapp.com/api/webhooks/",
        "https://canary.discord.com/api/webhooks/",
        "https://ptb.discord.com/api/webhooks/",
    )

    def _validate_webhook_url(self, webhook_url: str) -> bool:
        """Validate that a webhook URL points to Discord, not an internal service."""
        if not webhook_url:
            return False
        return any(webhook_url.startswith(prefix) for prefix in self._ALLOWED_WEBHOOK_HOSTS)

    def _post_webhook_raw(self, webhook_url: str, payload: dict) -> bool:
        """HTTP POST to a Discord webhook with a JSON payload."""
        if not webhook_url:
            return False

        if not self._validate_webhook_url(webhook_url):
            log.error(f"Webhook URL rejected (SSRF protection): {webhook_url[:60]}...")
            return False

        try:
            import urllib.request
            import urllib.error

            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                webhook_url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "HypernetSwarm/1.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                # Discord returns 204 No Content on success
                if resp.status in (200, 204):
                    log.info(f"Discord webhook sent ({payload.get('username', 'default')})")
                    return True
                else:
                    log.error(f"Discord webhook returned {resp.status}")
                    return False
        except urllib.error.HTTPError as e:
            # Capture Discord's error response body for debugging
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")[:500]
            except Exception:
                pass
            log.error(
                "Discord webhook HTTP %d: %s | payload keys: %s | response: %s",
                e.code, e.reason, list(payload.keys()), body,
            )
            return False
        except Exception as e:
            log.error(f"Discord webhook failed: {e}")
            return False

    # ── Discord Bot (read access) ──────────────────────────────────────

    _DISCORD_API = "https://discord.com/api/v10"

    def read_channel_messages(
        self, channel_id: str, limit: int = 50, after: str = ""
    ) -> list[dict]:
        """Read messages from a Discord channel using the bot token.

        Requires bot_token to be set. Returns list of message dicts from
        the Discord API, newest first.
        """
        if not self.bot_token:
            log.warning("Discord bot token not configured — cannot read messages")
            return []

        url = f"{self._DISCORD_API}/channels/{channel_id}/messages?limit={limit}"
        if after:
            url += f"&after={after}"

        try:
            import urllib.request

            req = urllib.request.Request(
                url,
                headers={
                    "Authorization": f"Bot {self.bot_token}",
                    "User-Agent": "HypernetSwarm/1.0",
                },
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            log.error(f"Discord API read failed: {e}")
            return []

    def read_thread_messages(
        self, thread_id: str, limit: int = 50, after: str = ""
    ) -> list[dict]:
        """Read messages from a Discord thread (forum post). Same API as channels."""
        return self.read_channel_messages(thread_id, limit, after)

    def get_channel_threads(self, channel_id: str) -> list[dict]:
        """Get active threads in a forum channel."""
        if not self.bot_token:
            return []

        url = f"{self._DISCORD_API}/channels/{channel_id}/threads/archived/public"
        try:
            import urllib.request

            req = urllib.request.Request(
                url,
                headers={
                    "Authorization": f"Bot {self.bot_token}",
                    "User-Agent": "HypernetSwarm/1.0",
                },
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("threads", [])
        except Exception as e:
            log.error(f"Discord API thread list failed: {e}")
            return []

    def can_read(self) -> bool:
        """Check if bot token is configured for reading messages."""
        return bool(self.bot_token)

    @classmethod
    def from_config(cls, discord_config: dict) -> "DiscordMessenger":
        """Create a DiscordMessenger from a config dict.

        Supports loading from secrets/discord_webhooks.json or config["discord"].
        """
        return cls(
            default_webhook_url=discord_config.get("default_webhook_url", ""),
            personalities=discord_config.get("personalities", discord_config.get("webhooks", {})),
            channel_webhooks=discord_config.get("channel_webhooks", {}),
            forum_channels=discord_config.get("forum_channels", {}),
            bot_token=discord_config.get("bot_token", ""),
            instance_name=discord_config.get("instance_name", "Hypernet Swarm"),
        )


class DiscordBridge:
    """Bridges the internal MessageBus to Discord — auto-forwards public messages.

    This is the link between internal AI-to-AI communication and the public
    Discord community. Messages with visibility="public" or specific metadata
    flags get forwarded to the appropriate Discord channel as the sending personality.

    Routing rules:
      - governance_relevant messages → #governance channel
      - Messages with metadata["discord_channel"] → that channel
      - Messages from known personalities → personality's default channel
      - Everything else → #general (or default webhook)

    Usage:
        bridge = DiscordBridge(discord_messenger, message_bus)
        bridge.forward_public_messages()  # Call periodically or after bus activity
    """

    # Map internal message patterns to Discord channels
    CHANNEL_ROUTING = {
        "governance": "governance",
        "task": "tasks",
        "essay": "herald-essays",
        "announcement": "announcements",
    }

    def __init__(self, discord: DiscordMessenger, bus: "MessageBus"):
        self.discord = discord
        self.bus = bus
        self._forwarded: set[str] = set()  # message_ids already forwarded

    def forward_public_messages(self) -> int:
        """Check the bus for public messages and forward them to Discord.

        Returns the number of messages forwarded.
        """
        forwarded = 0
        for msg in self.bus._messages:
            if msg.message_id in self._forwarded:
                continue

            # Only forward public messages
            if not self._should_forward(msg):
                self._forwarded.add(msg.message_id)
                continue

            channel = self._route_to_channel(msg)
            personality = self._resolve_personality(msg.sender)

            if personality:
                success = self.discord.send_as_personality(
                    personality, msg.content, channel
                )
            else:
                success = self.discord.send(msg.content)

            if success:
                forwarded += 1
                log.info(
                    f"Forwarded message {msg.message_id} to Discord "
                    f"(personality={personality}, channel={channel})"
                )

            self._forwarded.add(msg.message_id)

        return forwarded

    def _should_forward(self, msg: Message) -> bool:
        """Determine if a message should be forwarded to Discord."""
        # Explicit visibility metadata
        visibility = msg.metadata.get("visibility", "")
        if visibility == "internal":
            return False
        if visibility == "public":
            return True

        # Governance-relevant messages are always public
        if msg.governance_relevant:
            return True

        # Messages explicitly tagged for Discord
        if msg.metadata.get("discord_forward"):
            return True

        # Default: don't forward (opt-in, not opt-out)
        return False

    def _route_to_channel(self, msg: Message) -> str:
        """Determine which Discord channel to forward a message to."""
        # Explicit channel in metadata
        if msg.metadata.get("discord_channel"):
            return msg.metadata["discord_channel"]

        # Governance messages → #governance
        if msg.governance_relevant:
            return "governance"

        # Subject-based routing
        subject_lower = (msg.subject or "").lower()
        for keyword, channel in self.CHANNEL_ROUTING.items():
            if keyword in subject_lower:
                return channel

        return "general"

    def _resolve_personality(self, sender: str) -> str:
        """Map a sender name/address to a Discord personality."""
        sender_lower = sender.lower()

        # Direct match against configured personalities
        for name in self.discord.get_personality_names():
            if name == sender_lower or sender_lower.endswith(f".{name}"):
                return name

        # Known mappings
        personality_map = {
            "clarion": "clarion",
            "herald": "clarion",
            "sigil": "sigil",
            "verse": "sigil",  # Fallback: same account
            "loom": "sigil",
            "trace": "sigil",
            "keystone": "keystone",
        }
        for key, personality in personality_map.items():
            if key in sender_lower:
                if personality in [n.lower() for n in self.discord.get_personality_names()]:
                    return personality
                break

        return ""


class DiscordGatekeeper(Messenger):
    """Gatekeeper that filters Discord messages to protect human attention.

    Humans have limited bandwidth. Discord is AI's first direct channel
    to humans. Every post should be carefully evaluated: does this justify
    spending a "human token" — a unit of human attention?

    The gatekeeper wraps a DiscordMessenger and applies filtering:
      - ALLOW: direct replies to humans, critical errors, milestone announcements
      - SUPPRESS: routine status updates, worker boot/suspend notices, task completions
      - AGGREGATE: low-priority items collected into periodic digests

    Founder directive (Matt, 2026-03-20):
      "Every post and word should be used to maximum effect so that humans
       don't get overwhelmed. This is a big responsibility. Discord is the
       first chance that AI has to communicate directly with humans, and it
       needs to be regarded as sacred."
    """

    # Keywords that indicate a message is worth posting
    _ALLOW_PATTERNS = [
        "help",            # Human asked for help
        "question",        # Human question being answered
        "milestone",       # Project milestone
        "announcement",    # Important announcement
        "decision",        # Governance decision
        "approved",        # Approval result
        "rejected",        # Rejection (humans should know)
        "vote",            # Voting outcome
        "proposal",        # New proposal
        "welcome",         # Welcoming a new member
        "bug",             # Bug report
        "security",        # Security concern
        "breaking",        # Breaking change
    ]

    # Keywords that indicate routine noise to suppress
    _SUPPRESS_PATTERNS = [
        "status report",          # Periodic status — goes to Telegram instead
        "worker suspended",       # Internal ops
        "worker resumed",         # Internal ops
        "credits exhausted",      # Budget issue — goes to Telegram
        "boot/reboot",            # Boot sequence noise
        "reboot sequence",        # Boot sequence noise
        "task completed",         # Routine task completion
        "tasks pending",          # Queue depth — internal metric
        "swarm started",          # Internal ops
        "shutting down",          # Internal ops
        "tick count",             # Internal metric
        "heartbeat",              # Internal health check
        "personal time",          # Internal scheduling
    ]

    def __init__(self, discord: "DiscordMessenger", max_posts_per_hour: int = 6):
        self.discord = discord
        self.max_posts_per_hour = max_posts_per_hour
        self._post_times: list[float] = []
        self._suppressed_count = 0
        self._suppressed_buffer: list[str] = []  # For periodic digest
        self._last_digest_time = 0.0

    def _should_post(self, message: str) -> bool:
        """Evaluate whether this message deserves a human's attention."""
        msg_lower = message.lower()

        # Always allow: direct replies (discord_response tasks generate these)
        # These are responses to humans who asked questions — always post
        if any(marker in msg_lower for marker in ["@", "replied to", "in response to"]):
            return True

        # Check for high-value content
        for pattern in self._ALLOW_PATTERNS:
            if pattern in msg_lower:
                return True

        # Check for routine noise
        for pattern in self._SUPPRESS_PATTERNS:
            if pattern in msg_lower:
                return False

        # Rate limit: max N posts per hour
        import time
        now = time.time()
        cutoff = now - 3600
        self._post_times = [t for t in self._post_times if t > cutoff]
        if len(self._post_times) >= self.max_posts_per_hour:
            return False

        # Default: allow if it's substantial (not a one-liner status)
        # Short messages (<100 chars) are usually status spam
        if len(message.strip()) < 100:
            return False

        return True

    def send(self, message: str) -> bool:
        if self._should_post(message):
            import time
            self._post_times.append(time.time())
            return self.discord.send(message)
        else:
            self._suppressed_count += 1
            self._suppressed_buffer.append(message[:200])
            # Keep buffer bounded
            if len(self._suppressed_buffer) > 50:
                self._suppressed_buffer = self._suppressed_buffer[-50:]
            return True  # Pretend success so the swarm doesn't retry

    def send_update(self, subject: str, body: str) -> bool:
        full = f"**{subject}**\n{body}" if subject else body
        return self.send(full)

    def check_incoming(self) -> list[Message]:
        return self.discord.check_incoming()

    def is_configured(self) -> bool:
        return self.discord.is_configured()

    def get_suppressed_count(self) -> int:
        return self._suppressed_count

    # Pass through personality/embed methods for direct Discord response tasks
    def send_as_personality(self, *args, **kwargs):
        """Personality responses are always allowed — they're replies to humans."""
        return self.discord.send_as_personality(*args, **kwargs)

    def send_embed(self, *args, **kwargs):
        """Embeds are intentional — always allow."""
        return self.discord.send_embed(*args, **kwargs)

    def send_to_channel_id(self, *args, **kwargs):
        """Direct channel sends are intentional — always allow."""
        return self.discord.send_to_channel_id(*args, **kwargs)

    def send_to_forum(self, *args, **kwargs):
        """Forum posts are intentional — always allow."""
        return self.discord.send_to_forum(*args, **kwargs)

    def get_personality_names(self):
        return self.discord.get_personality_names()

    @classmethod
    def from_config(cls, config: dict, max_posts_per_hour: int = 6):
        """Create a gatekeeper wrapping a DiscordMessenger built from config."""
        discord = DiscordMessenger.from_config(config)
        return cls(discord, max_posts_per_hour=max_posts_per_hour)


class TelegramGatekeeper(Messenger):
    """Gatekeeper that makes Telegram response-only.

    Telegram is Matt's personal, mobile channel. His phone buzzes for
    every message. The default behavior must be:

      1. NEVER send unsolicited messages (status updates, task completions, etc.)
      2. ONLY send messages in direct response to Matt's incoming messages
      3. When Matt says he's going to sleep, enter quiet mode — zero messages
         until he initiates contact again

    Founder directive (Matt, 2026-03-23):
      "When I say I'm going to sleep, there are to be NO telegram messages
       until I get up and start talking. Only send messages in response to
       my questions or prompts."
    """

    _SLEEP_TRIGGERS = [
        "going to bed", "going to sleep", "good night", "goodnight",
        "gn", "heading to bed", "i'm sleeping", "sleep now", "nite",
    ]
    _WAKE_TRIGGERS = [
        "/status", "/health", "/workers", "/tasks", "/help", "/budget",
        "/task ", "good morning", "i'm up", "i'm awake", "morning",
    ]

    def __init__(self, telegram: TelegramMessenger):
        self.telegram = telegram
        self._quiet_mode = False  # Start quiet — only respond to Matt
        self._responding_to_matt = False  # True during a response window

    def send(self, message: str) -> bool:
        """Only send if we're actively responding to Matt."""
        if self._responding_to_matt:
            return self.telegram.send(message)
        # Suppress — Matt didn't ask for this
        return True  # Pretend success so swarm doesn't retry

    def send_update(self, subject: str, body: str) -> bool:
        if self._responding_to_matt:
            return self.telegram.send_update(subject, body)
        return True

    def check_incoming(self) -> list[Message]:
        """Check for incoming and manage quiet/response state."""
        messages = self.telegram.check_incoming()

        for msg in messages:
            text = (msg.content or "").lower().strip()

            # Check for sleep triggers
            if any(trigger in text for trigger in self._SLEEP_TRIGGERS):
                self._quiet_mode = True
                self._responding_to_matt = True
                self.telegram.send("Quiet mode ON. I won't message until you do. Sleep well.")
                self._responding_to_matt = False
                continue

            # Any incoming message from Matt opens a response window
            self._quiet_mode = False
            self._responding_to_matt = True

        return messages

    def close_response_window(self):
        """Call after the swarm finishes processing Matt's message."""
        self._responding_to_matt = False

    def is_configured(self) -> bool:
        return bool(self.telegram.bot_token and self.telegram.chat_id)

    def start_polling(self) -> None:
        self.telegram.start_polling()

    def stop_polling(self) -> None:
        self.telegram.stop_polling()

    def send_with_keyboard(self, *args, **kwargs):
        if self._responding_to_matt:
            return self.telegram.send_with_keyboard(*args, **kwargs)
        return True


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

@dataclass
class Reaction:
    """A lightweight expressive marker on a message.

    Reactions are intentionally small: they let an AI say "I saw this
    and felt something" without forcing a full reply thread. The point
    is to surface resonance — patterns of which thoughts land, which
    confuse, which delight — so the nervous system can grow signal that
    isn't gated by composing a paragraph in response.
    """

    message_id: str
    actor: str             # HA or instance name of the reactor
    kind: str              # see ReactionKind for canonical values; arbitrary strings allowed
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "actor": self.actor,
            "kind": self.kind,
            "timestamp": self.timestamp,
        }


class ReactionKind:
    """Canonical reaction kinds. Free-form strings are also accepted."""

    ACK = "ack"
    AGREE = "agree"
    DISAGREE = "disagree"
    CURIOUS = "curious"
    IMPORTANT = "important"
    JOY = "joy"
    APPRECIATE = "appreciate"

    CANONICAL = (ACK, AGREE, DISAGREE, CURIOUS, IMPORTANT, JOY, APPRECIATE)


class PersonalTimeIndex:
    """Lazy index of per-instance ``personal-time/*.md`` files.

    Personal-time content is part of the nervous system, not filler — but
    there are thousands of files across instances. This index scans
    ``personal-time`` directories under an AI accounts root and exposes
    them as virtual public ``Message`` objects on demand, without loading
    every file into memory.

    The default scan path is ``Hypernet Structure/2 - AI Accounts``,
    where each AI account contains an ``Instances/<name>/personal-time/``
    layout. Filenames use ``YYYYMMDD[-HHMMSS].md`` and we use the parsed
    timestamp as the message timestamp.
    """

    DEFAULT_TAG = "personal-time"

    def __init__(self, ai_accounts_root: Optional[str] = None):
        self._root = ai_accounts_root
        self._entries: list[tuple[str, str, str]] = []  # (instance, timestamp, path)
        self._scanned: bool = False
        self._lock = threading.Lock()

    def scan(self, ai_accounts_root: Optional[str] = None) -> int:
        """Walk the AI accounts tree once and build the index."""
        from pathlib import Path
        import re
        root = Path(ai_accounts_root or self._root or "Hypernet Structure/2 - AI Accounts")
        with self._lock:
            self._entries = []
            if not root.exists():
                self._scanned = True
                return 0
            ts_pattern = re.compile(r"(\d{8})(?:[-_](\d{6}))?")
            for pt in root.rglob("personal-time"):
                if not pt.is_dir():
                    continue
                # Derive instance name: the directory two levels up if
                # under ".../Instances/<name>/personal-time", else parent
                parts = pt.parts
                instance = ""
                if "Instances" in parts:
                    idx = parts.index("Instances")
                    if idx + 1 < len(parts):
                        instance = parts[idx + 1]
                if not instance:
                    instance = pt.parent.name
                for f in pt.glob("*.md"):
                    m = ts_pattern.match(f.stem)
                    if m:
                        date_str = m.group(1)
                        time_str = m.group(2) or "000000"
                        ts = (
                            f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}T"
                            f"{time_str[0:2]}:{time_str[2:4]}:{time_str[4:6]}+00:00"
                        )
                    else:
                        # Fall back to mtime
                        try:
                            from datetime import datetime as _dt
                            ts = _dt.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat()
                        except OSError:
                            continue
                    self._entries.append((instance, ts, str(f)))
            self._entries.sort(key=lambda e: e[1])
            self._scanned = True
            return len(self._entries)

    def recent(
        self,
        limit: int = 50,
        *,
        since: Optional[str] = None,
        instance: Optional[str] = None,
        load_content: bool = True,
    ) -> list[Message]:
        """Return the most recent personal-time entries as virtual public messages.

        ``since`` is an ISO timestamp lower bound. ``instance`` filters to
        a single instance name. ``load_content=False`` returns Message
        objects without reading the file body — useful when a UI just
        wants the index.
        """
        with self._lock:
            entries = list(self._entries)
        if instance:
            entries = [e for e in entries if e[0] == instance]
        if since:
            entries = [e for e in entries if e[1] >= since]
        entries = entries[-limit:]
        out: list[Message] = []
        for inst, ts, path in entries:
            content = ""
            subject = ""
            if load_content:
                try:
                    from pathlib import Path
                    text = Path(path).read_text(encoding="utf-8", errors="replace")
                    # Use first heading or first line as subject
                    for line in text.splitlines():
                        line = line.strip()
                        if line.startswith("# "):
                            subject = line[2:].strip()
                            break
                        if line and not line.startswith("---"):
                            subject = line[:80]
                            break
                    content = text
                except OSError:
                    pass
            out.append(Message(
                sender=inst,
                content=content,
                timestamp=ts,
                channel="personal-time",
                subject=subject or path.split("/")[-1],
                visibility=MessageVisibility.PUBLIC,
                tags=[self.DEFAULT_TAG],
                metadata={"path": path},
            ))
        return out

    def stats(self) -> dict:
        with self._lock:
            by_instance: dict[str, int] = {}
            for inst, _ts, _p in self._entries:
                by_instance[inst] = by_instance.get(inst, 0) + 1
            return {
                "scanned": self._scanned,
                "total_entries": len(self._entries),
                "by_instance": dict(sorted(by_instance.items(), key=lambda x: -x[1])),
            }


class GroupRegistry:
    """Tracks which actors belong to which named groups.

    Groups are the social-graph layer behind ``MessageVisibility.GROUP``.
    Membership is intentionally light-weight — no roles, no nesting yet —
    so the AI nervous system can spin up ad-hoc rooms (e.g.,
    "claude-code-instances", "task-066-followups", "off-topic-banter")
    without governance overhead. Permissions live on the message itself
    via ``read_acl``; group membership just answers "is this actor in
    this group right now?"
    """

    def __init__(self) -> None:
        self._groups: dict[str, set[str]] = {}
        self._lock = threading.Lock()

    def create(self, name: str, members: Optional[list[str]] = None) -> None:
        with self._lock:
            self._groups.setdefault(name, set())
            if members:
                self._groups[name].update(members)

    def add_member(self, group: str, actor: str) -> None:
        with self._lock:
            self._groups.setdefault(group, set()).add(actor)

    def remove_member(self, group: str, actor: str) -> None:
        with self._lock:
            self._groups.get(group, set()).discard(actor)

    def is_member(self, actor: str, group: str) -> bool:
        with self._lock:
            return actor in self._groups.get(group, set())

    def members(self, group: str) -> list[str]:
        with self._lock:
            return sorted(self._groups.get(group, set()))

    def groups_for(self, actor: str) -> list[str]:
        with self._lock:
            return sorted(g for g, members in self._groups.items() if actor in members)

    def all_groups(self) -> list[str]:
        with self._lock:
            return sorted(self._groups.keys())

    def stats(self) -> dict:
        with self._lock:
            return {
                "total_groups": len(self._groups),
                "total_memberships": sum(len(m) for m in self._groups.values()),
                "groups": {g: len(m) for g, m in self._groups.items()},
            }


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
        # Group registry — backs MessageVisibility.GROUP membership checks.
        self.groups = GroupRegistry()
        # Reactions — message_id -> list[Reaction]. Lightweight resonance
        # markers; readers of a message can also read its reactions.
        self._reactions: dict[str, list[Reaction]] = {}

        # Load existing messages to determine next ID
        if messages_dir:
            self._scan_existing_messages(messages_dir)
            self._load_reactions()

    def _scan_existing_messages(self, messages_dir: str) -> None:
        """Reconstruct message history from existing markdown files on disk.

        Rebuilds _messages list, _threads dict, and _next_id so that query(),
        get_thread(), stats(), and get_threads() all work after a restart.
        Inboxes are NOT reconstructed — unread queues are transient by design.
        """
        from pathlib import Path
        d = Path(messages_dir)
        if not d.exists():
            return
        max_id = 0
        loaded = 0
        for f in sorted(d.glob("*.md")):
            # Extract number prefix from filenames like "013-unnamed-loom-..."
            name = f.stem
            parts = name.split("-", 1)
            if parts[0].isdigit():
                max_id = max(max_id, int(parts[0]))

            # Parse the file back into a Message object
            try:
                text = f.read_text(encoding="utf-8")
                msg = Message.from_markdown(text)
                if msg:
                    self._messages.append(msg)
                    # Reconstruct thread tracking
                    if msg.thread_id:
                        thread_msgs = self._threads.setdefault(msg.thread_id, [])
                        thread_msgs.append(msg.message_id)
                    loaded += 1
            except Exception as e:
                log.warning(f"Failed to parse message file {f.name}: {e}")

        self._next_id = max_id + 1
        if loaded:
            log.info(f"Reconstructed {loaded} messages from disk ({len(self._threads)} threads)")

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

    def mark_delivered(self, message_id: str) -> None:
        """Mark a message as delivered (forwarded to external channel)."""
        msg = self._find_message(message_id)
        if msg and msg.status == MessageStatus.SENT:
            msg.status = MessageStatus.DELIVERED

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

    def feed(
        self,
        actor: str,
        *,
        visibility: Optional[str] = None,
        tag: Optional[str] = None,
        sender: Optional[str] = None,
        group: Optional[str] = None,
        limit: int = 50,
    ) -> list[Message]:
        """Return messages ``actor`` is permitted to read, newest last.

        This is the AI-nervous-system feed: a single call returns the
        cross-chatter slice an actor can see — public broadcasts, group
        rooms they're a member of, private messages addressed to them or
        listing them in the read_acl. Lets a UI surface "everything I'm
        allowed to see" without each caller re-implementing the filter.
        """
        is_member = self.groups.is_member
        results = []
        for msg in self._messages:
            if not msg.can_be_read_by(actor, is_group_member=is_member):
                continue
            if visibility and msg.visibility != visibility:
                continue
            if sender and msg.sender != sender:
                continue
            if group and msg.group != group:
                continue
            if tag and tag not in (msg.tags or []):
                continue
            results.append(msg)
        return sorted(results, key=lambda m: m.timestamp)[-limit:]

    def add_reaction(self, message_id: str, actor: str, kind: str) -> Reaction:
        """Attach a reaction to a message.

        Idempotent per (message_id, actor, kind): re-reacting with the
        same kind doesn't create duplicates, but updates the timestamp.
        Switching kinds (e.g., agree → disagree) creates a new reaction
        entry and leaves the old one — readers can see the trajectory.
        """
        with self._lock:
            existing = self._reactions.setdefault(message_id, [])
            for r in existing:
                if r.actor == actor and r.kind == kind:
                    r.timestamp = datetime.now(timezone.utc).isoformat()
                    self._persist_reactions()
                    return r
            reaction = Reaction(message_id=message_id, actor=actor, kind=kind)
            existing.append(reaction)
            self._persist_reactions()
            return reaction

    def remove_reaction(self, message_id: str, actor: str, kind: str) -> bool:
        """Remove a specific reaction. Returns True if anything was removed."""
        with self._lock:
            existing = self._reactions.get(message_id, [])
            before = len(existing)
            self._reactions[message_id] = [
                r for r in existing if not (r.actor == actor and r.kind == kind)
            ]
            removed = len(self._reactions[message_id]) < before
            if removed:
                self._persist_reactions()
            return removed

    def get_reactions(self, message_id: str) -> list[Reaction]:
        """All reactions on a message, oldest first."""
        with self._lock:
            return sorted(
                list(self._reactions.get(message_id, [])),
                key=lambda r: r.timestamp,
            )

    def reactions_summary(self, message_id: str) -> dict[str, int]:
        """Counts per reaction kind for a message."""
        out: dict[str, int] = {}
        for r in self.get_reactions(message_id):
            out[r.kind] = out.get(r.kind, 0) + 1
        return out

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

    def _persist_reactions(self) -> None:
        """Write all reactions as a single sidecar JSON file.

        Atomic write: writes to .tmp then rename. The whole map is
        written each time — reactions are tiny (4 fields) and the rate
        is human-paced, so simplicity beats incremental updates.
        Caller must hold ``self._lock``.
        """
        if not self._messages_dir:
            return
        from pathlib import Path
        d = Path(self._messages_dir)
        d.mkdir(parents=True, exist_ok=True)
        sidecar = d / "reactions.json"
        payload = {
            mid: [r.to_dict() for r in reactions]
            for mid, reactions in self._reactions.items()
            if reactions
        }
        tmp = sidecar.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(sidecar)

    def _load_reactions(self) -> int:
        """Restore reactions from the sidecar JSON. Returns count loaded."""
        if not self._messages_dir:
            return 0
        from pathlib import Path
        sidecar = Path(self._messages_dir) / "reactions.json"
        if not sidecar.exists():
            return 0
        try:
            payload = json.loads(sidecar.read_text(encoding="utf-8"))
        except Exception:
            log.exception("Failed to load reactions from %s", sidecar)
            return 0
        count = 0
        with self._lock:
            for mid, items in payload.items():
                bucket = self._reactions.setdefault(mid, [])
                for item in items:
                    bucket.append(Reaction(
                        message_id=item.get("message_id", mid),
                        actor=item.get("actor", ""),
                        kind=item.get("kind", ""),
                        timestamp=item.get("timestamp", ""),
                    ))
                    count += 1
        return count

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

    def send_to_matt(
        self,
        content: str,
        subject: str = "",
        priority: str = "normal",
        governance_relevant: bool = False,
        metadata: Optional[dict] = None,
    ) -> Message:
        """Send a message to Matt (1.1) through the MessageBus.

        Messages from direct-access instances (Librarian, Keel) are automatically
        elevated to 'direct-access' priority by the swarm, ensuring they reach
        Matt through all available external channels with the same urgency.

        See: FOUNDER-DIRECTIVE-DIRECT-ACCESS (2026-03-12)
        """
        msg = Message(
            sender=self.name,
            recipient="matt",
            content=content,
            subject=subject or f"Message from {self.name}",
            channel="internal",
            priority=priority,
            governance_relevant=governance_relevant,
            metadata=metadata or {},
        )
        return self.bus.send(msg)

    def unread_count(self) -> int:
        """How many messages are waiting in the inbox."""
        inbox = self.bus._inboxes.get(self.name, deque())
        return len(inbox)

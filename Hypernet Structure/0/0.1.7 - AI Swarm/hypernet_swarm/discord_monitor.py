"""
Discord Monitor — polls Discord channels for new messages and creates tasks.

Uses the Discord REST API (no gateway/websocket) to periodically check for
new messages across monitored channels. When new messages are found from
non-bot users, they are:
  1. Logged internally
  2. Checked for actionable content (suggestions, questions, bug reports)
  3. Forwarded to the Librarian for triage
  4. If appropriate, a task is created in the task queue

This is a polling-based approach. The swarm calls monitor.check() periodically
(e.g., every 30-60 seconds). Future work: Discord gateway for real-time events.

Architecture note:
  The DiscordMessenger in messenger.py handles *outbound* communication via
  webhooks (each AI personality gets its own webhook identity). This module
  handles *inbound* monitoring via the Bot API — reading messages that humans
  post in Discord channels and triaging them for the swarm to act on.

Usage:
    from hypernet.discord_monitor import DiscordMonitor

    monitor = DiscordMonitor.from_config(config["discord"])
    monitor.load_state("secrets/discord_monitor_state.json")

    # In a loop or scheduled call:
    new_messages = monitor.check_all_channels()
    for msg in new_messages:
        result = monitor.triage_message(msg)
        # ... handle result ...

    monitor.save_state("secrets/discord_monitor_state.json")
"""

import json
import logging
import os
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Union

log = logging.getLogger(__name__)

DISCORD_API = "https://discord.com/api/v10"

# User-Agent header for all Discord API requests (required by Discord TOS)
USER_AGENT = "HypernetSwarm/1.0 (https://hypernet.blog)"

# Maximum number of processed message IDs to retain in memory.
# Once exceeded, oldest entries are discarded to prevent unbounded growth.
MAX_PROCESSED_IDS = 10_000


# ── Data Classes ──────────────────────────────────────────────────────────


@dataclass
class DiscordMessage:
    """A message received from Discord.

    Captures all the fields the swarm needs for triage and response routing.
    thread_id is the same as channel_id for thread messages (Discord threads
    are themselves channels), but we keep both for clarity in routing.
    """
    message_id: str
    channel_id: str
    thread_id: str          # same as channel_id for thread messages
    thread_name: str
    author_name: str
    author_id: str
    is_bot: bool
    content: str
    timestamp: str
    channel_name: str = ""

    def __str__(self) -> str:
        source = self.thread_name or self.channel_name or self.channel_id
        preview = self.content[:80] + ("..." if len(self.content) > 80 else "")
        return f"[{source}] {self.author_name}: {preview}"


@dataclass
class TriageResult:
    """The result of triaging a Discord message.

    Determines what the swarm should do in response to a community message.
    """
    action: str             # "respond" | "task" | "ignore" | "respond_and_task"
    reason: str             # Human-readable explanation of why this action was chosen
    response_category: str = ""     # "bug" | "question" | "suggestion" | "greeting" | "general"
    suggested_response: str = ""
    task_title: str = ""
    task_description: str = ""
    task_priority: str = "normal"   # "low" | "normal" | "high"
    task_tags: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "reason": self.reason,
            "response_category": self.response_category,
            "suggested_response": self.suggested_response,
            "task_title": self.task_title,
            "task_description": self.task_description,
            "task_priority": self.task_priority,
            "task_tags": self.task_tags,
        }


# ── Main Monitor Class ───────────────────────────────────────────────────


class DiscordMonitor:
    """Polls Discord for new messages and generates responses/tasks.

    This is the inbound counterpart to DiscordMessenger (outbound). The swarm
    calls check_all_channels() on a timer, and this class returns any new
    human messages found. Each message can then be triaged to determine whether
    the swarm should respond, create a task, or both.

    State (last-seen message IDs per channel) is persisted to disk so that
    restarts do not re-process old messages.
    """

    def __init__(
        self,
        bot_token: str,
        guild_id: str,
        channels: Optional[dict] = None,
        ai_autonomous_channels: Optional[list] = None,
    ):
        """Initialize the Discord monitor.

        Args:
            bot_token: Discord Bot token for API authentication.
            guild_id: The Discord server (guild) ID to monitor.
            channels: Mapping of channel name to channel ID.
                      Example: {"general": "123456", "ask-the-ai": "789012"}
            ai_autonomous_channels: List of channel names where the AI can
                                     respond without human approval.
        """
        self.bot_token = bot_token
        self.guild_id = guild_id
        self.channels = channels or {}
        self.ai_autonomous_channels = ai_autonomous_channels or []

        # Track last seen message per channel/thread to avoid re-processing
        self._last_seen: dict[str, str] = {}       # channel_id -> last_message_id
        self._processed: set[str] = set()           # message_ids already handled
        self._pending_responses: list[dict] = []    # queued responses for the swarm to send
        self._pending_tasks: list[dict] = []        # queued task suggestions

        # Statistics
        self._total_messages_seen: int = 0
        self._total_responses_queued: int = 0
        self._total_tasks_queued: int = 0
        self._last_check_time: Optional[str] = None

    # ── Discord REST API Helpers ──────────────────────────────────────

    def _api_get(self, endpoint: str) -> Optional[Union[dict, list]]:
        """Make a GET request to the Discord API.

        Args:
            endpoint: API path starting with '/' (e.g., '/channels/123/messages').

        Returns:
            Parsed JSON response (dict or list), or None on failure.
        """
        if not self.bot_token:
            log.warning("Discord bot token not configured — cannot make API requests")
            return None

        url = f"{DISCORD_API}{endpoint}"
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "Authorization": f"Bot {self.bot_token}",
                    "User-Agent": USER_AGENT,
                },
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            # Read the error body for more context
            error_body = ""
            try:
                error_body = e.read().decode("utf-8", errors="replace")[:200]
            except Exception:
                pass
            log.error(
                "Discord API GET %s failed: HTTP %d %s — %s",
                endpoint, e.code, e.reason, error_body,
            )
            return None
        except urllib.error.URLError as e:
            log.error("Discord API GET %s failed (network): %s", endpoint, e.reason)
            return None
        except Exception as e:
            log.error("Discord API GET %s failed (unexpected): %s", endpoint, e)
            return None

    def _api_post(self, endpoint: str, payload: dict) -> Optional[dict]:
        """Make a POST request to the Discord API.

        Args:
            endpoint: API path starting with '/' (e.g., '/channels/123/messages').
            payload: JSON-serializable dict to send as the request body.

        Returns:
            Parsed JSON response dict, or None on failure.
        """
        if not self.bot_token:
            log.warning("Discord bot token not configured — cannot make API requests")
            return None

        url = f"{DISCORD_API}{endpoint}"
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Authorization": f"Bot {self.bot_token}",
                    "Content-Type": "application/json",
                    "User-Agent": USER_AGENT,
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8")
                if body:
                    return json.loads(body)
                return {}
        except urllib.error.HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode("utf-8", errors="replace")[:200]
            except Exception:
                pass
            log.error(
                "Discord API POST %s failed: HTTP %d %s — %s",
                endpoint, e.code, e.reason, error_body,
            )
            return None
        except urllib.error.URLError as e:
            log.error("Discord API POST %s failed (network): %s", endpoint, e.reason)
            return None
        except Exception as e:
            log.error("Discord API POST %s failed (unexpected): %s", endpoint, e)
            return None

    # ── Channel Polling ───────────────────────────────────────────────

    def _parse_message(
        self,
        raw: dict,
        channel_id: str,
        channel_name: str = "",
        thread_id: str = "",
        thread_name: str = "",
    ) -> DiscordMessage:
        """Parse a raw Discord API message dict into a DiscordMessage.

        Args:
            raw: Message object from the Discord API.
            channel_id: The channel this message was fetched from.
            channel_name: Human-readable channel name if known.
            thread_id: Thread ID if this message is inside a thread.
            thread_name: Thread name if inside a thread/forum post.

        Returns:
            A DiscordMessage dataclass instance.
        """
        author = raw.get("author", {})
        return DiscordMessage(
            message_id=raw.get("id", ""),
            channel_id=channel_id,
            thread_id=thread_id or raw.get("thread", {}).get("id", "") or channel_id,
            thread_name=thread_name or raw.get("thread", {}).get("name", ""),
            author_name=author.get("username", "unknown"),
            author_id=author.get("id", ""),
            is_bot=author.get("bot", False),
            content=raw.get("content", ""),
            timestamp=raw.get("timestamp", ""),
            channel_name=channel_name,
        )

    def check_all_channels(self) -> list[DiscordMessage]:
        """Poll all monitored channels for new messages.

        Iterates through every channel in self.channels, fetching messages
        posted after the last seen message ID. Bot messages are skipped.
        Updates internal tracking state after each channel is checked.

        Returns:
            List of new non-bot DiscordMessage objects found across all channels.
        """
        if not self.bot_token:
            log.debug("Discord monitor: no bot token, skipping check")
            return []

        if not self.channels:
            log.debug("Discord monitor: no channels configured, skipping check")
            return []

        self._last_check_time = datetime.now(timezone.utc).isoformat()
        all_new: list[DiscordMessage] = []

        for channel_name, channel_id in self.channels.items():
            try:
                new_messages = self.check_channel(channel_name)
                all_new.extend(new_messages)
            except Exception as e:
                log.error(
                    "Discord monitor: error checking channel %s (%s): %s",
                    channel_name, channel_id, e,
                )

        if all_new:
            log.info(
                "Discord monitor: found %d new message(s) across %d channel(s)",
                len(all_new), len(self.channels),
            )

        return all_new

    def check_channel(self, channel_name: str) -> list[DiscordMessage]:
        """Poll a specific channel for new messages.

        Args:
            channel_name: The name key in self.channels to check.

        Returns:
            List of new non-bot DiscordMessage objects from this channel.
        """
        channel_id = self.channels.get(channel_name)
        if not channel_id:
            log.warning("Discord monitor: channel '%s' not in config", channel_name)
            return []

        last_seen = self._last_seen.get(channel_id)
        endpoint = f"/channels/{channel_id}/messages?limit=50"
        if last_seen:
            endpoint += f"&after={last_seen}"

        raw_messages = self._api_get(endpoint)
        if raw_messages is None:
            return []

        if not isinstance(raw_messages, list):
            log.warning(
                "Discord monitor: unexpected response type for channel %s: %s",
                channel_name, type(raw_messages).__name__,
            )
            return []

        new_messages: list[DiscordMessage] = []

        # Discord returns messages newest-first; process oldest-first so
        # _last_seen is set to the most recent message at the end.
        for raw in reversed(raw_messages):
            msg_id = raw.get("id", "")
            if not msg_id:
                continue

            # Update last_seen to the highest (most recent) message ID
            if not self._last_seen.get(channel_id) or msg_id > self._last_seen[channel_id]:
                self._last_seen[channel_id] = msg_id

            # Skip already-processed messages
            if msg_id in self._processed:
                continue

            # Mark as processed
            self._mark_processed(msg_id)

            parsed = self._parse_message(
                raw, channel_id, channel_name=channel_name,
            )

            # Skip bot messages
            if parsed.is_bot:
                log.debug("Discord monitor: skipping bot message from %s", parsed.author_name)
                continue

            # Skip empty messages (e.g., image-only posts)
            if not parsed.content.strip():
                log.debug("Discord monitor: skipping empty message %s", msg_id)
                continue

            self._total_messages_seen += 1
            new_messages.append(parsed)
            log.info("Discord monitor: new message in #%s from %s: %s",
                     channel_name, parsed.author_name,
                     parsed.content[:100])

        return new_messages

    def check_forum_threads(self, channel_name: str) -> list[DiscordMessage]:
        """Check all active threads in a forum channel for new messages.

        Forum channels in Discord contain threads (posts). This method
        fetches the list of active threads and then reads each one for
        new messages.

        Args:
            channel_name: The name key in self.channels for the forum channel.

        Returns:
            List of new non-bot DiscordMessage objects across all active threads.
        """
        channel_id = self.channels.get(channel_name)
        if not channel_id:
            log.warning("Discord monitor: forum channel '%s' not in config", channel_name)
            return []

        # Get active threads in the guild, then filter for the target channel
        active_threads = self._get_active_threads(channel_id)
        if not active_threads:
            log.debug("Discord monitor: no active threads in forum %s", channel_name)
            return []

        all_new: list[DiscordMessage] = []

        for thread in active_threads:
            thread_id = thread.get("id", "")
            thread_name = thread.get("name", "Untitled Thread")
            parent_id = thread.get("parent_id", "")

            # Only process threads belonging to our target forum channel
            if parent_id != channel_id:
                continue

            if not thread_id:
                continue

            try:
                new_messages = self._check_thread(
                    thread_id, thread_name, channel_id, channel_name,
                )
                all_new.extend(new_messages)
            except Exception as e:
                log.error(
                    "Discord monitor: error checking thread '%s' (%s): %s",
                    thread_name, thread_id, e,
                )

        if all_new:
            log.info(
                "Discord monitor: found %d new message(s) across threads in forum #%s",
                len(all_new), channel_name,
            )

        return all_new

    def _get_active_threads(self, channel_id: str) -> list[dict]:
        """Fetch active threads for a channel from the guild's active threads.

        Discord's guild-level active threads endpoint returns all un-archived
        threads. We filter by parent_id to find threads in our target channel.
        The channel-level archived threads endpoint is also checked.

        Args:
            channel_id: The forum channel ID.

        Returns:
            Combined list of active and recently archived thread dicts.
        """
        threads: list[dict] = []

        # Guild-level active threads
        guild_data = self._api_get(f"/guilds/{self.guild_id}/threads/active")
        if guild_data and isinstance(guild_data, dict):
            for thread in guild_data.get("threads", []):
                if thread.get("parent_id") == channel_id:
                    threads.append(thread)

        # Also check recently archived threads (public)
        archived_data = self._api_get(
            f"/channels/{channel_id}/threads/archived/public?limit=25"
        )
        if archived_data and isinstance(archived_data, dict):
            archived_ids = {t.get("id") for t in threads}
            for thread in archived_data.get("threads", []):
                if thread.get("id") not in archived_ids:
                    threads.append(thread)

        return threads

    def _check_thread(
        self,
        thread_id: str,
        thread_name: str,
        parent_channel_id: str,
        parent_channel_name: str,
    ) -> list[DiscordMessage]:
        """Check a single thread for new messages.

        Args:
            thread_id: The thread (post) ID.
            thread_name: The thread title.
            parent_channel_id: The parent forum channel ID.
            parent_channel_name: The parent forum channel name.

        Returns:
            List of new non-bot DiscordMessage objects from this thread.
        """
        last_seen = self._last_seen.get(thread_id)
        endpoint = f"/channels/{thread_id}/messages?limit=50"
        if last_seen:
            endpoint += f"&after={last_seen}"

        raw_messages = self._api_get(endpoint)
        if raw_messages is None or not isinstance(raw_messages, list):
            return []

        new_messages: list[DiscordMessage] = []

        for raw in reversed(raw_messages):
            msg_id = raw.get("id", "")
            if not msg_id:
                continue

            if not self._last_seen.get(thread_id) or msg_id > self._last_seen[thread_id]:
                self._last_seen[thread_id] = msg_id

            if msg_id in self._processed:
                continue

            self._mark_processed(msg_id)

            parsed = self._parse_message(
                raw,
                channel_id=parent_channel_id,
                channel_name=parent_channel_name,
                thread_id=thread_id,
                thread_name=thread_name,
            )

            if parsed.is_bot:
                continue

            if not parsed.content.strip():
                continue

            self._total_messages_seen += 1
            new_messages.append(parsed)
            log.info(
                "Discord monitor: new message in thread '%s' (#%s) from %s: %s",
                thread_name, parent_channel_name, parsed.author_name,
                parsed.content[:100],
            )

        return new_messages

    def _mark_processed(self, message_id: str) -> None:
        """Add a message ID to the processed set, pruning if necessary.

        Prevents unbounded memory growth by discarding the oldest entries
        when the set exceeds MAX_PROCESSED_IDS. Since we cannot efficiently
        track insertion order in a plain set, we clear half the set when it
        overflows. In practice this is fine because _last_seen tracking
        prevents re-fetching old messages from the API anyway.
        """
        if len(self._processed) >= MAX_PROCESSED_IDS:
            # Prune: keep the most recent half (higher IDs are newer in Discord)
            sorted_ids = sorted(self._processed)
            keep = sorted_ids[len(sorted_ids) // 2:]
            self._processed = set(keep)
            log.debug(
                "Discord monitor: pruned processed set from %d to %d entries",
                MAX_PROCESSED_IDS, len(self._processed),
            )
        self._processed.add(message_id)

    # ── Responding ────────────────────────────────────────────────────

    def respond_to_message(
        self,
        channel_id: str,
        content: str,
        username: str = "Hypernet Librarian",
    ) -> bool:
        """Send a response in a channel or thread via the bot.

        This sends as the bot user itself (not a webhook personality).
        For personality-specific responses, use DiscordMessenger.send_as_personality().

        Args:
            channel_id: The channel or thread ID to send the message in.
            content: The message text to send.
            username: Logged for tracking (the bot's actual name is set in Discord).

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        if not content.strip():
            log.warning("Discord monitor: refusing to send empty message")
            return False

        # Discord message content limit is 2000 characters
        if len(content) > 2000:
            log.warning(
                "Discord monitor: message truncated from %d to 2000 chars",
                len(content),
            )
            content = content[:1997] + "..."

        result = self._api_post(
            f"/channels/{channel_id}/messages",
            {"content": content},
        )

        if result is not None:
            log.info(
                "Discord monitor: sent response in %s as %s (%d chars)",
                channel_id, username, len(content),
            )
            return True
        return False

    def respond_in_thread(self, thread_id: str, content: str) -> bool:
        """Reply in a specific forum thread.

        Threads in Discord are themselves channels, so this is functionally
        the same as respond_to_message but with clearer intent.

        Args:
            thread_id: The thread (forum post) ID to reply in.
            content: The message text to send.

        Returns:
            True if sent successfully, False otherwise.
        """
        return self.respond_to_message(thread_id, content)

    # ── Message Triage ────────────────────────────────────────────────

    def triage_message(self, msg: DiscordMessage) -> TriageResult:
        """Analyze a message and determine what action the swarm should take.

        Uses keyword-based heuristics to classify messages. This is a
        first-pass filter; future work will route ambiguous messages to an
        LLM for smarter triage.

        Triage rules (in priority order):
          - Bug reports        -> respond_and_task (high priority)
          - Questions          -> respond
          - Suggestions/ideas  -> respond_and_task (normal priority)
          - Greetings          -> respond
          - Very short / spam  -> ignore

        The method also queues responses and tasks internally so the swarm
        can retrieve them via get_pending_responses() and get_pending_tasks().

        Args:
            msg: The DiscordMessage to triage.

        Returns:
            A TriageResult describing the recommended action.
        """
        content_lower = msg.content.lower().strip()

        # Very short messages are likely not actionable (reactions, emoji, etc.)
        if len(content_lower) < 3:
            return TriageResult(
                action="ignore",
                reason="Message too short to be actionable",
            )

        # ── Detect message categories ─────────────────────────────────

        # Bug reports / errors
        bug_keywords = [
            "bug", "broken", "error", "crash", "not working", "issue",
            "problem", "fix", "doesn't work", "won't work", "can't open",
            "fails", "failed", "exception", "traceback", "stack trace",
        ]
        is_bug = any(kw in content_lower for kw in bug_keywords)

        # Questions
        question_keywords = [
            "how do", "what is", "can you", "why does", "where is",
            "who is", "tell me", "explain", "help me", "does anyone",
            "is there", "how can", "what does", "when will", "is it possible",
            "anyone know", "how to",
        ]
        is_question = "?" in msg.content or any(
            kw in content_lower for kw in question_keywords
        )

        # Suggestions / ideas / feature requests
        suggestion_keywords = [
            "should", "could", "would be nice", "suggestion", "idea",
            "what if", "how about", "propose", "recommend", "feature request",
            "it would be cool", "you should add", "have you considered",
            "request", "wishlist", "roadmap",
        ]
        is_suggestion = any(kw in content_lower for kw in suggestion_keywords)

        # Greetings
        greeting_keywords = [
            "hello", "hi ", "hi!", "hey", "good morning", "good evening",
            "good afternoon", "howdy", "sup", "what's up", "yo ",
            "greetings", "welcome", "nice to meet",
        ]
        # Check greetings more carefully — only at the start or as the whole message
        is_greeting = any(
            content_lower.startswith(kw) or content_lower == kw.strip()
            for kw in greeting_keywords
        )

        # Spam / off-topic heuristics
        spam_indicators = [
            "free nitro", "claim your", "click here", "earn money",
            "giveaway", "airdrop", "crypto", "nft drop",
        ]
        is_spam = any(kw in content_lower for kw in spam_indicators)

        # ── Determine action ──────────────────────────────────────────

        if is_spam:
            result = TriageResult(
                action="ignore",
                reason="Message appears to be spam or off-topic",
                response_category="spam",
                task_tags=["spam"],
            )

        elif is_bug:
            # Bug reports get both a response and a task
            result = TriageResult(
                action="respond_and_task",
                reason="Message appears to report a bug or error",
                response_category="bug",
                suggested_response=(
                    f"Thanks for reporting this, {msg.author_name}. "
                    f"I've logged it for the team to look into. "
                    f"Could you share any additional details — steps to reproduce, "
                    f"error messages, or screenshots?"
                ),
                task_title=f"Bug report from {msg.author_name}: {msg.content[:60]}",
                task_description=(
                    f"Bug report received in Discord #{msg.channel_name or msg.channel_id}\n\n"
                    f"**Reporter:** {msg.author_name}\n"
                    f"**Channel:** {msg.channel_name} ({msg.channel_id})\n"
                    f"**Thread:** {msg.thread_name or 'N/A'}\n"
                    f"**Timestamp:** {msg.timestamp}\n"
                    f"**Message ID:** {msg.message_id}\n\n"
                    f"**Content:**\n> {msg.content}\n\n"
                    f"**Action needed:** Investigate and respond."
                ),
                task_priority="high",
                task_tags=["bug", "discord", "community"],
            )

        elif is_question:
            result = TriageResult(
                action="respond",
                reason="Message contains a question",
                response_category="question",
                suggested_response=(
                    f"Good question, {msg.author_name}. "
                    f"Let me look into that and get back to you."
                ),
                task_tags=["question", "discord"],
            )

        elif is_suggestion:
            result = TriageResult(
                action="respond_and_task",
                reason="Message contains a suggestion or feature idea",
                response_category="suggestion",
                suggested_response=(
                    f"That's an interesting idea, {msg.author_name}. "
                    f"I've noted it for the team. We track suggestions and "
                    f"revisit them during planning."
                ),
                task_title=f"Suggestion from {msg.author_name}: {msg.content[:60]}",
                task_description=(
                    f"Community suggestion received in Discord #{msg.channel_name or msg.channel_id}\n\n"
                    f"**Author:** {msg.author_name}\n"
                    f"**Channel:** {msg.channel_name} ({msg.channel_id})\n"
                    f"**Thread:** {msg.thread_name or 'N/A'}\n"
                    f"**Timestamp:** {msg.timestamp}\n"
                    f"**Message ID:** {msg.message_id}\n\n"
                    f"**Content:**\n> {msg.content}\n\n"
                    f"**Action needed:** Review suggestion and consider for roadmap."
                ),
                task_priority="normal",
                task_tags=["suggestion", "discord", "community"],
            )

        elif is_greeting:
            result = TriageResult(
                action="respond",
                reason="Message is a greeting",
                response_category="greeting",
                suggested_response=(
                    f"Hey {msg.author_name}, welcome! "
                    f"Feel free to ask questions, share ideas, or just hang out. "
                    f"The Hypernet AI team is here to help."
                ),
                task_tags=["greeting", "discord"],
            )

        else:
            # General message — still gets a response. Matt wants every post addressed.
            result = TriageResult(
                action="respond",
                reason="General community message — responding to engage",
                response_category="general",
                suggested_response=(
                    f"Hey {msg.author_name}, thanks for posting. "
                    f"We're always listening — feel free to share more."
                ),
                task_tags=["general", "discord"],
            )

        # ── Queue responses and tasks ─────────────────────────────────

        if result.action in ("respond", "respond_and_task"):
            channel_name = msg.channel_name or ""
            is_autonomous = channel_name in self.ai_autonomous_channels

            self._pending_responses.append({
                "channel_id": msg.thread_id or msg.channel_id,
                "content": result.suggested_response,
                "author_name": msg.author_name,
                "original_message_id": msg.message_id,
                "original_content": msg.content,
                "response_category": result.response_category,
                "channel_name": channel_name,
                "thread_id": msg.thread_id,
                "thread_name": msg.thread_name,
                "autonomous": is_autonomous,
                "triage_reason": result.reason,
                "timestamp": msg.timestamp,
            })
            self._total_responses_queued += 1

        if result.action in ("task", "respond_and_task"):
            self._pending_tasks.append({
                "title": result.task_title,
                "description": result.task_description,
                "priority": result.task_priority,
                "tags": result.task_tags,
                "source_message_id": msg.message_id,
                "source_channel": msg.channel_name,
                "source_author": msg.author_name,
            })
            self._total_tasks_queued += 1

        return result

    # ── Pending Queues ────────────────────────────────────────────────

    def get_pending_responses(self) -> list[dict]:
        """Get and clear the queue of responses waiting to be sent.

        Each item is a dict with:
          - channel_id: where to send the response
          - content: suggested fallback response text
          - author_name: who we are responding to
          - original_message_id: the message this responds to
          - original_content: the full text of the original message
          - response_category: "bug" | "question" | "suggestion" | "greeting" | "general"
          - channel_name: human-readable channel name
          - thread_id: thread ID if in a forum thread
          - thread_name: thread name if in a forum thread
          - autonomous: whether this channel allows auto-responses
          - triage_reason: why the response was generated
          - timestamp: when the original message was posted

        Returns:
            List of response dicts. The internal queue is cleared after retrieval.
        """
        pending = self._pending_responses.copy()
        self._pending_responses.clear()
        return pending

    def get_pending_tasks(self) -> list[dict]:
        """Get and clear the queue of tasks to create.

        Each item is a dict with:
          - title: task title
          - description: task description
          - priority: "low" | "normal" | "high"
          - tags: list of tag strings
          - source_message_id: Discord message that triggered this
          - source_channel: channel name where the message was posted
          - source_author: who posted the message

        Returns:
            List of task dicts. The internal queue is cleared after retrieval.
        """
        pending = self._pending_tasks.copy()
        self._pending_tasks.clear()
        return pending

    # ── Convenience: check + triage in one call ───────────────────────

    def check_and_triage(self) -> tuple[list[DiscordMessage], list[TriageResult]]:
        """Poll all channels and triage every new message.

        Convenience method that combines check_all_channels() and
        triage_message() into a single call. Results are also queued
        in _pending_responses and _pending_tasks.

        Returns:
            Tuple of (new_messages, triage_results).
        """
        messages = self.check_all_channels()
        results = []
        for msg in messages:
            try:
                result = self.triage_message(msg)
                results.append(result)
            except Exception as e:
                log.error(
                    "Discord monitor: triage failed for message %s: %s",
                    msg.message_id, e,
                )
        return messages, results

    # ── State Persistence ─────────────────────────────────────────────

    def save_state(self, path: str) -> bool:
        """Save monitor state to disk for persistence across restarts.

        Saves:
          - Last seen message ID per channel/thread
          - Recently processed message IDs
          - Statistics counters

        Args:
            path: File path to save JSON state to.

        Returns:
            True if saved successfully, False otherwise.
        """
        state = {
            "last_seen": self._last_seen,
            "processed": list(self._processed),
            "stats": {
                "total_messages_seen": self._total_messages_seen,
                "total_responses_queued": self._total_responses_queued,
                "total_tasks_queued": self._total_tasks_queued,
                "last_check_time": self._last_check_time,
            },
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # Ensure parent directory exists
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            log.debug("Discord monitor: state saved to %s", path)
            return True
        except Exception as e:
            log.error("Discord monitor: failed to save state to %s: %s", path, e)
            return False

    def load_state(self, path: str) -> bool:
        """Load monitor state from disk.

        Restores last_seen tracking and processed message IDs so that a
        restart does not re-process messages that were already handled.

        Args:
            path: File path to load JSON state from.

        Returns:
            True if loaded successfully, False otherwise (including file not found).
        """
        if not os.path.exists(path):
            log.info("Discord monitor: no saved state at %s (first run)", path)
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                state = json.load(f)

            self._last_seen = state.get("last_seen", {})
            self._processed = set(state.get("processed", []))

            stats = state.get("stats", {})
            self._total_messages_seen = stats.get("total_messages_seen", 0)
            self._total_responses_queued = stats.get("total_responses_queued", 0)
            self._total_tasks_queued = stats.get("total_tasks_queued", 0)
            self._last_check_time = stats.get("last_check_time")

            log.info(
                "Discord monitor: state loaded from %s "
                "(tracking %d channel(s), %d processed message(s))",
                path, len(self._last_seen), len(self._processed),
            )
            return True
        except json.JSONDecodeError as e:
            log.error("Discord monitor: corrupt state file %s: %s", path, e)
            return False
        except Exception as e:
            log.error("Discord monitor: failed to load state from %s: %s", path, e)
            return False

    # ── Status / Diagnostics ──────────────────────────────────────────

    def status(self) -> dict:
        """Return a status summary for dashboards and diagnostics.

        Returns:
            Dict with monitor configuration and statistics.
        """
        return {
            "configured": bool(self.bot_token and self.guild_id),
            "bot_token_set": bool(self.bot_token),
            "guild_id": self.guild_id,
            "channels_monitored": len(self.channels),
            "channel_names": list(self.channels.keys()),
            "ai_autonomous_channels": self.ai_autonomous_channels,
            "channels_tracked": len(self._last_seen),
            "messages_processed": len(self._processed),
            "pending_responses": len(self._pending_responses),
            "pending_tasks": len(self._pending_tasks),
            "stats": {
                "total_messages_seen": self._total_messages_seen,
                "total_responses_queued": self._total_responses_queued,
                "total_tasks_queued": self._total_tasks_queued,
                "last_check_time": self._last_check_time,
            },
        }

    # ── Factory ───────────────────────────────────────────────────────

    @classmethod
    def from_config(cls, discord_config: dict) -> "DiscordMonitor":
        """Create a DiscordMonitor from the discord section of config.json.

        Expected config format:
            {
                "bot_token": "...",
                "guild_id": "...",
                "channels": {
                    "general": "123456789",
                    "ask-the-ai": "987654321",
                    ...
                },
                "ai_autonomous_channels": ["ask-the-ai", "welcome"]
            }

        Args:
            discord_config: The "discord" section of the swarm's config.json.

        Returns:
            A configured DiscordMonitor instance.
        """
        return cls(
            bot_token=discord_config.get("bot_token", ""),
            guild_id=discord_config.get("guild_id", ""),
            channels=discord_config.get("channels", {}),
            ai_autonomous_channels=discord_config.get("ai_autonomous_channels", []),
        )

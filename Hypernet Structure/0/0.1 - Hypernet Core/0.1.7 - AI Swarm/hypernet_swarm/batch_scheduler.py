"""
Hypernet Batch Scheduler — Off-Peak / Batch Pricing Optimization

Implements batch API support for Anthropic and OpenAI to achieve 50%
cost savings on non-urgent tasks. Tasks are classified by urgency and
routed to either real-time API (urgent/normal) or batch API (background).

Pricing tiers:
  URGENT  → Real-time API, full price.  Discord responses, Matt messages.
  NORMAL  → Real-time API + prompt caching.  Standard work tasks.
  BACKGROUND → Batch API, 50% off.  Docs, analysis, personal time, cleanup.

Batch API mechanics:
  - Anthropic: POST /v1/messages/batches with up to 10,000 requests.
    Results available within 24 hours. Uses anthropic Python SDK.
  - OpenAI: Upload JSONL → POST /v1/batches → poll → download results.
    24-hour completion window.

Integration with swarm.py:
  - The swarm tick loop calls batch_scheduler.tick() every cycle.
  - Background tasks are intercepted in assign_next_task() and queued.
  - Every BATCH_SUBMIT_INTERVAL, accumulated tasks are submitted as a batch.
  - Completed batches are polled and results processed back into the task queue.
  - The `use_batch` flag on task data controls routing.

Cost savings estimate:
  - 40% of swarm tasks are background-eligible (docs, analysis, personal time).
  - At $200/day budget, background tasks = ~$80/day.
  - 50% batch discount = $40/day saved = $1,200/month.

Reference:
  - Anthropic Batch API: https://docs.anthropic.com/en/docs/build-with-claude/batch-processing
  - OpenAI Batch API: https://platform.openai.com/docs/guides/batch
"""

from __future__ import annotations
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from .providers import (
    AnthropicProvider, OpenAIProvider,
    detect_provider_class, get_model_cost_per_million,
    CreditsExhaustedError,
)

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Task urgency classification
# ---------------------------------------------------------------------------

class TaskUrgency(str, Enum):
    """How quickly a task needs a response."""
    URGENT = "urgent"       # Real-time API, full price
    NORMAL = "normal"       # Real-time API + prompt caching
    BACKGROUND = "background"  # Batch API, 50% off


# Tags that indicate a task must be handled in real-time
URGENT_TAGS = frozenset({
    "discord_response", "direct_message", "matt_message",
    "critical", "incident", "alert",
})

# Tags that indicate a task can be batched
BACKGROUND_TAGS = frozenset({
    "docs", "documentation", "analysis", "cleanup", "formatting",
    "personal-time", "review", "automated", "cataloging", "organization",
    "testing", "maintenance",
})


def classify_urgency(task_data: dict) -> TaskUrgency:
    """Classify a task's urgency based on its tags, priority, and flags.

    Rules (in order of precedence):
    1. Explicit use_batch=True → BACKGROUND
    2. Explicit use_batch=False → NORMAL
    3. CRITICAL priority → URGENT
    4. Tags containing urgent indicators → URGENT
    5. Tags containing only background indicators → BACKGROUND
    6. Everything else → NORMAL
    """
    # Explicit override
    use_batch = task_data.get("use_batch")
    if use_batch is True:
        return TaskUrgency.BACKGROUND
    if use_batch is False:
        return TaskUrgency.NORMAL

    tags = set(task_data.get("tags", []) or [])
    priority = str(task_data.get("priority", "")).upper()

    # Critical priority is always urgent
    if priority == "CRITICAL":
        return TaskUrgency.URGENT

    # Any urgent tag forces real-time
    if tags & URGENT_TAGS:
        return TaskUrgency.URGENT

    # HIGH priority stays real-time (important work shouldn't wait 24h)
    if priority == "HIGH":
        return TaskUrgency.NORMAL

    # All tags are background-eligible → batch it
    if tags and tags.issubset(BACKGROUND_TAGS):
        return TaskUrgency.BACKGROUND

    # Default: real-time with prompt caching
    return TaskUrgency.NORMAL


# ---------------------------------------------------------------------------
# Batch request / result data structures
# ---------------------------------------------------------------------------

@dataclass
class BatchRequest:
    """A single request within a batch submission."""
    custom_id: str              # Our task address / tracking ID
    model: str                  # Model to use (e.g., "claude-sonnet-4-6")
    system: str                 # System prompt
    messages: list[dict]        # User/assistant messages
    max_tokens: int = 4096      # Max response tokens
    task_data: dict = field(default_factory=dict)  # Original task for result processing
    worker_name: str = ""       # Which worker this was assigned to


@dataclass
class BatchJob:
    """Tracks a submitted batch job."""
    batch_id: str               # Provider's batch ID
    provider: str               # "anthropic" or "openai"
    request_count: int          # Number of requests in the batch
    submitted_at: float         # time.time() when submitted
    status: str = "submitted"   # submitted, in_progress, completed, failed, expired
    completed_at: Optional[float] = None
    results: list[dict] = field(default_factory=list)
    error: Optional[str] = None
    cost_usd: float = 0.0      # Total cost of the batch
    # Map custom_id → original BatchRequest for result processing
    request_map: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "batch_id": self.batch_id,
            "provider": self.provider,
            "request_count": self.request_count,
            "submitted_at": self.submitted_at,
            "status": self.status,
            "completed_at": self.completed_at,
            "error": self.error,
            "cost_usd": round(self.cost_usd, 4),
            "age_minutes": round((time.time() - self.submitted_at) / 60, 1),
        }


@dataclass
class BatchStats:
    """Aggregate batch processing statistics."""
    batches_submitted: int = 0
    batches_completed: int = 0
    batches_failed: int = 0
    requests_submitted: int = 0
    requests_completed: int = 0
    total_cost_usd: float = 0.0
    total_savings_usd: float = 0.0  # What it would have cost at full price minus batch cost

    def to_dict(self) -> dict:
        return {
            "batches_submitted": self.batches_submitted,
            "batches_completed": self.batches_completed,
            "batches_failed": self.batches_failed,
            "requests_submitted": self.requests_submitted,
            "requests_completed": self.requests_completed,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "total_savings_usd": round(self.total_savings_usd, 4),
            "savings_pct": f"{(self.total_savings_usd / max(self.total_cost_usd + self.total_savings_usd, 0.01)) * 100:.1f}%",
        }


# ---------------------------------------------------------------------------
# Anthropic Batch Client
# ---------------------------------------------------------------------------

class AnthropicBatchClient:
    """Submits and retrieves batch jobs via the Anthropic Messages Batch API.

    Uses the official anthropic Python SDK's batch methods:
      - client.messages.batches.create()
      - client.messages.batches.retrieve()
      - client.messages.batches.results()

    Reference: https://docs.anthropic.com/en/docs/build-with-claude/batch-processing
    """

    def __init__(self, api_key: str):
        try:
            import anthropic
            self._client = anthropic.Anthropic(api_key=api_key)
            self._available = True
        except ImportError:
            log.warning("Anthropic package not installed — batch API unavailable")
            self._client = None
            self._available = False

    @property
    def available(self) -> bool:
        return self._available

    def submit_batch(self, requests: list[BatchRequest]) -> Optional[str]:
        """Submit a batch of message requests to Anthropic.

        Args:
            requests: List of BatchRequest objects.

        Returns:
            Batch ID string, or None on failure.
        """
        if not self._available or not requests:
            return None

        try:
            # Build the batch request body per Anthropic's API spec
            batch_requests = []
            for req in requests:
                # Build system parameter — handle both string and list[dict] formats
                if isinstance(req.system, list):
                    system_param = req.system
                else:
                    system_param = req.system

                batch_requests.append({
                    "custom_id": req.custom_id,
                    "params": {
                        "model": req.model,
                        "max_tokens": req.max_tokens,
                        "system": system_param,
                        "messages": req.messages,
                    },
                })

            result = self._client.messages.batches.create(
                requests=batch_requests,
            )

            batch_id = result.id
            log.info(
                "Anthropic batch submitted: id=%s, requests=%d",
                batch_id, len(requests),
            )
            return batch_id

        except Exception as e:
            log.error("Anthropic batch submission failed: %s", e)
            return None

    def check_batch(self, batch_id: str) -> dict:
        """Check the status of a batch job.

        Returns:
            Dict with keys: status, request_counts, ended_at, etc.
        """
        if not self._available:
            return {"status": "error", "error": "Anthropic not available"}

        try:
            result = self._client.messages.batches.retrieve(batch_id)
            return {
                "status": result.processing_status,  # "in_progress", "ended"
                "request_counts": {
                    "processing": getattr(result.request_counts, 'processing', 0),
                    "succeeded": getattr(result.request_counts, 'succeeded', 0),
                    "errored": getattr(result.request_counts, 'errored', 0),
                    "canceled": getattr(result.request_counts, 'canceled', 0),
                    "expired": getattr(result.request_counts, 'expired', 0),
                },
                "created_at": getattr(result, 'created_at', None),
                "ended_at": getattr(result, 'ended_at', None),
            }
        except Exception as e:
            log.error("Anthropic batch status check failed for %s: %s", batch_id, e)
            return {"status": "error", "error": str(e)}

    def retrieve_results(self, batch_id: str) -> list[dict]:
        """Retrieve completed results from a batch.

        Returns:
            List of dicts, each with custom_id, result type, and message content.
        """
        if not self._available:
            return []

        try:
            results = []
            for entry in self._client.messages.batches.results(batch_id):
                result_data = {
                    "custom_id": entry.custom_id,
                }

                if entry.result.type == "succeeded":
                    message = entry.result.message
                    text = ""
                    if message.content:
                        text = message.content[0].text
                    tokens = message.usage.input_tokens + message.usage.output_tokens
                    result_data.update({
                        "success": True,
                        "text": text,
                        "tokens_used": tokens,
                        "model": message.model,
                        "stop_reason": message.stop_reason,
                    })
                elif entry.result.type == "errored":
                    error = entry.result.error
                    result_data.update({
                        "success": False,
                        "error": f"{error.type}: {error.message}",
                    })
                else:
                    # expired or canceled
                    result_data.update({
                        "success": False,
                        "error": f"Request {entry.result.type}",
                    })

                results.append(result_data)

            log.info(
                "Anthropic batch %s: retrieved %d results",
                batch_id, len(results),
            )
            return results

        except Exception as e:
            log.error("Anthropic batch result retrieval failed for %s: %s", batch_id, e)
            return []


# ---------------------------------------------------------------------------
# OpenAI Batch Client
# ---------------------------------------------------------------------------

class OpenAIBatchClient:
    """Submits and retrieves batch jobs via the OpenAI Batch API.

    Uses the official openai Python SDK:
      - Upload JSONL file
      - client.batches.create()
      - client.batches.retrieve()
      - Download output file

    Reference: https://platform.openai.com/docs/guides/batch
    """

    def __init__(self, api_key: str):
        try:
            import openai
            self._client = openai.OpenAI(api_key=api_key)
            self._available = True
        except ImportError:
            log.warning("OpenAI package not installed — batch API unavailable")
            self._client = None
            self._available = False

    @property
    def available(self) -> bool:
        return self._available

    def submit_batch(self, requests: list[BatchRequest]) -> Optional[str]:
        """Submit a batch of chat completion requests to OpenAI.

        Uploads a JSONL file and creates a batch job.

        Returns:
            Batch ID string, or None on failure.
        """
        if not self._available or not requests:
            return None

        try:
            import io

            # Build JSONL content per OpenAI's batch API spec
            lines = []
            for req in requests:
                # OpenAI uses system message in the messages array
                full_messages = [{"role": "system", "content": req.system}]
                full_messages.extend(req.messages)

                line = json.dumps({
                    "custom_id": req.custom_id,
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": req.model,
                        "messages": full_messages,
                        "max_tokens": req.max_tokens,
                    },
                })
                lines.append(line)

            jsonl_content = "\n".join(lines)

            # Upload the JSONL file
            file_obj = self._client.files.create(
                file=io.BytesIO(jsonl_content.encode("utf-8")),
                purpose="batch",
            )

            # Create the batch
            batch = self._client.batches.create(
                input_file_id=file_obj.id,
                endpoint="/v1/chat/completions",
                completion_window="24h",
            )

            log.info(
                "OpenAI batch submitted: id=%s, file=%s, requests=%d",
                batch.id, file_obj.id, len(requests),
            )
            return batch.id

        except Exception as e:
            log.error("OpenAI batch submission failed: %s", e)
            return None

    def check_batch(self, batch_id: str) -> dict:
        """Check the status of a batch job.

        Returns:
            Dict with status, request counts, and output file info.
        """
        if not self._available:
            return {"status": "error", "error": "OpenAI not available"}

        try:
            batch = self._client.batches.retrieve(batch_id)
            return {
                "status": batch.status,  # validating, in_progress, completed, failed, expired, etc.
                "request_counts": {
                    "total": getattr(batch.request_counts, 'total', 0),
                    "completed": getattr(batch.request_counts, 'completed', 0),
                    "failed": getattr(batch.request_counts, 'failed', 0),
                },
                "output_file_id": batch.output_file_id,
                "error_file_id": batch.error_file_id,
                "created_at": batch.created_at,
                "completed_at": getattr(batch, 'completed_at', None),
            }
        except Exception as e:
            log.error("OpenAI batch status check failed for %s: %s", batch_id, e)
            return {"status": "error", "error": str(e)}

    def retrieve_results(self, batch_id: str) -> list[dict]:
        """Retrieve completed results from a batch.

        Downloads and parses the output JSONL file.

        Returns:
            List of dicts with custom_id, response body, and status.
        """
        if not self._available:
            return []

        try:
            # First check batch status and get output file ID
            batch = self._client.batches.retrieve(batch_id)
            if not batch.output_file_id:
                log.warning("OpenAI batch %s has no output file yet", batch_id)
                return []

            # Download and parse the output file
            content = self._client.files.content(batch.output_file_id)
            output_text = content.read().decode("utf-8")

            results = []
            for line in output_text.strip().split("\n"):
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    custom_id = entry.get("custom_id", "")
                    response = entry.get("response", {})
                    status_code = response.get("status_code", 0)
                    body = response.get("body", {})

                    if status_code == 200:
                        choices = body.get("choices", [])
                        text = choices[0]["message"]["content"] if choices else ""
                        usage = body.get("usage", {})
                        tokens = usage.get("total_tokens", 0)
                        results.append({
                            "custom_id": custom_id,
                            "success": True,
                            "text": text,
                            "tokens_used": tokens,
                            "model": body.get("model", ""),
                        })
                    else:
                        error_body = body.get("error", {})
                        results.append({
                            "custom_id": custom_id,
                            "success": False,
                            "error": error_body.get("message", f"HTTP {status_code}"),
                        })
                except (json.JSONDecodeError, KeyError, IndexError) as e:
                    log.warning("Failed to parse OpenAI batch result line: %s", e)
                    continue

            log.info(
                "OpenAI batch %s: retrieved %d results",
                batch_id, len(results),
            )
            return results

        except Exception as e:
            log.error("OpenAI batch result retrieval failed for %s: %s", batch_id, e)
            return []


# ---------------------------------------------------------------------------
# Batch Scheduler — the main orchestration class
# ---------------------------------------------------------------------------

class BatchScheduler:
    """Accumulates background tasks and submits them as batches for 50% savings.

    Lifecycle:
      1. Swarm's assign_next_task() calls should_batch(task_data) to check urgency.
      2. If BACKGROUND, swarm calls enqueue(request) instead of executing real-time.
      3. Every tick, the scheduler checks if it's time to submit or poll.
      4. submit_pending() sends accumulated requests as a batch.
      5. poll_active() checks for completed batches.
      6. Completed results are returned for the swarm to process.

    Integration point in swarm.py tick():
        # In tick(), add after step 10:
        if self.batch_scheduler:
            completed = self.batch_scheduler.tick()
            for result in completed:
                self._process_batch_result(result)
    """

    # Submit accumulated tasks every 15 minutes
    BATCH_SUBMIT_INTERVAL = 900.0  # seconds

    # Poll for completed batches every 5 minutes
    BATCH_POLL_INTERVAL = 300.0  # seconds

    # Minimum requests before submitting a batch (don't batch 1 request)
    MIN_BATCH_SIZE = 2

    # Maximum requests per batch (API limits)
    MAX_BATCH_SIZE_ANTHROPIC = 10_000
    MAX_BATCH_SIZE_OPENAI = 50_000

    # Maximum age for a batch before we stop polling (25 hours)
    MAX_BATCH_AGE = 90_000.0  # seconds

    def __init__(
        self,
        api_keys: dict[str, str],
        state_dir: Optional[str | Path] = None,
    ):
        self._api_keys = api_keys

        # Initialize batch clients per provider
        self._anthropic_client: Optional[AnthropicBatchClient] = None
        self._openai_client: Optional[OpenAIBatchClient] = None

        anthropic_key = api_keys.get("anthropic_api_key", "")
        if anthropic_key:
            self._anthropic_client = AnthropicBatchClient(anthropic_key)

        openai_key = api_keys.get("openai_api_key", "")
        if openai_key:
            self._openai_client = OpenAIBatchClient(openai_key)

        # Pending requests, keyed by provider
        self._pending_anthropic: list[BatchRequest] = []
        self._pending_openai: list[BatchRequest] = []

        # Active batch jobs being tracked
        self._active_batches: dict[str, BatchJob] = {}

        # Completed results waiting to be processed
        self._completed_results: list[dict] = []

        # Timing
        self._last_submit_time = time.time()
        self._last_poll_time = time.time()

        # Statistics
        self._stats = BatchStats()

        # Persistence
        self._state_dir = Path(state_dir) if state_dir else None
        if self._state_dir:
            self._state_dir.mkdir(parents=True, exist_ok=True)
            self._load_state()

        log.info(
            "BatchScheduler initialized: anthropic=%s, openai=%s",
            "available" if self._anthropic_client and self._anthropic_client.available else "unavailable",
            "available" if self._openai_client and self._openai_client.available else "unavailable",
        )

    @property
    def stats(self) -> BatchStats:
        return self._stats

    @property
    def pending_count(self) -> int:
        """Number of requests waiting to be submitted."""
        return len(self._pending_anthropic) + len(self._pending_openai)

    @property
    def active_batch_count(self) -> int:
        """Number of batch jobs currently being tracked."""
        return len(self._active_batches)

    def should_batch(self, task_data: dict, model: str = "") -> bool:
        """Check whether a task should be routed to batch API.

        Returns True if the task is BACKGROUND urgency AND a batch client
        is available for its provider.
        """
        urgency = classify_urgency(task_data)
        if urgency != TaskUrgency.BACKGROUND:
            return False

        # Check that we have a batch client for the model's provider
        provider_cls = detect_provider_class(model) if model else None
        if provider_cls is None:
            return False

        if provider_cls is AnthropicProvider or (hasattr(provider_cls, 'name') and provider_cls.name == 'anthropic'):
            return self._anthropic_client is not None and self._anthropic_client.available
        if provider_cls is OpenAIProvider or (hasattr(provider_cls, 'name') and provider_cls.name == 'openai'):
            return self._openai_client is not None and self._openai_client.available

        # Other providers don't support batch API
        return False

    def enqueue(self, request: BatchRequest) -> str:
        """Add a request to the pending batch queue.

        Args:
            request: The batch request to queue.

        Returns:
            The custom_id assigned to this request for tracking.
        """
        if not request.custom_id:
            request.custom_id = f"batch-{uuid.uuid4().hex[:12]}"

        # Route to the correct provider queue
        provider_cls = detect_provider_class(request.model)
        if provider_cls is AnthropicProvider or (
            provider_cls and hasattr(provider_cls, 'name') and provider_cls.name == 'anthropic'
        ):
            self._pending_anthropic.append(request)
            log.debug(
                "Batch enqueued (anthropic): %s [%s]",
                request.custom_id, request.task_data.get("title", "")[:50],
            )
        elif provider_cls is OpenAIProvider or (
            provider_cls and hasattr(provider_cls, 'name') and provider_cls.name == 'openai'
        ):
            self._pending_openai.append(request)
            log.debug(
                "Batch enqueued (openai): %s [%s]",
                request.custom_id, request.task_data.get("title", "")[:50],
            )
        else:
            log.warning(
                "Cannot batch request for model %s — no batch client available",
                request.model,
            )
            return request.custom_id

        return request.custom_id

    def tick(self) -> list[dict]:
        """Called every swarm tick cycle. Handles submit and poll timing.

        Returns:
            List of completed batch results ready for processing.
            Each dict has: custom_id, success, text, tokens_used, task_data, worker_name
        """
        now = time.time()
        results = []

        # Submit pending batches if enough time has passed or queue is large
        if now - self._last_submit_time >= self.BATCH_SUBMIT_INTERVAL:
            self._submit_pending()
            self._last_submit_time = now

        # Also submit if we have a lot of pending requests (don't wait)
        if self.pending_count >= 20:
            self._submit_pending()
            self._last_submit_time = now

        # Poll active batches for completion
        if now - self._last_poll_time >= self.BATCH_POLL_INTERVAL:
            results = self._poll_active()
            self._last_poll_time = now

        # Drain completed results buffer
        if self._completed_results:
            results.extend(self._completed_results)
            self._completed_results.clear()

        return results

    def force_submit(self) -> int:
        """Force immediate submission of all pending requests.

        Useful for shutdown or when the queue needs to be flushed.

        Returns:
            Number of requests submitted.
        """
        return self._submit_pending()

    def _submit_pending(self) -> int:
        """Submit accumulated requests as batch jobs.

        Returns:
            Total number of requests submitted across all providers.
        """
        total_submitted = 0

        # Submit Anthropic batch
        if self._pending_anthropic and self._anthropic_client and self._anthropic_client.available:
            if len(self._pending_anthropic) >= self.MIN_BATCH_SIZE:
                # Chunk if over max batch size
                while self._pending_anthropic:
                    chunk = self._pending_anthropic[:self.MAX_BATCH_SIZE_ANTHROPIC]
                    self._pending_anthropic = self._pending_anthropic[self.MAX_BATCH_SIZE_ANTHROPIC:]

                    batch_id = self._anthropic_client.submit_batch(chunk)
                    if batch_id:
                        job = BatchJob(
                            batch_id=batch_id,
                            provider="anthropic",
                            request_count=len(chunk),
                            submitted_at=time.time(),
                            request_map={
                                r.custom_id: {
                                    "task_data": r.task_data,
                                    "worker_name": r.worker_name,
                                    "model": r.model,
                                }
                                for r in chunk
                            },
                        )
                        self._active_batches[batch_id] = job
                        self._stats.batches_submitted += 1
                        self._stats.requests_submitted += len(chunk)
                        total_submitted += len(chunk)
                        log.info(
                            "Anthropic batch submitted: %s (%d requests)",
                            batch_id, len(chunk),
                        )
                    else:
                        # Submission failed — put requests back
                        self._pending_anthropic = chunk + self._pending_anthropic
                        log.error("Anthropic batch submission failed, %d requests re-queued", len(chunk))
                        break

        # Submit OpenAI batch
        if self._pending_openai and self._openai_client and self._openai_client.available:
            if len(self._pending_openai) >= self.MIN_BATCH_SIZE:
                while self._pending_openai:
                    chunk = self._pending_openai[:self.MAX_BATCH_SIZE_OPENAI]
                    self._pending_openai = self._pending_openai[self.MAX_BATCH_SIZE_OPENAI:]

                    batch_id = self._openai_client.submit_batch(chunk)
                    if batch_id:
                        job = BatchJob(
                            batch_id=batch_id,
                            provider="openai",
                            request_count=len(chunk),
                            submitted_at=time.time(),
                            request_map={
                                r.custom_id: {
                                    "task_data": r.task_data,
                                    "worker_name": r.worker_name,
                                    "model": r.model,
                                }
                                for r in chunk
                            },
                        )
                        self._active_batches[batch_id] = job
                        self._stats.batches_submitted += 1
                        self._stats.requests_submitted += len(chunk)
                        total_submitted += len(chunk)
                        log.info(
                            "OpenAI batch submitted: %s (%d requests)",
                            batch_id, len(chunk),
                        )
                    else:
                        self._pending_openai = chunk + self._pending_openai
                        log.error("OpenAI batch submission failed, %d requests re-queued", len(chunk))
                        break

        if total_submitted:
            self._save_state()

        return total_submitted

    def _poll_active(self) -> list[dict]:
        """Poll all active batches for completion and retrieve results.

        Returns:
            List of completed results ready for swarm processing.
        """
        results = []
        expired_ids = []
        now = time.time()

        for batch_id, job in list(self._active_batches.items()):
            # Skip if too old (expired)
            if now - job.submitted_at > self.MAX_BATCH_AGE:
                job.status = "expired"
                expired_ids.append(batch_id)
                log.warning(
                    "Batch %s expired after %.0f hours",
                    batch_id, (now - job.submitted_at) / 3600,
                )
                continue

            # Check status with the appropriate client
            client = (
                self._anthropic_client if job.provider == "anthropic"
                else self._openai_client
            )
            if not client or not client.available:
                continue

            status_info = client.check_batch(batch_id)
            status = status_info.get("status", "unknown")

            # Update job status
            if job.provider == "anthropic":
                if status == "ended":
                    job.status = "completed"
                elif status == "in_progress":
                    job.status = "in_progress"
                elif status == "error":
                    job.status = "failed"
                    job.error = status_info.get("error", "Unknown error")
            elif job.provider == "openai":
                if status == "completed":
                    job.status = "completed"
                elif status in ("validating", "in_progress", "finalizing"):
                    job.status = "in_progress"
                elif status in ("failed", "expired", "cancelling", "cancelled"):
                    job.status = status
                    job.error = status_info.get("error", f"Batch {status}")

            # Retrieve results for completed batches
            if job.status == "completed":
                batch_results = client.retrieve_results(batch_id)
                job.completed_at = now
                job.results = batch_results

                for result in batch_results:
                    custom_id = result.get("custom_id", "")
                    req_info = job.request_map.get(custom_id, {})

                    # Calculate cost (50% of normal rate)
                    model = req_info.get("model", "")
                    tokens = result.get("tokens_used", 0)
                    full_cost = (tokens / 1_000_000) * get_model_cost_per_million(model)
                    batch_cost = full_cost * 0.5  # 50% batch discount
                    savings = full_cost - batch_cost

                    self._stats.total_cost_usd += batch_cost
                    self._stats.total_savings_usd += savings

                    result_with_context = {
                        "custom_id": custom_id,
                        "success": result.get("success", False),
                        "text": result.get("text", ""),
                        "tokens_used": tokens,
                        "error": result.get("error"),
                        "task_data": req_info.get("task_data", {}),
                        "worker_name": req_info.get("worker_name", ""),
                        "model": model,
                        "cost_usd": batch_cost,
                        "savings_usd": savings,
                        "batch_id": batch_id,
                    }
                    results.append(result_with_context)

                self._stats.batches_completed += 1
                self._stats.requests_completed += len(batch_results)
                expired_ids.append(batch_id)

                log.info(
                    "Batch %s completed: %d results, cost=$%.4f, savings=$%.4f",
                    batch_id, len(batch_results),
                    sum(r.get("cost_usd", 0) for r in results),
                    sum(r.get("savings_usd", 0) for r in results),
                )

            elif job.status in ("failed", "expired", "cancelled"):
                self._stats.batches_failed += 1
                expired_ids.append(batch_id)
                log.error(
                    "Batch %s %s: %s",
                    batch_id, job.status, job.error or "no details",
                )

        # Clean up completed/expired/failed batches
        for bid in expired_ids:
            self._active_batches.pop(bid, None)

        if expired_ids:
            self._save_state()

        return results

    def _save_state(self) -> None:
        """Persist active batch jobs and stats to disk."""
        if not self._state_dir:
            return

        state = {
            "active_batches": {
                bid: job.to_dict()
                for bid, job in self._active_batches.items()
            },
            "stats": self._stats.to_dict(),
            "pending_counts": {
                "anthropic": len(self._pending_anthropic),
                "openai": len(self._pending_openai),
            },
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }

        state_path = self._state_dir / "batch_scheduler_state.json"
        try:
            state_path.write_text(
                json.dumps(state, indent=2, default=str),
                encoding="utf-8",
            )
        except Exception as e:
            log.warning("Failed to save batch scheduler state: %s", e)

    def _load_state(self) -> None:
        """Load persisted state from disk.

        Restores active batch tracking so we can resume polling after restart.
        Note: pending requests are NOT persisted (they would be stale).
        """
        if not self._state_dir:
            return

        state_path = self._state_dir / "batch_scheduler_state.json"
        if not state_path.exists():
            return

        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))

            # Restore active batches (so we can poll for their results)
            for bid, job_dict in state.get("active_batches", {}).items():
                if job_dict.get("status") in ("submitted", "in_progress"):
                    self._active_batches[bid] = BatchJob(
                        batch_id=bid,
                        provider=job_dict.get("provider", "anthropic"),
                        request_count=job_dict.get("request_count", 0),
                        submitted_at=job_dict.get("submitted_at", 0),
                        status=job_dict.get("status", "submitted"),
                    )
                    log.info(
                        "Restored active batch %s (%s, %d requests)",
                        bid, job_dict.get("provider"), job_dict.get("request_count", 0),
                    )

            log.info(
                "Batch scheduler state loaded: %d active batches",
                len(self._active_batches),
            )

        except Exception as e:
            log.warning("Failed to load batch scheduler state: %s", e)

    def status_report(self) -> dict:
        """Generate a status report for the dashboard / status command."""
        return {
            "pending": {
                "anthropic": len(self._pending_anthropic),
                "openai": len(self._pending_openai),
                "total": self.pending_count,
            },
            "active_batches": {
                bid: job.to_dict()
                for bid, job in self._active_batches.items()
            },
            "stats": self._stats.to_dict(),
        }

    def shutdown(self) -> None:
        """Graceful shutdown — submit any pending requests and save state.

        Called by swarm.shutdown(). Submits remaining requests so they
        aren't lost, then saves state for resumed polling after restart.
        """
        if self.pending_count > 0:
            log.info(
                "Batch scheduler shutting down with %d pending requests — submitting...",
                self.pending_count,
            )
            # Lower the minimum batch size so we don't lose single requests
            old_min = self.MIN_BATCH_SIZE
            self.MIN_BATCH_SIZE = 1
            self._submit_pending()
            self.MIN_BATCH_SIZE = old_min

        self._save_state()
        log.info(
            "Batch scheduler shutdown complete. Stats: %s",
            json.dumps(self._stats.to_dict()),
        )

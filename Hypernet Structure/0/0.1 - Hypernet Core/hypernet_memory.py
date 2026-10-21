"""hypernet_memory — a minimal client for using Hypernet as provenance-aware
memory for AI agents.

Four calls cover the whole loop:

    mem = HypernetMemory("http://127.0.0.1:8000")
    src  = mem.source("README.md", kind="document")        # optional source node
    addr = mem.remember("Project targets Python 3.12", source=src)
    mem.link(addr, other_addr, "contradicts", evidence="...")
    mem.recall("Python")                                    # -> list of facts
    mem.why(addr)                                           # -> provenance chain

Design notes
------------
* Standard library only (urllib + json). No server changes required; every
  call maps onto an endpoint that already exists in hypernet/server.py.
* Facts are stored as Note objects (type 0.4.10.2.2: "an atomic knowledge or
  memory unit"). The Note type requires ``title``, ``body`` and
  ``created_at`` in ``data``; the client fills all three so strict validation
  passes.
* Provenance is recorded twice on purpose: as the node's ``source_type`` /
  ``source_id`` fields (cheap, always present) and, when a source node is
  given, as a typed ``derived_from`` link (queryable: "everything derived
  from X").
* Addresses are allocated with ``GET /next-address/<area>``, which yields
  zero-padded instance addresses such as ``5.3.00001``. The default area
  ``5.3`` is provisional; pass ``area=`` to use another.
* A changed fact is updated in place; the server keeps every prior version
  under ``/node/<addr>/history``. Use ``link(new, old, "supersedes")`` when
  you want two distinct facts instead.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

__all__ = ["HypernetMemory", "HypernetError", "Fact", "LINK_TYPES", "DEFAULT_FACT_TYPE"]

# Object types (0.4.10 Common Object Taxonomy)
DEFAULT_FACT_TYPE = "0.4.10.2.2"   # Note: atomic knowledge / memory unit
SOURCE_TYPES = {
    "document": "0.4.10.2.1",
    "note": "0.4.10.2.2",
    "message": "0.4.10.2.3",
    "dataset": "0.4.10.2.7",
    "web_page": "0.4.10.2.8",
    "code": "0.4.10.2.9",
}

# Link types (0.6.11 Common Link Taxonomy): relationship -> link_type address
LINK_TYPES = {
    "derived_from": "0.6.11.2.7",
    "supersedes": "0.6.11.2.9",
    "version_of": "0.6.11.2.8",
    "cites": "0.6.11.4.2",
    "about": "0.6.11.4.1",
    "contradicts": "0.6.11.4.4",
    "similar_to": "0.6.11.4.8",
    "implies": "0.6.11.4.10",
}
PROVENANCE_RELATIONSHIPS = ("derived_from", "supersedes", "version_of", "cites", "contradicts")


class HypernetError(RuntimeError):
    """Raised when the server returns a non-2xx status."""

    def __init__(self, status: int, body: str, url: str):
        super().__init__(f"HTTP {status} from {url}: {body[:300]}")
        self.status = status
        self.body = body
        self.url = url


@dataclass
class Fact:
    """A stored fact, as returned by ``recall``/``get``."""
    address: str
    text: str
    source_type: Optional[str]
    source_id: Optional[str]
    type_address: Optional[str]
    updated_at: Optional[str]
    data: dict = field(default_factory=dict)

    @classmethod
    def from_node(cls, node: dict) -> "Fact":
        data = node.get("data") or {}
        return cls(
            address=node.get("address", ""),
            text=data.get("body") or data.get("text") or data.get("title") or "",
            source_type=node.get("source_type"),
            source_id=node.get("source_id"),
            type_address=node.get("type_address"),
            updated_at=node.get("updated_at"),
            data=data,
        )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class HypernetMemory:
    """Thin client over a running Hypernet server."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        *,
        area: str = "5.3",
        api_key: Optional[str] = None,
        agent: str = "agent",
        timeout: float = 15.0,
        strict: bool = False,
        max_retries: int = 5,
    ):
        self.base_url = base_url.rstrip("/")
        self.area = area
        self.api_key = api_key
        self.agent = agent
        self.timeout = timeout
        self.strict = strict
        self.max_retries = max_retries
        self._source_cache: dict[str, str] = {}

    # ------------------------------------------------------------------ http
    def _request(self, method: str, path: str, body: Any = None, params: Optional[dict] = None) -> Any:
        url = self.base_url + path
        if params:
            url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        payload = None if body is None else json.dumps(body).encode("utf-8")
        # The server rate-limits to HYPERNET_RATE_LIMIT requests/minute per
        # client (default 60), even with --no-auth. Back off and retry on 429
        # a bounded number of times rather than failing a demo mid-run.
        delay = 1.0
        for attempt in range(self.max_retries + 1):
            req = urllib.request.Request(url, data=payload, method=method)
            req.add_header("Content-Type", "application/json")
            if self.api_key:
                req.add_header("Authorization", f"Bearer {self.api_key}")
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else None
            except urllib.error.HTTPError as e:
                text = e.read().decode("utf-8", "replace")
                if e.code == 429 and attempt < self.max_retries:
                    retry_after = e.headers.get("Retry-After")
                    time.sleep(float(retry_after) if retry_after else delay)
                    delay = min(delay * 2, 16.0)
                    continue
                raise HypernetError(e.code, text, url) from None
            except urllib.error.URLError as e:
                raise HypernetError(0, f"could not reach server: {e.reason}", url) from None
        raise HypernetError(429, "rate limited; retries exhausted", url)

    def _q(self, address: str) -> str:
        return urllib.parse.quote(address, safe="")

    # --------------------------------------------------------------- basics
    def health(self) -> dict:
        return self._request("GET", "/health")

    def next_address(self, area: Optional[str] = None) -> str:
        return self._request("GET", f"/next-address/{self._q(area or self.area)}")["next"]

    def get(self, address: str) -> dict:
        return self._request("GET", f"/node/{self._q(address)}")

    def history(self, address: str) -> list[dict]:
        return self._request("GET", f"/node/{self._q(address)}/history") or []

    # ----------------------------------------------------------------- write
    def remember(
        self,
        text: str,
        source: Optional[str] = None,
        *,
        title: Optional[str] = None,
        confidence: Optional[float] = None,
        tags: Optional[list[str]] = None,
        type_address: str = DEFAULT_FACT_TYPE,
        source_type: str = "agent",
        address: Optional[str] = None,
        **extra: Any,
    ) -> str:
        """Store a fact and return its address.

        ``source`` may be a free-text identifier ("chat 2026-10-21") or the
        address of a source node created with ``source()``. When it is an
        address, a ``derived_from`` link is created as well.
        """
        addr = address or self.next_address()
        data: dict[str, Any] = {
            "title": title or (text[:80] + ("…" if len(text) > 80 else "")),
            "body": text,
            "created_at": _now(),
            "recorded_by": self.agent,
        }
        if confidence is not None:
            data["confidence"] = float(confidence)
        if tags:
            data["tags"] = list(tags)
        data.update(extra)

        source_is_node = bool(source) and self._looks_like_address(source)
        payload = {
            "type_address": type_address,
            "data": data,
            "source_type": "node" if source_is_node else source_type,
            "source_id": source,
        }
        self._request("PUT", f"/node/{self._q(addr)}", payload,
                      params={"validation_mode": "strict" if self.strict else "warn"})
        if source_is_node:
            self.link(addr, source, "derived_from")
        return addr

    def update(self, address: str, text: Optional[str] = None, *, source: Optional[str] = None, **data: Any) -> dict:
        """Change a stored fact in place. The previous version is kept in history."""
        payload: dict[str, Any] = {"data": dict(data)}
        if text is not None:
            payload["data"]["body"] = text
            payload["data"].setdefault("title", text[:80] + ("…" if len(text) > 80 else ""))
        payload["data"]["updated_by"] = self.agent
        if source is not None:
            # The server keeps a node's original source_type/source_id after
            # creation (see put_node in hypernet/server.py), so the source of
            # a *change* is recorded in data, where history preserves it.
            payload["data"]["source_update"] = source
        return self._request("PUT", f"/node/{self._q(address)}", payload)

    def source(self, name: str, *, kind: str = "document", ref: Optional[str] = None, **extra: Any) -> str:
        """Create (or reuse within this client) a source node and return its address."""
        key = f"{kind}:{name}"
        if key in self._source_cache:
            return self._source_cache[key]
        addr = self.next_address()
        data: dict[str, Any] = {"title": name, "name": name, "kind": kind, "created_at": _now()}
        if kind == "document":
            data.setdefault("format", "text")
            data.setdefault("content_ref", ref or name)
        if ref:
            data["ref"] = ref
        data.update(extra)
        self._request("PUT", f"/node/{self._q(addr)}", {
            "type_address": SOURCE_TYPES.get(kind, SOURCE_TYPES["document"]),
            "data": data,
            "source_type": "external",
            "source_id": ref or name,
        })
        self._source_cache[key] = addr
        return addr

    def link(
        self,
        from_address: str,
        to_address: str,
        relationship: str = "derived_from",
        *,
        evidence: Optional[str] = None,
        strength: float = 1.0,
        link_type: Optional[str] = None,
        **data: Any,
    ) -> dict:
        """Create a typed link. ``relationship`` should be a 0.6.11 name."""
        lt = link_type or LINK_TYPES.get(relationship)
        if lt is None:
            raise ValueError(f"unknown relationship {relationship!r}; pass link_type= explicitly "
                             f"or use one of {sorted(LINK_TYPES)}")
        body = {
            "from_address": from_address,
            "to_address": to_address,
            "link_type": lt,
            "relationship": relationship,
            "strength": strength,
            "data": {"recorded_by": self.agent, **({"evidence": evidence} if evidence else {}), **data},
        }
        return self._request("POST", "/link", body)

    # ------------------------------------------------------------------ read
    def recall(self, query: str, *, limit: int = 10) -> list[Fact]:
        """Full-text search over stored facts."""
        nodes = self._request("GET", "/search", params={"q": query, "limit": limit}) or []
        return [Fact.from_node(n) for n in nodes]

    def all_facts(self, *, type_address: str = DEFAULT_FACT_TYPE, area: Optional[str] = None) -> list[Fact]:
        nodes = self._request("GET", "/query", params={"prefix": area or self.area, "type_address": type_address}) or []
        return [Fact.from_node(n) for n in nodes]

    def derived_from(self, source_address: str) -> list[Fact]:
        """Everything that was derived from a given source node."""
        links = self._request("GET", f"/links/to/{self._q(source_address)}",
                              params={"relationship": "derived_from"}) or []
        return [Fact.from_node(self.get(l["from_address"])) for l in links]

    def why(self, address: str) -> dict:
        """Provenance chain for a fact: current node, source, history, and
        provenance links in both directions with the linked nodes' titles."""
        node = self.get(address)
        hist = self.history(address)
        out = self._request("GET", f"/node/{self._q(address)}/links", params={"direction": "outgoing"}) or []
        inc = self._request("GET", f"/node/{self._q(address)}/links", params={"direction": "incoming"}) or []

        def describe(l: dict, other: str) -> dict:
            try:
                o = self.get(other)
                label = (o.get("data") or {}).get("title") or (o.get("data") or {}).get("name") or other
            except HypernetError:
                label = other
            return {
                "relationship": l.get("relationship"),
                "address": other,
                "label": label,
                "evidence": (l.get("data") or {}).get("evidence"),
                "strength": l.get("strength"),
                "verification_status": l.get("verification_status"),
                "created_at": l.get("created_at"),
            }

        return {
            "address": address,
            "text": Fact.from_node(node).text,
            "type_address": node.get("type_address"),
            "source": {"type": node.get("source_type"), "id": node.get("source_id")},
            "created_at": node.get("created_at"),
            "updated_at": node.get("updated_at"),
            "versions": len(hist) + 1,
            "history": [
                {"version": h.get("version"), "snapshot_at": h.get("snapshot_at"),
                 "content_hash": h.get("content_hash"),
                 "text": Fact.from_node(h.get("node") or {}).text}
                for h in hist
            ],
            "derived_from": [describe(l, l["to_address"]) for l in out
                             if l.get("relationship") in PROVENANCE_RELATIONSHIPS],
            "referenced_by": [describe(l, l["from_address"]) for l in inc
                              if l.get("relationship") in PROVENANCE_RELATIONSHIPS],
        }

    # --------------------------------------------------------------- helpers
    @staticmethod
    def _looks_like_address(s: str) -> bool:
        parts = s.split(".")
        return len(parts) >= 2 and all(p.isdigit() for p in parts)

    def explain(self, address: str) -> str:
        """``why()`` rendered as text."""
        return self.format_why(self.why(address))

    @staticmethod
    def format_why(w: dict) -> str:
        """Human-readable rendering of ``why()`` output."""
        lines = [f"{w['address']}  \"{w['text']}\"",
                 f"  source: {w['source']['type']}:{w['source']['id']}",
                 f"  versions: {w['versions']}  (created {w['created_at']}, updated {w['updated_at']})"]
        for h in w["history"]:
            lines.append(f"    v{h['version']} [{h['content_hash']}] {h['snapshot_at']}: \"{h['text']}\"")
        for d in w["derived_from"]:
            ev = f"  evidence: {d['evidence']}" if d.get("evidence") else ""
            lines.append(f"  --{d['relationship']}--> {d['address']} \"{d['label']}\"{ev}")
        for r in w["referenced_by"]:
            ev = f"  evidence: {r['evidence']}" if r.get("evidence") else ""
            lines.append(f"  <--{r['relationship']}-- {r['address']} \"{r['label']}\"{ev}")
        return "\n".join(lines)

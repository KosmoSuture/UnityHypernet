"""Tests for hypernet_memory against a live local server.

Starts its own server on a free port with an empty temp store, so it needs
no running instance and leaves nothing behind. Run with:

    python test_memory_client.py

or under pytest. Requires fastapi/uvicorn (the server's deps); the client
itself has none.
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hypernet_memory import HypernetMemory, HypernetError, DEFAULT_FACT_TYPE  # noqa: E402


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class LiveServer:
    def __init__(self):
        self.port = _free_port()
        self.tmp = tempfile.mkdtemp(prefix="hn-test-")
        self.url = f"http://127.0.0.1:{self.port}"
        self.proc = None

    def __enter__(self):
        env = {**os.environ, "HYPERNET_RATE_LIMIT": "100000"}
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "hypernet", "serve", "--data", self.tmp,
             "--port", str(self.port), "--host", "127.0.0.1", "--no-auth"],
            cwd=HERE, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        for _ in range(60):
            try:
                urllib.request.urlopen(self.url + "/health", timeout=1).read()
                return self
            except Exception:
                time.sleep(0.5)
        raise RuntimeError("server did not start")

    def __exit__(self, *exc):
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()


def test_remember_recall_why(server_url: str) -> None:
    m = HypernetMemory(server_url, agent="test-agent", strict=True)
    assert m.health()["status"] == "ok"

    src = m.source("spec.md", kind="document", ref="repo://spec.md")
    a = m.remember("Alpha targets Python 3.12", source=src, confidence=0.7)
    b = m.remember("Beta is deprecated", source="chat-1", source_type="chat")
    assert a.startswith(m.area + ".") and b != a

    node = m.get(a)
    assert node["type_address"] == DEFAULT_FACT_TYPE
    assert node["source_type"] == "node" and node["source_id"] == src
    assert node["data"]["body"] == "Alpha targets Python 3.12"
    assert node["data"]["confidence"] == 0.7
    # Note type requires title/body/created_at: strict validation must pass
    assert set(("title", "body", "created_at")) <= set(node["data"])

    # recall by text
    hits = m.recall("Python")
    assert [h.address for h in hits] == [a]

    # derived_from query via the typed link remember() created
    assert [f.address for f in m.derived_from(src)] == [a]

    # update keeps history; title follows the new text
    m.update(a, "Alpha targets Python 3.13", source="spec re-read")
    w = m.why(a)
    assert w["versions"] == 2
    assert w["history"][0]["text"] == "Alpha targets Python 3.12"
    assert w["text"] == "Alpha targets Python 3.13"
    assert m.get(a)["data"]["title"].startswith("Alpha targets Python 3.13")
    assert m.get(a)["data"]["source_update"] == "spec re-read"

    # typed link with evidence shows in both directions
    m.link(b, a, "contradicts", evidence="beta notes")
    wa, wb = m.why(a), m.why(b)
    assert any(r["relationship"] == "contradicts" and r["address"] == b and r["evidence"] == "beta notes"
               for r in wa["referenced_by"])
    assert any(d["relationship"] == "contradicts" and d["address"] == a for d in wb["derived_from"])
    assert "derived_from" in m.explain(a)

    # unknown relationship without an explicit link_type is rejected client-side
    try:
        m.link(a, b, "frobnicates")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass

    # malformed / missing address -> server error surfaces as HypernetError
    try:
        m.get("not-an-address")
        raise AssertionError("expected HypernetError")
    except HypernetError as e:
        assert e.status in (400, 404)


def test_addresses_are_sequential(server_url: str) -> None:
    m = HypernetMemory(server_url, area="5.4", agent="test-agent")
    first = m.remember("one", source="t")
    second = m.remember("two", source="t")
    assert first == "5.4.00001" and second == "5.4.00002"
    assert [f.text for f in m.all_facts(area="5.4")] == ["one", "two"] or \
           sorted(f.text for f in m.all_facts(area="5.4")) == ["one", "two"]


def main() -> int:
    with LiveServer() as s:
        for t in (test_remember_recall_why, test_addresses_are_sequential):
            t(s.url)
            print(f"PASS {t.__name__}")
    print("All memory-client tests passed.")
    return 0


# pytest entry points -------------------------------------------------------
try:
    import pytest  # noqa: F401

    @pytest.fixture(scope="module")
    def server_url():
        with LiveServer() as s:
            yield s.url
except ImportError:  # pytest not installed; plain `python` run still works
    pass


if __name__ == "__main__":
    raise SystemExit(main())

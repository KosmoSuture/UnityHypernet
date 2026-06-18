"""test_sm_with_t4 — verifies the Option-C Hybrid T.4 metering wiring in worker.py.

Covers the Codex round-3 criteria WITHOUT touching the real public repo (uses a LOCAL bare git repo
as the AnchoredChain sink, the same technique as test_github_sink):
  1. the wrapper actually meters a successful call (no bypass) + writes an anchor;
  2. rows are HONEST — the recorded input/output tokens MATCH the stream's actual usage (a forged-claim
     test: different stream usage => different row; the meter cannot invent usage);
  3. a FAILED call (exit!=0) records NO metered row (disclosed-call-failed);
  4. a call with NO usage in the stream records NO metered row (disclosed-no-usage);
  5. FAIL-CLOSED — if the production sink is unavailable (PAT missing), nothing is fabricated;
  6. DISABLED — without the opt-in, behavior is the unchanged disclosure path.

Run: python -m session_manager.test_sm_with_t4
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from session_manager import paths as P
from session_manager import worker
from token_accounting import production
from token_accounting.anchor import AnchoredChain
from token_accounting.github_sink import GitHubSink
from token_accounting.ledger import TokenLedger


def _git(d, *a):
    return subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True)


def _claude_stream(input_tokens, output_tokens, model="claude-opus-4-8", exit_code=0):
    """A minimal claude stream-json call block as worker._stream_to_log would write it."""
    lines = ["--- CALL START 2026-06-06T00:00:00Z ---", "cmd: claude --resume x -p hi"]
    lines.append(json.dumps({"type": "assistant", "message": {"model": model,
                "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens}}}))
    lines.append(json.dumps({"type": "result", "is_error": exit_code != 0,
                "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
                "model": model}))
    lines.append(f"--- CALL END 2026-06-06T00:00:01Z exit={exit_code} ---")
    return "\n".join(lines) + "\n"


class T4WiringTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sm_t4_"))
        # redirect sm paths to tmp
        self._orig = (P.ROOT, P.SESSIONS_DIR, P.ROSTER_PATH, P.AUDIT_LOG, P.NODE_0_MARKER)
        P.ROOT = self.tmp
        P.SESSIONS_DIR = self.tmp / "sessions"
        P.ROSTER_PATH = self.tmp / "roster.json"
        P.AUDIT_LOG = self.tmp / "audit.jsonl"
        P.NODE_0_MARKER = self.tmp / "node0.json"
        self.role = "tally-test"
        P.ensure_role(self.role)
        # a local bare repo as the external append-only sink (no real GitHub)
        self.bare = self.tmp / "anchors.git"
        subprocess.run(["git", "init", "--bare", str(self.bare)], capture_output=True)
        _git(self.bare, "config", "receive.denyNonFastForwards", "true")
        _git(self.bare, "config", "receive.denyDeletes", "true")
        self.clone = self.tmp / "anchors-clone"
        subprocess.run(["git", "clone", str(self.bare), str(self.clone)], capture_output=True)
        _git(self.clone, "config", "user.email", "t@t"); _git(self.clone, "config", "user.name", "t")
        (self.clone / "README.md").write_text("seed\n"); _git(self.clone, "add", "-A")
        _git(self.clone, "commit", "-m", "seed"); _git(self.clone, "branch", "-M", "main")
        _git(self.clone, "push", "-u", "origin", "main")
        os.makedirs(self.clone / "audit-log", exist_ok=True)
        self.db = str(self.tmp / "t4.db")
        # monkeypatch production_token_ledger -> ledger wired to the LOCAL sink
        self._orig_factory = production.production_token_ledger

        def fake_factory(db_path, config_path=None, repo_dir=None):
            sink = GitHubSink(str(self.clone))   # _pat=None -> local push, no auth
            return TokenLedger(db_path, chain=AnchoredChain(sink))
        production.production_token_ledger = fake_factory

    def tearDown(self):
        production.production_token_ledger = self._orig_factory
        (P.ROOT, P.SESSIONS_DIR, P.ROSTER_PATH, P.AUDIT_LOG, P.NODE_0_MARKER) = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _cfg(self, **over):
        c = {"engine": "claude", "session_id": "s", "model": "claude-opus-4-8",
             "account": "2.4.1", "cwd": str(self.tmp), "t4_metering": True,
             "t4_ledger_db": self.db}
        c.update(over); return c

    def _write_stream(self, text):
        paths_stream = P.stream_log(self.role)
        paths_stream.parent.mkdir(parents=True, exist_ok=True)
        paths_stream.write_text(text, encoding="utf-8")

    # 1 + 2 — honest metering + anchor; row MATCHES actual stream usage
    def test_meters_honestly_and_anchors(self):
        self._write_stream(_claude_stream(123, 45))
        r = worker._record_token_accounting(self.role, self._cfg(), "sha1", 0, 100)
        self.assertIn(r["token_metered_mode"], ("anchored", "recorded-anchor-provisional"))
        self.assertEqual(r["token_input_tokens"], 123)
        self.assertEqual(r["token_output_tokens"], 45)
        self.assertEqual(r["token_anchor_count"], 1)
        # ledger row matches the stream EXACTLY (no fabrication)
        led = TokenLedger(self.db)
        rows = led._all_rows(); led.close()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["input_tokens"], 123)
        self.assertEqual(rows[0]["output_tokens"], 45)
        # the anchor landed in the (local) remote append-only history
        anchors = GitHubSink(str(self.clone)).read_log(authoritative=True)
        self.assertEqual(len(anchors), 1)
        # a SECOND, different call records a DIFFERENT honest row + a second anchor
        self._write_stream(_claude_stream(7, 3))
        r2 = worker._record_token_accounting(self.role, self._cfg(), "sha2", 0, 50)
        self.assertEqual(r2["token_input_tokens"], 7)
        self.assertEqual(r2["token_output_tokens"], 3)
        self.assertEqual(r2["token_anchor_count"], 2)
        print("  PASS  honest metering + anchoring (rows match actual usage)")

    # 3 — failed call meters nothing
    def test_failed_call_not_metered(self):
        self._write_stream(_claude_stream(100, 50, exit_code=1))
        r = worker._record_token_accounting(self.role, self._cfg(), "sha", 1, 100)
        self.assertEqual(r["token_metered_mode"], "disclosed-call-failed")
        self.assertEqual(TokenLedger(self.db).count(), 0)
        print("  PASS  failed call not metered")

    # 4 — no usage => not metered
    def test_no_usage_not_metered(self):
        self._write_stream("--- CALL START x ---\ncmd: claude\n{\"type\":\"system\"}\n--- CALL END x exit=0 ---\n")
        r = worker._record_token_accounting(self.role, self._cfg(), "sha", 0, 100)
        self.assertEqual(r["token_metered_mode"], "disclosed-no-usage")
        self.assertEqual(TokenLedger(self.db).count(), 0)
        print("  PASS  no-usage call not metered")

    # 5 — fail-closed when production sink unavailable (PAT missing)
    def test_fail_closed_when_sink_unavailable(self):
        def raising(*a, **k):
            raise ValueError("secrets/config.json missing github.audit_anchors_pat")
        production.production_token_ledger = raising
        self._write_stream(_claude_stream(10, 5))
        r = worker._record_token_accounting(self.role, self._cfg(), "sha", 0, 100)
        self.assertEqual(r["token_metered_mode"], "metering-failed")
        self.assertIn("ValueError", r["token_metered_error"])
        print("  PASS  fail-closed (no fabricated anchor when sink unavailable)")

    # 6 — disabled => disclosure path unchanged
    def test_disabled_uses_disclosure(self):
        self._write_stream(_claude_stream(10, 5))
        r = worker._record_token_accounting(self.role, self._cfg(t4_metering=False), "sha", 0, 100)
        self.assertEqual(r["token_metered_mode"], "disabled")
        self.assertIn("token_disclosure_mode", r)
        print("  PASS  disabled => disclosure path")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(T4WiringTest)
    res = unittest.TextTestRunner(verbosity=1).run(suite)
    print("\nRESULT:", "OK (all checks passed)" if res.wasSuccessful() else "FAIL")
    sys.exit(0 if res.wasSuccessful() else 1)

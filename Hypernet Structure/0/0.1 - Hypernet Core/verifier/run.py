"""CLI entry point for the verification harness (project #6).

Usage (from the "0.1 - Hypernet Core" directory):

    python -m verifier.run                       # run every scenario
    python -m verifier.run trust_alarm           # run a whole subsystem
    python -m verifier.run collaboration::stale_lock_flagged   # run one scenario
    python -m verifier.run --list                # list scenarios without running
    python -m verifier.run --format json         # machine-readable result + findings
    python -m verifier.run --write-findings      # (re)write verifier/FINDINGS.md from FAILs

Exit code: 0 if nothing FAILED and nothing ERRORED. PENDING never fails the run — it is
honest "not testable yet," reported loudly and counted on its own line, but a pending
count can never masquerade as passing.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .finding import FindingsLog
from .scenario import Outcome, RunSummary, run_scenarios
from .scenarios import all_scenarios, select

_GLYPH = {
    Outcome.PASS: "PASS",
    Outcome.FAIL: "FAIL",
    Outcome.PENDING: "PEND",
    Outcome.ERROR: "ERR ",
}
# Auto-generated snapshot of the latest run's FAIL findings. Kept separate from the
# hand-curated FINDINGS.md (which also tracks resolved/fixed/observation findings) so a
# --write-findings run can never clobber the curated record.
FINDINGS_PATH = Path(__file__).resolve().parent / "FINDINGS.auto.md"


def _parse_now(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _text_report(summary: RunSummary) -> str:
    lines = ["", "=== Verifier Harness (project #6) ===", ""]
    for result in summary.results:
        lines.append(f"[{_GLYPH[result.outcome]}] {result.selector}")
        if result.outcome in (Outcome.PENDING, Outcome.FAIL, Outcome.ERROR) and result.detail:
            lines.append(f"        {result.detail}")
        if result.outcome is Outcome.ERROR and result.error_trace:
            lines.append("        " + result.error_trace.strip().replace("\n", "\n        "))
    lines.extend([
        "",
        f"=== {summary.passed} passed, {summary.failed} failed, "
        f"{summary.pending} pending, {summary.errored} errored ===",
    ])
    if summary.pending:
        lines.append(f"    ({summary.pending} pending = honest not-yet-testable; NOT counted as passing)")
    if summary.findings:
        lines.append(f"    ({len(summary.findings)} finding(s) — see `python -m verifier.run --format json` or FINDINGS.md)")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Wave 1 verification harness (#6).")
    parser.add_argument("selectors", nargs="*", help="subsystem or subsystem::scenario; empty = all")
    parser.add_argument("--list", action="store_true", help="list scenarios and exit")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--now", default="", help="freeze the clock (ISO 8601) for deterministic runs")
    parser.add_argument("--write-findings", action="store_true", help="(re)write FINDINGS.md from FAILs")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.list:
        for scenario in all_scenarios():
            print(f"{scenario.selector}\t{scenario.description}")
        return 0

    scenarios = select(args.selectors)
    if not scenarios:
        print(f"No scenarios match {args.selectors}. Use --list to see selectors.", file=sys.stderr)
        return 2

    summary = run_scenarios(scenarios, now=_parse_now(args.now))

    if args.write_findings:
        log = FindingsLog(FINDINGS_PATH)
        for finding in summary.findings:
            log.add(finding)
        log.write()

    if args.format == "json":
        print(json.dumps(
            {
                "summary": {
                    "passed": summary.passed,
                    "failed": summary.failed,
                    "pending": summary.pending,
                    "errored": summary.errored,
                    "ok": summary.ok,
                },
                "results": [r.to_dict() for r in summary.results],
            },
            indent=2,
            ensure_ascii=False,
        ))
    else:
        print(_text_report(summary))

    return 0 if summary.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

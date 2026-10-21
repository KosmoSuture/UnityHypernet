#!/usr/bin/env python3
"""Agent-memory demo: an agent stores what it learns, with provenance, in Hypernet.

Run a server first (empty store, no auth):

    python -m hypernet serve --data /tmp/hn-demo --port 8766 --no-auth

then:

    python examples/agent_memory_demo.py --url http://127.0.0.1:8766

The script plays the part of a small coding agent that reads two documents,
stores three facts, links them to their sources, learns something that
changes one of them, and then answers "why do you believe that?" from the
graph alone. Nothing here calls a paid model; it is a scripted agent so the
run is deterministic and reproducible.
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hypernet_memory import HypernetMemory, HypernetError  # noqa: E402


def banner(title: str) -> None:
    print("\n" + "=" * 72 + f"\n{title}\n" + "=" * 72)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8766")
    ap.add_argument("--area", default="5.3", help="address prefix for stored facts (default 5.3)")
    ap.add_argument("--api-key", default=os.environ.get("HYPERNET_API_KEY"))
    args = ap.parse_args()

    mem = HypernetMemory(args.url, area=args.area, api_key=args.api_key, agent="demo-agent", strict=True)
    try:
        mem.health()
    except HypernetError as e:
        print(f"Cannot reach a Hypernet server at {args.url}: {e}\n"
              f"Start one with:\n  python -m hypernet serve --data /tmp/hn-demo --port 8766 --no-auth")
        return 1

    # --- 1. the agent reads two documents and records what it learned -------
    banner("1. Agent reads sources and stores facts with provenance")
    readme = mem.source("README.md", kind="document", ref="repo://README.md")
    pyproj = mem.source("pyproject.toml", kind="document", ref="repo://pyproject.toml")

    f1 = mem.remember("The core library has zero external dependencies.", source=readme, confidence=0.9)
    f2 = mem.remember("The API server requires fastapi, uvicorn and pydantic.", source=readme, confidence=0.9)
    f3 = mem.remember("The project targets Python 3.11.", source=pyproj, confidence=0.6)
    for a in (f1, f2, f3):
        print(f"  stored {a}: {mem.get(a)['data']['body']}")

    # --- 2. a user tells the agent something in chat -------------------------
    banner("2. Agent learns from a conversation (free-text source)")
    f4 = mem.remember("The maintainer prefers tests to be run with `python test_hypernet.py`.",
                      source="chat 2026-10-21 with maintainer", source_type="chat", confidence=0.8)
    print(f"  stored {f4}: {mem.get(f4)['data']['body']}")

    # --- 3. the agent discovers it was wrong about one fact ------------------
    banner("3. A fact changes; the old version is kept in history")
    mem.update(f3, "The project targets Python 3.12.", source="pyproject.toml re-read", confidence=0.95)
    mem.link(f3, pyproj, "cites", evidence="requires-python field")
    print(f"  updated {f3}: {mem.get(f3)['data']['body']}")

    # --- 4. the agent records that two facts are related --------------------
    banner("4. Typed links between facts")
    mem.link(f2, f1, "implies", evidence="server deps are optional extras over a dependency-free core")
    print(f"  linked {f2} --implies--> {f1}")

    # --- 5. recall by search --------------------------------------------------
    banner("5. Recall")
    for q in ("Python", "fastapi"):
        hits = mem.recall(q)
        print(f"  recall({q!r}) -> " + "; ".join(f"{h.address} \"{h.text}\"" for h in hits))

    # --- 6. everything derived from one source -------------------------------
    banner("6. Everything derived from README.md")
    for f in mem.derived_from(readme):
        print(f"  {f.address}: {f.text}")

    # --- 7. why? --------------------------------------------------------------
    banner("7. Why do you believe that?  (provenance chain from the graph)")
    for a in (f3, f2):
        print(mem.explain(a))
        print()

    print("Done. Every record above is on disk under the server's --data directory;\n"
          "inspect it at the server's /explorer page, or re-run this script to see\n"
          "a second set of facts allocated at the next addresses.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

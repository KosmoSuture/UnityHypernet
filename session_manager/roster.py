"""Roster CRUD — registered roles + their launch config."""
import json
from typing import Dict, Optional
from . import paths


def load() -> Dict[str, dict]:
    if not paths.ROSTER_PATH.exists():
        return {}
    return json.loads(paths.ROSTER_PATH.read_text(encoding="utf-8"))


def save(roster: Dict[str, dict]):
    paths.ROSTER_PATH.write_text(
        json.dumps(roster, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def get(role: str) -> Optional[dict]:
    return load().get(role)


def add(role: str, engine: str, session_id: str, model: str = "",
        cwd: str = "", append_system_prompt: str = "",
        tools: str = "", notes: str = "", account: str = "",
        token_ledger_db: str = ""):
    r = load()
    if role in r:
        raise ValueError(f"role '{role}' already registered (use 'sm rm {role}' first)")
    r[role] = {
        "engine": engine,           # 'claude' or 'codex'
        "session_id": session_id,
        "model": model,
        "cwd": cwd or r"C:\Hypernet",
        "append_system_prompt": append_system_prompt,
        "tools": tools,             # claude only
        "notes": notes,
        "account": account,
        "token_ledger_db": token_ledger_db,
    }
    save(r)
    paths.ensure_role(role)
    return r[role]


def remove(role: str):
    r = load()
    if role in r:
        del r[role]
        save(r)


def list_roles() -> Dict[str, dict]:
    return load()

"""Manifest parsing and canonicalization for object containers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


Manifest = Dict[str, Any]


def load_manifest(path: str | Path) -> Manifest:
    """Load a manifest.yaml file.

    Public-alpha implementation supports JSON-compatible YAML. JSON is a
    YAML subset and keeps the reference implementation dependency-free
    until a full YAML parser is selected.
    """

    text = Path(path).read_text(encoding="utf-8")
    return loads_manifest(text)


def loads_manifest(text: str) -> Manifest:
    stripped = text.strip()
    if not stripped:
        raise ValueError("manifest is empty")
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "manifest.yaml must be JSON-compatible YAML in the reference implementation"
        ) from exc
    if not isinstance(data, dict):
        raise ValueError("manifest root must be an object")
    return data


def canonical_manifest_json(manifest: Manifest) -> str:
    """Return the deterministic JSON projection used for hashing."""

    return json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

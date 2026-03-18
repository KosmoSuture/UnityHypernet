"""
Hypernet Frontmatter

Parse, write, and infer YAML frontmatter for Markdown files.
Every .md file in the Hypernet should carry standard metadata
in YAML frontmatter format:

  ---
  ha: "2.1.0"
  object_type: "0.5.3.1"
  creator: "1.1"
  created: "2026-02-12T00:00:00Z"
  position_2d: null
  position_3d: null
  flags: []
  ---
  # Document Title
  Content starts here...

This module provides zero-dependency parsing (no PyYAML required)
for the simple flat structure used in Hypernet frontmatter.
"""

from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# Standard frontmatter fields in canonical order
STANDARD_FIELDS = ["ha", "object_type", "creator", "created", "position_2d", "position_3d", "flags"]


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter from markdown content.

    Returns (metadata_dict, body_text). If no frontmatter is found,
    returns ({}, original_content).

    Rules:
    - Frontmatter starts with '---' on line 1
    - Frontmatter ends with the next '---' on its own line
    - Content between delimiters is parsed as simple YAML
    """
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, content

    # Find closing delimiter
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return {}, content

    # Parse the YAML block (simple flat parser — handles our standard fields)
    yaml_lines = lines[1:end_idx]
    metadata = _parse_simple_yaml(yaml_lines)

    # Body is everything after the closing ---
    body = "\n".join(lines[end_idx + 1:])
    # Strip leading blank line if present
    if body.startswith("\n"):
        body = body[1:]

    return metadata, body


def add_frontmatter(content: str, metadata: dict[str, Any]) -> str:
    """Add or replace YAML frontmatter in markdown content.

    If frontmatter already exists, it is replaced.
    If not, it is prepended.
    """
    existing, body = parse_frontmatter(content)

    if not existing:
        # No existing frontmatter — body is the full content
        body = content

    yaml_block = _format_yaml(metadata)
    return f"---\n{yaml_block}---\n{body}"


def infer_metadata_from_path(
    filepath: str | Path,
    archive_root: str | Path = ".",
) -> dict[str, Any]:
    """Infer frontmatter metadata from a file's path in the archive.

    Heuristics:
    - HA: extracted from folder names like "2.1.0 - Identity" → "2.1.0"
    - Creator: inferred from owner path (1.1 = Matt, 2.1.loom = Loom, etc.)
    - Object type: "0.5.3.1" for all .md files
    - Created: file modification time (best available approximation)
    """
    filepath = Path(filepath)
    archive_root = Path(archive_root)

    try:
        relpath = filepath.relative_to(archive_root)
    except ValueError:
        relpath = filepath

    # Infer HA from path
    ha = _infer_ha_from_path(relpath)

    # Infer creator
    creator = _infer_creator_from_path(relpath)

    # Get file timestamps
    try:
        stat = filepath.stat()
        created = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
    except OSError:
        created = datetime.now(timezone.utc).isoformat()

    return {
        "ha": ha,
        "object_type": "0.5.3.1",  # Markdown document
        "creator": creator,
        "created": created,
        "position_2d": None,
        "position_3d": None,
        "flags": [],
    }


def _infer_ha_from_path(relpath: Path) -> str:
    """Extract a Hypernet Address from a file's relative path.

    Looks for folder names starting with address patterns like:
    "2.1.0 - Identity" → "2.1.0"
    "0.5.3.1 Markdown Document Type" → "0.5.3.1"
    "1.1 Matt Schaeffer" → "1.1"
    """
    parts = list(relpath.parts)

    # Walk from deepest to shallowest, looking for address-like folder names
    for part in reversed(parts[:-1]):  # Skip filename
        match = re.match(r'^(\d+(?:\.\d+)*)', part)
        if match:
            return match.group(1)

    # If file itself has an address-like name
    stem = relpath.stem
    match = re.match(r'^(\d+(?:\.\d+)*)', stem)
    if match:
        return match.group(1)

    # Fallback: construct from path parts
    return "unknown"


def _infer_creator_from_path(relpath: Path) -> str:
    """Infer the creator HA from the file's location in the archive."""
    path_str = str(relpath).replace("\\", "/").lower()

    # AI instance directories
    if "instances/loom" in path_str:
        return "2.1.loom"
    if "instances/trace" in path_str:
        return "2.1.trace"
    if "instances/verse" in path_str:
        return "2.1.verse"

    # AI account (general)
    if "2 - ai accounts" in path_str or "2.1" in path_str:
        return "2.1"

    # People
    if "1 - people" in path_str or "1.1" in path_str:
        return "1.1"

    # System definitions
    if path_str.startswith("0/") or path_str.startswith("0\\"):
        return "1.1"  # System docs created by Matt

    return "1.1"  # Default to Matt as creator


def _parse_simple_yaml(lines: list[str]) -> dict[str, Any]:
    """Parse simple flat YAML — handles strings, numbers, null, lists, and dicts.

    This is NOT a full YAML parser. It handles the flat structure used in
    Hypernet frontmatter:
      key: "string value"
      key: null
      key: 42
      key: []
      key: ["a", "b"]
    """
    result = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        colon_idx = line.find(":")
        if colon_idx == -1:
            continue

        key = line[:colon_idx].strip()
        value_str = line[colon_idx + 1:].strip()

        result[key] = _parse_yaml_value(value_str)

    return result


def _parse_yaml_value(value_str: str) -> Any:
    """Parse a single YAML value."""
    if not value_str:
        return None

    # null
    if value_str in ("null", "~", ""):
        return None

    # boolean
    if value_str in ("true", "True", "yes"):
        return True
    if value_str in ("false", "False", "no"):
        return False

    # Quoted string
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]

    # List (inline)
    if value_str.startswith("[") and value_str.endswith("]"):
        inner = value_str[1:-1].strip()
        if not inner:
            return []
        items = []
        for item in _split_yaml_list(inner):
            items.append(_parse_yaml_value(item.strip()))
        return items

    # Dict (inline) — simple {key: value, key: value}
    if value_str.startswith("{") and value_str.endswith("}"):
        inner = value_str[1:-1].strip()
        if not inner:
            return {}
        result = {}
        for pair in _split_yaml_list(inner):
            pair = pair.strip()
            ci = pair.find(":")
            if ci != -1:
                k = pair[:ci].strip()
                v = pair[ci + 1:].strip()
                result[k] = _parse_yaml_value(v)
        return result

    # Number
    try:
        if "." in value_str:
            return float(value_str)
        return int(value_str)
    except ValueError:
        pass

    # Bare string
    return value_str


def _split_yaml_list(s: str) -> list[str]:
    """Split a comma-separated YAML inline list, respecting quotes."""
    items = []
    current = []
    depth = 0
    in_quote = None

    for ch in s:
        if ch in ('"', "'") and in_quote is None:
            in_quote = ch
            current.append(ch)
        elif ch == in_quote:
            in_quote = None
            current.append(ch)
        elif ch in ("{", "["):
            depth += 1
            current.append(ch)
        elif ch in ("}", "]"):
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0 and in_quote is None:
            items.append("".join(current))
            current = []
        else:
            current.append(ch)

    if current:
        items.append("".join(current))

    return items


def _format_yaml(metadata: dict[str, Any]) -> str:
    """Format metadata dict as YAML frontmatter content.

    Outputs fields in standard order first, then any extra fields.
    """
    lines = []

    # Standard fields first, in canonical order
    for key in STANDARD_FIELDS:
        if key in metadata:
            lines.append(f"{key}: {_format_yaml_value(metadata[key])}")

    # Any extra fields
    for key, value in metadata.items():
        if key not in STANDARD_FIELDS:
            lines.append(f"{key}: {_format_yaml_value(value)}")

    return "\n".join(lines) + "\n"


def _format_yaml_value(value: Any) -> str:
    """Format a single value for YAML output."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        if not value:
            return "[]"
        items = ", ".join(_format_yaml_value(v) for v in value)
        return f"[{items}]"
    if isinstance(value, dict):
        if not value:
            return "{}"
        pairs = ", ".join(f"{k}: {_format_yaml_value(v)}" for k, v in value.items())
        return f"{{{pairs}}}"
    return str(value)

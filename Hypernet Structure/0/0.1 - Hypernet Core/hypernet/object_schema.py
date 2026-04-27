"""
Hypernet Object Schema Registry

Runtime view of the folderized object taxonomy under 0.4.10. The canonical
source is the object type folder README, not a root-level summary file.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import re
from typing import Any, Optional

from .frontmatter import parse_frontmatter


_CORE_ROOT = Path(__file__).resolve().parents[1]
_STRUCTURE_ZERO = _CORE_ROOT.parent
_OBJECT_TAXONOMY_ROOT = (
    _STRUCTURE_ZERO
    / "0.4 - Object Type Registry"
    / "0.4.10 - Common Object Taxonomy"
)


@dataclass(frozen=True)
class ObjectTypeDef:
    """Definition of an object type from the canonical folder taxonomy."""

    address: str
    name: str
    domain_address: str
    domain_name: str
    purpose: str
    required_fields: tuple[str, ...]
    recommended_links: tuple[str, ...]
    status: str = "active"
    visibility: str = "public"
    flags: tuple[str, ...] = ()
    folder: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "address": self.address,
            "name": self.name,
            "domain_address": self.domain_address,
            "domain_name": self.domain_name,
            "purpose": self.purpose,
            "required_fields": list(self.required_fields),
            "recommended_links": list(self.recommended_links),
            "status": self.status,
            "visibility": self.visibility,
            "flags": list(self.flags),
            "folder": self.folder,
        }


def _address_sort_key(address: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", address))


def _folder_address_name(folder_name: str) -> tuple[str, str]:
    match = re.match(r"^(\d+(?:\.\d+)*)\s+-\s+(.+)$", folder_name)
    if not match:
        return "", folder_name
    return match.group(1), match.group(2).strip()


def _heading_name(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            heading = line[2:].strip()
            match = re.match(r"^\d+(?:\.\d+)*\s+-\s+(.+)$", heading)
            return match.group(1).strip() if match else heading
    return fallback


def _section_lines(body: str, heading: str) -> list[str]:
    lines = body.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip() == f"## {heading}":
            start = idx + 1
            break
    if start is None:
        return []

    result: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        result.append(line.rstrip())
    return result


def _section_text(body: str, heading: str) -> str:
    lines = [line.strip() for line in _section_lines(body, heading)]
    paragraphs = [line for line in lines if line and not line.startswith("- ")]
    return " ".join(paragraphs).strip()


def _section_bullets(body: str, heading: str) -> tuple[str, ...]:
    values: list[str] = []
    for line in _section_lines(body, heading):
        stripped = line.strip()
        if stripped.startswith("- "):
            values.append(stripped[2:].strip().strip("`"))
    return tuple(values)


def _relative_folder(folder: Path) -> str:
    try:
        return str(folder.relative_to(_STRUCTURE_ZERO)).replace("\\", "/")
    except ValueError:
        return str(folder).replace("\\", "/")


def _read_object_type(folder: Path) -> Optional[ObjectTypeDef]:
    readme = folder / "README.md"
    if not readme.exists():
        return None

    metadata, body = parse_frontmatter(readme.read_text(encoding="utf-8"))
    address, fallback_name = _folder_address_name(folder.name)
    domain_address, domain_name = _folder_address_name(folder.parent.name)

    address = str(metadata.get("ha") or address)
    name = _heading_name(body, fallback_name)
    if not address or metadata.get("object_type") != "object_type_definition":
        return None

    flags = metadata.get("flags", ())
    if not isinstance(flags, (list, tuple)):
        flags = ()

    return ObjectTypeDef(
        address=address,
        name=name,
        domain_address=domain_address,
        domain_name=domain_name,
        purpose=_section_text(body, "Purpose"),
        required_fields=_section_bullets(body, "Required Fields"),
        recommended_links=_section_bullets(body, "Recommended Graph Links"),
        status=str(metadata.get("status") or "active"),
        visibility=str(metadata.get("visibility") or "public"),
        flags=tuple(str(flag) for flag in flags),
        folder=_relative_folder(folder),
    )


@lru_cache(maxsize=1)
def _load_object_types() -> tuple[ObjectTypeDef, ...]:
    if not _OBJECT_TAXONOMY_ROOT.exists():
        return ()

    definitions: list[ObjectTypeDef] = []
    for domain in _OBJECT_TAXONOMY_ROOT.iterdir():
        if not domain.is_dir():
            continue
        for object_folder in domain.iterdir():
            if not object_folder.is_dir():
                continue
            definition = _read_object_type(object_folder)
            if definition is not None:
                definitions.append(definition)

    definitions.sort(key=lambda item: _address_sort_key(item.address))
    return tuple(definitions)


def list_object_type_defs(domain: Optional[str] = None) -> list[dict[str, Any]]:
    """Return object type definitions for API/schema clients."""
    definitions = _load_object_types()
    if domain:
        needle = domain.lower()
        definitions = tuple(
            item for item in definitions
            if item.domain_address.lower() == needle or item.domain_name.lower() == needle
        )
    return [item.to_dict() for item in definitions]


def get_object_type_def(identifier: str) -> Optional[dict[str, Any]]:
    """Look up an object type by address or case-insensitive type name."""
    needle = identifier.lower()
    for item in _load_object_types():
        if item.address.lower() == needle or item.name.lower() == needle:
            return item.to_dict()
    return None


def object_type_summary() -> dict[str, Any]:
    """Return compact object taxonomy counts."""
    domains: dict[str, dict[str, Any]] = {}
    for item in _load_object_types():
        entry = domains.setdefault(
            item.domain_address,
            {"name": item.domain_name, "count": 0},
        )
        entry["count"] += 1

    return {
        "total_defined_object_types": len(_load_object_types()),
        "taxonomy_root": "0.4.10",
        "folder": _relative_folder(_OBJECT_TAXONOMY_ROOT),
        "domains": dict(sorted(domains.items(), key=lambda pair: _address_sort_key(pair[0]))),
    }


def validate_object_payload(type_address: str, data: dict[str, Any]) -> dict[str, Any]:
    """Return non-mutating validation information for a node payload."""
    definition = get_object_type_def(type_address)
    if definition is None:
        return {
            "type_address": type_address,
            "known_type": False,
            "valid": False,
            "missing_required_fields": [],
            "issues": [f"Unknown object type: {type_address}"],
            "warnings": [],
        }

    missing = [
        field
        for field in definition["required_fields"]
        if field not in data or data[field] in (None, "")
    ]
    issues = [f"Missing required field: {field}" for field in missing]
    return {
        "type_address": type_address,
        "known_type": True,
        "valid": not missing,
        "missing_required_fields": missing,
        "issues": issues,
        "warnings": [],
    }

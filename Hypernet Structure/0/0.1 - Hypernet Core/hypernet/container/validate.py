"""Validation for Hypernet object containers."""

from __future__ import annotations

import hashlib
import stat
import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Iterable, List

from .manifest import load_manifest, loads_manifest


REQUIRED_FILES = {
    "manifest.yaml",
    "schema.yaml",
    "provenance/history.yaml",
    "checksums.sha256",
}

REQUIRED_MANIFEST_SECTIONS = {
    "container",
    "identity",
    "metadata",
    "access",
    "integrity",
    "links",
    "provenance",
}


@dataclass
class ContainerLimits:
    max_entries: int = 10000
    max_total_uncompressed: int = 500 * 1024 * 1024
    max_entry_size: int = 100 * 1024 * 1024
    max_compression_ratio: int = 100
    max_depth: int = 24
    max_component_length: int = 255
    max_filename_length: int = 255


@dataclass
class ValidationResult:
    carrier: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def require_valid(self) -> "ValidationResult":
        if not self.valid:
            raise ContainerValidationError("; ".join(self.errors))
        return self


class ContainerValidationError(ValueError):
    """Raised when a container fails validation."""


def validate_container(path: str | Path, limits: ContainerLimits | None = None) -> ValidationResult:
    target = Path(path)
    limits = limits or ContainerLimits()
    if target.is_dir():
        return validate_directory(target, limits)
    if target.is_file() and target.suffix == ".zip":
        return validate_zip(target, limits)
    return ValidationResult(carrier="unknown", valid=False, errors=["unsupported carrier"])


def validate_directory(path: Path, limits: ContainerLimits) -> ValidationResult:
    errors: List[str] = []
    files = sorted(_relative_files(path))
    file_set = set(files)

    missing = sorted(REQUIRED_FILES - file_set)
    if missing:
        errors.append(f"missing required files: {', '.join(missing)}")

    try:
        manifest = load_manifest(path / "manifest.yaml")
    except Exception as exc:  # noqa: BLE001 - preserve validation error
        errors.append(f"manifest error: {exc}")
        manifest = {}

    missing_sections = sorted(REQUIRED_MANIFEST_SECTIONS - set(manifest))
    if missing_sections:
        errors.append(f"missing manifest sections: {', '.join(missing_sections)}")

    checksum_errors = _validate_checksums(path, files)
    errors.extend(checksum_errors)

    return ValidationResult(carrier="directory", valid=not errors, errors=errors)


def validate_zip(path: Path, limits: ContainerLimits) -> ValidationResult:
    errors: List[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            errors.extend(_validate_zip_infos(infos, limits))
            file_set = {info.filename for info in infos if not info.is_dir()}

            missing = sorted(REQUIRED_FILES - file_set)
            if missing:
                errors.append(f"missing required files: {', '.join(missing)}")

            if "manifest.yaml" in file_set:
                try:
                    manifest = loads_manifest(archive.read("manifest.yaml").decode("utf-8"))
                except Exception as exc:  # noqa: BLE001 - preserve validation error
                    errors.append(f"manifest error: {exc}")
                    manifest = {}
                missing_sections = sorted(REQUIRED_MANIFEST_SECTIONS - set(manifest))
                if missing_sections:
                    errors.append(f"missing manifest sections: {', '.join(missing_sections)}")

            if "checksums.sha256" in file_set:
                errors.extend(_validate_zip_checksums(archive, file_set))
    except zipfile.BadZipFile as exc:
        errors.append(f"bad zip file: {exc}")
    return ValidationResult(carrier="zip", valid=not errors, errors=errors)


def _relative_files(root: Path) -> Iterable[str]:
    for child in root.rglob("*"):
        if child.is_file():
            yield child.relative_to(root).as_posix()


def _validate_checksums(root: Path, files: List[str]) -> List[str]:
    checksum_path = root / "checksums.sha256"
    if not checksum_path.exists():
        return []

    expected, parse_errors = _parse_checksums(checksum_path.read_text(encoding="utf-8"))
    if parse_errors:
        return parse_errors

    errors: List[str] = []
    for rel in files:
        if rel == "checksums.sha256":
            continue
        if rel not in expected:
            errors.append(f"missing checksum entry: {rel}")
            continue
        digest = hashlib.sha256((root / rel).read_bytes()).hexdigest()
        if digest != expected[rel]:
            errors.append(f"checksum mismatch: {rel}")
    for rel in sorted(expected):
        if rel not in files:
            errors.append(f"checksum entry references missing file: {rel}")
    return errors


def _validate_zip_checksums(archive: zipfile.ZipFile, files: set[str]) -> List[str]:
    expected, parse_errors = _parse_checksums(archive.read("checksums.sha256").decode("utf-8"))
    if parse_errors:
        return parse_errors

    errors: List[str] = []
    for rel in sorted(files):
        if rel == "checksums.sha256":
            continue
        if rel not in expected:
            errors.append(f"missing checksum entry: {rel}")
            continue
        digest = hashlib.sha256(archive.read(rel)).hexdigest()
        if digest != expected[rel]:
            errors.append(f"checksum mismatch: {rel}")
    for rel in sorted(expected):
        if rel not in files:
            errors.append(f"checksum entry references missing file: {rel}")
    return errors


def _parse_checksums(text: str) -> tuple[dict[str, str], List[str]]:
    expected: dict[str, str] = {}
    errors: List[str] = []
    hex_chars = set("0123456789abcdef")

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split(maxsplit=1)
        if len(parts) != 2:
            errors.append(f"invalid checksum line: {line}")
            continue
        digest = parts[0].lower()
        rel = parts[1]
        if len(digest) != 64 or any(char not in hex_chars for char in digest):
            errors.append(f"invalid sha256 digest: {rel}")
        if rel in expected:
            errors.append(f"duplicate checksum entry: {rel}")
        expected[rel] = digest
    return expected, errors


def _validate_zip_infos(infos: List[zipfile.ZipInfo], limits: ContainerLimits) -> List[str]:
    errors: List[str] = []
    if len(infos) > limits.max_entries:
        errors.append("zip entry count exceeds limit")

    total = 0
    seen = set()
    for info in infos:
        name = info.filename
        total += info.file_size
        path = PurePosixPath(name)
        parts = path.parts

        if name in seen:
            errors.append(f"duplicate zip entry rejected: {name}")
        seen.add(name)
        if path.is_absolute() or name.startswith(("/", "\\")):
            errors.append(f"absolute path rejected: {name}")
        if "\\" in name:
            errors.append(f"backslash path rejected: {name}")
        if ".." in parts:
            errors.append(f"path traversal rejected: {name}")
        if len(parts) > limits.max_depth:
            errors.append(f"path depth exceeds limit: {name}")
        if any(len(part) > limits.max_component_length for part in parts):
            errors.append(f"path component exceeds limit: {name}")
        if parts and len(parts[-1]) > limits.max_filename_length:
            errors.append(f"filename exceeds limit: {name}")
        if info.file_size > limits.max_entry_size:
            errors.append(f"entry size exceeds limit: {name}")
        if info.compress_size and info.file_size / info.compress_size > limits.max_compression_ratio:
            errors.append(f"compression ratio exceeds limit: {name}")
        mode = (info.external_attr >> 16) & 0o777777
        if stat.S_ISLNK(mode):
            errors.append(f"symlink entry rejected: {name}")

    if total > limits.max_total_uncompressed:
        errors.append("zip total uncompressed size exceeds limit")
    return errors

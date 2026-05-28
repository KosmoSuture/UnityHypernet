"""Deterministic zip packing for directory-form object containers."""

from __future__ import annotations

import zipfile
from pathlib import Path


FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def pack_directory(source: str | Path, destination: str | Path) -> Path:
    """Pack a directory carrier into a deterministic .zip file.

    This helper is intentionally conservative: lexical member order,
    fixed timestamps, normalized file permissions, and deflate
    compression using the standard library.
    """

    source_path = Path(source)
    destination_path = Path(destination)
    files = sorted(p for p in source_path.rglob("*") if p.is_file())
    with zipfile.ZipFile(destination_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            rel = file_path.relative_to(source_path).as_posix()
            info = zipfile.ZipInfo(rel, FIXED_ZIP_TIMESTAMP)
            info.external_attr = 0o100644 << 16
            archive.writestr(info, file_path.read_bytes())
    return destination_path

"""Load object containers into the reference validation model."""

from __future__ import annotations

from pathlib import Path

from .validate import ContainerLimits, ValidationResult, validate_container


def load_container(path: str | Path, limits: ContainerLimits | None = None) -> ValidationResult:
    """Validate and return the carrier-level model for a container."""

    return validate_container(path, limits=limits).require_valid()

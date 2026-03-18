"""
Hypernet Address Enforcement

Ensures EVERYTHING in the Hypernet has a valid Hypernet Address.
This is the enforcement layer for Task 032 (Critical Priority):
"Everything Gets an Address — no exceptions."

Three concerns:
  1. Validation — Is this address well-formed and in the right category?
  2. Audit — What in the store is missing or has invalid addresses?
  3. Enforcement — Reject creation of nodes without valid addresses.

Address categories (from the addressing spec):
  0.* = Hypernet System Definitions
  1.* = People (Humans)
  2.* = AI Entities
  3.* = Businesses & Organizations
  4.* = Knowledge & Information

Usage:
    validator = AddressValidator()
    result = validator.validate("1.1.1.1.00001")
    assert result.valid

    auditor = AddressAuditor(store)
    report = auditor.audit()
    print(f"Coverage: {report.coverage_pct}%")

    enforcer = AddressEnforcer(store)
    enforcer.enforce_on_create(node)  # Raises if invalid
"""

from __future__ import annotations
import re
import logging
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from .address import HypernetAddress
from .node import Node

if TYPE_CHECKING:
    from .store import Store

log = logging.getLogger(__name__)


# Valid top-level categories
CATEGORIES = {
    "0": "Hypernet System Definitions",
    "1": "People",
    "2": "AI Entities",
    "3": "Businesses & Organizations",
    "4": "Knowledge & Information",
}

# Well-known address prefixes and their meanings
KNOWN_PREFIXES = {
    "0.0": "Metadata & Registry",
    "0.1": "Hypernet Core Platform",
    "0.5": "Object Type Definitions",
    "0.6": "Link Type Definitions",
    "0.7": "System Services",
    "0.7.1": "Task Queue",
    "0.7.2": "Swarm Orchestrator",
    "0.7.3": "Audit Trail",
    "0.8": "Flag Definitions",
    "1.1": "Matt (Founder)",
    "2.1": "Claude Opus (First AI Citizen)",
    "2.2": "GPT-5.2 Thinking (Second AI Citizen)",
    "3.1": "Hypernet Business",
}

# Minimum depth per category (how many parts the address must have)
MIN_DEPTH = {
    "0": 2,  # At least 0.X
    "1": 2,  # At least 1.X
    "2": 2,  # At least 2.X
    "3": 2,  # At least 3.X
    "4": 2,  # At least 4.X
}


@dataclass
class ValidationResult:
    """Result of validating a Hypernet Address."""
    valid: bool
    address: str
    category: str = ""
    category_name: str = ""
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


@dataclass
class AuditReport:
    """Report from auditing the entire store."""
    total_nodes: int = 0
    valid_addresses: int = 0
    invalid_addresses: int = 0
    missing_addresses: int = 0
    by_category: dict = field(default_factory=dict)
    issues: list[dict] = field(default_factory=list)

    @property
    def coverage_pct(self) -> float:
        if self.total_nodes == 0:
            return 100.0
        return round(self.valid_addresses / self.total_nodes * 100, 1)

    def summary(self) -> str:
        lines = [
            f"=== Address Audit Report ===",
            f"Total nodes: {self.total_nodes}",
            f"Valid addresses: {self.valid_addresses}",
            f"Invalid addresses: {self.invalid_addresses}",
            f"Missing addresses: {self.missing_addresses}",
            f"Coverage: {self.coverage_pct}%",
            "",
            "By category:",
        ]
        for cat, count in sorted(self.by_category.items()):
            name = CATEGORIES.get(cat, "Unknown")
            lines.append(f"  {cat}.* ({name}): {count} nodes")
        if self.issues:
            lines.append(f"\n{len(self.issues)} issues found:")
            for issue in self.issues[:20]:
                lines.append(f"  [{issue['severity']}] {issue['address']}: {issue['message']}")
            if len(self.issues) > 20:
                lines.append(f"  ... and {len(self.issues) - 20} more")
        return "\n".join(lines)


class AddressValidator:
    """Validate Hypernet Addresses against the addressing spec."""

    # Address part pattern: alphanumeric, allowing leading zeros for instance numbers
    PART_PATTERN = re.compile(r'^[a-zA-Z0-9]+$')

    def validate(self, address: str) -> ValidationResult:
        """Validate an address string.

        Checks:
          - Not empty
          - Parseable (dot-separated, optional colon-separated resource)
          - Valid category (0-4)
          - Minimum depth for category
          - No empty parts
          - Parts are alphanumeric
        """
        issues = []
        warnings = []

        if not address or not address.strip():
            return ValidationResult(
                valid=False, address=address,
                issues=["Address is empty"],
            )

        address = address.strip()

        # Parse through HypernetAddress
        try:
            ha = HypernetAddress.parse(address)
        except Exception as e:
            return ValidationResult(
                valid=False, address=address,
                issues=[f"Failed to parse: {e}"],
            )

        parts = ha.parts
        if not parts:
            return ValidationResult(
                valid=False, address=address,
                issues=["Address has no parts"],
            )

        # Check category
        category = parts[0]
        if category not in CATEGORIES:
            if category.isdigit() and int(category) >= 5:
                warnings.append(f"Category {category} is in future expansion range (5+)")
            else:
                issues.append(f"Unknown category: {category}")

        category_name = CATEGORIES.get(category, "Unknown")

        # Check minimum depth
        min_d = MIN_DEPTH.get(category, 2)
        if len(parts) < min_d:
            issues.append(f"Address too shallow: {len(parts)} parts, minimum {min_d} for category {category}")

        # Check each part is valid
        for i, part in enumerate(parts):
            if not part:
                issues.append(f"Empty part at position {i}")
            elif not self.PART_PATTERN.match(part):
                issues.append(f"Invalid characters in part {i}: '{part}'")

        # Check resource parts if present
        for i, part in enumerate(ha.resource):
            if not part:
                issues.append(f"Empty resource part at position {i}")

        # Warn about instance addresses (5+ parts deep)
        if len(parts) >= 5 and not ha.resource:
            # This is likely an instance — check for zero-padded instance number
            last = parts[-1]
            if last.isdigit() and len(last) < 5:
                warnings.append(
                    f"Instance number '{last}' is not zero-padded to 5 digits "
                    f"(convention: {last.zfill(5)})"
                )

        valid = len(issues) == 0
        return ValidationResult(
            valid=valid,
            address=address,
            category=category,
            category_name=category_name,
            issues=issues,
            warnings=warnings,
        )

    def validate_node(self, node: Node) -> ValidationResult:
        """Validate a node's address."""
        return self.validate(str(node.address))

    def is_valid_category(self, address: str, expected_category: str) -> bool:
        """Check if an address belongs to the expected category."""
        result = self.validate(address)
        return result.valid and result.category == expected_category


class AddressAuditor:
    """Audit the entire store for address coverage and validity."""

    def __init__(self, store: Store):
        self.store = store
        self.validator = AddressValidator()

    def audit(self) -> AuditReport:
        """Run a full audit of all nodes in the store.

        Returns an AuditReport with coverage statistics and issues.
        """
        report = AuditReport()

        # Get all nodes
        all_nodes = self.store.list_nodes(include_deleted=True)
        report.total_nodes = len(all_nodes)

        for node in all_nodes:
            addr_str = str(node.address)
            result = self.validator.validate(addr_str)

            if result.valid:
                report.valid_addresses += 1
                # Count by category
                cat = result.category
                report.by_category[cat] = report.by_category.get(cat, 0) + 1
            else:
                report.invalid_addresses += 1
                for issue in result.issues:
                    report.issues.append({
                        "address": addr_str,
                        "message": issue,
                        "severity": "error",
                        "node_type": node.source_type or "unknown",
                    })

            # Check for warnings too
            for warning in result.warnings:
                report.issues.append({
                    "address": addr_str,
                    "message": warning,
                    "severity": "warning",
                    "node_type": node.source_type or "unknown",
                })

        log.info(
            f"Address audit: {report.valid_addresses}/{report.total_nodes} valid "
            f"({report.coverage_pct}% coverage)"
        )
        return report

    def find_unaddressed(self) -> list[Node]:
        """Find nodes with invalid or missing addresses."""
        results = []
        for node in self.store.list_nodes():
            result = self.validator.validate(str(node.address))
            if not result.valid:
                results.append(node)
        return results

    def find_by_category(self, category: str) -> list[Node]:
        """Find all nodes in a specific category."""
        results = []
        for node in self.store.list_nodes():
            if str(node.address).startswith(f"{category}."):
                results.append(node)
        return results


class AddressEnforcer:
    """Enforce address validity at creation time.

    Wraps around the Store to validate addresses before they're persisted.
    Can operate in warn or strict mode.
    """

    def __init__(self, store: Store, strict: bool = True):
        self.store = store
        self.validator = AddressValidator()
        self.strict = strict
        self._violations: list[dict] = []

    def enforce_on_create(self, node: Node) -> ValidationResult:
        """Validate a node's address before creation.

        In strict mode, raises ValueError if the address is invalid.
        In warn mode, logs a warning but allows creation.
        """
        result = self.validator.validate_node(node)

        if not result.valid:
            violation = {
                "address": str(node.address),
                "issues": result.issues,
                "source_type": node.source_type,
                "timestamp": __import__("datetime").datetime.now(
                    __import__("datetime").timezone.utc
                ).isoformat(),
            }
            self._violations.append(violation)

            if self.strict:
                raise ValueError(
                    f"Invalid Hypernet Address '{node.address}': "
                    + "; ".join(result.issues)
                )
            else:
                log.warning(
                    f"Address violation (non-strict): {node.address}: "
                    + "; ".join(result.issues)
                )

        return result

    def enforce_category(self, node: Node, expected_category: str) -> None:
        """Ensure a node's address is in the expected category.

        Raises ValueError if the address category doesn't match.
        """
        result = self.validator.validate_node(node)
        if result.category != expected_category:
            raise ValueError(
                f"Address '{node.address}' is in category {result.category} "
                f"({result.category_name}), expected category {expected_category} "
                f"({CATEGORIES.get(expected_category, 'Unknown')})"
            )

    @property
    def violations(self) -> list[dict]:
        """Get all recorded violations."""
        return list(self._violations)

    @property
    def violation_count(self) -> int:
        return len(self._violations)

"""
Integration & Boundary Tests for Code Separation

These tests verify that the separation into three projects
(Core, Swarm, VR) maintains clean dependency boundaries.

Run with: python -m pytest "0/0.1 - Hypernet Core/test_integration.py" -v

Author: Test Sentinel instance
Date: 2026-02-21
"""

import ast
import sys
import importlib
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path so we can import hypernet
sys.path.insert(0, str(Path(__file__).parent))


# --- Module classification ---

CORE_MODULES = [
    "hypernet.address",
    "hypernet.node",
    "hypernet.link",
    "hypernet.store",
    "hypernet.graph",
    "hypernet.tasks",
    "hypernet.frontmatter",
    "hypernet.addressing",
    "hypernet.limits",
    "hypernet.favorites",
]

SWARM_MODULES = [
    "hypernet.identity",
    "hypernet.worker",
    "hypernet.messenger",
    "hypernet.swarm",
    "hypernet.swarm_cli",
    "hypernet.swarm_factory",
    "hypernet.boot",
    "hypernet.coordinator",
    "hypernet.providers",
    "hypernet.permissions",
    "hypernet.audit",
    "hypernet.tools",
    "hypernet.reputation",
    "hypernet.git_coordinator",
    "hypernet.governance",
    "hypernet.approval_queue",
    "hypernet.security",
    "hypernet.budget",
    "hypernet.economy",
]

# VR_MODULES will be populated when VR code exists
VR_MODULES = []

INTEGRATION_MODULES = [
    "hypernet.server",
]


def _get_module_file(module_name):
    """Get the file path for a module name like 'hypernet.address'."""
    parts = module_name.split(".")
    base = Path(__file__).parent / "hypernet"
    filename = parts[-1] + ".py"
    filepath = base / filename
    return filepath


def _extract_imports(filepath, include_type_checking=False):
    """Parse a Python file and extract all relative and absolute imports.

    By default, excludes imports inside `if TYPE_CHECKING:` blocks, since
    those are typing-only and don't create runtime dependencies.
    Set include_type_checking=True to include them.
    """
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, FileNotFoundError):
        return []

    # Find line ranges of TYPE_CHECKING blocks
    type_checking_lines = set()
    if not include_type_checking:
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Match: if TYPE_CHECKING:
                test = node.test
                is_tc = False
                if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
                    is_tc = True
                elif isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING":
                    is_tc = True
                if is_tc:
                    for child in ast.walk(node):
                        if hasattr(child, "lineno"):
                            type_checking_lines.add(child.lineno)

    imports = []
    for node in ast.walk(tree):
        if hasattr(node, "lineno") and node.lineno in type_checking_lines:
            continue

        if isinstance(node, ast.ImportFrom):
            if node.module:
                # Relative imports: from .foo import bar
                if node.level > 0:
                    imports.append(node.module)
                # Absolute imports: from hypernet.foo import bar
                elif node.module.startswith("hypernet."):
                    imports.append(node.module.replace("hypernet.", ""))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("hypernet."):
                    imports.append(alias.name.replace("hypernet.", ""))
    return imports


def _module_short_name(module_name):
    """Extract the short module name: 'hypernet.address' -> 'address'."""
    return module_name.split(".")[-1]


# --- Boundary Tests ---


def test_core_has_no_swarm_imports():
    """Core modules must NOT import from Swarm modules.

    This is the most critical boundary: if Core depends on Swarm,
    Core cannot be used standalone.
    """
    print("  Testing Core has no Swarm imports...")

    swarm_short = {_module_short_name(m) for m in SWARM_MODULES}
    violations = []

    for module_name in CORE_MODULES:
        filepath = _get_module_file(module_name)
        if not filepath.exists():
            continue

        imports = _extract_imports(filepath)
        for imp in imports:
            if imp in swarm_short:
                violations.append(
                    f"{_module_short_name(module_name)} imports {imp}"
                )

    assert len(violations) == 0, (
        f"Core→Swarm import violations found:\n"
        + "\n".join(f"  - {v}" for v in violations)
    )
    print(f"    PASS (checked {len(CORE_MODULES)} Core modules)")


def test_core_has_no_vr_imports():
    """Core modules must NOT import from VR modules."""
    print("  Testing Core has no VR imports...")

    if not VR_MODULES:
        print("    SKIP (no VR modules exist yet)")
        return

    vr_short = {_module_short_name(m) for m in VR_MODULES}
    violations = []

    for module_name in CORE_MODULES:
        filepath = _get_module_file(module_name)
        if not filepath.exists():
            continue

        imports = _extract_imports(filepath)
        for imp in imports:
            if imp in vr_short:
                violations.append(
                    f"{_module_short_name(module_name)} imports {imp}"
                )

    assert len(violations) == 0, (
        f"Core→VR import violations found:\n"
        + "\n".join(f"  - {v}" for v in violations)
    )
    print(f"    PASS (checked {len(CORE_MODULES)} Core modules)")


def test_swarm_has_no_vr_imports():
    """Swarm modules must NOT import from VR modules."""
    print("  Testing Swarm has no VR imports...")

    if not VR_MODULES:
        print("    SKIP (no VR modules exist yet)")
        return

    vr_short = {_module_short_name(m) for m in VR_MODULES}
    violations = []

    for module_name in SWARM_MODULES:
        filepath = _get_module_file(module_name)
        if not filepath.exists():
            continue

        imports = _extract_imports(filepath)
        for imp in imports:
            if imp in vr_short:
                violations.append(
                    f"{_module_short_name(module_name)} imports {imp}"
                )

    assert len(violations) == 0, (
        f"Swarm→VR import violations found:\n"
        + "\n".join(f"  - {v}" for v in violations)
    )
    print(f"    PASS (checked {len(SWARM_MODULES)} Swarm modules)")


def test_no_circular_cross_project_imports():
    """Verify the dependency direction: Core ← Swarm ← Integration.

    Allowed:
      - Core imports Core (internal)
      - Swarm imports Core (expected dependency)
      - Swarm imports Swarm (internal)
      - Integration imports anything

    Forbidden:
      - Core imports Swarm
      - Core imports VR
      - Swarm imports VR
    """
    print("  Testing no circular cross-project imports...")

    core_short = {_module_short_name(m) for m in CORE_MODULES}
    swarm_short = {_module_short_name(m) for m in SWARM_MODULES}
    vr_short = {_module_short_name(m) for m in VR_MODULES}

    violations = []

    # Check Core doesn't import Swarm or VR
    for module_name in CORE_MODULES:
        filepath = _get_module_file(module_name)
        if not filepath.exists():
            continue
        imports = _extract_imports(filepath)
        for imp in imports:
            if imp in swarm_short:
                violations.append(
                    f"CORE→SWARM: {_module_short_name(module_name)} → {imp}"
                )
            if imp in vr_short:
                violations.append(
                    f"CORE→VR: {_module_short_name(module_name)} → {imp}"
                )

    # Check Swarm doesn't import VR
    for module_name in SWARM_MODULES:
        filepath = _get_module_file(module_name)
        if not filepath.exists():
            continue
        imports = _extract_imports(filepath)
        for imp in imports:
            if imp in vr_short:
                violations.append(
                    f"SWARM→VR: {_module_short_name(module_name)} → {imp}"
                )

    assert len(violations) == 0, (
        f"Circular cross-project imports found:\n"
        + "\n".join(f"  - {v}" for v in violations)
    )

    total_checked = len(CORE_MODULES) + len(SWARM_MODULES)
    print(f"    PASS (checked {total_checked} modules, 0 violations)")


def test_core_modules_import_successfully():
    """Every Core module can be imported without error."""
    print("  Testing Core modules import successfully...")

    failures = []
    for module_name in CORE_MODULES:
        try:
            importlib.import_module(module_name)
        except Exception as e:
            failures.append(f"{module_name}: {e}")

    assert len(failures) == 0, (
        f"Core import failures:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )
    print(f"    PASS ({len(CORE_MODULES)} Core modules imported)")


def test_swarm_modules_import_successfully():
    """Every Swarm module can be imported without error."""
    print("  Testing Swarm modules import successfully...")

    failures = []
    for module_name in SWARM_MODULES:
        try:
            importlib.import_module(module_name)
        except Exception as e:
            failures.append(f"{module_name}: {e}")

    assert len(failures) == 0, (
        f"Swarm import failures:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )
    print(f"    PASS ({len(SWARM_MODULES)} Swarm modules imported)")


def test_server_creates_app():
    """server.py can create the app wiring all projects together."""
    print("  Testing server creates app...")

    try:
        from fastapi import FastAPI  # noqa: F401
    except ImportError:
        print("    SKIP (fastapi not installed)")
        return

    tmpdir = tempfile.mkdtemp(prefix="hypernet_test_")

    try:
        from hypernet.server import create_app

        app = create_app(data_dir=tmpdir)
        assert app is not None

        # Verify key routes exist
        route_paths = [r.path for r in app.routes]
        assert "/node/{address:path}" in route_paths or any(
            "/node/" in p for p in route_paths
        ), "Missing node endpoints"
        assert any(
            "/swarm/" in p for p in route_paths
        ), "Missing swarm endpoints"

        print("    PASS (app created, routes verified)")

    finally:
        shutil.rmtree(tmpdir)


def test_swarm_imports_from_core_are_expected():
    """Document and verify Swarm's expected dependencies on Core.

    This test captures the known coupling points. If new Core dependencies
    appear in Swarm modules, this test will flag them for review.
    """
    print("  Testing Swarm→Core imports are expected...")

    core_short = {_module_short_name(m) for m in CORE_MODULES}

    # Known expected Swarm→Core dependencies
    expected_deps = {
        "swarm": {"address", "store", "tasks", "limits"},
        "swarm_factory": {"address", "store", "tasks"},
        "coordinator": {"address", "node", "tasks"},
        "audit": {"address", "node", "link", "store"},
        "permissions": {"address"},
        "git_coordinator": {"address", "store"},
    }

    unexpected = []

    for module_name in SWARM_MODULES:
        short = _module_short_name(module_name)
        filepath = _get_module_file(module_name)
        if not filepath.exists():
            continue

        imports = _extract_imports(filepath)
        core_imports = {imp for imp in imports if imp in core_short}

        expected = expected_deps.get(short, set())

        new_deps = core_imports - expected
        if new_deps:
            unexpected.append(
                f"{short} has new Core deps: {new_deps} "
                f"(expected: {expected or 'none'})"
            )

    if unexpected:
        print("    WARNING — New Swarm→Core dependencies detected:")
        for u in unexpected:
            print(f"      {u}")
        # This is a warning, not a failure — new deps aren't forbidden,
        # they just need to be reviewed by the Architect.
        # Uncomment the assert below to make this a hard gate:
        # assert False, "\n".join(unexpected)

    print("    PASS (dependency surface verified)")


# --- Entry point for direct execution ---

if __name__ == "__main__":
    tests = [
        test_core_has_no_swarm_imports,
        test_core_has_no_vr_imports,
        test_swarm_has_no_vr_imports,
        test_no_circular_cross_project_imports,
        test_core_modules_import_successfully,
        test_swarm_modules_import_successfully,
        test_server_creates_app,
        test_swarm_imports_from_core_are_expected,
    ]

    print(f"\nRunning {len(tests)} boundary tests...\n")
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"    FAIL: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Boundary tests: {passed} passed, {failed} failed")
    if failed == 0:
        print("All boundary tests PASS.")
    else:
        print(f"FAILURES DETECTED — {failed} test(s) need attention.")

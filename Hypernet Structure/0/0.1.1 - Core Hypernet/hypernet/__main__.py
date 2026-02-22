"""
Run the Hypernet Core server or management commands.

Usage:
    python -m hypernet_core              # Start server on port 8000
    python -m hypernet_core serve        # Same as above
    python -m hypernet_core audit        # Run address audit on data store
    python -m hypernet_core status       # Show system status
"""

import argparse
import sys


def cmd_serve(args):
    """Start the Hypernet Core server."""
    try:
        from .server import run
    except ImportError:
        print("Server requires FastAPI and uvicorn.")
        print("Install with: pip install fastapi uvicorn")
        sys.exit(1)

    print(f"Starting Hypernet Core server...")
    print(f"  Data:     {args.data}")
    print(f"  URL:      http://localhost:{args.port}/")
    print()
    run(data_dir=args.data, host=args.host, port=args.port)


def cmd_audit(args):
    """Run address audit on the data store."""
    from .store import Store

    print(f"Running address audit on: {args.data}")
    print()

    store = Store(args.data)
    report = store.audit_addresses()
    print(report.summary())

    if report.invalid_addresses > 0:
        sys.exit(1)


def cmd_status(args):
    """Show system status: version, modules, store stats."""
    import importlib
    from pathlib import Path
    from . import __version__
    from .store import Store
    from .link import LinkRegistry

    print(f"Hypernet Core v{__version__}")
    print(f"{'=' * 40}")

    # Module inventory
    pkg_dir = Path(__file__).parent
    py_files = sorted(p for p in pkg_dir.glob("*.py") if p.name != "__pycache__")
    module_count = len([f for f in py_files if not f.name.startswith("_")])
    total_lines = 0
    for f in py_files:
        total_lines += sum(1 for _ in f.open())
    print(f"\nModules:     {module_count} ({total_lines:,} lines)")

    # Store stats
    data_path = Path(args.data)
    if data_path.exists():
        store = Store(args.data)
        stats = store.stats()
        print(f"\nData Store:  {args.data}")
        print(f"  Nodes:     {stats.get('total_nodes', 0):,}")
        print(f"  Links:     {stats.get('total_links', 0):,}")
    else:
        print(f"\nData Store:  {args.data} (not found)")


def main():
    parser = argparse.ArgumentParser(
        description="Hypernet Core — Data model and graph infrastructure"
    )
    subparsers = parser.add_subparsers(dest="command")

    # serve
    serve_parser = subparsers.add_parser("serve", help="Start the Hypernet Core server")
    serve_parser.add_argument("--data", default="data", help="Data directory")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind")

    # audit
    audit_parser = subparsers.add_parser("audit", help="Run address audit")
    audit_parser.add_argument("--data", default="data", help="Data directory")

    # status
    status_parser = subparsers.add_parser("status", help="Show system status")
    status_parser.add_argument("--data", default="data", help="Data directory")

    args = parser.parse_args()

    if args.command == "audit":
        cmd_audit(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "serve":
        cmd_serve(args)
    else:
        # Default: serve
        args.data = "data"
        args.host = "0.0.0.0"
        args.port = 8000
        cmd_serve(args)


if __name__ == "__main__":
    main()

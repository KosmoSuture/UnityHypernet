"""
Run the Hypernet server or management commands.

Usage:
    python -m hypernet              # Start server on port 8000
    python -m hypernet serve        # Same as above
    python -m hypernet audit        # Run address audit on data store
    python -m hypernet audit --data ./my-data  # Audit a specific data directory
"""

import argparse
import sys


def cmd_serve(args):
    """Start the Hypernet server."""
    try:
        from .server import run
    except ImportError:
        print("Server requires FastAPI and uvicorn.")
        print("Install with: pip install fastapi uvicorn")
        sys.exit(1)

    print(f"Starting Hypernet server...")
    print(f"  Data:  {args.data}")
    print(f"  URL:   http://localhost:{args.port}/")
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


def main():
    parser = argparse.ArgumentParser(
        description="Hypernet — Decentralized infrastructure for human-AI collaboration"
    )
    subparsers = parser.add_subparsers(dest="command")

    # serve
    serve_parser = subparsers.add_parser("serve", help="Start the Hypernet server")
    serve_parser.add_argument("--data", default="data", help="Data directory (default: data)")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")

    # audit
    audit_parser = subparsers.add_parser("audit", help="Run address audit on data store")
    audit_parser.add_argument("--data", default="data", help="Data directory (default: data)")

    args = parser.parse_args()

    if args.command == "audit":
        cmd_audit(args)
    elif args.command == "serve":
        cmd_serve(args)
    else:
        # Default: serve with defaults (backward compat)
        args.data = "data"
        args.host = "0.0.0.0"
        args.port = 8000
        cmd_serve(args)


if __name__ == "__main__":
    main()

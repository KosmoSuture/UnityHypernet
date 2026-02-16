"""
Run the Hypernet server.

Usage:
    python -m hypernet              # Start server on port 8000
    python -m hypernet --port 9000  # Custom port
    python -m hypernet --data ./my-data  # Custom data directory
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Hypernet — Decentralized infrastructure for human-AI collaboration"
    )
    parser.add_argument("--data", default="data", help="Data directory (default: data)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    args = parser.parse_args()

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


if __name__ == "__main__":
    main()

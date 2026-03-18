"""
Run Hypernet AI Swarm management commands.

Usage:
    python -m hypernet_swarm              # Start swarm (live mode)
    python -m hypernet_swarm --mock       # Start swarm (mock mode)
    python -m hypernet_swarm approvals    # Review pending approvals
    python -m hypernet_swarm setup        # Set up as a contributor
    python -m hypernet_swarm sync         # Pull, push, and detect conflicts
"""

import sys


def main():
    """Entry point for the swarm CLI."""
    from .swarm_cli import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()

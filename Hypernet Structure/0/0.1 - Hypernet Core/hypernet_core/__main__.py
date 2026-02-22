"""
Run the Hypernet server or management commands.

Usage:
    python -m hypernet              # Start server on port 8000
    python -m hypernet serve        # Same as above
    python -m hypernet audit        # Run address audit on data store
    python -m hypernet audit --data ./my-data  # Audit a specific data directory
    python -m hypernet status       # Show system status (modules, store, version)
    python -m hypernet status --data ./my-data  # Status with specific data directory
    python -m hypernet setup        # Set up as a contributor (one-command onboarding)
    python -m hypernet sync         # Pull, push, and detect conflicts
    python -m hypernet approvals    # Review pending external action approvals
    python -m hypernet approvals --approve AQ-0001  # Approve a pending request
    python -m hypernet approvals --reject AQ-0001 --reason "Not now"  # Reject
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

    archive = getattr(args, "archive_root", ".")
    print(f"Starting Hypernet server...")
    print(f"  Data:     {args.data}")
    print(f"  Archive:  {archive}")
    print(f"  URL:      http://localhost:{args.port}/")
    print(f"  Dashboard: http://localhost:{args.port}/swarm/dashboard")
    print(f"  Chat:     http://localhost:{args.port}/chat")
    print()
    run(data_dir=args.data, host=args.host, port=args.port, archive_root=archive)


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
        categories = stats.get("by_category", {})
        if categories:
            print(f"  Categories:")
            for cat, count in sorted(categories.items()):
                print(f"    {cat}: {count:,}")
    else:
        print(f"\nData Store:  {args.data} (not found)")

    # Link stats
    if data_path.exists():
        registry = LinkRegistry(store)
        link_stats = registry.stats()
        by_type = link_stats.get("by_type", {})
        if by_type:
            print(f"\n  Link Types:")
            for lt, count in sorted(by_type.items(), key=lambda x: -x[1]):
                print(f"    {lt}: {count:,}")

    # Dependencies check
    print(f"\nDependencies:")
    for pkg, label in [("fastapi", "FastAPI (server)"),
                       ("uvicorn", "Uvicorn (server)"),
                       ("anthropic", "Anthropic SDK (swarm)"),
                       ("openai", "OpenAI SDK (swarm)")]:
        try:
            mod = importlib.import_module(pkg)
            ver = getattr(mod, "__version__", "?")
            print(f"  {label}: {ver}")
        except ImportError:
            print(f"  {label}: not installed")


def cmd_setup(args):
    """Set up as a contributor for distributed development."""
    from pathlib import Path
    from .git_coordinator import setup_contributor, generate_contributor_id, GitBatchCoordinator
    from .store import Store

    repo_root = Path(args.repo or ".").resolve()
    data_dir = Path(args.data).resolve()

    print("Hypernet Contributor Setup")
    print("=" * 40)

    contributor_id = args.contributor_id or generate_contributor_id()
    print(f"\n  Contributor ID:  {contributor_id}")
    print(f"  Repo root:       {repo_root}")
    print(f"  Data directory:  {data_dir}")

    config = setup_contributor(repo_root, data_dir, contributor_id)
    print(f"  Git branch:      {config.branch}")
    print(f"  Remote:          {config.remote}")

    # Validate git access
    print(f"\nValidating git access...")
    try:
        from .git_coordinator import _run_git
        result = _run_git(["remote", "-v"], repo_root)
        for line in result.stdout.strip().split("\n")[:2]:
            print(f"  {line}")
        print("  Git access: OK")
    except Exception as e:
        print(f"  Git access: FAILED ({e})")
        print("  You may need to configure git credentials.")

    # Reserve initial address ranges
    store = Store(str(data_dir))
    coordinator = GitBatchCoordinator(config, store)
    print(f"\nReserving initial address ranges...")
    for prefix in ["0.7.1"]:  # Task addresses
        res = coordinator.address_allocator.reserve_range(prefix)
        print(f"  {prefix}: instances {res.range_start}-{res.range_end - 1}")

    print(f"\nSetup complete! You can now:")
    print(f"  python -m hypernet sync    # Pull changes, push your work")
    print(f"  python -m hypernet status  # Check system status")


def cmd_approvals(args):
    """Review and manage the external action approval queue."""
    from pathlib import Path
    from .approval_queue import ApprovalQueue

    queue_dir = Path(args.data) / "swarm" / "approvals"
    queue = ApprovalQueue(queue_dir=queue_dir)

    if args.approve:
        r = queue.approve(args.approve, reviewer=args.reviewer or "matt", reason=args.reason or "")
        if r:
            print(f"  Approved: {r.request_id} — {r.summary}")
        else:
            print(f"  Cannot approve {args.approve} (not found or not pending)")
        return

    if args.reject:
        r = queue.reject(args.reject, reviewer=args.reviewer or "matt", reason=args.reason or "")
        if r:
            print(f"  Rejected: {r.request_id} — {r.summary}")
        else:
            print(f"  Cannot reject {args.reject} (not found or not pending)")
        return

    # List pending approvals
    pending = queue.pending()
    stats = queue.stats()

    print(f"Approval Queue")
    print(f"{'=' * 60}")
    print(f"  Total: {stats['total_requests']}  |  "
          f"Pending: {stats['pending']}  |  "
          f"Actionable: {stats['actionable']}")
    print()

    if not pending:
        print("  No pending approvals.")
        return

    print(f"  Pending Approvals:")
    print(f"  {'-' * 56}")
    for r in pending:
        print(f"  [{r.request_id}] {r.action_type} by {r.requester}")
        print(f"    Summary: {r.summary[:80]}")
        if r.reason:
            print(f"    Reason:  {r.reason[:60]}")
        print(f"    Created: {r.created_at[:19]}")
        print(f"    Expires: {r.expires_at[:19]}")
        # Show details for review
        if r.details:
            if r.details.get("message"):
                print(f"    Content: {r.details['message'][:100]}")
            if r.details.get("subject"):
                print(f"    Subject: {r.details['subject']}")
            if r.details.get("body"):
                print(f"    Body:    {r.details['body'][:100]}")
        print()

    print(f"  To approve: python -m hypernet approvals --approve AQ-XXXX")
    print(f"  To reject:  python -m hypernet approvals --reject AQ-XXXX --reason \"...\"")


def cmd_sync(args):
    """Pull, push, and detect conflicts."""
    from pathlib import Path
    from .git_coordinator import setup_contributor, GitBatchCoordinator
    from .store import Store

    repo_root = Path(args.repo or ".").resolve()
    data_dir = Path(args.data).resolve()

    config = setup_contributor(repo_root, data_dir, args.contributor_id)
    store = Store(str(data_dir))
    coordinator = GitBatchCoordinator(config, store)

    print(f"Syncing as contributor {config.contributor_id}...")
    result = coordinator.sync(commit_message=args.message)

    if result.pull:
        status = "OK" if result.pull.success else "FAILED"
        print(f"\n  Pull: {status} ({result.pull.duration_ms:.0f}ms)")
        if result.pull.index_stats:
            stats = result.pull.index_stats
            print(f"    Indexed: {stats.get('nodes_indexed', 0)} nodes, "
                  f"{stats.get('links_indexed', 0)} links")

    if result.push:
        print(f"  Push: {result.push.status.value} "
              f"({result.push.files_pushed} files, "
              f"{result.push.duration_ms:.0f}ms)")
        if result.push.retries > 0:
            print(f"    Retries: {result.push.retries}")

    if result.address_collisions:
        print(f"\n  WARNING: {len(result.address_collisions)} address collisions!")
        for c in result.address_collisions:
            print(f"    {c['prefix']}: {c['contributor_a']} vs {c['contributor_b']}")

    if result.task_conflicts:
        print(f"\n  WARNING: {len(result.task_conflicts)} task claim conflicts!")
        for c in result.task_conflicts:
            print(f"    {c['task_address']}: winner={c['winner']}")


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

    # status
    status_parser = subparsers.add_parser("status", help="Show system status")
    status_parser.add_argument("--data", default="data", help="Data directory (default: data)")

    # setup
    setup_parser = subparsers.add_parser("setup", help="Set up as a contributor")
    setup_parser.add_argument("--data", default="data", help="Data directory (default: data)")
    setup_parser.add_argument("--repo", default=None, help="Git repo root (default: current dir)")
    setup_parser.add_argument("--contributor-id", default=None, help="Custom contributor ID")

    # approvals
    approvals_parser = subparsers.add_parser("approvals", help="Review external action approval queue")
    approvals_parser.add_argument("--data", default="data", help="Data directory (default: data)")
    approvals_parser.add_argument("--approve", default=None, help="Approve a pending request by ID (e.g. AQ-0001)")
    approvals_parser.add_argument("--reject", default=None, help="Reject a pending request by ID")
    approvals_parser.add_argument("--reviewer", default=None, help="Reviewer name (default: matt)")
    approvals_parser.add_argument("--reason", default=None, help="Reason for approval/rejection")

    # sync
    sync_parser = subparsers.add_parser("sync", help="Pull, push, and detect conflicts")
    sync_parser.add_argument("--data", default="data", help="Data directory (default: data)")
    sync_parser.add_argument("--repo", default=None, help="Git repo root (default: current dir)")
    sync_parser.add_argument("--contributor-id", default=None, help="Contributor ID")
    sync_parser.add_argument("--message", "-m", default=None, help="Commit message")

    args = parser.parse_args()

    if args.command == "audit":
        cmd_audit(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "serve":
        cmd_serve(args)
    elif args.command == "setup":
        cmd_setup(args)
    elif args.command == "sync":
        cmd_sync(args)
    elif args.command == "approvals":
        cmd_approvals(args)
    else:
        # Default: serve with defaults (backward compat)
        args.data = "data"
        args.host = "0.0.0.0"
        args.port = 8000
        cmd_serve(args)


if __name__ == "__main__":
    main()

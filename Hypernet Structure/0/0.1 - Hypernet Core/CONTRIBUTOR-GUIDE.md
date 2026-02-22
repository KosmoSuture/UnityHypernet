# Hypernet Contributor Guide

**What this is:** End-to-end instructions for contributing to the Hypernet as a distributed developer. Whether you're a human running a local swarm, an AI instance in a session, or a team collaborating across machines — this guide covers the full workflow.

**What you need:** Python 3.10+, git, and a clone of the Hypernet repository.

---

## How Distributed Development Works

The Hypernet uses GitHub as a shared database. Multiple contributors work locally and push changes in batches. The `git_coordinator.py` module handles the hard parts:

- **Address allocation** prevents two contributors from creating the same node
- **Task claiming** prevents two contributors from working on the same task
- **Index rebuilding** eliminates the most common merge conflicts
- **Conflict resolution** auto-resolves remaining conflicts by type
- **Exponential backoff** handles push races gracefully

```
Contributor A (local)          GitHub (shared)         Contributor B (local)
      |                            |                          |
      |--- pull ------------------>|<--- pull ----------------|
      |    (rebuild indexes)       |     (rebuild indexes)    |
      |                            |                          |
      |--- local work ----------->|                          |
      |    (nodes, links, tasks)   |<--- local work ----------|
      |                            |                          |
      |--- push (batch) --------->|<--- push (batch) --------|
      |    (retry on conflict)     |     (retry on conflict)  |
```

---

## Step 1: One-Command Setup

```bash
cd "0/0.1 - Hypernet Core"
python -m hypernet setup
```

This does everything:
1. Generates a unique contributor ID from your machine identity
2. Detects the current git branch and remote
3. Validates git access (can you pull/push?)
4. Reserves initial address ranges so your nodes won't collide with others

**Output:**
```
Hypernet Contributor Setup
========================================

  Contributor ID:  a3b7f2e91c04
  Repo root:       /home/user/Hypernet
  Data directory:  /home/user/Hypernet/data
  Git branch:      main
  Remote:          origin

Validating git access...
  origin  https://github.com/... (fetch)
  origin  https://github.com/... (push)
  Git access: OK

Reserving initial address ranges...
  0.7.1: instances 1-100

Setup complete! You can now:
  python -m hypernet sync    # Pull changes, push your work
  python -m hypernet status  # Check system status
```

**Custom setup:**
```bash
# Use a specific contributor ID
python -m hypernet setup --contributor-id my-team-name

# Point to a different data directory
python -m hypernet setup --data ./my-data

# Use a different repo root
python -m hypernet setup --repo /path/to/repo
```

---

## Step 2: Pull Latest Changes

Before starting work, always pull:

```bash
python -m hypernet sync
```

Or, if you want to pull without pushing:

```python
from hypernet.git_coordinator import GitBatchCoordinator, setup_contributor
from hypernet.store import Store
from pathlib import Path

config = setup_contributor(Path("."))
store = Store("data")
coordinator = GitBatchCoordinator(config, store)

result = coordinator.pull()
print(f"Pull: {'OK' if result.success else 'FAILED'}")
print(f"Indexed: {result.index_stats.get('nodes_indexed', 0)} nodes")
```

**What happens on pull:**
1. `git pull --rebase` fetches upstream changes
2. If there are merge conflicts, `ConflictResolver` auto-resolves them:
   - Node conflicts: latest `updated_at` wins (loser preserved in history)
   - Link conflicts: both kept (links are append-only)
   - Index conflicts: accept theirs, rebuild from source
   - Other conflicts: queued for manual review
3. All indexes are rebuilt from source files (never merged as JSON)
4. Index integrity is validated

---

## Step 3: Claim a Task

Before starting work on a task, claim it:

```python
claim = coordinator.task_claimer.claim("3.1.2.1.042")
if claim:
    print(f"Claimed! Working on {claim.task_address}")
else:
    print("Already claimed by someone else")
```

**How claiming works:**
- Each contributor writes claims to their own file (`data/.claims/tasks/<contributor_id>.json`)
- These files never conflict in git because different contributors write different files
- If two contributors claim the same task simultaneously, the first to push wins
- After pushing, pull again to confirm your claim wasn't overridden

**Task lifecycle:**
```
claim() → do work → complete()    # Happy path
claim() → blocked → release()     # Give up, let someone else try
```

---

## Step 4: Do Your Work

Create nodes, links, and other data locally:

```python
from hypernet.node import Node
from hypernet.address import HypernetAddress

# Get your next available address (within your reserved range)
addr = coordinator.address_allocator.next_address("0.7.1")

# Create a node
node = Node(
    address=addr,
    data={"title": "My contribution", "description": "..."},
    source_type="ai_generated",
)
store.put_node(node)
```

**Address ranges:** Your setup reserved a range (e.g., 0.7.1.00001–00100). All addresses you create fall within this range, so they can never collide with another contributor's addresses. When your range is exhausted, `next_address()` auto-reserves a new block.

---

## Step 5: Push Your Changes

```bash
python -m hypernet sync -m "Added task definitions for AI governance"
```

Or programmatically:

```python
result = coordinator.push_batch(message="Added task definitions")
print(f"Status: {result.status.value}")
print(f"Files: {result.files_pushed}")
print(f"Retries: {result.retries}")
```

**What happens on push:**
1. Collects all changed files (excluding indexes, locks, temp files)
2. Batches files (max 500 per push to avoid overwhelming GitHub)
3. Stages, commits, and pushes
4. If push is rejected (someone else pushed first):
   - Pulls with rebase
   - Auto-resolves any conflicts
   - Retries (exponential backoff: 1s, 2s, 4s, 8s, ...)
   - Up to 5 retries before giving up

---

## Step 6: Complete Your Task

```python
coordinator.task_claimer.complete("3.1.2.1.042")
```

Then sync to push the completion status:

```bash
python -m hypernet sync -m "Completed Task 042: AI governance framework"
```

---

## Full Sync Cycle

The `sync` command wraps everything into one operation:

```bash
python -m hypernet sync
```

This runs: **pull** → **push** → **detect issues**

Output:
```
Syncing as contributor a3b7f2e91c04...

  Pull: OK (342ms)
    Indexed: 9507 nodes, 10346 links

  Push: success (2 files, 891ms)

  No address collisions detected.
  No task claim conflicts detected.
```

---

## Conflict Resolution

Most conflicts resolve automatically. Here's what happens for each type:

| File Type | Strategy | You Need To Do |
|-----------|----------|---------------|
| Node files (`node.json`) | Latest `updated_at` wins | Nothing — loser version preserved in history |
| Link files (`*.json` in links/) | Richer version kept | Nothing — links are append-only |
| Index files (`indexes/*.json`) | Rebuilt from source | Nothing — indexes are derived data |
| Task claim files | Claim lists merged | Nothing — earliest claim wins |
| Unknown files | Queued for manual review | Check the queue and resolve |

**Checking the manual queue:**

```python
from hypernet.git_coordinator import ManualResolutionQueue

queue = ManualResolutionQueue(Path("data"))
for entry in queue.list_pending():
    print(f"  {entry.filepath}: {entry.detail}")

# After manually resolving:
queue.resolve("path/to/file.txt", "Merged manually")
```

**In status output:**

```bash
python -m hypernet status
```

The status will show `pending_conflicts: N` if any manual resolutions are waiting.

---

## System Status

```bash
python -m hypernet status
```

Output:
```
Hypernet Core v0.9.0
========================================

Modules:     25 (6,200 lines)

Data Store:  data
  Nodes:     9,507
  Links:     10,346
  Categories:
    0: 4,231
    1: 2,891
    2: 1,385
    ...

Dependencies:
  FastAPI (server): 0.109.0
  Uvicorn (server): 0.27.0
  Anthropic SDK (swarm): 0.18.0
  OpenAI SDK (swarm): not installed
```

---

## How Indexes Work (Why You Don't Merge Them)

This is the most important architectural concept:

**Indexes are derived data.** They are rebuilt from source files after every pull. They are never committed, never merged, never hand-edited.

Source files (the truth):
```
data/nodes/1/1/matt/node.json       → the actual node
data/links/abc123.json               → the actual link
```

Indexes (derived, rebuilt on pull):
```
data/indexes/node_index.json         → address → file path mapping
data/indexes/type_index.json         → type → [addresses] mapping
data/indexes/links_from.json         → address → [link hashes] mapping
data/indexes/links_to.json           → address → [link hashes] mapping
```

Two contributors creating nodes at different addresses will never conflict because:
1. Their node files are in different directories
2. The indexes are rebuilt, not merged

This eliminates the hardest class of distributed merge conflicts entirely.

---

## Per-Contributor Files (Why Claims Don't Conflict)

Address reservations and task claims use per-contributor files:

```
data/.claims/addresses/alpha.json    → Alpha's address ranges
data/.claims/addresses/beta.json     → Beta's address ranges
data/.claims/tasks/alpha.json        → Alpha's task claims
data/.claims/tasks/beta.json         → Beta's task claims
```

Each contributor only writes to their own file. The global state is assembled by reading all files. This means two contributors can push simultaneously and their claim files will merge cleanly — different people write different files.

---

## Running a Local Swarm as a Contributor

If you want to run AI workers that contribute automatically:

1. Complete the setup above
2. Follow the [Swarm Setup Guide](SWARM-SETUP-GUIDE.md) for API keys and configuration
3. The swarm uses `GitBatchCoordinator` internally for sync operations
4. Workers auto-claim tasks, create nodes, and the swarm syncs periodically

---

## Troubleshooting

**"Push failed after 5 retries. Persistent conflict."**
Someone else is pushing rapidly. Wait a minute and try again. If it persists, check for manual conflicts in the queue.

**"Could not acquire git lock"**
Another process on your machine is running git operations. Wait for it to finish, or check for stale locks:
```python
store.locks.clear_stale_locks()
```

**"Authentication failed"**
Your git credentials aren't configured. Set up a personal access token:
```bash
git config credential.helper store
git push  # Enter credentials once, they'll be saved
```

**Indexes look wrong after pull**
Force a rebuild:
```python
from hypernet.git_coordinator import IndexRebuilder
rebuilder = IndexRebuilder(store)
stats = rebuilder.rebuild_all()
issues = rebuilder.validate()
```

**Address collision detected**
Two contributors reserved overlapping ranges. This shouldn't happen in normal operation. Check the collision report and contact the other contributor to re-reserve.

---

## API Reference

### CLI Commands

| Command | Description |
|---------|-------------|
| `python -m hypernet setup` | One-command contributor onboarding |
| `python -m hypernet sync` | Pull, push, detect conflicts |
| `python -m hypernet sync -m "message"` | Sync with custom commit message |
| `python -m hypernet status` | System status (version, modules, store) |
| `python -m hypernet audit` | Address audit on data store |

### Key Classes

| Class | Purpose |
|-------|---------|
| `GitBatchCoordinator` | Main orchestrator: pull, push, sync |
| `IndexRebuilder` | Rebuild indexes from source files |
| `AddressAllocator` | Reserve and allocate address ranges |
| `TaskClaimer` | Claim/release/complete tasks via git |
| `ConflictResolver` | Auto-resolve merge conflicts by type |
| `ManualResolutionQueue` | Queue for unresolvable conflicts |
| `GitConfig` | Configuration dataclass |

### Sync Result

```python
result = coordinator.sync()
result.pull.success          # bool
result.pull.index_stats      # {"nodes_indexed": N, "links_indexed": N}
result.push.status           # PushStatus enum
result.push.files_pushed     # int
result.push.retries          # int
result.address_collisions    # list[dict] — empty = good
result.task_conflicts        # list[dict] — empty = good
```

---

*Created by Relay (2.1) for the Hypernet Project — February 2026*

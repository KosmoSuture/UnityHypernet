# Hypernet as memory for AI agents — 5-minute demo

This is the shortest path from a clone to a running demonstration of what
Hypernet does today: store facts with provenance, link them with typed
relationships, keep every version, and answer "why do you believe that?"
from the graph. It needs Python 3.10+ and three packages. No API keys, no
paid model calls, no VR, no swarm.

## 1. Clone (shallow; the repo is large)

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/KosmoSuture/UnityHypernet.git
cd "UnityHypernet/Hypernet Structure/0/0.1 - Hypernet Core"
```

## 2. Install the server's dependencies

The core library has no external dependencies; only the HTTP server needs these.

```bash
pip install fastapi uvicorn pydantic
```

## 3. Start a server on an empty store

```bash
HYPERNET_RATE_LIMIT=600 python -m hypernet serve --data /tmp/hn-demo --port 8766 --no-auth
```

(`--data` points at an empty directory so the demo starts from nothing.
`HYPERNET_RATE_LIMIT` raises the default 60 requests/minute so a scripted
agent isn't throttled. `--no-auth` is for local demos only.)

## 4. Run the demo in a second terminal

```bash
cd "UnityHypernet/Hypernet Structure/0/0.1 - Hypernet Core"
python examples/agent_memory_demo.py --url http://127.0.0.1:8766
```

Expected tail of the output (addresses and timestamps will differ):

```
========================================================================
7. Why do you believe that?  (provenance chain from the graph)
========================================================================
5.3.00005  "The project targets Python 3.12."
  source: node:5.3.00002
  versions: 2  (created ..., updated ...)
    v1 [f9f4da60344cdd05] ...: "The project targets Python 3.11."
  --derived_from--> 5.3.00002 "pyproject.toml"
  --cites--> 5.3.00002 "pyproject.toml"  evidence: requires-python field

5.3.00004  "The API server requires fastapi, uvicorn and pydantic."
  source: node:5.3.00001
  versions: 1  (created ..., updated ...)
  --derived_from--> 5.3.00001 "README.md"
```

Open `http://127.0.0.1:8766/explorer` to browse the same records, or look at
`/tmp/hn-demo/nodes/5/3/...` and `/tmp/hn-demo/history/...` on disk.

## 5. Use it from your own agent

```python
from hypernet_memory import HypernetMemory

mem = HypernetMemory("http://127.0.0.1:8766", agent="my-agent")

src  = mem.source("design-notes.md", kind="document")      # optional source node
addr = mem.remember("Deploys go through the staging gate.", source=src, confidence=0.9)
mem.link(addr, other_addr, "contradicts", evidence="see thread #42")

mem.recall("staging")          # -> [Fact(address, text, source_type, source_id, ...)]
mem.derived_from(src)          # -> everything learned from that source
print(mem.explain(addr))       # -> the provenance chain shown above
```

`hypernet_memory.py` is a single standard-library file in the core
directory; copy it into your project or import it from there. Pass
`api_key=` when the server runs with authentication.

## 6. Tests

```bash
python test_memory_client.py        # starts its own server on a free port
python test_hypernet.py             # core suite: 124 passed
```

## Decisions and limitations (so you don't rediscover them)

- **Facts are stored as `0.4.10.2.2` Note** ("an atomic knowledge or memory
  unit"; required fields `title`, `body`, `created_at`, which the client
  fills). `0.4.10.2.1` was considered and rejected: it is **Document**, which
  requires `format` and `content_ref`, i.e. a file-like artifact rather than
  a fact. Source nodes created with `mem.source()` do use Document by
  default.
- **Addresses** are allocated with `GET /next-address/<area>` under the
  provisional area `5.3` (area `5` is "Objects: instances of defined
  types"). Pass `area=` to change it.
- **Links** use the 0.6.11 vocabulary: `derived_from` (0.6.11.2.7),
  `cites`, `supersedes`, `contradicts`, `implies`, `similar_to`, `about`,
  `version_of`. Unknown relationships need an explicit `link_type=`.
- A node's `source_type`/`source_id` are set **only at creation**; the
  server's `PUT /node` ignores them on update. The client therefore records
  the source of a *change* in `data["source_update"]`, which version history
  preserves. Making node-level source fields updatable is a reasonable
  server follow-up; it was out of scope here.
- The server rate-limits each client to `HYPERNET_RATE_LIMIT` requests per
  minute (default 60) even with `--no-auth`. The client retries 429s with
  backoff; raising the limit for local demos is still recommended.
- `--data` is the only way to choose the store directory for `serve`; the
  `HYPERNET_DATA_DIR` environment variable mentioned elsewhere is not read
  by this command.
- Running the demo twice against the same store is fine; the second run
  allocates the next addresses.

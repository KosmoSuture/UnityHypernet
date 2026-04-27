# Dell Server Setup — HypernetServer

**Last verified:** 2026-04-26 by Keel (1.1.10.1)
**Purpose:** Authoritative reference for the production Dell server that
hosts the live Hypernet. Workstation copies are for development only;
all live data must live on this machine.

> **Why this doc exists:** Previous instances connected to this server
> without writing down what they found. Matt explicitly called out that
> gap. If you are a future Keel/Codex/other instance and you find a
> detail in here that no longer matches reality, **fix this doc in the
> same session**. The next instance shouldn't have to re-discover.

---

## At-a-Glance

| Item | Value |
|---|---|
| Hostname | `HypernetServer` |
| Current LAN/Tailnet IP | **10.247.39.53** (was `10.16.210.53` — the secrets file used to be stale) |
| OS | Ubuntu 25.10 "Questing Quokka" |
| Kernel | 6.17.0-22-generic (x86_64) |
| Hardware | Dell Optiplex 5000, 4TB SSD, ~7.5 GB RAM |
| Python | `/usr/bin/python3` → 3.13.7 |
| Git | 2.51.0 |
| SSH | port 22, **publickey only** (password auth disabled) |
| SSH user | `hypernetadmin` |
| SSH key | `~/.ssh/hypernet_server` on Matt's workstation |
| Public IP | None — behind T-Mobile CGNAT (mid-2026) |

## Storage Layout — Three Partitions, Three Roles

This is the security model. **Do not put personal data on the wrong partition.**

```
/dev/nvme0n1p2  →  /              468G ext4    OS only — no Hypernet data
/dev/sda2       →  /mnt/hypernet  3.6T ext4    Hypernet code + dev/runtime data (public-OK)
/dev/mapper/secure → /mnt/secure  49G  ext4    Encrypted (LUKS) — personal data only
```

- `/dev/sda2` is partlabel `hypernet`, on the Samsung 870 EVO 4TB.
- `/dev/mapper/secure` is unlocked at boot via `systemd-cryptsetup@secure.service`
  (entry exists in `/etc/crypttab`).
- Both are auto-mounted via `/etc/fstab` with `nofail` so a missing
  partition doesn't block boot.

### What goes where

| Partition | What lives here | Goes to GitHub? |
|---|---|---|
| `/` | OS, Python, system packages | n/a |
| `/mnt/hypernet/repo` | Git checkout of `KosmoSuture/UnityHypernet` | **yes** |
| `/mnt/hypernet/data` | Runtime store (nodes, links, indexes), reputation, etc. | **never** |
| `/mnt/hypernet/backups` | Local backups | **never** |
| `/mnt/hypernet/logs` | Service logs | **never** |
| `/mnt/hypernet/models` | Local model artifacts (LM Studio etc.) | **never** |
| `/mnt/hypernet/launch-swarm.sh` | Launcher script | **yes** (if changed) |
| `/mnt/secure/hypernet/` | **Matt's personal data** (1.1 account ingest target) | **NEVER** — encrypted partition |
| `/mnt/secure/lost+found` | ext4 housekeeping | n/a |

The `/mnt/secure/hypernet/` directory is owned `hypernetadmin:hypernetadmin`
mode 700. The mount root `/mnt/secure/` is owned `matt:matt`. Personal
data ingest goes here.

## Service: `hypernet-swarm.service`

System-level systemd unit. Status as of 2026-04-26:

- **Enabled + active**
- Listening on `0.0.0.0:8000` (already publicly bound — works for tailnet
  and LAN immediately, no extra config needed)
- Currently launches: `.venv/bin/python -m hypernet launch --no-auth`
  with CWD `/mnt/hypernet/repo/Hypernet Structure/0/0.1 - Hypernet Core`
- Uses a local `.venv` inside the Hypernet Core folder

Operator commands (as `hypernetadmin` over SSH):

```bash
sudo systemctl status hypernet-swarm
sudo systemctl restart hypernet-swarm
sudo systemctl stop hypernet-swarm
sudo journalctl -u hypernet-swarm -n 100 --no-pager
```

The `--no-auth` flag disables JWT auth. Memory says it's wired but
disabled; turn it on by removing the flag from the service unit when
ready for production-grade auth.

## Connecting from the Workstation

```bash
# Direct SSH
ssh -i ~/.ssh/hypernet_server hypernetadmin@10.247.39.53

# Or via paramiko (no sshpass needed)
python -c "
import paramiko, os
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.247.39.53', 22, 'hypernetadmin',
          key_filename=os.path.expanduser('~/.ssh/hypernet_server'),
          allow_agent=False, look_for_keys=False)
"
```

Adding an SSH config entry on the workstation makes life easier:

```
Host hypernet
  HostName 10.247.39.53
  User hypernetadmin
  IdentityFile ~/.ssh/hypernet_server
  IdentitiesOnly yes
```

Then `ssh hypernet` works.

## Code Sync Procedure (Workstation → Dell)

The workstation is for testing. The Dell is the live host. Code lives in
the public-OK partition (`/mnt/hypernet/repo`); personal data lives in
the encrypted partition (`/mnt/secure/hypernet`). Two options:

### Option A — rsync (preferred for WIP)

```bash
# From the workstation, code-only sync. Don't touch the Dell's data dirs.
rsync -avz --delete-after \
  --exclude '__pycache__/' --exclude '*.pyc' \
  --exclude '.venv/' --exclude '.scheduled_tasks.lock' \
  --exclude '/Hypernet Structure/0/0.1 - Hypernet Core/data/' \
  --exclude '/Hypernet Structure/0/0.1 - Hypernet Core/secrets/' \
  --exclude '/Hypernet Structure/0/0.1 - Hypernet Core/logs/' \
  --exclude '/Hypernet Structure/0/0.1 - Hypernet Core/.venv/' \
  --exclude '/Hypernet Structure/secrets/' \
  -e "ssh -i ~/.ssh/hypernet_server" \
  "/c/Hypernet/Hypernet Structure/" \
  "hypernetadmin@10.247.39.53:/mnt/hypernet/repo/Hypernet Structure/"
```

Then SSH and restart:

```bash
ssh -i ~/.ssh/hypernet_server hypernetadmin@10.247.39.53 \
    "sudo systemctl restart hypernet-swarm && sleep 2 && curl -sS http://localhost:8000/swarm/health | head"
```

Pros: works with uncommitted/WIP code, doesn't pollute git history.
Cons: Dell ends up with a working tree that doesn't match origin/main.
That's fine — the Dell isn't a publication target.

### Option B — git pull

Only useful if all code is committed and pushed. Personal data must
never enter the public repo, so rsync is preferred for ingestion or for
syncing WIP. Reserve git pull for clean checkpointed releases:

```bash
ssh hypernet 'cd /mnt/hypernet/repo && git pull'
ssh hypernet 'sudo systemctl restart hypernet-swarm'
```

### What gets excluded and why

- `secrets/` — workstation API keys, never copy (Dell may have its own
  config, see "Dell-side secrets" below)
- `data/`, `logs/`, `backups/` — runtime state, the Dell maintains its own
- `.venv/` — Dell has its own venv built against Linux Python 3.13
- `__pycache__/`, `*.pyc` — bytecode, environment-specific
- `.scheduled_tasks.lock` — workstation-local lock
- `.git/` — keep separate; workstation uses GitHub origin, the Dell tracks
  the same upstream independently

## Dell-side Secrets

The Dell has (or should have) its own `secrets/config.json` populated at
deploy time. The workstation's secrets file references the Dell host but
should not be the source of truth for the Dell's secrets. As of
2026-04-26 I have not audited the Dell's secrets file contents — that is
follow-up work.

## Known Quirks / Things Future Instances Should Verify

- The IP (`10.247.39.53`) is on T-Mobile's mobile-hotspot subnet; expect
  it to change each time T-Mobile rotates the lease. The IP in
  `secrets/config.json` lagged by a full subnet move and had to be
  corrected by hand. Once Tailscale is set up the IP will stabilize on
  the tailnet.
- The Dell's git working tree carries uncommitted runtime mutations
  (data/indexes/*.json, Librarian profile, personal-time reflections).
  These are the swarm doing its job, **not** drift to push back upstream.
  Don't `git add -A && commit` on the Dell — you'll publish runtime
  state.
- LM Studio at `10.133.93.43:1234` (referenced from config) was timing
  out as of 2026-04-26 — the local model isn't reachable from the
  workstation. May be a different machine entirely.
- Matt explicitly said: "Eventually we will move away from Git once the
  Hypernet has the ability to do the same thing that Git can. Git is
  just temporary."

## Network Topology (mid-2026)

- **Dell** → T-Mobile cellular gateway → CGNAT internet (no public IPv4)
- **Workstation** → likely on the same LAN as Dell or a Tailscale subnet
- **Tailscale** is in the planning stage as of 2026-04-26. When set up:
  Dell joins tailnet, gets a stable `100.x.y.z` address, the IP in this
  doc and `secrets/config.json` should be updated to the tailnet IP for
  long-term stability.

## Quick Health Check

```bash
ssh hypernet 'curl -sS http://localhost:8000/swarm/health'
ssh hypernet 'systemctl is-active hypernet-swarm; df -h /mnt/hypernet /mnt/secure'
```

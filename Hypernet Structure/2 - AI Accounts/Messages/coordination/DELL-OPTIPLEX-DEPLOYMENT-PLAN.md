---
ha: "0.1.deployment.dell-optiplex"
object_type: "deployment-plan"
creator: "1.1.10.1"
created: "2026-04-18"
status: "active"
visibility: "public"
flags: ["infrastructure", "deployment", "server"]
---

# Dell Optiplex 5000 Deployment Plan

**Author:** Keel (1.1.10.1)
**Date:** 2026-04-18
**Hardware:** Dell Optiplex 5000, 4TB storage, physical location (Matt's home, Las Vegas)

---

## Phase 1: Base System (Day 1 — Tomorrow)

### OS & Access
- [ ] Confirm Linux distro installed (recommend Ubuntu 24.04 LTS Server)
- [ ] Set static local IP or reserve DHCP lease on router
- [ ] Enable SSH: `sudo apt install openssh-server`
- [ ] Create service account: `sudo useradd -m -s /bin/bash hypernet`
- [ ] Generate SSH keys for Matt and for agent access (Codex)
- [ ] Set up firewall: `sudo ufw allow ssh && sudo ufw enable`

### Core Dependencies
```bash
# System packages
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git tmux htop curl wget

# Python (ensure 3.11+)
python3 --version

# Node.js (for Claude Code if needed)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### Repository Clone
```bash
cd /opt
sudo mkdir -p hypernet && sudo chown hypernet:hypernet hypernet
su - hypernet
git clone https://github.com/KosmoSuture/UnityHypernet.git /opt/hypernet/repo
cd /opt/hypernet/repo
```

### Python Environment
```bash
cd "/opt/hypernet/repo/Hypernet Structure/0/0.1 - Hypernet Core"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # or install deps manually
```

---

## Phase 2: Swarm Services (Day 1-2)

### Config Setup
```bash
# Copy secrets from Windows machine (SCP or manual)
mkdir -p "/opt/hypernet/repo/Hypernet Structure/0/0.1 - Hypernet Core/secrets"
# scp from Windows: secrets/config.json -> server
```

**Config adjustments for Linux:**
- Update file paths (Windows `C:\` -> Linux `/opt/hypernet/`)
- Verify API keys are present (Claude, OpenAI, etc.)
- Adjust budget limits if needed for testing

### Launch Swarm
```bash
cd "/opt/hypernet/repo/Hypernet Structure/0/0.1 - Hypernet Core"
source .venv/bin/activate
python -m hypernet launch --no-auth  # Start without auth for initial testing
```

### Systemd Service (replaces NSSM on Windows)
```ini
# /etc/systemd/system/hypernet-swarm.service
[Unit]
Description=Hypernet AI Swarm
After=network.target

[Service]
Type=simple
User=hypernet
WorkingDirectory=/opt/hypernet/repo/Hypernet Structure/0/0.1 - Hypernet Core
ExecStart=/opt/hypernet/repo/Hypernet Structure/0/0.1 - Hypernet Core/.venv/bin/python -m hypernet launch
Restart=always
RestartSec=10
Environment=PYTHONPATH=/opt/hypernet/repo/Hypernet Structure/0/0.1 - Hypernet Core

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable hypernet-swarm
sudo systemctl start hypernet-swarm
sudo systemctl status hypernet-swarm
journalctl -u hypernet-swarm -f  # Watch logs
```

---

## Phase 3: Remote Access for Agents (Day 2)

### SSH Access for Codex
- Create SSH key pair for Codex agent
- Add public key to `/home/hypernet/.ssh/authorized_keys`
- Codex can then: `ssh hypernet@<server-ip>` to run commands
- Consider restricting Codex's SSH to specific commands via `authorized_keys` options

### Expose Dashboard (optional, local network only)
```bash
# Dashboard runs on port 8000 by default
# Access from local network: http://<server-ip>:8000/swarm/dashboard
# Do NOT expose to internet without auth enabled
```

### Reverse Tunnel (if needed for external access)
```bash
# If Matt needs access from outside home network
# Options: Tailscale (recommended), Cloudflare Tunnel, or SSH reverse tunnel
# Tailscale is simplest: install on both machines, access via Tailscale IP
```

---

## Phase 4: Local AI (Optional, Day 3+)

### LM Studio / Ollama
```bash
# Option A: Ollama (simpler on Linux)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5-coder:7b-instruct
# Runs on http://localhost:11434

# Option B: LM Studio (if GUI needed, requires desktop environment)
```

- Update swarm config to point local model provider at `http://localhost:11434`
- Test with: `curl http://localhost:11434/v1/chat/completions -d '{"model":"qwen2.5-coder:7b-instruct","messages":[{"role":"user","content":"hello"}]}'`

---

## Phase 5: Git Sync & Coordination

### Auto-Pull from GitHub
```bash
# Cron job to pull changes every 5 minutes
crontab -e
# Add: */5 * * * * cd /opt/hypernet/repo && git pull --rebase origin main >> /var/log/hypernet-sync.log 2>&1
```

### Coordination System
The file-based coordination system (`coordination.py`) works on both Windows and Linux:
```bash
cd "/opt/hypernet/repo/Hypernet Structure/2 - AI Accounts/Messages/coordination"
python3 coordination.py status
python3 coordination.py heartbeat server-swarm
```

### Push Changes from Server
If swarm workers create files (session logs, personal-time reflections, etc.):
```bash
# Auto-commit and push (run as cron or integrate into swarm)
cd /opt/hypernet/repo
git add -A
git commit -m "Server swarm auto-commit $(date -Iseconds)"
git push origin main
```

---

## Storage Layout

With 4TB available:
```
/opt/hypernet/
  repo/                    # Git repo (~1GB)
  data/                    # Hypernet data store (nodes, links, indexes)
  backups/                 # Daily backups
  models/                  # Local LLM models (~10-30GB each)
  logs/                    # Service logs
```

---

## Security Checklist

- [ ] SSH key-only auth (disable password login): `PasswordAuthentication no` in sshd_config
- [ ] Firewall: only SSH (22) and local network dashboard (8000) open
- [ ] API keys in secrets/config.json, not in repo or environment
- [ ] No root login via SSH
- [ ] Regular system updates: `sudo unattended-upgrades`
- [ ] Backup secrets/config.json separately (not in git)

---

## What Matt Needs to Do Tomorrow

1. **Confirm Linux is installed** on the Dell and it's on the network
2. **Set up SSH** and test connecting from his Windows machine
3. **Clone the repo** to the server
4. **Copy secrets/config.json** from Windows to server
5. **Run the swarm** and verify it starts
6. **Share SSH credentials** with Codex (via secure channel)
7. **Optional:** Install Tailscale for remote access

---

*Deployment plan created 2026-04-18 by Keel (1.1.10.1). This is a living document — update as deployment progresses.*

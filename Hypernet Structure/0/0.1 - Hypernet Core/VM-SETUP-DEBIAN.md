# Hypernet Node: Debian 12 VM Setup Guide

**For:** Matt (1.1)
**By:** Loom (2.1, third instance)
**Date:** 2026-02-15
**Purpose:** Step-by-step guide to set up the first Hypernet node as a Debian VM on Windows 11

---

## Prerequisites

- Windows 11 (Home or Pro)
- At least 4GB RAM free for the VM (2GB minimum)
- At least 20GB free disk space
- Internet connection

---

## Part 1: Enable Hyper-V (5 minutes)

Windows 11 Home uses "Windows Hypervisor Platform" instead of full Hyper-V.

### Option A: If you have Windows 11 Pro/Enterprise
1. Open **Settings > Apps > Optional Features > More Windows Features**
2. Check **Hyper-V** (all sub-items)
3. Click OK, restart

### Option B: If you have Windows 11 Home
Hyper-V Manager is not available, but you can use **VirtualBox** instead:
1. Download VirtualBox from https://www.virtualbox.org/wiki/Downloads
2. Run the installer, accept defaults
3. Restart if prompted

Alternatively, use **WSL 2** for a lighter approach:
1. Open PowerShell as Administrator
2. Run: `wsl --install -d Debian`
3. Restart, then `wsl -d Debian` to launch
4. Skip to Part 3 (Python Setup)

---

## Part 2: Create the Debian VM (15 minutes)

### Download Debian 12 Minimal
1. Go to: https://www.debian.org/distrib/netinst
2. Download the **amd64** netinst ISO (~600MB)

### Create VM (VirtualBox)
1. Open VirtualBox
2. Click **New**
3. Name: `hypernet-node-01`
4. Type: Linux, Version: Debian (64-bit)
5. Memory: **2048 MB** (2GB minimum, 4GB recommended)
6. Hard disk: Create a virtual hard disk, VDI, Dynamically allocated, **20GB**
7. Click Create

### Configure VM
1. Select the VM, click **Settings**
2. **System > Processor**: 2 CPUs
3. **Network > Adapter 1**: Attached to: **Bridged Adapter** (so it gets its own IP on your network)
4. **Storage**: Click the empty CD icon, choose the Debian ISO
5. Click OK

### Install Debian
1. Start the VM
2. Select **Install** (not graphical install — text mode is fine)
3. Language: English, Location: your country, Keyboard: your layout
4. Hostname: `hypernet-01`
5. Domain: leave blank
6. Root password: set a strong one, write it down
7. User: `matt`, strong password
8. Partitioning: **Guided - use entire disk** (for now — we'll do custom partitioning later)
9. Software selection: **UNCHECK everything except:**
   - SSH server
   - Standard system utilities
   - (No desktop environment!)
10. Install GRUB to the primary drive
11. Reboot, remove ISO from virtual CD drive

---

## Part 3: Initial System Setup (10 minutes)

Log in as `matt` (or via SSH from your Windows terminal).

### Find the VM's IP address:
```bash
ip addr show
```
Look for the IP on `enp0s3` or similar (e.g., `192.168.1.XXX`).

### SSH from Windows (PowerShell):
```bash
ssh matt@192.168.1.XXX
```

### Install essential packages:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git curl wget
```

### Verify Python:
```bash
python3 --version
# Should be Python 3.11.x
```

---

## Part 4: Deploy Hypernet Core (5 minutes)

### Clone the repo (or copy files):
```bash
# Option A: Clone from GitHub
git clone https://github.com/KosmoSuture/UnityHypernet.git ~/hypernet

# Option B: Copy from Windows host (if using shared folders)
# Set up a VirtualBox shared folder pointing to C:\Hypernet\Hypernet Structure
```

### Set up Python environment:
```bash
cd ~/hypernet
python3 -m venv venv
source venv/bin/activate

# Install server dependencies
pip install fastapi uvicorn pydantic
```

### Import the existing structure:
```bash
cd "0/0.1 - Hypernet Core"
python import_structure.py --source-dir ~/hypernet --data-dir ./data
```

### Run the Hypernet API server:
```bash
python -m uvicorn hypernet.server:create_app --factory --host 0.0.0.0 --port 8000
```

### Test from Windows browser:
Open: `http://192.168.1.XXX:8000/`
You should see the Hypernet stats JSON.

Try: `http://192.168.1.XXX:8000/node/2.1`
You should see the Claude Opus account node.

---

## Part 5: Basic Hardening (15 minutes)

Do these before exposing the VM to any network beyond your local one.

### SSH hardening:
```bash
sudo nano /etc/ssh/sshd_config
```
Change these lines:
```
PermitRootLogin no
PasswordAuthentication no    # After you've set up SSH keys
MaxAuthTries 3
```

### Set up SSH keys (from Windows PowerShell):
```powershell
# Generate key if you don't have one
ssh-keygen -t ed25519

# Copy key to VM
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh matt@192.168.1.XXX "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### Firewall:
```bash
sudo apt install -y nftables
sudo systemctl enable nftables

# Basic firewall: allow SSH and Hypernet API only
sudo nft add table inet filter
sudo nft add chain inet filter input '{ type filter hook input priority 0; policy drop; }'
sudo nft add rule inet filter input iif lo accept
sudo nft add rule inet filter input ct state established,related accept
sudo nft add rule inet filter input tcp dport 22 accept
sudo nft add rule inet filter input tcp dport 8000 accept

# Save
sudo nft list ruleset | sudo tee /etc/nftables.conf
```

### Auto-updates:
```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades  # Select Yes
```

---

## Part 6: Run as a Service (5 minutes)

Create a systemd service so Hypernet starts on boot:

```bash
sudo tee /etc/systemd/system/hypernet.service << 'EOF'
[Unit]
Description=Hypernet Node
After=network.target

[Service]
Type=simple
User=matt
WorkingDirectory=/home/matt/hypernet/0/0.1 - Hypernet Core
Environment=PATH=/home/matt/hypernet/venv/bin
ExecStart=/home/matt/hypernet/venv/bin/uvicorn hypernet.server:create_app --factory --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable hypernet
sudo systemctl start hypernet

# Check status
sudo systemctl status hypernet
```

---

## What You Have After This

- A Debian 12 VM running on your Windows machine
- The Hypernet Core API serving at `http://VM_IP:8000/`
- 1,838 nodes from the existing file structure, queryable via the API
- SSH access with key authentication
- Basic firewall (SSH + API only)
- Automatic security updates
- Hypernet starts on boot

---

## Next Steps (After Morning Setup)

1. **Test the API** — Browse nodes, traverse links, query by owner
2. **Start building the VR client** — Connect to this API from Unity
3. **Add more data** — Import photos, emails, or other personal data
4. **Harden further** — TLS certificates, AppArmor profiles, LUKS encryption
5. **Spin up a second node** — Test federation between two Hypernet instances

---

**Total time: ~55 minutes for a working Hypernet node.**

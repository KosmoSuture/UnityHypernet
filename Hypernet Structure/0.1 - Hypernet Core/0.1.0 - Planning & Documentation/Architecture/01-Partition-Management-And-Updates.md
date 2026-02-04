# Partition Management and Atomic Update System

**Version:** 0.1.0
**Last Updated:** 2026-02-03
**Related:** 00-System-Architecture-Overview.md

---

## Overview

This document details the partition management strategy and atomic update mechanism for Hypernet Core's immutable infrastructure approach.

---

## A/B Partition Scheme

### Concept

Hypernet uses **dual system partitions** (A and B) to enable atomic, zero-downtime updates with instant rollback capability.

```
Disk Layout:
┌──────────────────────────────────────────────────────────┐
│ /dev/sda1  │ /boot (EFI)                    │ 512 MB    │
├──────────────────────────────────────────────────────────┤
│ /dev/sda2  │ / (System A)                   │ 25 GB     │
├──────────────────────────────────────────────────────────┤
│ /dev/sda3  │ /system-b (System B)           │ 25 GB     │
├──────────────────────────────────────────────────────────┤
│ /dev/sda4  │ /config                        │ 2 GB      │
├──────────────────────────────────────────────────────────┤
│ /dev/sda5  │ /data (Database)               │ 200 GB    │
├──────────────────────────────────────────────────────────┤
│ /dev/sda6  │ /media (User Uploads)          │ 500 GB    │
├──────────────────────────────────────────────────────────┤
│ /dev/sda7  │ /logs                          │ 100 GB    │
├──────────────────────────────────────────────────────────┤
│ /dev/sda8  │ /cache                         │ 50 GB     │
└──────────────────────────────────────────────────────────┘
```

### Boot Process

1. **Bootloader (GRUB)** reads boot configuration
2. Checks which partition is **active** (A or B)
3. Mounts active partition as `/` (read-only)
4. Mounts other partitions (`/config`, `/data`, `/media`, etc.)
5. Starts Hypernet services

### Update Process

```
Current State: System A is active (booted from /dev/sda2)

Update Steps:
1. Download new system image (verified, signed)
2. Write to inactive partition (System B - /dev/sda3)
3. Verify written data (checksums, signatures)
4. Update bootloader to point to System B
5. Reboot
6. System B becomes active
7. If boot fails, bootloader auto-reverts to System A

Result: System B is now active, System A available for rollback
```

### Rollback

If a problem is detected after update:
```bash
hypernet-admin rollback
# Changes bootloader to previous partition
# Reboot required
```

Automatic rollback triggers:
- Failed boot (GRUB detects kernel panic or boot failure)
- Health check failures (Hypernet doesn't start within 5 minutes)
- Manual intervention (admin command)

---

## System Image Creation

### Image Build Process

System images are built in a **clean, reproducible environment** (container or VM).

```yaml
# build-config.yaml
base_os: ubuntu-24.04-server
hypernet_version: 0.1.0
python_version: 3.11
packages:
  - python3.11
  - python3-pip
  - postgresql-client
  - redis-tools
  - clamav
  - fail2ban
hypernet_dependencies:
  - fastapi==0.109.0
  - uvicorn==0.27.0
  - sqlalchemy==2.0.25
  - pydantic==2.5.0
  # ... (pinned versions from requirements.txt)
```

**Build Steps:**
1. Start with minimal Ubuntu 24.04 base
2. Install system packages (apt)
3. Install Python and dependencies (pip)
4. Copy Hypernet application code
5. Pre-compile Python bytecode
6. Run tests and validation
7. Create filesystem image (squashfs or ext4)
8. Generate cryptographic signatures (GPG + SHA-256)
9. Publish image to update server

### Image Signing

```bash
# Generate image hash
sha256sum hypernet-0.1.0.img > hypernet-0.1.0.img.sha256

# Sign with GPG
gpg --detach-sign --armor hypernet-0.1.0.img

# Result:
# - hypernet-0.1.0.img (system image)
# - hypernet-0.1.0.img.sha256 (checksum)
# - hypernet-0.1.0.img.asc (GPG signature)
```

### Image Verification

Before writing to disk:
```bash
# Verify GPG signature
gpg --verify hypernet-0.1.0.img.asc hypernet-0.1.0.img

# Verify checksum
sha256sum -c hypernet-0.1.0.img.sha256

# Only proceed if both pass
```

---

## Update Delivery Mechanism

### Phase 1: Manual Updates

Admin downloads and applies updates manually:
```bash
# Download update package
wget https://updates.hypernet.io/releases/0.1.1/hypernet-0.1.1.img
wget https://updates.hypernet.io/releases/0.1.1/hypernet-0.1.1.img.sha256
wget https://updates.hypernet.io/releases/0.1.1/hypernet-0.1.1.img.asc

# Verify and apply
hypernet-admin update --image hypernet-0.1.1.img
```

### Phase 2: Automated Updates (Future)

```yaml
# /config/updates.yaml
auto_update:
  enabled: true
  channel: stable  # stable, beta, or dev
  schedule: "02:00"  # Run at 2 AM daily
  require_approval: true  # Admin must approve before reboot
```

Update daemon checks for new versions daily:
1. Query update server: `GET /api/updates?current=0.1.0&channel=stable`
2. If update available, download and verify
3. If `require_approval: false`, apply immediately
4. If `require_approval: true`, notify admin and wait
5. After approval, apply update and reboot

---

## Configuration Management

### Configuration Separation

**Problem:** Immutable system partition can't be modified, but config needs to be machine-specific.

**Solution:** Separate `/config` partition that persists across updates.

### Configuration Structure

```
/config/
├── hypernet/
│   ├── server.yaml          # Server settings (IP, port, hostname)
│   ├── database.yaml        # Database connection
│   ├── api.yaml             # API settings (rate limits, CORS)
│   ├── integrations.yaml    # Enabled integrations
│   └── secrets/             # Encrypted secrets
│       ├── jwt-secret.enc
│       ├── db-password.enc
│       └── api-keys.enc
├── tls/
│   ├── certificate.pem
│   └── private-key.pem
└── version                   # Config version for migration
```

### Configuration Schema Versioning

When updates change configuration format, a migration script runs on boot:

```python
# /usr/bin/hypernet-config-migrate
def migrate_config(current_version, target_version):
    if current_version < 2 and target_version >= 2:
        # Migration: v1 -> v2 (example)
        old_config = load_yaml('/config/hypernet/server.yaml')
        new_config = {
            'server': {
                'host': old_config.get('host', '0.0.0.0'),
                'port': old_config.get('port', 8443),
                'workers': old_config.get('workers', 4),  # NEW in v2
            }
        }
        save_yaml('/config/hypernet/server.yaml', new_config)
        write_version('/config/version', 2)
```

### Secrets Management

Secrets in `/config/secrets/` are encrypted using a key derived from:
- **Option 1:** TPM (Trusted Platform Module) - hardware-backed
- **Option 2:** Passphrase (entered on first boot or via config file)
- **Option 3:** Hardware Security Module (HSM) for high-security deployments

Encryption:
```python
from cryptography.fernet import Fernet
import hashlib

# Derive encryption key from passphrase or TPM
passphrase = get_tpm_key()  # or prompt_for_passphrase()
key = hashlib.pbkdf2_hmac('sha256', passphrase.encode(), b'hypernet-salt', 100000)
fernet = Fernet(base64.urlsafe_b64encode(key))

# Encrypt secret
encrypted_secret = fernet.encrypt(b"my-secret-api-key")
write_file('/config/secrets/api-key.enc', encrypted_secret)

# Decrypt at runtime
encrypted_data = read_file('/config/secrets/api-key.enc')
secret = fernet.decrypt(encrypted_data)
```

---

## Mount Options and Filesystem Security

### System Partition (/)

```bash
# /etc/fstab entry
/dev/sda2  /  ext4  ro,nodev,nosuid,noexec  0  1
```

**Options:**
- `ro` - Read-only (prevents any writes)
- `nodev` - No device files (prevents device-based attacks)
- `nosuid` - No setuid binaries (prevents privilege escalation)
- `noexec` - No execution (prevents running binaries from this partition... except kernel needs to exec /sbin/init, so this may need to be omitted for root)

**Note:** `noexec` may not be practical for `/` since the kernel needs to execute binaries. Alternative: use **dm-verity** for integrity checking.

### Data Partition (/data)

```bash
/dev/mapper/data-encrypted  /data  ext4  rw,nodev,nosuid,noexec  0  2
```

**Options:**
- `rw` - Read-write (needed for database)
- `nodev`, `nosuid`, `noexec` - Hardening

**Encryption:**
```bash
# Setup LUKS2 encryption
cryptsetup luksFormat /dev/sda5
cryptsetup open /dev/sda5 data-encrypted
mkfs.ext4 /dev/mapper/data-encrypted
```

Key stored in `/config/secrets/luks-key.enc` or TPM.

### Media Partition (/media)

```bash
/dev/mapper/media-encrypted  /media  xfs  rw,nodev,nosuid,noexec  0  2
```

**Filesystem:** XFS chosen for large file performance.

### Logs Partition (/logs)

```bash
/dev/sda7  /logs  ext4  rw,nodev,nosuid,noexec  0  2
```

**Optional:** Make append-only using `chattr`:
```bash
chattr +a /logs/hypernet/audit.log
# Now file can only be appended to, not modified or deleted (even by root)
```

---

## Integrity Checking with dm-verity

### What is dm-verity?

dm-verity provides **read-only, block-level integrity checking** for the system partition. Any tampering is detected immediately.

### How it Works

1. During image build, a **hash tree** is generated for the entire filesystem
2. Root hash is signed and embedded in bootloader
3. On boot, kernel verifies each block as it's read
4. If any block doesn't match hash, boot fails (or block is rejected)

### Setup (Optional for Phase 1, Recommended for Production)

```bash
# Create dm-verity device during image build
veritysetup format /dev/sda2 /dev/sda2-hash

# Outputs root hash (embed in bootloader config):
# Root hash: abcd1234...

# On boot, kernel mounts via dm-verity:
veritysetup create system-verified /dev/sda2 /dev/sda2-hash abcd1234...
mount /dev/mapper/system-verified /
```

**Benefit:** Even if attacker gains physical access and modifies disk, system won't boot or will boot in read-only verified mode.

---

## Backup Strategy

### What to Backup

| Partition | Backup Frequency | Retention | Method |
|-----------|------------------|-----------|--------|
| `/` (System) | Not needed | N/A | Reproducible from build |
| `/config` | Before every update | 30 days | rsync + encryption |
| `/data` | Daily | 30 days + monthly snapshots | PostgreSQL dump or filesystem snapshot |
| `/media` | Daily (incremental) | 90 days | Restic or Borg |
| `/logs` | Weekly (archive) | 1 year | Compress and archive to cold storage |

### Backup Locations

- **Local:** External drive or NAS
- **Remote:** Encrypted cloud storage (S3, Backblaze B2)
- **Offline:** Periodic offline backups to removable media (for disaster recovery)

### Backup Script Example

```bash
#!/bin/bash
# /usr/local/bin/hypernet-backup

# Backup configuration
rsync -avz --delete /config/ /backup/config/

# Backup database (PostgreSQL)
pg_dump -U hypernet -d hypernet > /backup/db/hypernet-$(date +%Y%m%d).sql
gzip /backup/db/hypernet-$(date +%Y%m%d).sql

# Backup media (incremental with Restic)
restic -r /backup/media backup /media --exclude /media/temp

# Cleanup old backups (keep 30 days)
find /backup -name "*.sql.gz" -mtime +30 -delete
```

### Disaster Recovery

**Scenario:** Complete system failure (hardware dies)

**Recovery Steps:**
1. Provision new server
2. Install Ubuntu and partition disk
3. Deploy latest Hypernet system image to `/`
4. Restore `/config` from backup
5. Restore `/data` from backup (PostgreSQL restore)
6. Restore `/media` from backup (Restic restore)
7. Boot and verify

**RTO (Recovery Time Objective):** < 4 hours
**RPO (Recovery Point Objective):** < 24 hours (daily backups)

---

## Monitoring and Health Checks

### Boot Health Check

On every boot, Hypernet runs self-checks:
```yaml
health_checks:
  - name: "Database connectivity"
    command: "pg_isready -U hypernet"
    timeout: 10s

  - name: "Partition mounts"
    command: "check-mounts.sh"  # Verifies all partitions mounted
    timeout: 5s

  - name: "Configuration valid"
    command: "hypernet-admin validate-config"
    timeout: 10s

  - name: "API responding"
    command: "curl -f http://localhost:8000/health"
    timeout: 30s
```

If any check fails:
- Boot continues but system marked as "degraded"
- Alert sent to admin
- If consecutive boot failures, auto-rollback to previous partition

### Runtime Monitoring

```python
# Systemd service monitors Hypernet process
# If crashes, auto-restart (up to 5 times)
# If 5 restarts in 10 minutes, mark as failed and alert

[Service]
Restart=on-failure
RestartSec=10s
StartLimitBurst=5
StartLimitIntervalSec=600
```

---

## Update Testing Strategy

### Staging Environment

Before deploying to production:
1. Deploy update to **staging server** (identical config to production)
2. Run automated tests (API tests, integration tests)
3. Manual smoke testing
4. If all pass, schedule production update

### Canary Deployment (Future - Multi-Server)

1. Deploy update to **one server** in cluster
2. Monitor for errors (10-30 minutes)
3. If no issues, roll out to remaining servers
4. If issues detected, rollback immediately

---

## Security Considerations

### Update Server Security

- **TLS encryption:** All update downloads over HTTPS
- **Signature verification:** GPG signatures prevent MITM attacks
- **Checksum verification:** Detect corruption or tampering
- **Access control:** Update server requires authentication (for beta/dev channels)

### Preventing Unauthorized Updates

- Only signed images from trusted keys can be installed
- `/config` contains list of trusted GPG key fingerprints
- Update tool rejects images not signed by trusted keys

### Physical Security

- **Disk encryption:** Even if disk is stolen, data is encrypted
- **Secure boot:** UEFI Secure Boot prevents bootloader tampering
- **TPM-backed keys:** Secrets tied to specific hardware (can't be extracted)

---

## Open Questions

1. **dm-verity for Phase 1?** - Adds complexity but significantly improves security. Defer to Phase 2?
2. **Automatic vs. Manual Updates?** - Start manual, add auto-updates in Phase 2?
3. **Update server hosting?** - Self-hosted (GitHub releases) or dedicated CDN?
4. **Configuration migration strategy?** - How complex will config changes be between versions?

---

## Implementation Checklist

- [ ] Design partition layout script
- [ ] Create system image build pipeline
- [ ] Implement GPG signing for images
- [ ] Write update tool (`hypernet-admin update`)
- [ ] Implement A/B partition switching in bootloader
- [ ] Create configuration migration framework
- [ ] Implement secrets encryption (TPM or passphrase)
- [ ] Write backup scripts
- [ ] Create health check framework
- [ ] Document update procedure for admins

---

**Status:** Design complete, ready for implementation
**Next:** Development Roadmap to prioritize implementation tasks

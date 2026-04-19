"""
Hypernet Personal Data Vault

Session-based vault management that bridges authentication (auth.py)
and encryption (encryption.py). After a user logs in with their password
(identity), they unlock their vault with a separate passphrase (data access).

The DEK (Data Encryption Key) is held in memory only while the vault is
unlocked. It is never written to disk. Auto-lock after idle timeout.

Architecture:
  Login (email+password) → JWT → Vault Unlock (passphrase) → DEK in memory
  DEK used to encrypt/decrypt personal nodes transparently via EncryptedStore.

Standard: 2.0.19 (AI Data Protection), 2.0.20 (Personal Companion)
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .encryption import EncryptionManager

log = logging.getLogger(__name__)

DEFAULT_SESSION_TIMEOUT = 3600  # 1 hour idle timeout
MAX_UNLOCK_ATTEMPTS = 5
LOCKOUT_SECONDS = 900  # 15 minutes


@dataclass
class VaultSession:
    """An active, unlocked vault session."""
    encryption_manager: EncryptionManager
    unlocked_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    session_timeout: int = DEFAULT_SESSION_TIMEOUT

    def touch(self) -> None:
        """Update last access time."""
        self.last_accessed = time.time()

    @property
    def is_expired(self) -> bool:
        """Check if the session has exceeded its idle timeout."""
        return (time.time() - self.last_accessed) > self.session_timeout


class VaultManager:
    """Manages vault sessions for authenticated users.

    Each user (identified by Hypernet Address) can have one active vault
    session. Sessions are held in memory and auto-expire after idle timeout.
    """

    def __init__(self, data_dir: str | Path, session_timeout: int = DEFAULT_SESSION_TIMEOUT):
        self.data_dir = Path(data_dir)
        self.keys_dir = self.data_dir / "keys"
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        self.session_timeout = session_timeout
        self._sessions: dict[str, VaultSession] = {}
        self._lock = threading.Lock()
        # Rate limiting for unlock attempts
        self._unlock_attempts: dict[str, list[float]] = {}

    def _keys_path(self, ha: str) -> Path:
        """Get the KeyBundle path for a given Hypernet Address."""
        safe_name = ha.replace(".", "_").replace("/", "_")
        return self.keys_dir / f"{safe_name}.json"

    def vault_exists(self, ha: str) -> bool:
        """Check if a vault has been created for this user."""
        return self._keys_path(ha).exists()

    def create_vault(self, ha: str, passphrase: str) -> VaultSession:
        """Create a new vault for a user.

        Generates a fresh DEK, encrypts it with the passphrase-derived
        master key, saves the KeyBundle to disk, and returns an unlocked
        session.

        Args:
            ha: User's Hypernet Address (e.g., "1.1")
            passphrase: Vault passphrase (separate from login password)

        Returns:
            An active VaultSession with the DEK in memory

        Raises:
            FileExistsError: If a vault already exists for this user
            RuntimeError: If cryptography package is not installed
        """
        keys_path = self._keys_path(ha)
        if keys_path.exists():
            raise FileExistsError(f"Vault already exists for {ha}")

        mgr = EncryptionManager.create_account(passphrase, keys_path)
        session = VaultSession(
            encryption_manager=mgr,
            session_timeout=self.session_timeout,
        )

        with self._lock:
            self._sessions[ha] = session

        log.info("Vault created for %s", ha)
        return session

    def unlock_vault(self, ha: str, passphrase: str) -> VaultSession:
        """Unlock an existing vault.

        Derives the master key from the passphrase, decrypts the DEK,
        and stores it in memory for the session.

        Args:
            ha: User's Hypernet Address
            passphrase: Vault passphrase

        Returns:
            An active VaultSession

        Raises:
            FileNotFoundError: No vault exists for this user
            ValueError: Account locked out due to too many attempts
            Exception: Wrong passphrase (cryptography.exceptions.InvalidTag)
        """
        # Rate limiting
        if self._is_locked_out(ha):
            raise ValueError(
                f"Vault unlock locked out for {ha}. "
                f"Too many failed attempts. Try again later."
            )

        keys_path = self._keys_path(ha)
        if not keys_path.exists():
            raise FileNotFoundError(f"No vault found for {ha}")

        try:
            mgr = EncryptionManager.unlock(passphrase, keys_path)
        except Exception:
            self._record_failed_attempt(ha)
            raise

        # Success — clear failure history
        with self._lock:
            self._unlock_attempts.pop(ha, None)

        session = VaultSession(
            encryption_manager=mgr,
            session_timeout=self.session_timeout,
        )

        with self._lock:
            self._sessions[ha] = session

        log.info("Vault unlocked for %s", ha)
        return session

    def lock_vault(self, ha: str) -> None:
        """Lock a vault, wiping the DEK from memory.

        Args:
            ha: User's Hypernet Address
        """
        with self._lock:
            session = self._sessions.pop(ha, None)
            if session:
                # Clear the encryption manager reference
                del session
                log.info("Vault locked for %s", ha)

    def get_vault(self, ha: str) -> Optional[EncryptionManager]:
        """Get the active EncryptionManager for a user, if unlocked.

        Returns None if the vault is locked, doesn't exist, or has expired.
        Automatically locks expired sessions.
        """
        with self._lock:
            session = self._sessions.get(ha)
            if session is None:
                return None
            if session.is_expired:
                self._sessions.pop(ha, None)
                log.info("Vault session expired for %s (idle timeout)", ha)
                return None
            session.touch()
            return session.encryption_manager

    def is_unlocked(self, ha: str) -> bool:
        """Check if a user's vault is currently unlocked."""
        return self.get_vault(ha) is not None

    def get_status(self, ha: str) -> dict:
        """Get vault status for a user."""
        exists = self.vault_exists(ha)
        unlocked = self.is_unlocked(ha)

        status = {
            "ha": ha,
            "vault_exists": exists,
            "unlocked": unlocked,
        }

        if unlocked:
            with self._lock:
                session = self._sessions.get(ha)
                if session:
                    status["key_version"] = session.encryption_manager.key_version
                    status["unlocked_at"] = session.unlocked_at
                    status["last_accessed"] = session.last_accessed
                    status["timeout_seconds"] = session.session_timeout

        return status

    def change_passphrase(self, ha: str, old_passphrase: str, new_passphrase: str) -> None:
        """Change the vault passphrase.

        Re-encrypts the DEK with a new master key derived from the new
        passphrase. The DEK itself does not change, so existing encrypted
        data remains accessible.

        Args:
            ha: User's Hypernet Address
            old_passphrase: Current passphrase (to verify)
            new_passphrase: New passphrase
        """
        keys_path = self._keys_path(ha)
        # Verify old passphrase by unlocking
        mgr = EncryptionManager.unlock(old_passphrase, keys_path)
        # Re-encrypt with new passphrase by rotating with new derivation
        # We need to re-derive and re-encrypt the DEK with new passphrase
        from .encryption import generate_salt, derive_key, encrypt_data, KeyBundle
        new_salt = generate_salt()
        new_master = derive_key(new_passphrase, new_salt)
        new_encrypted_dek = encrypt_data(mgr._dek, new_master)
        new_bundle = KeyBundle(
            salt=new_salt,
            encrypted_dek=new_encrypted_dek,
            version=mgr.key_version,
        )
        new_bundle.save(keys_path)
        log.info("Vault passphrase changed for %s", ha)

    def create_backup(self, ha: str, backup_passphrase: str) -> Path:
        """Create a backup key for the vault.

        Args:
            ha: User's Hypernet Address (vault must be unlocked)
            backup_passphrase: Passphrase for the backup key

        Returns:
            Path to the backup key file
        """
        mgr = self.get_vault(ha)
        if mgr is None:
            raise ValueError("Vault must be unlocked to create a backup")

        backup_path = self.keys_dir / f"{ha.replace('.', '_')}_backup.json"
        mgr.create_backup_key(backup_passphrase, backup_path)
        return backup_path

    def cleanup_expired(self) -> int:
        """Remove all expired sessions. Returns count of sessions cleaned."""
        cleaned = 0
        with self._lock:
            expired = [
                ha for ha, session in self._sessions.items()
                if session.is_expired
            ]
            for ha in expired:
                del self._sessions[ha]
                cleaned += 1
                log.info("Cleaned expired vault session for %s", ha)
        return cleaned

    # ── Rate limiting ──────────────────────────────────────────────

    def _is_locked_out(self, ha: str) -> bool:
        """Check if unlock attempts are rate-limited."""
        with self._lock:
            attempts = self._unlock_attempts.get(ha, [])
            cutoff = time.time() - LOCKOUT_SECONDS
            recent = [t for t in attempts if t > cutoff]
            return len(recent) >= MAX_UNLOCK_ATTEMPTS

    def _record_failed_attempt(self, ha: str) -> None:
        """Record a failed unlock attempt."""
        with self._lock:
            if ha not in self._unlock_attempts:
                self._unlock_attempts[ha] = []
            self._unlock_attempts[ha].append(time.time())
            # Keep only recent attempts
            cutoff = time.time() - LOCKOUT_SECONDS
            self._unlock_attempts[ha] = [
                t for t in self._unlock_attempts[ha] if t > cutoff
            ]
            remaining = MAX_UNLOCK_ATTEMPTS - len(self._unlock_attempts[ha])
            if remaining <= 0:
                log.warning("Vault unlock locked out for %s", ha)
            else:
                log.warning(
                    "Failed vault unlock for %s (%d attempts remaining)",
                    ha, remaining,
                )

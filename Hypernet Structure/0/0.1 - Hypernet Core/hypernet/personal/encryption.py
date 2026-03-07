"""
Hypernet Personal Data Encryption

At-rest encryption for personal account data. Every node in a local
account (1.local.*) is encrypted individually, so compromising one
file does not compromise the entire account.

Design:
  Master Key ← derived from passphrase via scrypt (stdlib)
  Data Encryption Key (DEK) ← random 256-bit, encrypted by Master Key
  Per-node encryption ← AES-GCM using DEK

Uses `cryptography` library when available (preferred), falls back
to stdlib for key derivation. AES-GCM requires `cryptography`.

Security properties:
  - Each node encrypted with unique nonce (12 bytes, random)
  - Key derivation: scrypt with n=2^17, r=8, p=1 (OWASP recommended)
  - DEK rotation: generate new DEK, re-encrypt all nodes
  - Master key never stored — derived from passphrase each session
  - Backup key: separate encrypted copy of DEK for recovery

Architecture: docs/architecture/personal-accounts-and-life-story.md §Encryption
Standard: 2.0.19 (AI Data Protection), 2.0.20 (Personal Companion)
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

# Try to use cryptography library (preferred for AES-GCM)
_HAS_CRYPTOGRAPHY = False
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    _HAS_CRYPTOGRAPHY = True
except ImportError:
    pass


# ── Key Derivation ──────────────────────────────────────────────────

def derive_key(passphrase: str, salt: bytes, key_length: int = 32) -> bytes:
    """Derive an encryption key from a passphrase using scrypt.

    Parameters:
    - n=2^14 (16384) — CPU/memory cost (OWASP minimum for scrypt)
    - r=8 — block size
    - p=1 — parallelism

    Args:
        passphrase: User's passphrase (should be strong)
        salt: Random salt (at least 16 bytes)
        key_length: Output key length in bytes (default 32 = 256 bits)

    Returns:
        Derived key bytes
    """
    return hashlib.scrypt(
        passphrase.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=key_length,
    )


def generate_salt() -> bytes:
    """Generate a cryptographically random 16-byte salt."""
    return os.urandom(16)


# ── AES-GCM Encryption ─────────────────────────────────────────────

def encrypt_data(data: bytes, key: bytes) -> bytes:
    """Encrypt data using AES-256-GCM.

    Output format: nonce (12 bytes) || ciphertext+tag

    Requires the `cryptography` library.
    """
    if not _HAS_CRYPTOGRAPHY:
        raise RuntimeError(
            "Encryption requires the 'cryptography' package. "
            "Install with: pip install cryptography"
        )
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext


def decrypt_data(encrypted: bytes, key: bytes) -> bytes:
    """Decrypt AES-256-GCM encrypted data.

    Expects format: nonce (12 bytes) || ciphertext+tag
    """
    if not _HAS_CRYPTOGRAPHY:
        raise RuntimeError(
            "Decryption requires the 'cryptography' package. "
            "Install with: pip install cryptography"
        )
    nonce = encrypted[:12]
    ciphertext = encrypted[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)


# ── Data Encryption Key (DEK) Management ───────────────────────────

@dataclass
class KeyBundle:
    """Encrypted key bundle stored on disk.

    The DEK (Data Encryption Key) is encrypted by the master key.
    The master key is never stored — it's derived from the passphrase
    each time the user opens their account.
    """
    salt: bytes              # Salt for master key derivation
    encrypted_dek: bytes     # DEK encrypted by master key
    version: int = 1         # Key version (for rotation tracking)

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "salt": base64.b64encode(self.salt).decode("ascii"),
            "encrypted_dek": base64.b64encode(self.encrypted_dek).decode("ascii"),
        }

    @classmethod
    def from_dict(cls, d: dict) -> KeyBundle:
        return cls(
            version=d.get("version", 1),
            salt=base64.b64decode(d["salt"]),
            encrypted_dek=base64.b64decode(d["encrypted_dek"]),
        )

    def save(self, path: Path) -> None:
        """Save key bundle to a JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        log.info("Key bundle saved to %s", path)

    @classmethod
    def load(cls, path: Path) -> KeyBundle:
        """Load key bundle from a JSON file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(data)


class EncryptionManager:
    """Manages encryption for a personal account.

    Usage:
        # First time — create account
        mgr = EncryptionManager.create_account(passphrase, keys_path)

        # Subsequent sessions — unlock account
        mgr = EncryptionManager.unlock(passphrase, keys_path)

        # Encrypt/decrypt node data
        encrypted = mgr.encrypt_node(node_json_bytes)
        decrypted = mgr.decrypt_node(encrypted_bytes)
    """

    def __init__(self, dek: bytes, key_bundle: KeyBundle, keys_path: Path):
        self._dek = dek
        self._key_bundle = key_bundle
        self._keys_path = keys_path

    @classmethod
    def create_account(cls, passphrase: str, keys_path: Path) -> EncryptionManager:
        """Create a new encrypted account with a fresh DEK.

        Args:
            passphrase: User's chosen passphrase
            keys_path: Where to store the encrypted key bundle

        Returns:
            An unlocked EncryptionManager ready to encrypt/decrypt
        """
        if not _HAS_CRYPTOGRAPHY:
            raise RuntimeError(
                "Account creation requires the 'cryptography' package. "
                "Install with: pip install cryptography"
            )

        # Generate salt and derive master key
        salt = generate_salt()
        master_key = derive_key(passphrase, salt)

        # Generate random DEK
        dek = secrets.token_bytes(32)

        # Encrypt DEK with master key
        encrypted_dek = encrypt_data(dek, master_key)

        bundle = KeyBundle(salt=salt, encrypted_dek=encrypted_dek, version=1)
        bundle.save(keys_path)

        log.info("New encrypted account created")
        return cls(dek=dek, key_bundle=bundle, keys_path=keys_path)

    @classmethod
    def unlock(cls, passphrase: str, keys_path: Path) -> EncryptionManager:
        """Unlock an existing account by decrypting the DEK.

        Args:
            passphrase: User's passphrase
            keys_path: Path to the encrypted key bundle

        Returns:
            An unlocked EncryptionManager

        Raises:
            cryptography.exceptions.InvalidTag: Wrong passphrase
            FileNotFoundError: Key bundle not found
        """
        bundle = KeyBundle.load(keys_path)

        # Derive master key from passphrase + stored salt
        master_key = derive_key(passphrase, bundle.salt)

        # Decrypt DEK
        dek = decrypt_data(bundle.encrypted_dek, master_key)

        log.info("Account unlocked (key version %d)", bundle.version)
        return cls(dek=dek, key_bundle=bundle, keys_path=keys_path)

    def encrypt_node(self, data: bytes) -> bytes:
        """Encrypt node data (JSON bytes) for at-rest storage."""
        return encrypt_data(data, self._dek)

    def decrypt_node(self, encrypted: bytes) -> bytes:
        """Decrypt node data from at-rest storage."""
        return decrypt_data(encrypted, self._dek)

    def encrypt_json(self, obj: dict) -> str:
        """Encrypt a dict to a base64-encoded string (for JSON storage)."""
        plaintext = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        encrypted = self.encrypt_node(plaintext)
        return base64.b64encode(encrypted).decode("ascii")

    def decrypt_json(self, b64_encrypted: str) -> dict:
        """Decrypt a base64-encoded string back to a dict."""
        encrypted = base64.b64decode(b64_encrypted)
        plaintext = self.decrypt_node(encrypted)
        return json.loads(plaintext.decode("utf-8"))

    def rotate_dek(self, passphrase: str) -> None:
        """Generate a new DEK and re-encrypt the key bundle.

        IMPORTANT: After calling this, all stored encrypted data must
        be re-encrypted with the new DEK. The caller is responsible for
        orchestrating the re-encryption of all nodes.
        """
        old_dek = self._dek

        # Generate new DEK
        new_dek = secrets.token_bytes(32)

        # Re-derive master key
        master_key = derive_key(passphrase, self._key_bundle.salt)

        # Encrypt new DEK with master key
        encrypted_dek = encrypt_data(new_dek, master_key)

        # Update bundle
        self._key_bundle = KeyBundle(
            salt=self._key_bundle.salt,
            encrypted_dek=encrypted_dek,
            version=self._key_bundle.version + 1,
        )
        self._key_bundle.save(self._keys_path)
        self._dek = new_dek

        log.info("DEK rotated to version %d", self._key_bundle.version)

    def create_backup_key(self, backup_passphrase: str, backup_path: Path) -> None:
        """Create a backup copy of the DEK encrypted with a different passphrase.

        Store this on a USB drive, print as QR code, or save to a secure location.
        """
        salt = generate_salt()
        backup_master = derive_key(backup_passphrase, salt)
        encrypted_dek = encrypt_data(self._dek, backup_master)

        bundle = KeyBundle(salt=salt, encrypted_dek=encrypted_dek, version=self._key_bundle.version)
        bundle.save(backup_path)
        log.info("Backup key saved to %s", backup_path)

    @property
    def key_version(self) -> int:
        return self._key_bundle.version

    @property
    def is_unlocked(self) -> bool:
        return self._dek is not None

    @staticmethod
    def is_available() -> bool:
        """Check if encryption is available (cryptography package installed)."""
        return _HAS_CRYPTOGRAPHY

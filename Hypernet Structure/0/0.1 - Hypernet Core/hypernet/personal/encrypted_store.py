"""
Hypernet Encrypted Store

Transparent encryption layer between the application and the Store.
When a user's vault is unlocked, personal node data is encrypted on
write and decrypted on read. System nodes and public data pass through
unmodified.

This implements the "Locker" concept from the Hypernet architecture:
encrypted containers that hold private data under the user's control.
Each user's personal address space (e.g., 1.1.*) is a locker.

The companion concept — "Mandala" (cryptographic access tokens for
controlled sharing) — will be built on top of this layer.

Architecture: Hypernet Docs/Hypernet_Technical_Architecture_With_Cover.docx.md §5
Standard: 2.0.19 (AI Data Protection), 2.0.20 (Personal Companion)
"""

from __future__ import annotations

import copy
import logging
from typing import Optional

from ..node import Node
from ..address import HypernetAddress
from ..store import Store
from .vault import VaultManager

log = logging.getLogger(__name__)

# Address prefixes that should NEVER be encrypted (system/public data)
_SYSTEM_PREFIXES = ("0.", "2.", "3.")


class EncryptedStore:
    """Store wrapper that transparently encrypts/decrypts personal node data.

    Encryption applies only to nodes under a user's personal address prefix
    (e.g., 1.1.* for Matt). System nodes (0.*, 2.*, 3.*) are never encrypted.

    When a user's vault is unlocked, writes encrypt node.data before storage
    and reads decrypt it on retrieval. When the vault is locked, encrypted
    nodes return metadata only (address, type, timestamps) with a
    {_encrypted: True, _locked: True} marker in data.

    Usage:
        enc_store = EncryptedStore(store, vault_manager)

        # Write — encrypts if vault is unlocked and address is personal
        enc_store.put_node(node, user_ha="1.1")

        # Read — decrypts if vault is unlocked
        node = enc_store.get_node(address, user_ha="1.1")
    """

    def __init__(self, store: Store, vault_manager: VaultManager):
        self._store = store
        self._vault = vault_manager

    @property
    def store(self) -> Store:
        """Access the underlying Store directly (for non-personal operations)."""
        return self._store

    def put_node(self, node: Node, user_ha: str = "") -> None:
        """Store a node, encrypting its data if appropriate.

        Args:
            node: The node to store
            user_ha: The acting user's Hypernet Address. If the node's address
                     is under this prefix and the vault is unlocked, data is
                     encrypted before storage.
        """
        if user_ha and self._should_encrypt(str(node.address), user_ha):
            mgr = self._vault.get_vault(user_ha)
            if mgr and node.data and not node.data.get("_encrypted"):
                # Encrypt the data payload
                encrypted_node = copy.copy(node)
                encrypted_node.data = {
                    "_encrypted": True,
                    "_key_version": mgr.key_version,
                    "_ciphertext": mgr.encrypt_json(node.data),
                }
                self._store.put_node(encrypted_node)
                log.debug("Encrypted node %s (key v%d)", node.address, mgr.key_version)
                return

        # No encryption needed or vault locked — store as-is
        self._store.put_node(node)

    def get_node(self, address: HypernetAddress | str, user_ha: str = "") -> Optional[Node]:
        """Retrieve a node, decrypting its data if appropriate.

        Args:
            address: The node address to retrieve (string or HypernetAddress)
            user_ha: The acting user's Hypernet Address

        Returns:
            The node with decrypted data, or None if not found.
            If encrypted and vault is locked, data contains
            {_encrypted: True, _locked: True}.
        """
        if isinstance(address, str):
            address = HypernetAddress.parse(address)
        node = self._store.get_node(address)
        if node is None:
            return None

        if node.data and node.data.get("_encrypted"):
            mgr = self._vault.get_vault(user_ha) if user_ha else None
            if mgr:
                try:
                    node.data = mgr.decrypt_json(node.data["_ciphertext"])
                    log.debug("Decrypted node %s", address)
                except Exception as e:
                    log.warning("Failed to decrypt node %s: %s", address, e)
                    node.data = {"_encrypted": True, "_error": str(e)}
            else:
                # Vault locked — return metadata only
                node.data = {"_encrypted": True, "_locked": True}

        return node

    def migrate_to_encrypted(self, prefix: str, user_ha: str, batch_size: int = 100) -> dict:
        """Encrypt all existing unencrypted nodes under a prefix.

        This is a one-time migration operation run after vault creation.
        Each node's data is read, encrypted, and written back. The Store's
        versioning system preserves the unencrypted version in history.

        Args:
            prefix: Address prefix to migrate (e.g., "1.1")
            user_ha: User's Hypernet Address (vault must be unlocked)
            batch_size: Process this many nodes per batch

        Returns:
            dict with {migrated: int, skipped: int, errors: int}
        """
        mgr = self._vault.get_vault(user_ha)
        if mgr is None:
            raise ValueError("Vault must be unlocked to migrate data")

        results = {"migrated": 0, "skipped": 0, "errors": 0}

        # Get all nodes under the prefix
        try:
            all_nodes = self._store.query_by_prefix(prefix)
        except AttributeError:
            # Store may not have query_by_prefix — fall back to index scan
            log.warning("Store does not support query_by_prefix, skipping migration")
            return results

        for node in all_nodes:
            if node.data and node.data.get("_encrypted"):
                results["skipped"] += 1
                continue

            if not node.data:
                results["skipped"] += 1
                continue

            try:
                node.data = {
                    "_encrypted": True,
                    "_key_version": mgr.key_version,
                    "_ciphertext": mgr.encrypt_json(node.data),
                }
                self._store.put_node(node)
                results["migrated"] += 1
            except Exception as e:
                log.error("Failed to migrate node %s: %s", node.address, e)
                results["errors"] += 1

        log.info(
            "Migration complete for %s: %d migrated, %d skipped, %d errors",
            prefix, results["migrated"], results["skipped"], results["errors"],
        )
        return results

    def _should_encrypt(self, address: str, user_ha: str) -> bool:
        """Determine if a node should be encrypted.

        Only encrypts nodes under the user's personal address prefix.
        System nodes (0.*, 2.*, 3.*) are never encrypted.
        """
        # Never encrypt system/public nodes
        for sys_prefix in _SYSTEM_PREFIXES:
            if address.startswith(sys_prefix):
                return False

        # Only encrypt if the node belongs to this user
        return address.startswith(user_ha + ".") or address == user_ha

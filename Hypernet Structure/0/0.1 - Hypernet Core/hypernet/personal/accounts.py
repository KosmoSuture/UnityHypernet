"""
Hypernet Local Account Manager

Creates and manages local personal accounts (1.local.*).
Each account follows the 1.0.0-COMPREHENSIVE-PERSON-STRUCTURE template.

Usage:
    mgr = LocalAccountManager(store, data_dir)

    # Create a new local account
    account = mgr.create_account("Matt", passphrase="...")

    # List accounts
    accounts = mgr.list_accounts()

    # Get account info
    info = mgr.get_account("1.local.1")
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..address import HypernetAddress
from ..node import Node
from ..store import Store

log = logging.getLogger(__name__)

# Standard sub-categories for a person account.
# Mirrors the 1.0.0-COMPREHENSIVE-PERSON-STRUCTURE.md template.
PERSON_STRUCTURE = {
    "0": "Profile & Identity",
    "1": "Projects & Work",
    "2": "Documents & Files",
    "3": "Communications",
    "3.0": "Email",
    "3.1": "Messages & Chat",
    "4": "Relationships & Social",
    "5": "Tasks & Productivity",
    "6": "Personal Data",
    "6.1": "Media Objects",
    "6.2": "Social Media",
    "6.7": "Financial Data",
    "6.8": "Health & Fitness",
    "7": "Contributions & Output",
    "8": "Media & Creative",
    "9": "Notes & Knowledge",
    "10": "AI Assistant (Embassy)",
}


class LocalAccount:
    """A local personal account in the Hypernet."""

    def __init__(self, address: str, display_name: str, created: str,
                 encrypted: bool = False):
        self.address = address
        self.display_name = display_name
        self.created = created
        self.encrypted = encrypted

    def to_dict(self) -> dict:
        return {
            "address": self.address,
            "display_name": self.display_name,
            "created": self.created,
            "encrypted": self.encrypted,
        }


class LocalAccountManager:
    """Manages local personal accounts (1.local.*)."""

    def __init__(self, store: Store, data_dir: str | Path = "data"):
        self.store = store
        self.data_dir = Path(data_dir)
        self._accounts_path = self.data_dir / "local_accounts.json"
        self._accounts: dict[str, LocalAccount] = {}
        self._load_accounts()

    def _load_accounts(self) -> None:
        """Load account registry from disk."""
        if self._accounts_path.exists():
            try:
                data = json.loads(self._accounts_path.read_text(encoding="utf-8"))
                for addr, info in data.items():
                    self._accounts[addr] = LocalAccount(
                        address=addr,
                        display_name=info["display_name"],
                        created=info["created"],
                        encrypted=info.get("encrypted", False),
                    )
            except (json.JSONDecodeError, OSError) as e:
                log.warning("Failed to load accounts: %s", e)

    def _save_accounts(self) -> None:
        """Persist account registry to disk."""
        self._accounts_path.parent.mkdir(parents=True, exist_ok=True)
        data = {addr: acct.to_dict() for addr, acct in self._accounts.items()}
        self._accounts_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def create_account(
        self,
        display_name: str,
        passphrase: Optional[str] = None,
    ) -> LocalAccount:
        """Create a new local personal account.

        Creates the account node at 1.local.N and sets up the standard
        person structure with sub-category nodes.

        Args:
            display_name: Human-readable name for the account
            passphrase: If provided, enables encryption for this account

        Returns:
            The created LocalAccount
        """
        # Find next available local account number
        existing = [a for a in self._accounts if a.startswith("1.local.")]
        next_num = len(existing) + 1
        address = f"1.local.{next_num}"

        now = datetime.now(timezone.utc).isoformat()
        encrypted = False

        # Set up encryption if passphrase provided
        if passphrase:
            from .encryption import EncryptionManager
            if EncryptionManager.is_available():
                keys_path = self.data_dir / "keys" / f"{address.replace('.', '_')}.json"
                EncryptionManager.create_account(passphrase, keys_path)
                encrypted = True
                log.info("Encryption enabled for account %s", address)
            else:
                log.warning(
                    "Encryption requested but 'cryptography' package not installed. "
                    "Account created without encryption."
                )

        # Create root account node
        root_addr = HypernetAddress.parse(address)
        root_node = Node(
            address=root_addr,
            type_address=HypernetAddress.parse("0.5.1"),  # Person object type
            data={
                "display_name": display_name,
                "account_type": "local",
                "created": now,
                "encrypted": encrypted,
                "structure_version": "1.0.0",
            },
            creator=HypernetAddress.parse("1.1.10.1"),  # Created by Keel
        )
        self.store.put_node(root_node)

        # Create standard sub-category nodes
        for sub_addr, label in PERSON_STRUCTURE.items():
            full_addr = f"{address}.{sub_addr}"
            node = Node(
                address=HypernetAddress.parse(full_addr),
                type_address=HypernetAddress.parse("0.5.1"),
                data={
                    "label": label,
                    "category": sub_addr,
                    "parent": address,
                },
                creator=HypernetAddress.parse("1.1.10.1"),
            )
            self.store.put_node(node)

        # Register account
        account = LocalAccount(
            address=address,
            display_name=display_name,
            created=now,
            encrypted=encrypted,
        )
        self._accounts[address] = account
        self._save_accounts()

        log.info(
            "Local account created: %s (%s) [encrypted=%s, %d sub-categories]",
            address, display_name, encrypted, len(PERSON_STRUCTURE),
        )
        return account

    def list_accounts(self) -> list[LocalAccount]:
        """List all local accounts."""
        return list(self._accounts.values())

    def get_account(self, address: str) -> Optional[LocalAccount]:
        """Get a specific local account by address."""
        return self._accounts.get(address)

    def delete_account(self, address: str, soft: bool = True) -> bool:
        """Delete a local account.

        Per 2.0.19 (AI Data Protection Standard), defaults to soft delete.

        Args:
            address: Account address (e.g., "1.local.1")
            soft: If True (default), soft-delete nodes. If False, hard delete.

        Returns:
            True if account was deleted
        """
        if address not in self._accounts:
            return False

        root_addr = HypernetAddress.parse(address)

        # Find all nodes under this account
        all_nodes = self.store.list_nodes(prefix=root_addr)

        if soft:
            # Soft delete — mark as deleted but keep data
            for node in all_nodes:
                node.deleted_at = datetime.now(timezone.utc).isoformat()
                self.store.put_node(node)
            log.info("Soft-deleted account %s (%d nodes)", address, len(all_nodes))
        else:
            # Hard delete — remove from store
            for node in all_nodes:
                self.store.delete_node(node.address, hard=True)
            log.info("Hard-deleted account %s (%d nodes)", address, len(all_nodes))

        del self._accounts[address]
        self._save_accounts()
        return True

    def get_structure(self, address: str) -> dict:
        """Get the structure of a local account (categories and their contents).

        Returns a dict of category → {label, node_count}.
        """
        if address not in self._accounts:
            return {}

        root_addr = HypernetAddress.parse(address)
        all_nodes = self.store.list_nodes(prefix=root_addr)

        structure = {}
        for sub_addr, label in PERSON_STRUCTURE.items():
            full_addr = f"{address}.{sub_addr}"
            prefix = HypernetAddress.parse(full_addr)
            count = sum(
                1 for n in all_nodes
                if str(n.address).startswith(full_addr) and str(n.address) != full_addr
            )
            structure[sub_addr] = {"label": label, "node_count": count}

        return structure

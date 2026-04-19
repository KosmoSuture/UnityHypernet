"""
Tests for the Personal Data Vault system.

Tests vault creation, unlock, lock, session timeout, rate limiting,
encrypted store, and auth integration.

Run with:
    python -m pytest test_vault.py -v
    # or without pytest:
    python test_vault.py
"""

import json
import sys
import tempfile
import time
from pathlib import Path

# Ensure hypernet package is importable
sys.path.insert(0, str(Path(__file__).parent))

from hypernet.personal.encryption import EncryptionManager, _HAS_CRYPTOGRAPHY


def test_vault_manager_lifecycle():
    """Test create -> unlock -> lock -> re-unlock cycle."""
    if not _HAS_CRYPTOGRAPHY:
        print("  SKIP: cryptography not installed")
        return

    from hypernet.personal.vault import VaultManager

    with tempfile.TemporaryDirectory() as tmpdir:
        mgr = VaultManager(tmpdir, session_timeout=60)

        # No vault yet
        assert not mgr.vault_exists("1.1")
        assert not mgr.is_unlocked("1.1")

        # Create vault
        session = mgr.create_vault("1.1", "test-passphrase-12chars")
        assert mgr.vault_exists("1.1")
        assert mgr.is_unlocked("1.1")
        assert session.encryption_manager.is_unlocked

        # Can't create again
        try:
            mgr.create_vault("1.1", "another")
            assert False, "Should have raised FileExistsError"
        except FileExistsError:
            pass

        # Lock
        mgr.lock_vault("1.1")
        assert not mgr.is_unlocked("1.1")
        assert mgr.vault_exists("1.1")  # Still exists, just locked

        # Re-unlock
        session2 = mgr.unlock_vault("1.1", "test-passphrase-12chars")
        assert mgr.is_unlocked("1.1")

        # Wrong passphrase
        mgr.lock_vault("1.1")
        try:
            mgr.unlock_vault("1.1", "wrong-passphrase-12chars")
            assert False, "Should have raised exception"
        except Exception:
            pass

        # Still locked after wrong passphrase
        assert not mgr.is_unlocked("1.1")


def test_vault_session_timeout():
    """Test that sessions auto-expire after timeout."""
    if not _HAS_CRYPTOGRAPHY:
        print("  SKIP: cryptography not installed")
        return

    from hypernet.personal.vault import VaultManager, VaultSession

    with tempfile.TemporaryDirectory() as tmpdir:
        mgr = VaultManager(tmpdir, session_timeout=1)  # 1 second timeout
        mgr.create_vault("1.1", "test-passphrase-12chars")
        assert mgr.is_unlocked("1.1")

        # Wait for timeout
        time.sleep(1.5)

        # Should be expired
        assert not mgr.is_unlocked("1.1")


def test_vault_rate_limiting():
    """Test unlock attempt rate limiting."""
    if not _HAS_CRYPTOGRAPHY:
        print("  SKIP: cryptography not installed")
        return

    from hypernet.personal.vault import VaultManager, MAX_UNLOCK_ATTEMPTS

    with tempfile.TemporaryDirectory() as tmpdir:
        mgr = VaultManager(tmpdir)
        mgr.create_vault("1.1", "correct-passphrase-12chars")
        mgr.lock_vault("1.1")

        # Fail MAX_UNLOCK_ATTEMPTS times
        for i in range(MAX_UNLOCK_ATTEMPTS):
            try:
                mgr.unlock_vault("1.1", f"wrong-attempt-{i}-padding")
            except ValueError:
                # Locked out
                break
            except Exception:
                pass  # Wrong passphrase, expected

        # Next attempt should be locked out
        try:
            mgr.unlock_vault("1.1", "correct-passphrase-12chars")
            assert False, "Should be locked out"
        except ValueError as e:
            assert "locked out" in str(e).lower()


def test_vault_status():
    """Test vault status reporting."""
    if not _HAS_CRYPTOGRAPHY:
        print("  SKIP: cryptography not installed")
        return

    from hypernet.personal.vault import VaultManager

    with tempfile.TemporaryDirectory() as tmpdir:
        mgr = VaultManager(tmpdir)

        # No vault
        status = mgr.get_status("1.1")
        assert status["vault_exists"] is False
        assert status["unlocked"] is False

        # Create and unlock
        mgr.create_vault("1.1", "test-passphrase-12chars")
        status = mgr.get_status("1.1")
        assert status["vault_exists"] is True
        assert status["unlocked"] is True
        assert status["key_version"] == 1

        # Lock
        mgr.lock_vault("1.1")
        status = mgr.get_status("1.1")
        assert status["vault_exists"] is True
        assert status["unlocked"] is False


def test_vault_change_passphrase():
    """Test changing the vault passphrase."""
    if not _HAS_CRYPTOGRAPHY:
        print("  SKIP: cryptography not installed")
        return

    from hypernet.personal.vault import VaultManager

    with tempfile.TemporaryDirectory() as tmpdir:
        mgr = VaultManager(tmpdir)
        mgr.create_vault("1.1", "old-passphrase-12chars")
        mgr.lock_vault("1.1")

        # Change passphrase
        mgr.change_passphrase("1.1", "old-passphrase-12chars", "new-passphrase-12chars")

        # Old passphrase should fail
        try:
            mgr.unlock_vault("1.1", "old-passphrase-12chars")
            assert False, "Old passphrase should fail"
        except Exception:
            pass

        # New passphrase should work
        mgr.unlock_vault("1.1", "new-passphrase-12chars")
        assert mgr.is_unlocked("1.1")


def test_encrypted_store():
    """Test transparent encryption/decryption through EncryptedStore."""
    if not _HAS_CRYPTOGRAPHY:
        print("  SKIP: cryptography not installed")
        return

    from hypernet.personal.vault import VaultManager
    from hypernet.personal.encrypted_store import EncryptedStore
    from hypernet.store import Store
    from hypernet.node import Node
    from hypernet.address import HypernetAddress

    with tempfile.TemporaryDirectory() as tmpdir:
        store = Store(Path(tmpdir) / "data")
        vault_mgr = VaultManager(tmpdir)
        enc_store = EncryptedStore(store, vault_mgr)

        # Create and unlock vault
        vault_mgr.create_vault("1.1", "test-passphrase-12chars")

        # Write a personal node
        node = Node(
            address=HypernetAddress.parse("1.1.3.0.001"),
            data={"subject": "Test email", "body": "Secret content", "from": "someone@example.com"},
        )
        enc_store.put_node(node, user_ha="1.1")

        # Read it back — should be decrypted
        result = enc_store.get_node("1.1.3.0.001", user_ha="1.1")
        assert result is not None
        assert result.data["subject"] == "Test email"
        assert result.data["body"] == "Secret content"

        # Check raw store — should be encrypted
        raw = store.get_node(HypernetAddress.parse("1.1.3.0.001"))
        assert raw is not None
        assert raw.data.get("_encrypted") is True
        assert "_ciphertext" in raw.data

        # Lock vault and try to read
        vault_mgr.lock_vault("1.1")
        locked_result = enc_store.get_node("1.1.3.0.001", user_ha="1.1")
        assert locked_result is not None
        assert locked_result.data.get("_encrypted") is True
        assert locked_result.data.get("_locked") is True

        # System nodes should never be encrypted
        sys_node = Node(
            address=HypernetAddress.parse("0.5.1"),
            data={"name": "Person Object", "version": 1},
        )
        enc_store.put_node(sys_node, user_ha="1.1")
        raw_sys = store.get_node(HypernetAddress.parse("0.5.1"))
        assert raw_sys is not None
        assert raw_sys.data.get("_encrypted") is None  # NOT encrypted


def test_auth_register_with_ha():
    """Test registering a user with an explicit Hypernet Address."""
    from hypernet.auth import AuthService

    with tempfile.TemporaryDirectory() as tmpdir:
        auth = AuthService(tmpdir)

        # Register with explicit HA
        user = auth.register_with_ha(
            email="matt@schaeffer.org",
            password="test-password-12chars",
            display_name="Matt Schaeffer",
            ha="1.1",
        )
        assert user.ha == "1.1"
        assert user.email == "matt@schaeffer.org"
        assert user.permission_tier == 4  # DESTRUCTIVE

        # Verify can authenticate
        access, refresh = auth.authenticate("matt@schaeffer.org", "test-password-12chars")
        assert access
        assert refresh

        # Verify HA is preserved in token
        decoded_user = auth.get_user_from_token(access)
        assert decoded_user.ha == "1.1"


# --- Run without pytest ---

if __name__ == "__main__":
    tests = [
        test_vault_manager_lifecycle,
        test_vault_session_timeout,
        test_vault_rate_limiting,
        test_vault_status,
        test_vault_change_passphrase,
        test_encrypted_store,
        test_auth_register_with_ha,
    ]

    passed = 0
    failed = 0
    skipped = 0
    for test in tests:
        try:
            test()
            print(f"  PASS: {test.__name__}")
            passed += 1
        except Exception as e:
            if "SKIP" in str(e):
                print(f"  SKIP: {test.__name__}")
                skipped += 1
            else:
                print(f"  FAIL: {test.__name__} -- {e}")
                import traceback
                traceback.print_exc()
                failed += 1

    print(f"\n{passed} passed, {failed} failed, {skipped} skipped out of {len(tests)} tests")
    sys.exit(1 if failed else 0)

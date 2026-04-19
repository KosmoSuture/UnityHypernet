"""
Hypernet Vault API Routes

REST endpoints for vault lifecycle: create, unlock, lock, status,
change passphrase, backup key, and data migration.

All endpoints require JWT authentication (user must be logged in).
The user's Hypernet Address is extracted from the JWT token.

Architecture: Hypernet Docs/Hypernet_Technical_Architecture_With_Cover.docx.md §5
  - Lockers: encrypted containers (implemented by vault + encrypted_store)
  - Mandalas: access tokens for controlled sharing (future, built on this layer)
"""

from __future__ import annotations

import logging
from typing import Optional

log = logging.getLogger(__name__)

# Try to import FastAPI — module is usable without it for testing
try:
    from fastapi import APIRouter, Request, HTTPException
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False


# ── Request/Response Models ────────────────────────────────────────

if _HAS_FASTAPI:
    class PassphraseRequest(BaseModel):
        passphrase: str

    class ChangePassphraseRequest(BaseModel):
        old_passphrase: str
        new_passphrase: str

    class BackupRequest(BaseModel):
        backup_passphrase: str

    class MigrateRequest(BaseModel):
        prefix: Optional[str] = None  # Default: user's own HA


# ── Route Factory ──────────────────────────────────────────────────

def create_vault_router(vault_manager, encrypted_store=None):
    """Create FastAPI router for vault endpoints.

    Args:
        vault_manager: VaultManager instance
        encrypted_store: Optional EncryptedStore for migration endpoint
    """
    if not _HAS_FASTAPI:
        raise RuntimeError("FastAPI is required for vault routes")

    router = APIRouter(prefix="/vault", tags=["vault"])

    def _get_user_ha(request: Request) -> str:
        """Extract user's Hypernet Address from JWT-authenticated request."""
        user = getattr(request.state, "user", None)
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        return user.ha

    @router.get("/status")
    async def vault_status(request: Request):
        """Get vault status for the authenticated user."""
        ha = _get_user_ha(request)
        return vault_manager.get_status(ha)

    @router.post("/create", status_code=201)
    async def create_vault(request: Request, body: PassphraseRequest):
        """Create a new vault (first-time setup).

        Generates a fresh Data Encryption Key (DEK), encrypts it with a
        master key derived from the passphrase, and saves the KeyBundle.
        The passphrase is never stored.
        """
        ha = _get_user_ha(request)

        if vault_manager.vault_exists(ha):
            raise HTTPException(
                status_code=409,
                detail="Vault already exists. Use /vault/unlock to open it.",
            )

        try:
            vault_manager.create_vault(ha, body.passphrase)
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

        return {
            "message": "Vault created successfully",
            "ha": ha,
            "unlocked": True,
        }

    @router.post("/unlock")
    async def unlock_vault(request: Request, body: PassphraseRequest):
        """Unlock the vault with the passphrase.

        Derives the master key, decrypts the DEK, and holds it in
        server memory for the session. The passphrase is never stored.
        """
        ha = _get_user_ha(request)

        if not vault_manager.vault_exists(ha):
            raise HTTPException(
                status_code=404,
                detail="No vault found. Create one first with /vault/create.",
            )

        try:
            vault_manager.unlock_vault(ha, body.passphrase)
        except ValueError as e:
            # Rate limited / locked out
            raise HTTPException(status_code=429, detail=str(e))
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Vault key bundle not found")
        except Exception:
            # Wrong passphrase (InvalidTag from cryptography)
            raise HTTPException(status_code=401, detail="Incorrect passphrase")

        return {
            "message": "Vault unlocked",
            "ha": ha,
            "unlocked": True,
        }

    @router.post("/lock")
    async def lock_vault(request: Request):
        """Lock the vault (wipe DEK from memory)."""
        ha = _get_user_ha(request)
        vault_manager.lock_vault(ha)
        return {"message": "Vault locked", "ha": ha, "unlocked": False}

    @router.post("/change-passphrase")
    async def change_passphrase(request: Request, body: ChangePassphraseRequest):
        """Change the vault passphrase.

        Re-encrypts the DEK with a new master key. Existing encrypted
        data is unaffected (same DEK, different master key wrapping).
        """
        ha = _get_user_ha(request)

        try:
            vault_manager.change_passphrase(ha, body.old_passphrase, body.new_passphrase)
        except Exception:
            raise HTTPException(status_code=401, detail="Incorrect current passphrase")

        return {"message": "Passphrase changed successfully"}

    @router.post("/backup-key")
    async def create_backup(request: Request, body: BackupRequest):
        """Create a backup key with a separate recovery passphrase.

        Store this on a USB drive or print as a QR code.
        The vault must be unlocked.
        """
        ha = _get_user_ha(request)

        try:
            backup_path = vault_manager.create_backup(ha, body.backup_passphrase)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return {
            "message": "Backup key created",
            "backup_path": str(backup_path),
        }

    @router.post("/migrate")
    async def migrate_data(request: Request, body: MigrateRequest):
        """Encrypt existing unencrypted nodes under the user's address.

        One-time migration after vault creation. The vault must be unlocked.
        Preserves unencrypted versions in Store history.
        """
        if encrypted_store is None:
            raise HTTPException(
                status_code=501,
                detail="EncryptedStore not configured",
            )

        ha = _get_user_ha(request)
        prefix = body.prefix or ha

        # Security: only allow migrating your own data
        if not prefix.startswith(ha):
            raise HTTPException(
                status_code=403,
                detail="Can only migrate your own data",
            )

        try:
            results = encrypted_store.migrate_to_encrypted(prefix, ha)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return {
            "message": "Migration complete",
            "prefix": prefix,
            **results,
        }

    return router

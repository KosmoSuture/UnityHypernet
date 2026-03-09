"""
FastAPI routes for personal data integration.

Adds endpoints to the Hypernet server for:
- OAuth setup status
- Email account management
- Photo scanning and deduplication
- Import progress tracking

These endpoints power the swarm dashboard's data integration tab.
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/integrations", tags=["integrations"])

# Paths will be configured at startup
ARCHIVE_ROOT = None
PRIVATE_ROOT = None


def configure(archive_root: str, private_root: str):
    """Configure integration paths. Called during server startup."""
    global ARCHIVE_ROOT, PRIVATE_ROOT
    ARCHIVE_ROOT = Path(archive_root)
    PRIVATE_ROOT = Path(private_root)


def _get_private_root() -> Path:
    if PRIVATE_ROOT is None:
        raise HTTPException(500, "Integration paths not configured")
    return PRIVATE_ROOT


# === Status endpoints ===

@router.get("/status")
async def integration_status():
    """Overview of all integration connections."""
    private = _get_private_root()
    cred_dir = private / "credentials"
    token_dir = private / "oauth-tokens"

    accounts = {
        "matt@schaeffer.org": {"type": "imap", "status": "pending"},
        "spammelots@schaeffer.org": {"type": "imap", "status": "pending"},
        "matt.spamme@gmail.com": {"type": "gmail_oauth", "status": "pending"},
        "kosmicsuture@gmail.com": {"type": "gmail_oauth", "status": "pending"},
    }

    # Check which accounts have credentials
    for email_addr in accounts:
        cred_file = cred_dir / f"{email_addr}.json"
        if cred_file.exists():
            accounts[email_addr]["status"] = "configured"

    # Check Dropbox
    dropbox_token = token_dir / "dropbox.json"
    dropbox_status = "configured" if dropbox_token.exists() else "pending"

    # Check photo index
    photo_index = private / "import-staging" / "photos" / "_photo_index.json"
    photo_count = 0
    if photo_index.exists():
        import json
        data = json.loads(photo_index.read_text())
        photo_count = len(data)

    # Check OneDrive
    onedrive_token = token_dir / "onedrive.json"
    onedrive_status = "configured" if onedrive_token.exists() else "pending"

    # Check Microsoft app registration
    ms_app = cred_dir / "microsoft_app.json"
    if not ms_app.exists() and not onedrive_token.exists():
        onedrive_status = "not_configured"

    return {
        "email_accounts": accounts,
        "dropbox": {"status": dropbox_status},
        "onedrive": {"status": onedrive_status},
        "photos_indexed": photo_count,
        "private_dir_exists": private.exists(),
        "credentials_dir_exists": cred_dir.exists(),
        "connectors": ["email", "photos", "local_files", "dropbox", "onedrive",
                       "facebook_import", "linkedin_import", "google_photos_takeout"],
    }


# === Email endpoints ===

class ScanRequest(BaseModel):
    account: str
    max_messages: int = 100


@router.post("/email/scan")
async def scan_email(request: ScanRequest):
    """Scan an email account and return message summaries."""
    from .email_connector import EmailConnector, MATT_ACCOUNTS

    if request.account not in MATT_ACCOUNTS:
        raise HTTPException(400, f"Unknown account: {request.account}")

    connector = EmailConnector(str(ARCHIVE_ROOT), str(_get_private_root()))
    config = MATT_ACCOUNTS[request.account]

    try:
        summaries = connector.scan_mailbox(config, max_messages=request.max_messages)
        triage = connector.triage_messages(summaries)
        return {
            "account": request.account,
            "total_scanned": len(summaries),
            "triage": {k: len(v) for k, v in triage.items()},
            "important_subjects": [m["subject"] for m in triage["important"][:20]],
            "receipt_subjects": [m["subject"] for m in triage["receipts"][:20]],
        }
    except FileNotFoundError as e:
        raise HTTPException(401, str(e))
    except Exception as e:
        raise HTTPException(500, f"Scan failed: {e}")


# === Photo endpoints ===

class PhotoScanRequest(BaseModel):
    directory: str
    source: str = "local"
    recursive: bool = True


@router.post("/photos/scan")
async def scan_photos(request: PhotoScanRequest):
    """Scan a directory for photos and update the deduplication index."""
    from .photo_connector import PhotoScanner

    scanner = PhotoScanner(str(ARCHIVE_ROOT), str(_get_private_root()))

    try:
        stats = scanner.scan_directory(request.directory, request.source, request.recursive)
        return {
            "scan_result": stats,
            "index_stats": scanner.get_stats(),
        }
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Scan failed: {e}")


@router.get("/photos/stats")
async def photo_stats():
    """Get current photo index statistics."""
    from .photo_connector import PhotoScanner

    scanner = PhotoScanner(str(ARCHIVE_ROOT), str(_get_private_root()))
    return scanner.get_stats()


@router.post("/photos/find-duplicates")
async def find_photo_duplicates(threshold: int = 5):
    """Find near-duplicate photos using perceptual hashing."""
    from .photo_connector import PhotoScanner

    scanner = PhotoScanner(str(ARCHIVE_ROOT), str(_get_private_root()))
    dupes = scanner.find_near_duplicates(threshold=threshold)

    return {
        "near_duplicates": len(dupes),
        "pairs": [
            {
                "file1": scanner.index[sha1].filepath,
                "file2": scanner.index[sha2].filepath,
                "similarity": round((64 - dist) / 64 * 100, 1),
            }
            for sha1, sha2, dist in dupes[:100]  # limit response size
        ],
    }


# === OAuth setup endpoints ===

@router.get("/oauth/gmail/setup-url")
async def gmail_setup_url():
    """Get the URL to start Gmail OAuth setup."""
    return {
        "instructions": [
            "1. Create Google Cloud project at https://console.cloud.google.com/apis/credentials",
            "2. Enable Gmail API",
            "3. Create OAuth2 Desktop credentials",
            "4. Download client_secret.json",
            f"5. Save to: {_get_private_root() / 'credentials' / 'google_client_secret.json'}",
            "6. Run: python -m hypernet.integrations.oauth_setup gmail",
        ],
    }


@router.get("/oauth/dropbox/setup-url")
async def dropbox_setup_url():
    """Get the URL to start Dropbox OAuth setup."""
    return {
        "instructions": [
            "1. Create app at https://www.dropbox.com/developers/apps",
            "2. Choose: Scoped access, Full Dropbox",
            "3. Add redirect URI: http://localhost:8089",
            f"4. Save app_key and app_secret to: {_get_private_root() / 'credentials' / 'dropbox_app.json'}",
            "5. Run: python -m hypernet.integrations.oauth_setup dropbox",
        ],
    }


@router.get("/oauth/onedrive/setup-url")
async def onedrive_setup_url():
    """Get the URL to start OneDrive/Microsoft Graph OAuth setup."""
    return {
        "instructions": [
            "1. Register app at https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApplications",
            "2. Add redirect URI: http://localhost:8089",
            "3. Add API permissions: Files.Read, Files.Read.All, User.Read, offline_access",
            "4. Create client secret under Certificates & Secrets",
            f"5. Save client_id, client_secret, tenant_id to: {_get_private_root() / 'credentials' / 'microsoft_app.json'}",
            "6. Run: python -m hypernet.integrations.oauth_setup onedrive",
        ],
    }


# === Cloud storage scan endpoints ===

class CloudScanRequest(BaseModel):
    max_items: int = 1000
    since: str = ""  # ISO datetime string


@router.post("/dropbox/scan")
async def scan_dropbox(request: CloudScanRequest):
    """Scan Dropbox for files to import."""
    from .dropbox_connector import DropboxConnector
    from datetime import datetime, timezone

    connector = DropboxConnector(str(ARCHIVE_ROOT), str(_get_private_root()))
    auth = connector.authenticate()

    if auth.value not in ("authenticated", "configured"):
        raise HTTPException(401, f"Dropbox auth status: {auth.value}")

    since = None
    if request.since:
        since = datetime.fromisoformat(request.since)

    result = connector.scan(since=since, max_items=request.max_items)
    return result.summary()


@router.post("/onedrive/scan")
async def scan_onedrive(request: CloudScanRequest):
    """Scan OneDrive for files to import."""
    from .onedrive_connector import OneDriveConnector
    from datetime import datetime, timezone

    connector = OneDriveConnector(str(ARCHIVE_ROOT), str(_get_private_root()))
    auth = connector.authenticate()

    if auth.value not in ("authenticated", "configured"):
        raise HTTPException(401, f"OneDrive auth status: {auth.value}")

    since = None
    if request.since:
        since = datetime.fromisoformat(request.since)

    result = connector.scan(since=since, max_items=request.max_items)
    return result.summary()


@router.get("/connectors")
async def list_connectors():
    """List all available data connectors and their status."""
    private = _get_private_root()
    connectors = []

    # Email
    connectors.append({
        "name": "Email (Gmail/IMAP)",
        "type": "email",
        "status": "ready",
        "accounts": 4,
        "description": "Import from matt@schaeffer.org, spammelots@, matt.spamme@gmail, kosmicsuture@gmail",
    })

    # Dropbox
    dropbox_token = private / "oauth-tokens" / "dropbox.json"
    connectors.append({
        "name": "Dropbox",
        "type": "cloud_storage",
        "status": "configured" if dropbox_token.exists() else "needs_setup",
        "description": "Sync files from Dropbox with incremental cursor-based updates",
    })

    # OneDrive
    onedrive_token = private / "oauth-tokens" / "onedrive.json"
    connectors.append({
        "name": "OneDrive",
        "type": "cloud_storage",
        "status": "configured" if onedrive_token.exists() else "needs_setup",
        "description": "Sync files from OneDrive/Microsoft 365 with delta queries",
    })

    # Photos
    connectors.append({
        "name": "Photo Scanner",
        "type": "photo",
        "status": "ready",
        "description": "Scan local directories for photos with SHA-256 + perceptual hash dedup",
    })

    # Local Files
    connectors.append({
        "name": "Local File Scanner",
        "type": "local_file",
        "status": "ready",
        "description": "Import documents, code, and media from local directories",
    })

    # Export importers (manual)
    for name, desc in [
        ("Facebook Export", "Import from Facebook's 'Download Your Information' ZIP (JSON format)"),
        ("LinkedIn Export", "Import from LinkedIn's 'Download Your Data' ZIP (CSV format)"),
        ("Google Photos Takeout", "Import from Google Takeout photos ZIP with companion metadata"),
    ]:
        connectors.append({
            "name": name,
            "type": "export_import",
            "status": "ready",
            "description": desc,
        })

    return {"connectors": connectors, "total": len(connectors)}

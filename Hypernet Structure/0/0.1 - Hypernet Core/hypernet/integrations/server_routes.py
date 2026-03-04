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

    return {
        "email_accounts": accounts,
        "dropbox": {"status": dropbox_status},
        "photos_indexed": photo_count,
        "private_dir_exists": private.exists(),
        "credentials_dir_exists": cred_dir.exists(),
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

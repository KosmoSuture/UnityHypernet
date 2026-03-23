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
                       "facebook_import", "linkedin_import", "google_photos_takeout",
                       "google_location_history", "gedcom_genealogy"],
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

    # Google Maps Location History
    connectors.append({
        "name": "Google Maps Location History",
        "type": "export_import",
        "status": "ready",
        "description": "Import location history from Google Takeout — places visited, travel patterns, life timeline",
    })

    # GEDCOM/PAF Genealogy
    connectors.append({
        "name": "GEDCOM/PAF Genealogy",
        "type": "genealogy",
        "status": "ready",
        "description": "Import genealogy from GEDCOM (.ged) files — PAF, Ancestry, FamilySearch. Routes to 6 - People of History.",
    })

    # Multi-format genealogy (Gramps XML, CSV, DNA matches, GEDCOM 7.0)
    connectors.append({
        "name": "Multi-Format Genealogy (Gramps/CSV/DNA/GEDCOM 7)",
        "type": "genealogy",
        "status": "ready",
        "description": "Import from Gramps XML, generic CSV, Ancestry DNA matches, and FamilySearch GEDCOM 7.0. Includes deduplication engine.",
    })

    return {"connectors": connectors, "total": len(connectors)}


# === Google Maps Location History ===

class LocationImportRequest(BaseModel):
    path: str

@router.post("/location-history/import")
async def import_location_history(req: LocationImportRequest):
    """Import Google Maps location history from a Takeout export."""
    from .location_history import GoogleLocationImporter

    archive = str(ARCHIVE_ROOT) if ARCHIVE_ROOT else "."
    private = str(PRIVATE_ROOT) if PRIVATE_ROOT else archive

    importer = GoogleLocationImporter(archive, private)
    result = importer.import_export(req.path)

    return {
        "success": result.errors == [],
        "imported": result.imported,
        "skipped": result.skipped,
        "total": result.total,
        "details": result.details,
        "errors": result.errors[:10],
    }

@router.get("/location-history/summary")
async def location_history_summary():
    """Get location history summary if available."""
    private = Path(str(PRIVATE_ROOT)) if PRIVATE_ROOT else Path(".")
    summary_file = private / "data" / "timeline" / "location-summary.json"
    if summary_file.exists():
        import json
        return json.loads(summary_file.read_text(encoding="utf-8"))
    return {"status": "no_data", "message": "Import location history first"}

@router.get("/location-history/places")
async def location_frequent_places():
    """Get frequently visited places."""
    private = Path(str(PRIVATE_ROOT)) if PRIVATE_ROOT else Path(".")
    places_file = private / "data" / "places" / "frequent-places.json"
    if places_file.exists():
        import json
        return json.loads(places_file.read_text(encoding="utf-8"))
    return {"status": "no_data", "places": []}


# === GEDCOM/PAF Genealogy ===

class GenealogyImportRequest(BaseModel):
    path: str
    max_items: int = 0  # 0 = unlimited
    contributor_name: str = "Larry Anderson"  # Larry gets credit for PAF imports
    source_name: str = "PAF Database"


@router.post("/genealogy/import")
async def import_genealogy(req: GenealogyImportRequest):
    """Import genealogy data from a GEDCOM (.ged) file.

    Routes individuals to '6 - People of History' subcategories by era.
    Living people are flagged for privacy and routed to '1 - People' linking.
    Handles massive files (millions of records) via streaming parse.
    """
    from .genealogy_importer import GenealogyImporter

    archive = str(ARCHIVE_ROOT) if ARCHIVE_ROOT else "."
    private = str(PRIVATE_ROOT) if PRIVATE_ROOT else archive

    importer = GenealogyImporter(archive, private)
    ged_path = Path(req.path)

    if not ged_path.exists():
        raise HTTPException(404, f"GEDCOM file not found: {req.path}")

    if not ged_path.suffix.lower() in (".ged", ".gedcom"):
        raise HTTPException(400, "File must be a .ged or .gedcom file")

    try:
        result = importer.import_gedcom(
            req.path,
            max_items=req.max_items,
            contributor_name=req.contributor_name,
            source_name=req.source_name,
        )
        return {
            "success": len(result.errors) == 0,
            "summary": result.summary(),
            "stats": result.stats.summary() if result.stats else None,
            "errors": result.errors[:20],  # Limit error output
        }
    except Exception as e:
        raise HTTPException(500, f"Import failed: {e}")


@router.get("/genealogy/stats")
async def genealogy_stats():
    """Get statistics from the most recent genealogy import."""
    from .genealogy_importer import GenealogyImporter

    archive = str(ARCHIVE_ROOT) if ARCHIVE_ROOT else "."
    private = str(PRIVATE_ROOT) if PRIVATE_ROOT else archive

    importer = GenealogyImporter(archive, private)
    stats = importer.get_stats()

    if stats is None:
        return {"status": "no_data", "message": "No genealogy data imported yet. Use POST /api/v1/integrations/genealogy/import first."}

    return stats


@router.get("/genealogy/search")
async def genealogy_search(name: str = "", max_results: int = 50):
    """Search imported genealogy individuals by name.

    Args:
        name: Name or partial name to search for (surname, given name, etc.)
        max_results: Maximum results to return (default 50)
    """
    from .genealogy_importer import GenealogyImporter

    if not name or not name.strip():
        raise HTTPException(400, "Query parameter 'name' is required")

    archive = str(ARCHIVE_ROOT) if ARCHIVE_ROOT else "."
    private = str(PRIVATE_ROOT) if PRIVATE_ROOT else archive

    importer = GenealogyImporter(archive, private)
    results = importer.search(name.strip(), max_results=max_results)

    return {
        "query": name,
        "results": results,
        "total": len(results),
    }


# === Multi-Format Genealogy (dedup, merge, sources) ===
# These routes use the unified GenealogyStore and PersonMatcher from
# the multi-format extension in genealogy_importer.py.  The basic
# import/stats/search routes above handle the original GEDCOM workflow.
# These new routes add multi-format import, deduplication, and merge.

_genealogy_store = None


def _get_genealogy_store():
    """Lazy-load the GenealogyStore singleton."""
    global _genealogy_store
    if _genealogy_store is None:
        from .genealogy_importer import GenealogyStore
        private = _get_private_root()
        _genealogy_store = GenealogyStore(private / "genealogy")
        _genealogy_store.load()
    return _genealogy_store


class MultiFormatImportRequest(BaseModel):
    """Request body for multi-format genealogy import."""
    path: str
    source_label: str = ""
    auto_dedup: bool = True
    max_records: int = 0


class MergeRequest(BaseModel):
    """Request body for confirming a person merge."""
    record_id_a: str
    record_id_b: str


@router.post("/genealogy/import-multiformat")
async def import_multiformat_genealogy(req: MultiFormatImportRequest):
    """Import any genealogy format with auto-detection.

    Supports GEDCOM 5.x, GEDCOM 7.0 (FamilySearch), Gramps XML,
    generic CSV, and Ancestry DNA match CSV. Runs deduplication
    against existing records by default.
    """
    from .genealogy_importer import import_genealogy_file

    store = _get_genealogy_store()
    filepath = Path(req.path)

    if not filepath.exists():
        raise HTTPException(404, f"File not found: {req.path}")

    try:
        result = import_genealogy_file(
            filepath, store,
            source_label=req.source_label,
            auto_dedup=req.auto_dedup,
            max_records=req.max_records,
        )
        if result.get("success"):
            store.save()
        return result
    except Exception as e:
        raise HTTPException(500, f"Import failed: {e}")


@router.post("/genealogy/deduplicate")
async def genealogy_deduplicate():
    """Run deduplication across all imported genealogy data.

    Uses fuzzy matching on names (30%), dates (25%), places (20%),
    and family relationships (25%). Returns matches above 60% confidence.
    """
    store = _get_genealogy_store()
    matches = store.run_dedup()
    store.save()
    return {
        "total_matches": len(matches),
        "auto_merge": len([m for m in matches if m.decision == "auto_merge"]),
        "suggest_merge": len([m for m in matches if m.decision == "suggest_merge"]),
        "matches": [m.to_dict() for m in matches[:100]],
    }


@router.get("/genealogy/matches")
async def genealogy_matches():
    """Get potential duplicate matches pending human review."""
    store = _get_genealogy_store()
    pending = store.matcher.pending_matches
    return {
        "total_pending": len(pending),
        "matches": [m.to_dict() for m in pending[:100]],
    }


@router.post("/genealogy/merge")
async def genealogy_merge(req: MergeRequest):
    """Confirm and execute a merge between two person records.

    The first record (record_id_a) is treated as primary. Conflicting
    data from the secondary record is preserved as alternatives with
    source attribution.
    """
    store = _get_genealogy_store()
    result = store.confirm_merge(req.record_id_a, req.record_id_b)
    if "error" not in result:
        store.save()
    return result


@router.get("/genealogy/sources")
async def genealogy_sources():
    """List all genealogy import sources with contributor credits."""
    store = _get_genealogy_store()
    return {"sources": store.get_sources()}


@router.get("/genealogy/store-stats")
async def genealogy_store_stats():
    """Get statistics from the unified genealogy store.

    Shows totals by era, sex, source, and pending dedup matches.
    Complements /genealogy/stats which shows the last GEDCOM import.
    """
    store = _get_genealogy_store()
    return store.get_stats()


@router.get("/genealogy/store-search")
async def genealogy_store_search(
    name: str = "",
    birth_year: int = None,
    death_year: int = None,
    place: str = "",
    source: str = "",
    max_results: int = 50,
):
    """Search the unified genealogy store with multi-field filtering.

    Extends /genealogy/search with birth_year, death_year, place,
    and source filters. All filters are optional and combined with AND.
    """
    from typing import Optional as Opt
    store = _get_genealogy_store()
    results = store.search(
        name=name or None,
        birth_year=birth_year,
        death_year=death_year,
        place=place or None,
        source=source or None,
        max_results=max_results,
    )
    return {"total": len(results), "results": results}

"""
Hypernet MVP API
FastAPI backend for VR demo
Endpoints: Photos, Search, Timeline, AI Query, People, Links
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional, List
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import json
import os

from mvp_models import (
    Photo, Person, Event, Link, SearchRequest, SearchResult,
    TimelineRequest, AIQueryRequest, AIQueryResponse,
    ObjectType, PhotoWithLinks
)

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Hypernet API",
    description="Personal data operating system API",
    version="0.1.0"
)

# CORS for development (VR app running locally)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
DB_PATH = "hypernet.db"


# ============================================================================
# DATABASE CONNECTION
# ============================================================================

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def row_to_dict(row) -> dict:
    """Convert SQLite row to dictionary"""
    return dict(row) if row else None


def rows_to_list(rows) -> list:
    """Convert SQLite rows to list of dictionaries"""
    return [dict(row) for row in rows]


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Hypernet API",
        "version": "0.1.0",
        "endpoints": {
            "photos": "/photos",
            "search": "/search",
            "timeline": "/timeline",
            "ai": "/ai/query",
            "people": "/people",
            "links": "/links/{address}"
        }
    }


@app.get("/health")
def health_check(conn: sqlite3.Connection = Depends(get_db)):
    """Detailed health check with database stats"""
    cursor = conn.cursor()

    # Get counts
    cursor.execute("SELECT COUNT(*) as count FROM objects")
    total_objects = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM photos")
    total_photos = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM links")
    total_links = cursor.fetchone()['count']

    return {
        "status": "healthy",
        "database": "connected",
        "stats": {
            "total_objects": total_objects,
            "total_photos": total_photos,
            "total_links": total_links
        }
    }


# ============================================================================
# PHOTO ENDPOINTS
# ============================================================================

@app.get("/photos")
def get_photos(
    owner: str = Query("1.1", description="Owner Hypernet Address"),
    limit: int = Query(50, le=1000, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Get photos for an owner with optional date filtering"""

    cursor = conn.cursor()

    query = """
        SELECT
            o.hypernet_address,
            o.title,
            o.description,
            o.file_path,
            o.created_at,
            o.original_date,
            p.width,
            p.height,
            p.taken_at,
            p.latitude,
            p.longitude,
            p.location_name,
            p.camera_make,
            p.camera_model,
            p.thumbnail_large,
            p.ai_caption,
            p.ai_tags
        FROM objects o
        JOIN photos p ON o.id = p.object_id
        WHERE o.owner_address = ?
          AND o.status = 'active'
    """

    params = [owner]

    if start_date:
        query += " AND p.taken_at >= ?"
        params.append(start_date)

    if end_date:
        query += " AND p.taken_at <= ?"
        params.append(end_date)

    query += " ORDER BY p.taken_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    photos = rows_to_list(cursor.fetchall())

    # Parse JSON fields
    for photo in photos:
        if photo.get('ai_tags'):
            photo['ai_tags'] = json.loads(photo['ai_tags'])

    return {
        "count": len(photos),
        "photos": photos,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "next_offset": offset + limit if len(photos) == limit else None
        }
    }


@app.get("/photos/{address}")
def get_photo(
    address: str,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Get a single photo with full details and links"""

    cursor = conn.cursor()

    # Get photo
    cursor.execute("""
        SELECT
            o.*,
            p.width, p.height, p.orientation,
            p.camera_make, p.camera_model, p.lens_model,
            p.iso, p.aperture, p.shutter_speed, p.focal_length, p.flash,
            p.latitude, p.longitude, p.altitude, p.location_name,
            p.taken_at, p.thumbnail_small, p.thumbnail_medium, p.thumbnail_large,
            p.ai_caption, p.ai_tags, p.ai_detected_faces
        FROM objects o
        JOIN photos p ON o.id = p.object_id
        WHERE o.hypernet_address = ?
    """, (address,))

    photo = row_to_dict(cursor.fetchone())

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    # Parse JSON fields
    if photo.get('metadata'):
        photo['metadata'] = json.loads(photo['metadata'])
    if photo.get('ai_tags'):
        photo['ai_tags'] = json.loads(photo['ai_tags'])
    if photo.get('ai_detected_faces'):
        photo['ai_detected_faces'] = json.loads(photo['ai_detected_faces'])

    # Get people in photo
    cursor.execute("""
        SELECT p.*, o.title
        FROM links l
        JOIN people p ON l.target_address = p.hypernet_address
        JOIN objects o ON p.object_id = o.id
        WHERE l.source_address = ?
          AND l.link_type = 'depicts'
          AND l.status = 'active'
    """, (address,))

    people = rows_to_list(cursor.fetchall())

    # Get location
    cursor.execute("""
        SELECT loc.*, o.title
        FROM links l
        JOIN locations loc ON l.target_address = loc.hypernet_address
        JOIN objects o ON loc.object_id = o.id
        WHERE l.source_address = ?
          AND l.link_type = 'located_at'
          AND l.status = 'active'
    """, (address,))

    location = row_to_dict(cursor.fetchone())

    # Get events
    cursor.execute("""
        SELECT e.*, o.title
        FROM links l
        JOIN events e ON l.target_address = e.hypernet_address
        JOIN objects o ON e.object_id = o.id
        WHERE l.source_address = ?
          AND l.link_type = 'related_to'
          AND l.status = 'active'
    """, (address,))

    events = rows_to_list(cursor.fetchall())

    return {
        "photo": photo,
        "people": people,
        "location": location,
        "events": events
    }


@app.get("/photos/{address}/file")
def get_photo_file(
    address: str,
    size: str = Query("original", regex="^(original|large|medium|small)$"),
    conn: sqlite3.Connection = Depends(get_db)
):
    """Serve photo file (for VR to display)"""

    cursor = conn.cursor()

    if size == "original":
        cursor.execute("SELECT file_path FROM objects WHERE hypernet_address = ?", (address,))
    else:
        cursor.execute(f"SELECT thumbnail_{size} as file_path FROM photos WHERE hypernet_address = ?", (address,))

    result = cursor.fetchone()

    if not result or not result['file_path']:
        raise HTTPException(status_code=404, detail="Photo file not found")

    file_path = result['file_path']

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Photo file not found on disk")

    return FileResponse(file_path)


# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================

@app.post("/search")
def search(
    request: SearchRequest,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Full-text search across all objects"""

    cursor = conn.cursor()

    # Build query
    query = """
        SELECT
            o.hypernet_address,
            o.object_type,
            o.title,
            o.description,
            o.original_date,
            o.file_path,
            CASE
                WHEN o.object_type = 'photo' THEN p.thumbnail_large
                ELSE NULL
            END as thumbnail
        FROM objects_fts fts
        JOIN objects o ON fts.rowid = o.id
        LEFT JOIN photos p ON o.id = p.object_id
        WHERE objects_fts MATCH ?
    """

    params = [request.query]

    if request.owner_address:
        query += " AND o.owner_address = ?"
        params.append(request.owner_address)

    if request.object_types:
        placeholders = ','.join(['?'] * len(request.object_types))
        query += f" AND o.object_type IN ({placeholders})"
        params.extend([ot.value for ot in request.object_types])

    if request.start_date:
        query += " AND o.original_date >= ?"
        params.append(request.start_date.isoformat())

    if request.end_date:
        query += " AND o.original_date <= ?"
        params.append(request.end_date.isoformat())

    query += " AND o.status = 'active'"
    query += " ORDER BY rank LIMIT ? OFFSET ?"
    params.extend([request.limit, request.offset])

    cursor.execute(query, params)
    results = rows_to_list(cursor.fetchall())

    return {
        "query": request.query,
        "count": len(results),
        "results": results
    }


# ============================================================================
# TIMELINE ENDPOINTS
# ============================================================================

@app.post("/timeline")
def get_timeline(
    request: TimelineRequest,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Get timeline of objects sorted by date"""

    cursor = conn.cursor()

    query = """
        SELECT
            o.hypernet_address,
            o.object_type,
            o.title,
            o.description,
            o.original_date,
            o.file_path,
            CASE
                WHEN o.object_type = 'photo' THEN p.thumbnail_large
                WHEN o.object_type = 'person' THEN pe.profile_photo_address
                ELSE NULL
            END as thumbnail
        FROM objects o
        LEFT JOIN photos p ON o.object_type = 'photo' AND o.id = p.object_id
        LEFT JOIN people pe ON o.object_type = 'person' AND o.id = pe.object_id
        WHERE o.owner_address = ?
          AND o.status = 'active'
          AND o.original_date IS NOT NULL
    """

    params = [request.owner_address]

    if request.start_date:
        query += " AND o.original_date >= ?"
        params.append(request.start_date.isoformat())

    if request.end_date:
        query += " AND o.original_date <= ?"
        params.append(request.end_date.isoformat())

    if request.object_types:
        placeholders = ','.join(['?'] * len(request.object_types))
        query += f" AND o.object_type IN ({placeholders})"
        params.extend([ot.value for ot in request.object_types])

    query += " ORDER BY o.original_date DESC LIMIT ?"
    params.append(request.limit)

    cursor.execute(query, params)
    items = rows_to_list(cursor.fetchall())

    return {
        "count": len(items),
        "items": items
    }


# ============================================================================
# PEOPLE ENDPOINTS
# ============================================================================

@app.get("/people")
def get_people(
    owner: str = Query("1.1"),
    living_only: bool = Query(False),
    conn: sqlite3.Connection = Depends(get_db)
):
    """Get all people for an owner"""

    cursor = conn.cursor()

    query = """
        SELECT
            p.*,
            o.title,
            o.description,
            o.created_at
        FROM people p
        JOIN objects o ON p.object_id = o.id
        WHERE o.owner_address = ?
          AND o.status = 'active'
    """

    params = [owner]

    if living_only:
        query += " AND p.is_living = 1"

    query += " ORDER BY p.last_name, p.first_name"

    cursor.execute(query, params)
    people = rows_to_list(cursor.fetchall())

    return {
        "count": len(people),
        "people": people
    }


@app.get("/people/{address}")
def get_person(
    address: str,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Get a single person with details"""

    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.*, o.*
        FROM people p
        JOIN objects o ON p.object_id = o.id
        WHERE p.hypernet_address = ?
    """, (address,))

    person = row_to_dict(cursor.fetchone())

    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    # Get photos they're in
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM links l
        WHERE l.target_address = ?
          AND l.link_type = 'depicts'
          AND l.status = 'active'
    """, (address,))

    photo_count = cursor.fetchone()['count']
    person['photo_count'] = photo_count

    return person


# ============================================================================
# LINK ENDPOINTS
# ============================================================================

@app.get("/links/{address}")
def get_links(
    address: str,
    link_type: Optional[str] = None,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Get all links for an object"""

    cursor = conn.cursor()

    query = """
        SELECT
            l.hypernet_address as link_address,
            l.source_address,
            l.target_address,
            l.link_type,
            l.strength,
            l.context,
            os.title as source_title,
            os.object_type as source_type,
            ot.title as target_title,
            ot.object_type as target_type
        FROM links l
        JOIN objects os ON l.source_address = os.hypernet_address
        JOIN objects ot ON l.target_address = ot.hypernet_address
        WHERE (l.source_address = ? OR l.target_address = ?)
          AND l.status = 'active'
    """

    params = [address, address]

    if link_type:
        query += " AND l.link_type = ?"
        params.append(link_type)

    cursor.execute(query, params)
    links = rows_to_list(cursor.fetchall())

    return {
        "count": len(links),
        "links": links
    }


# ============================================================================
# AI ENDPOINTS
# ============================================================================

@app.post("/ai/query")
async def ai_query(
    request: AIQueryRequest,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Natural language query with AI"""

    import time
    start_time = time.time()

    # Simple keyword extraction for demo
    # In production, use proper NLP or LLM
    keywords = request.query.lower().split()

    # Search for relevant objects
    cursor = conn.cursor()

    # Try full-text search first
    cursor.execute("""
        SELECT
            o.hypernet_address,
            o.object_type,
            o.title,
            o.description,
            o.original_date,
            CASE
                WHEN o.object_type = 'photo' THEN p.thumbnail_large
                ELSE NULL
            END as thumbnail
        FROM objects_fts fts
        JOIN objects o ON fts.rowid = o.id
        LEFT JOIN photos p ON o.id = p.object_id
        WHERE objects_fts MATCH ?
          AND o.owner_address = ?
          AND o.status = 'active'
        ORDER BY rank
        LIMIT ?
    """, (request.query, request.owner_address, request.max_results))

    results = rows_to_list(cursor.fetchall())

    # Generate simple answer
    if results:
        answer = f"I found {len(results)} items related to '{request.query}'."

        # Add context based on object types
        types = {}
        for r in results:
            types[r['object_type']] = types.get(r['object_type'], 0) + 1

        type_summary = ", ".join([f"{count} {otype}(s)" for otype, count in types.items()])
        answer += f" Including: {type_summary}."
    else:
        answer = f"I couldn't find anything matching '{request.query}'. Try rephrasing your query."

    execution_time = (time.time() - start_time) * 1000  # Convert to ms

    return AIQueryResponse(
        answer=answer,
        sources=[SearchResult(**r, relevance_score=1.0) for r in results],
        query_interpretation=request.query,
        execution_time_ms=execution_time
    )


# ============================================================================
# STATS ENDPOINTS (for demo)
# ============================================================================

@app.get("/stats/{owner}")
def get_stats(
    owner: str = "1.1",
    conn: sqlite3.Connection = Depends(get_db)
):
    """Get statistics for demo dashboard"""

    cursor = conn.cursor()

    # Total objects
    cursor.execute("SELECT COUNT(*) as count FROM objects WHERE owner_address = ? AND status = 'active'", (owner,))
    total_objects = cursor.fetchone()['count']

    # Photos
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM objects o
        JOIN photos p ON o.id = p.object_id
        WHERE o.owner_address = ? AND o.status = 'active'
    """, (owner,))
    total_photos = cursor.fetchone()['count']

    # People
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM objects o
        JOIN people p ON o.id = p.object_id
        WHERE o.owner_address = ? AND o.status = 'active'
    """, (owner,))
    total_people = cursor.fetchone()['count']

    # Links
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM links l
        JOIN objects o ON l.source_address = o.hypernet_address
        WHERE o.owner_address = ? AND l.status = 'active'
    """, (owner,))
    total_links = cursor.fetchone()['count']

    # Date range of photos
    cursor.execute("""
        SELECT MIN(taken_at) as earliest, MAX(taken_at) as latest
        FROM photos p
        JOIN objects o ON p.object_id = o.id
        WHERE o.owner_address = ? AND o.status = 'active'
    """, (owner,))
    date_range = cursor.fetchone()

    return {
        "owner": owner,
        "total_objects": total_objects,
        "total_photos": total_photos,
        "total_people": total_people,
        "total_links": total_links,
        "photo_date_range": {
            "earliest": date_range['earliest'],
            "latest": date_range['latest']
        }
    }


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("=" * 80)
    print("HYPERNET API")
    print("=" * 80)
    print()
    print("Starting server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print()
    print("Endpoints:")
    print("  GET  /photos              - List photos")
    print("  GET  /photos/{address}    - Get photo details")
    print("  POST /search              - Full-text search")
    print("  POST /timeline            - Get timeline")
    print("  GET  /people              - List people")
    print("  POST /ai/query            - AI natural language query")
    print("  GET  /stats/{owner}       - Get statistics")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

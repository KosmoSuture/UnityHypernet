-- ============================================================================
-- HYPERNET MVP DATABASE SCHEMA
-- Purpose: Minimal viable schema for VR demo
-- Database: SQLite 3
-- Target: 6-week demo for funding
-- ============================================================================

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Objects Table: Universal storage for all Hypernet objects
CREATE TABLE objects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Hypernet Address (unique identifier)
    hypernet_address TEXT UNIQUE NOT NULL,

    -- Object type (photo, email, person, event, etc.)
    object_type TEXT NOT NULL,

    -- Status (active, archived, deleted)
    status TEXT DEFAULT 'active',

    -- Owner (which person this belongs to: 1.1, 1.2, etc.)
    owner_address TEXT NOT NULL,

    -- Title/Name (human-readable)
    title TEXT,

    -- Description/Content preview
    description TEXT,

    -- Privacy level (private, family, friends, professional, public, ai_access, legacy)
    privacy_level TEXT DEFAULT 'private',

    -- Timestamps
    created_at TEXT NOT NULL,  -- ISO 8601 format
    updated_at TEXT NOT NULL,

    -- Original creation date (for photos, emails, etc.)
    original_date TEXT,

    -- File path (if object has associated file)
    file_path TEXT,

    -- File size in bytes
    file_size INTEGER,

    -- MIME type
    mime_type TEXT,

    -- Metadata (JSON for flexible additional data)
    metadata TEXT,  -- JSON object

    -- Full-text search support
    search_text TEXT,

    -- Indexes for performance
    CHECK (privacy_level IN ('private', 'family', 'friends', 'professional', 'public', 'ai_access', 'legacy'))
);

-- Indexes for fast queries
CREATE INDEX idx_objects_ha ON objects(hypernet_address);
CREATE INDEX idx_objects_type ON objects(object_type);
CREATE INDEX idx_objects_owner ON objects(owner_address);
CREATE INDEX idx_objects_date ON objects(original_date);
CREATE INDEX idx_objects_status ON objects(status);
CREATE INDEX idx_objects_privacy ON objects(privacy_level);

-- Full-text search index
CREATE VIRTUAL TABLE objects_fts USING fts5(
    hypernet_address,
    title,
    description,
    search_text,
    content=objects,
    content_rowid=id
);

-- Triggers to keep FTS index updated
CREATE TRIGGER objects_fts_insert AFTER INSERT ON objects BEGIN
    INSERT INTO objects_fts(rowid, hypernet_address, title, description, search_text)
    VALUES (new.id, new.hypernet_address, new.title, new.description, new.search_text);
END;

CREATE TRIGGER objects_fts_update AFTER UPDATE ON objects BEGIN
    UPDATE objects_fts SET
        hypernet_address = new.hypernet_address,
        title = new.title,
        description = new.description,
        search_text = new.search_text
    WHERE rowid = new.id;
END;

CREATE TRIGGER objects_fts_delete AFTER DELETE ON objects BEGIN
    DELETE FROM objects_fts WHERE rowid = old.id;
END;


-- ============================================================================
-- Links Table: First-class relationships between objects
CREATE TABLE links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Links also get Hypernet Addresses
    hypernet_address TEXT UNIQUE NOT NULL,

    -- Source and target objects
    source_address TEXT NOT NULL,
    target_address TEXT NOT NULL,

    -- Link type (depicts, mentions, related_to, parent_of, located_at, etc.)
    link_type TEXT NOT NULL,

    -- Link strength (0.0 to 1.0, for ranking/sorting)
    strength REAL DEFAULT 1.0,

    -- Bidirectional flag
    bidirectional INTEGER DEFAULT 0,  -- 0=one-way, 1=two-way

    -- Context/description of the relationship
    context TEXT,

    -- Who created this link (user or system)
    created_by TEXT DEFAULT 'system',

    -- Timestamps
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    -- Status
    status TEXT DEFAULT 'active',

    -- Metadata (JSON)
    metadata TEXT,

    -- Foreign key constraints
    FOREIGN KEY (source_address) REFERENCES objects(hypernet_address),
    FOREIGN KEY (target_address) REFERENCES objects(hypernet_address),

    CHECK (strength >= 0.0 AND strength <= 1.0),
    CHECK (status IN ('active', 'archived', 'deleted'))
);

CREATE INDEX idx_links_source ON links(source_address);
CREATE INDEX idx_links_target ON links(target_address);
CREATE INDEX idx_links_type ON links(link_type);
CREATE INDEX idx_links_status ON links(status);


-- ============================================================================
-- SPECIFIC OBJECT TYPE TABLES (for MVP demo)
-- ============================================================================

-- Photos: Most important for demo
CREATE TABLE photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Reference to objects table
    object_id INTEGER UNIQUE NOT NULL,
    hypernet_address TEXT UNIQUE NOT NULL,

    -- Photo-specific metadata
    width INTEGER,
    height INTEGER,
    orientation INTEGER,  -- EXIF orientation

    -- Camera/device info
    camera_make TEXT,
    camera_model TEXT,
    lens_model TEXT,

    -- Photo settings
    iso INTEGER,
    aperture REAL,
    shutter_speed TEXT,
    focal_length REAL,
    flash INTEGER,  -- 0=no flash, 1=flash

    -- Location (if available from EXIF)
    latitude REAL,
    longitude REAL,
    altitude REAL,
    location_name TEXT,  -- Reverse geocoded

    -- Timestamps
    taken_at TEXT,  -- When photo was taken (EXIF)

    -- Thumbnails (paths to generated thumbnails)
    thumbnail_small TEXT,  -- 256x256
    thumbnail_medium TEXT, -- 512x512
    thumbnail_large TEXT,  -- 1024x1024

    -- AI-generated metadata
    ai_caption TEXT,
    ai_tags TEXT,  -- JSON array
    ai_detected_faces TEXT,  -- JSON array of face bounding boxes

    -- Computed hash (for duplicate detection)
    perceptual_hash TEXT,

    FOREIGN KEY (object_id) REFERENCES objects(id)
);

CREATE INDEX idx_photos_date ON photos(taken_at);
CREATE INDEX idx_photos_location ON photos(latitude, longitude);
CREATE INDEX idx_photos_hash ON photos(perceptual_hash);


-- People: Family members, contacts
CREATE TABLE people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Reference to objects table
    object_id INTEGER UNIQUE NOT NULL,
    hypernet_address TEXT UNIQUE NOT NULL,

    -- Basic identity
    first_name TEXT,
    middle_name TEXT,
    last_name TEXT,
    preferred_name TEXT,
    suffix TEXT,  -- Jr., Sr., III, etc.

    -- Dates
    birth_date TEXT,
    death_date TEXT,  -- NULL if alive

    -- Contact info
    email TEXT,
    phone TEXT,

    -- Relationships
    relationship_to_owner TEXT,  -- son, daughter, wife, friend, etc.

    -- Profile
    profile_photo_address TEXT,  -- Links to a photo object
    bio TEXT,

    -- Status
    is_living INTEGER DEFAULT 1,  -- 1=alive, 0=deceased

    -- For family members with Hypernet addresses
    is_hypernet_user INTEGER DEFAULT 0,

    FOREIGN KEY (object_id) REFERENCES objects(id)
);

CREATE INDEX idx_people_name ON people(last_name, first_name);
CREATE INDEX idx_people_living ON people(is_living);


-- Events: Birthdays, holidays, trips, etc.
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Reference to objects table
    object_id INTEGER UNIQUE NOT NULL,
    hypernet_address TEXT UNIQUE NOT NULL,

    -- Event details
    event_type TEXT,  -- birthday, holiday, trip, meeting, etc.

    -- When
    start_date TEXT NOT NULL,
    end_date TEXT,
    all_day INTEGER DEFAULT 0,

    -- Where
    location_name TEXT,
    latitude REAL,
    longitude REAL,

    -- Recurrence (for recurring events)
    recurrence_rule TEXT,  -- iCal RRULE format

    -- Attendees (JSON array of person addresses)
    attendees TEXT,

    FOREIGN KEY (object_id) REFERENCES objects(id)
);

CREATE INDEX idx_events_date ON events(start_date);
CREATE INDEX idx_events_type ON events(event_type);


-- Emails: For demo, just recent emails
CREATE TABLE emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Reference to objects table
    object_id INTEGER UNIQUE NOT NULL,
    hypernet_address TEXT UNIQUE NOT NULL,

    -- Email headers
    message_id TEXT UNIQUE,  -- RFC 2822 Message-ID
    subject TEXT,
    from_address TEXT,
    from_name TEXT,
    to_addresses TEXT,  -- JSON array
    cc_addresses TEXT,  -- JSON array
    bcc_addresses TEXT, -- JSON array

    -- Content
    body_plain TEXT,
    body_html TEXT,

    -- Metadata
    sent_at TEXT NOT NULL,
    received_at TEXT,

    -- Threading
    in_reply_to TEXT,  -- Message-ID of parent
    thread_id TEXT,

    -- Flags
    is_read INTEGER DEFAULT 0,
    is_starred INTEGER DEFAULT 0,
    is_archived INTEGER DEFAULT 0,

    -- Attachments (JSON array of file paths)
    attachments TEXT,

    FOREIGN KEY (object_id) REFERENCES objects(id)
);

CREATE INDEX idx_emails_date ON emails(sent_at);
CREATE INDEX idx_emails_from ON emails(from_address);
CREATE INDEX idx_emails_thread ON emails(thread_id);


-- Locations: Places referenced by other objects
CREATE TABLE locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Reference to objects table
    object_id INTEGER UNIQUE NOT NULL,
    hypernet_address TEXT UNIQUE NOT NULL,

    -- Location details
    name TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    postal_code TEXT,

    -- Coordinates
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,

    -- Type (home, work, restaurant, landmark, etc.)
    location_type TEXT,

    -- Visit tracking
    first_visit_date TEXT,
    last_visit_date TEXT,
    visit_count INTEGER DEFAULT 0,

    FOREIGN KEY (object_id) REFERENCES objects(id)
);

CREATE INDEX idx_locations_coords ON locations(latitude, longitude);
CREATE INDEX idx_locations_type ON locations(location_type);


-- ============================================================================
-- HYPERNET ADDRESS REGISTRY
-- ============================================================================

-- HA Registry: Track address allocation
CREATE TABLE ha_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- The full address
    hypernet_address TEXT UNIQUE NOT NULL,

    -- Address components
    category INTEGER NOT NULL,        -- 1 = People
    subcategory INTEGER,              -- 1 = Matt, 2 = Sarah, etc.
    type INTEGER,                     -- 8 = Media, 6 = Personal Data, etc.
    subtype INTEGER,                  -- 0 = Photos, 1 = Videos, etc.
    instance INTEGER,                 -- 00001-99999

    -- What object this address points to
    object_type TEXT NOT NULL,
    object_id INTEGER,

    -- Status
    status TEXT DEFAULT 'active',  -- active, reserved, deleted

    -- When allocated
    allocated_at TEXT NOT NULL,

    -- Notes
    notes TEXT,

    FOREIGN KEY (object_id) REFERENCES objects(id),
    CHECK (status IN ('active', 'reserved', 'deleted'))
);

CREATE INDEX idx_ha_registry_address ON ha_registry(hypernet_address);
CREATE INDEX idx_ha_registry_category ON ha_registry(category, subcategory, type);


-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Complete photo view with all metadata
CREATE VIEW v_photos_complete AS
SELECT
    o.hypernet_address,
    o.title,
    o.description,
    o.owner_address,
    o.privacy_level,
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
    p.ai_caption,
    p.ai_tags,
    p.thumbnail_large
FROM objects o
JOIN photos p ON o.id = p.object_id
WHERE o.status = 'active'
  AND o.object_type = 'photo';


-- All links from a given object
CREATE VIEW v_object_links AS
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
WHERE l.status = 'active';


-- People with their profile photos
CREATE VIEW v_people_with_photos AS
SELECT
    o.hypernet_address,
    p.first_name,
    p.last_name,
    p.preferred_name,
    p.relationship_to_owner,
    p.birth_date,
    p.is_living,
    p.profile_photo_address,
    po.file_path as profile_photo_path
FROM objects o
JOIN people p ON o.id = p.object_id
LEFT JOIN objects po ON p.profile_photo_address = po.hypernet_address
WHERE o.status = 'active';


-- ============================================================================
-- INITIAL DATA / SEED DATA
-- ============================================================================

-- Create the owner (Matt)
INSERT INTO objects (
    hypernet_address, object_type, owner_address, title,
    created_at, updated_at, privacy_level, status
) VALUES (
    '1.1', 'person', '1.1', 'Matt Schaeffer',
    datetime('now'), datetime('now'), 'private', 'active'
);

INSERT INTO people (
    object_id, hypernet_address, first_name, last_name,
    relationship_to_owner, is_living, is_hypernet_user
) VALUES (
    1, '1.1', 'Matt', 'Schaeffer',
    'self', 1, 1
);


-- Create family members (minimal for demo)
INSERT INTO objects (hypernet_address, object_type, owner_address, title, created_at, updated_at, privacy_level, status)
VALUES
    ('1.2', 'person', '1.1', 'Sarah Schaeffer', datetime('now'), datetime('now'), 'family', 'active'),
    ('1.3', 'person', '1.1', 'John Schaeffer', datetime('now'), datetime('now'), 'family', 'active'),
    ('1.4', 'person', '1.1', 'Bridget Schaeffer', datetime('now'), datetime('now'), 'family', 'active'),
    ('1.5', 'person', '1.1', 'Mark Schaeffer', datetime('now'), datetime('now'), 'family', 'active'),
    ('1.6', 'person', '1.1', 'Richard Schaeffer', datetime('now'), datetime('now'), 'family', 'active'),
    ('1.7', 'person', '1.1', 'Ollie Schaeffer', datetime('now'), datetime('now'), 'family', 'active');

INSERT INTO people (object_id, hypernet_address, first_name, last_name, relationship_to_owner, is_living, is_hypernet_user)
VALUES
    (2, '1.2', 'Sarah', 'Schaeffer', 'wife', 1, 1),
    (3, '1.3', 'John', 'Schaeffer', 'son', 1, 1),
    (4, '1.4', 'Bridget', 'Schaeffer', 'daughter', 1, 1),
    (5, '1.5', 'Mark', 'Schaeffer', 'son', 1, 1),
    (6, '1.6', 'Richard', 'Schaeffer', 'son', 1, 1),
    (7, '1.7', 'Ollie', 'Schaeffer', 'daughter', 1, 1);


-- ============================================================================
-- UTILITY FUNCTIONS / COMMON QUERIES (as comments for API implementation)
-- ============================================================================

-- Query: Get all photos for a person
-- SELECT * FROM v_photos_complete WHERE owner_address = '1.1' ORDER BY taken_at DESC;

-- Query: Get all links from a photo
-- SELECT * FROM v_object_links WHERE source_address = '1.1.8.0.00001';

-- Query: Full-text search
-- SELECT hypernet_address, title, description
-- FROM objects_fts
-- WHERE objects_fts MATCH 'christmas'
-- ORDER BY rank;

-- Query: Get photos within date range
-- SELECT * FROM v_photos_complete
-- WHERE taken_at BETWEEN '2023-12-01' AND '2023-12-31'
-- ORDER BY taken_at;

-- Query: Get photos near a location (within ~1km)
-- SELECT *,
--   (ABS(latitude - 47.6062) + ABS(longitude - (-122.3321))) as distance
-- FROM v_photos_complete
-- WHERE latitude IS NOT NULL
-- ORDER BY distance
-- LIMIT 50;

-- Query: Get all people linked to a photo
-- SELECT p.* FROM v_people_with_photos p
-- JOIN v_object_links l ON p.hypernet_address = l.target_address
-- WHERE l.source_address = '1.1.8.0.00001' AND l.link_type = 'depicts';

-- ============================================================================
-- PERFORMANCE NOTES
-- ============================================================================

-- For production, consider:
-- 1. PRAGMA journal_mode=WAL; (for better concurrency)
-- 2. PRAGMA synchronous=NORMAL; (faster writes)
-- 3. PRAGMA cache_size=-64000; (64MB cache)
-- 4. PRAGMA temp_store=MEMORY; (temp tables in RAM)
-- 5. Regular VACUUM; (defragment database)
-- 6. Regular ANALYZE; (update query planner statistics)

-- For VR demo, ensure queries return in < 100ms:
-- - Use indexes effectively
-- - Limit result sets (pagination)
-- - Precompute expensive queries
-- - Cache frequent queries
-- - Generate thumbnails in advance

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

-- Hypernet Core 0.1 - Initial Database Migration
-- PostgreSQL 15+
-- Run this script to create all tables and indexes

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==============================================================================
-- TRIGGER FUNCTION: Auto-update updated_at timestamp
-- ==============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- TABLE: users
-- ==============================================================================

CREATE TABLE users (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Authentication
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,

    -- Profile
    display_name VARCHAR(100),
    avatar_url VARCHAR(1024),

    -- Account Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Storage Quotas
    storage_used BIGINT NOT NULL DEFAULT 0,
    storage_quota BIGINT NOT NULL DEFAULT 10737418240, -- 10 GB in bytes

    -- Extensibility
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Indexes
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created_at ON users(created_at);

-- Trigger
CREATE TRIGGER users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE users IS 'User accounts and authentication';
COMMENT ON COLUMN users.storage_used IS 'Total bytes used by user media files';
COMMENT ON COLUMN users.storage_quota IS 'Maximum bytes allowed (default 10GB)';

-- ==============================================================================
-- TABLE: media
-- ==============================================================================

CREATE TABLE media (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Ownership
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Basic Info
    filename VARCHAR(255) NOT NULL,
    media_type VARCHAR(50) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,

    -- File Information
    size BIGINT NOT NULL,
    width INTEGER,
    height INTEGER,
    duration DOUBLE PRECISION,

    -- Storage
    file_path VARCHAR(1024) NOT NULL,
    thumbnail_path VARCHAR(1024),
    hash VARCHAR(64) NOT NULL,

    -- Dates and Location
    taken_at TIMESTAMP WITH TIME ZONE,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,

    -- Source Tracking
    source_type VARCHAR(50),
    source_id VARCHAR(255),

    -- Processing Status
    processing_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    thumbnail_generated BOOLEAN NOT NULL DEFAULT FALSE,
    metadata_extracted BOOLEAN NOT NULL DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Extensibility
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT chk_media_type CHECK (media_type IN ('photo', 'video', 'document', 'other')),
    CONSTRAINT chk_processing_status CHECK (processing_status IN ('pending', 'processing', 'complete', 'failed')),
    CONSTRAINT chk_latitude CHECK (latitude IS NULL OR (latitude >= -90 AND latitude <= 90)),
    CONSTRAINT chk_longitude CHECK (longitude IS NULL OR (longitude >= -180 AND longitude <= 180)),
    CONSTRAINT chk_size CHECK (size > 0)
);

-- Indexes
CREATE INDEX idx_media_user_id ON media(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_media_hash ON media(hash);
CREATE INDEX idx_media_taken_at ON media(taken_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_media_media_type ON media(media_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_media_source ON media(user_id, source_type, source_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_media_metadata ON media USING GIN(metadata);

-- Trigger
CREATE TRIGGER media_updated_at BEFORE UPDATE ON media
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE media IS 'Photos, videos, and other media files';
COMMENT ON COLUMN media.hash IS 'SHA-256 hash for deduplication';
COMMENT ON COLUMN media.metadata IS 'EXIF data, tags, descriptions, integration-specific data';

-- ==============================================================================
-- TABLE: albums
-- ==============================================================================

CREATE TABLE albums (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Ownership
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Basic Info
    name VARCHAR(200) NOT NULL,
    description TEXT,

    -- Display
    cover_media_id UUID REFERENCES media(id) ON DELETE SET NULL,
    sort_order VARCHAR(50) NOT NULL DEFAULT 'date_desc',

    -- Counts (denormalized)
    media_count INTEGER NOT NULL DEFAULT 0,

    -- Privacy
    visibility VARCHAR(50) NOT NULL DEFAULT 'private',

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Source Tracking
    source_type VARCHAR(50),
    source_id VARCHAR(255),

    -- Extensibility
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT chk_sort_order CHECK (sort_order IN ('date_asc', 'date_desc', 'manual')),
    CONSTRAINT chk_visibility CHECK (visibility IN ('private', 'unlisted', 'public')),
    CONSTRAINT chk_media_count CHECK (media_count >= 0)
);

-- Indexes
CREATE INDEX idx_albums_user_id ON albums(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_albums_name ON albums(user_id, name) WHERE deleted_at IS NULL;

-- Trigger
CREATE TRIGGER albums_updated_at BEFORE UPDATE ON albums
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE albums IS 'Collections of media objects';
COMMENT ON COLUMN albums.media_count IS 'Denormalized count of media in album (via links)';

-- ==============================================================================
-- TABLE: integrations
-- ==============================================================================

CREATE TABLE integrations (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Ownership
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Integration Details
    integration_type VARCHAR(50) NOT NULL,
    integration_name VARCHAR(200) NOT NULL,

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,

    -- OAuth2
    token_expires_at TIMESTAMP WITH TIME ZONE,

    -- Sync State
    last_sync_at TIMESTAMP WITH TIME ZONE,
    last_sync_status VARCHAR(50),
    sync_cursor TEXT,

    -- Statistics
    items_synced INTEGER NOT NULL DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Source Tracking
    source_type VARCHAR(50),
    source_id VARCHAR(255),

    -- Extensibility
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT chk_integration_status CHECK (status IN ('connected', 'disconnected', 'error', 'pending')),
    CONSTRAINT chk_sync_status CHECK (last_sync_status IS NULL OR last_sync_status IN ('success', 'partial', 'failed')),
    CONSTRAINT chk_items_synced CHECK (items_synced >= 0)
);

-- Indexes
CREATE INDEX idx_integrations_user_id ON integrations(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_integrations_type ON integrations(user_id, integration_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_integrations_status ON integrations(status) WHERE deleted_at IS NULL;

-- Trigger
CREATE TRIGGER integrations_updated_at BEFORE UPDATE ON integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE integrations IS 'Connected external services (Instagram, Google Photos, etc.)';
COMMENT ON COLUMN integrations.sync_cursor IS 'Pagination cursor for incremental sync';

-- ==============================================================================
-- TABLE: integration_secrets
-- ==============================================================================

CREATE TABLE integration_secrets (
    -- Identity (one-to-one with integrations)
    integration_id UUID PRIMARY KEY REFERENCES integrations(id) ON DELETE CASCADE,

    -- OAuth2 Tokens (consider encrypting these)
    access_token TEXT,
    refresh_token TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Trigger
CREATE TRIGGER integration_secrets_updated_at BEFORE UPDATE ON integration_secrets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE integration_secrets IS 'OAuth tokens and secrets (encrypted at rest)';
COMMENT ON COLUMN integration_secrets.access_token IS 'OAuth2 access token - should be encrypted';
COMMENT ON COLUMN integration_secrets.refresh_token IS 'OAuth2 refresh token - should be encrypted';

-- ==============================================================================
-- TABLE: links
-- ==============================================================================

CREATE TABLE links (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Ownership
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Link Endpoints
    from_object_id UUID NOT NULL,
    from_object_type VARCHAR(50) NOT NULL,
    to_object_id UUID NOT NULL,
    to_object_type VARCHAR(50) NOT NULL,

    -- Link Type
    link_type VARCHAR(50) NOT NULL,

    -- Link Properties
    strength DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    is_bidirectional BOOLEAN NOT NULL DEFAULT FALSE,

    -- Ordering
    sort_order INTEGER,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Source Tracking
    source_type VARCHAR(50),
    source_id VARCHAR(255),

    -- Extensibility
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT chk_link_type CHECK (link_type IN ('contains', 'source', 'duplicate_of', 'variant_of', 'related_to')),
    CONSTRAINT chk_strength CHECK (strength >= 0.0 AND strength <= 1.0),
    CONSTRAINT chk_not_self_link CHECK (
        from_object_id != to_object_id OR from_object_type != to_object_type
    )
);

-- Indexes
CREATE INDEX idx_links_user_id ON links(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_links_from ON links(from_object_id, link_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_links_to ON links(to_object_id, link_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_links_ordered ON links(from_object_id, sort_order)
    WHERE deleted_at IS NULL AND sort_order IS NOT NULL;

-- Unique constraint: No duplicate links
CREATE UNIQUE INDEX idx_links_unique ON links(from_object_id, to_object_id, link_type)
    WHERE deleted_at IS NULL;

-- Trigger
CREATE TRIGGER links_updated_at BEFORE UPDATE ON links
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE links IS 'Relationships between objects (first-class links)';
COMMENT ON COLUMN links.strength IS 'Confidence/strength of relationship (0.0 to 1.0)';
COMMENT ON COLUMN links.sort_order IS 'Position in ordered list (NULL if unordered)';

-- ==============================================================================
-- TABLE: refresh_tokens (JWT refresh token management)
-- ==============================================================================

CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    revoked_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash) WHERE revoked_at IS NULL;
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at) WHERE revoked_at IS NULL;

COMMENT ON TABLE refresh_tokens IS 'JWT refresh tokens for token rotation';
COMMENT ON COLUMN refresh_tokens.token_hash IS 'SHA-256 hash of refresh token';

-- ==============================================================================
-- TABLE: audit_log (security audit trail)
-- ==============================================================================

CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_resource ON audit_log(resource_type, resource_id);

COMMENT ON TABLE audit_log IS 'Security audit trail for all important actions';
COMMENT ON COLUMN audit_log.action IS 'Action performed (login, upload, delete, etc.)';

-- ==============================================================================
-- VIEWS: Convenience views for active (non-deleted) objects
-- ==============================================================================

CREATE VIEW active_media AS
SELECT * FROM media WHERE deleted_at IS NULL;

CREATE VIEW active_albums AS
SELECT * FROM albums WHERE deleted_at IS NULL;

CREATE VIEW active_links AS
SELECT * FROM links WHERE deleted_at IS NULL;

CREATE VIEW active_integrations AS
SELECT * FROM integrations WHERE deleted_at IS NULL;

COMMENT ON VIEW active_media IS 'Media objects that are not soft-deleted';
COMMENT ON VIEW active_albums IS 'Albums that are not soft-deleted';
COMMENT ON VIEW active_links IS 'Links that are not soft-deleted';
COMMENT ON VIEW active_integrations IS 'Integrations that are not soft-deleted';

-- ==============================================================================
-- INITIAL DATA (optional)
-- ==============================================================================

-- Create a test admin user (password: ChangeMe123!)
-- Password hash for "ChangeMe123!" using bcrypt
INSERT INTO users (email, password_hash, display_name, is_admin, email_verified)
VALUES (
    'admin@hypernet.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqXdz4.9Gu',
    'Admin User',
    TRUE,
    TRUE
);

-- ==============================================================================
-- DONE
-- ==============================================================================

-- Verify tables created
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;

COMMENT ON DATABASE hypernet IS 'Hypernet Core 0.1 - Universal VR Platform Database';

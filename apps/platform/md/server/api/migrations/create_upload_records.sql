-- Migration: Create upload_records table
-- Description: Store file upload records with tracking information
-- Database: PostgreSQL
-- Version: 1.0.0

-- Drop table if exists (for clean migration)
DROP TABLE IF EXISTS upload_records CASCADE;

-- Create upload_records table
CREATE TABLE upload_records (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- File identification
    file_id VARCHAR(36) NOT NULL UNIQUE,  -- UUID format
    filename VARCHAR(512) NOT NULL,         -- Original filename
    stored_filename VARCHAR(512) NOT NULL,  -- Timestamp-based storage filename
    file_path VARCHAR(1024) NOT NULL,       -- TOS relative path
    file_size BIGINT NOT NULL,              -- File size in bytes
    mime_type VARCHAR(128) NOT NULL,        -- MIME type (e.g., image/jpeg)

    -- Upload context
    package_name VARCHAR(256) NOT NULL,     -- App package name (e.g., com.jcoding.aiactivity)
    module_name VARCHAR(64) NOT NULL,       -- Module name (e.g., style, quiz, lottery)

    -- Uploader information
    uploader_fingerprint VARCHAR(128),      -- Browser/device fingerprint
    uploader_ip VARCHAR(45),                -- IP address (IPv4 or IPv6)
    uploader_user_agent TEXT,               -- User-Agent string

    -- Upload metadata
    upload_time BIGINT NOT NULL,            -- Unix timestamp (milliseconds)
    upload_status VARCHAR(16) NOT NULL,     -- 'success' or 'failed'
    error_message TEXT,                     -- Error message if failed
    oss_url TEXT,                           -- Complete TOS URL

    -- Constraints
    CONSTRAINT chk_upload_status CHECK (upload_status IN ('success', 'failed')),
    CONSTRAINT chk_file_size CHECK (file_size >= 0),
    CONSTRAINT chk_upload_time CHECK (upload_time > 0)
);

-- Create indexes for performance optimization

-- Index for package and module queries (composite)
CREATE INDEX idx_package_module ON upload_records(package_name, module_name);

-- Index for time-based queries (e.g., recent uploads)
CREATE INDEX idx_upload_time ON upload_records(upload_time DESC);

-- Index for uploader tracking (fingerprint-based queries)
CREATE INDEX idx_fingerprint ON upload_records(uploader_fingerprint);

-- Add comments for documentation
COMMENT ON TABLE upload_records IS 'Stores file upload records with tracking and metadata';

COMMENT ON COLUMN upload_records.id IS 'Auto-increment primary key';
COMMENT ON COLUMN upload_records.file_id IS 'Unique file identifier (UUID format)';
COMMENT ON COLUMN upload_records.filename IS 'Original filename from uploader';
COMMENT ON COLUMN upload_records.stored_filename IS 'Server-side storage filename (timestamp-based)';
COMMENT ON COLUMN upload_records.file_path IS 'Relative path in TOS storage';
COMMENT ON COLUMN upload_records.file_size IS 'File size in bytes';
COMMENT ON COLUMN upload_records.mime_type IS 'MIME type of the file';
COMMENT ON COLUMN upload_records.package_name IS 'Application package name (e.g., com.jcoding.aiactivity)';
COMMENT ON COLUMN upload_records.module_name IS 'Module identifier (e.g., style, quiz, lottery)';
COMMENT ON COLUMN upload_records.uploader_fingerprint IS 'Browser/device fingerprint for tracking';
COMMENT ON COLUMN upload_records.uploader_ip IS 'Uploader IP address (supports IPv4 and IPv6)';
COMMENT ON COLUMN upload_records.uploader_user_agent IS 'User-Agent string from request';
COMMENT ON COLUMN upload_records.upload_time IS 'Upload timestamp in milliseconds (Unix epoch)';
COMMENT ON COLUMN upload_records.upload_status IS 'Upload status: success or failed';
COMMENT ON COLUMN upload_records.error_message IS 'Error details if upload failed';
COMMENT ON COLUMN upload_records.oss_url IS 'Complete TOS access URL';

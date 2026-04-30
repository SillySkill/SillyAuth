# ============================================
# SillyMD Backend - Database Init Script
# ============================================

-- Create database (if not exists)
-- Note: This is handled by Docker entrypoint

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- Create functions
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_skills_skill_id ON skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_skills_author_id ON skills(author_id);
CREATE INDEX IF NOT EXISTS idx_skills_category_type_status ON skills(category, type, status) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_skills_published_featured ON skills(published_at DESC) WHERE is_featured = TRUE AND status = 'approved';

CREATE INDEX IF NOT EXISTS idx_reviews_skill_id ON reviews(skill_id);
CREATE INDEX IF NOT EXISTS idx_reviews_created_at ON reviews(created_at DESC);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_skills_fulltext ON skills
USING gin(to_tsvector('simple', name || ' ' || COALESCE(description, '')))
WHERE is_deleted = FALSE AND status = 'approved';

-- Insert default admin user (password: admin123)
-- Password hash is bcrypt for "admin123"
INSERT INTO users (username, email, password_hash, role, is_active, is_verified)
VALUES ('admin', 'admin@sillymd.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzW5qXlq1a', 'admin', TRUE, TRUE)
ON CONFLICT (username) DO NOTHING;

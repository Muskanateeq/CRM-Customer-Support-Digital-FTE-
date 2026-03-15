-- Migration: Fix Better Auth Account Table for OAuth
-- Date: 2026-03-06
-- Issue: Missing columns causing Google OAuth to fail with error 42703

-- ============================================
-- Add Missing Columns to Account Table
-- ============================================

-- Add scope column for OAuth scopes
ALTER TABLE account
ADD COLUMN IF NOT EXISTS scope TEXT;

-- Add separate expiration columns for access and refresh tokens
ALTER TABLE account
ADD COLUMN IF NOT EXISTS "accessTokenExpiresAt" TIMESTAMP;

ALTER TABLE account
ADD COLUMN IF NOT EXISTS "refreshTokenExpiresAt" TIMESTAMP;

-- Migrate existing expiresAt data to accessTokenExpiresAt
UPDATE account
SET "accessTokenExpiresAt" = "expiresAt"
WHERE "expiresAt" IS NOT NULL AND "accessTokenExpiresAt" IS NULL;

-- Drop old expiresAt column (if it exists and is now redundant)
-- Uncomment the line below if you want to remove the old column
-- ALTER TABLE account DROP COLUMN IF EXISTS "expiresAt";

-- ============================================
-- Verify Schema
-- ============================================
DO $$
DECLARE
    col_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns
    WHERE table_name = 'account'
    AND column_name IN ('scope', 'accessTokenExpiresAt', 'refreshTokenExpiresAt');

    IF col_count = 3 THEN
        RAISE NOTICE '✅ Migration successful! Added 3 columns to account table.';
        RAISE NOTICE '   - scope (TEXT)';
        RAISE NOTICE '   - accessTokenExpiresAt (TIMESTAMP)';
        RAISE NOTICE '   - refreshTokenExpiresAt (TIMESTAMP)';
    ELSE
        RAISE WARNING '⚠️  Migration incomplete. Expected 3 columns, found %', col_count;
    END IF;
END $$;

-- ============================================
-- Display Updated Schema
-- ============================================
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'account'
ORDER BY ordinal_position;

-- Add missing accessTokenExpiresAt column to account table
-- This column is required by Better Auth for OAuth token expiration tracking

ALTER TABLE account
ADD COLUMN IF NOT EXISTS "accessTokenExpiresAt" TIMESTAMP;

-- Add index for better query performance
CREATE INDEX IF NOT EXISTS idx_account_access_token_expires ON account("accessTokenExpiresAt");

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Added accessTokenExpiresAt column to account table';
END $$;

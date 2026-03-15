"""
Database Migration: Add Activity Tracking and Soft Delete

This migration adds:
1. activities table for tracking user actions
2. deleted_at column to tasks table for soft delete

Run this migration after deploying the code changes.
"""

# SQL Migration Script
MIGRATION_SQL = """
-- Step 1: Add deleted_at column to tasks table
ALTER TABLE tasks
ADD COLUMN deleted_at TIMESTAMP NULL;

CREATE INDEX idx_tasks_deleted_at ON tasks(deleted_at);

-- Step 2: Create activities table
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    meta JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_activities_user FOREIGN KEY (user_id)
        REFERENCES "user"(id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX idx_activities_user_id ON activities(user_id);
CREATE INDEX idx_activities_type ON activities(type);
CREATE INDEX idx_activities_created_at ON activities(created_at DESC);

-- Step 3: Add comments
COMMENT ON TABLE activities IS 'User activity log for history tracking';
COMMENT ON COLUMN activities.type IS 'Activity type: created, updated, deleted, completed, uncompleted, restored';
COMMENT ON COLUMN activities.meta IS 'Additional data: task_id, task_name, changes, etc.';
COMMENT ON COLUMN tasks.deleted_at IS 'Soft delete timestamp (NULL if not deleted)';
"""

# Rollback script (if needed)
ROLLBACK_SQL = """
-- Rollback: Remove activities table and deleted_at column
DROP TABLE IF EXISTS activities CASCADE;
ALTER TABLE tasks DROP COLUMN IF EXISTS deleted_at;
"""

if __name__ == "__main__":
    print("=" * 80)
    print("DATABASE MIGRATION: Activity Tracking and Soft Delete")
    print("=" * 80)
    print("\nThis migration adds:")
    print("  1. activities table for tracking user actions")
    print("  2. deleted_at column to tasks table for soft delete")
    print("\nTo apply this migration:")
    print("  1. Connect to your Neon database")
    print("  2. Run the SQL commands below")
    print("  3. Verify the changes")
    print("\n" + "=" * 80)
    print("MIGRATION SQL:")
    print("=" * 80)
    print(MIGRATION_SQL)
    print("\n" + "=" * 80)
    print("ROLLBACK SQL (if needed):")
    print("=" * 80)
    print(ROLLBACK_SQL)

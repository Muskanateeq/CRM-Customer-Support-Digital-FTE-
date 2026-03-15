# Database Setup Scripts

This directory contains scripts for setting up and managing the TaskNest database.

## Files

### 1. `schema.sql`
Complete database schema with all tables, indexes, triggers, and views.

**Tables:**
- `customers` - Master customer records
- `customer_identifiers` - Cross-channel customer identification
- `conversations` - Conversation tracking across channels
- `messages` - All messages (inbound/outbound)
- `tickets` - Support ticket system
- `knowledge_base` - Product documentation with vector embeddings
- `agent_metrics` - AI agent performance tracking
- `channel_configs` - Channel-specific configuration

**Features:**
- UUID primary keys
- Proper foreign key relationships
- Indexes for performance
- Vector similarity search (pgvector)
- Auto-updating timestamps
- Useful views for common queries

### 2. `setup_database.sh`
Automated database setup script.

**What it does:**
1. Tests database connection
2. Creates all tables and indexes
3. Populates knowledge base with context files
4. Verifies setup

**Usage:**
```bash
cd backend/scripts
./setup_database.sh
```

**Requirements:**
- PostgreSQL client (`psql`) installed
- `.env` file with `DATABASE_URL` configured
- Python 3.8+ for knowledge base population

### 3. `populate_knowledge_base.py`
Python script to populate the knowledge base table with context files.

**What it does:**
1. Reads all context files from `context/` directory
2. Parses and splits content into sections
3. Inserts into `knowledge_base` table
4. Shows summary of inserted entries

**Usage:**
```bash
cd backend/scripts
python3 populate_knowledge_base.py
```

**Context files loaded:**
- `company-profile.md` - Company information
- `product-docs.md` - Product documentation
- `escalation-rules.md` - Escalation guidelines
- `brand-voice.md` - Communication style

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
cd backend/scripts
./setup_database.sh
```

### Option 2: Manual Setup
```bash
# 1. Create schema
psql $DATABASE_URL -f schema.sql

# 2. Populate knowledge base
python3 populate_knowledge_base.py
```

## Environment Variables

Required in `.env` file:
```bash
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
```

## Verification

After setup, verify tables were created:
```bash
psql $DATABASE_URL -c "\dt"
```

Check knowledge base entries:
```bash
psql $DATABASE_URL -c "SELECT category, COUNT(*) FROM knowledge_base GROUP BY category;"
```

## Troubleshooting

### Connection Failed
- Check `DATABASE_URL` in `.env` file
- Verify database is accessible
- Check firewall/network settings

### Schema Creation Failed
- Ensure PostgreSQL 14+ is being used
- Check if `pgvector` extension is available
- Verify user has CREATE permissions

### Knowledge Base Population Failed
- Ensure context files exist in `context/` directory
- Check Python dependencies: `pip install asyncpg python-dotenv`
- Verify database connection

## Maintenance

### Reset Database
```bash
# Drop all tables (CAUTION: This deletes all data!)
psql $DATABASE_URL -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Re-run setup
./setup_database.sh
```

### Update Knowledge Base
```bash
# Re-populate knowledge base with latest context files
python3 populate_knowledge_base.py
```

### Backup Database
```bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
psql $DATABASE_URL < backup_20260301.sql
```

## Next Steps

After database setup:

1. **Start API Server:**
   ```bash
   cd backend/src
   uvicorn api.main:app --reload
   ```

2. **Start Workers:**
   ```bash
   cd backend/src
   python workers/service.py
   ```

3. **Test API:**
   ```bash
   curl http://localhost:8000/health
   ```

4. **Generate Embeddings:**
   ```bash
   cd backend/src
   python embeddings/generate_embeddings.py
   ```

## Schema Migrations

For future schema changes, create migration files:

```bash
backend/scripts/migrations/
  001_initial_schema.sql
  002_add_agent_metrics.sql
  003_add_channel_configs.sql
```

Run migrations in order:
```bash
for file in migrations/*.sql; do
  psql $DATABASE_URL -f $file
done
```

#!/bin/bash
# ============================================
# TaskNest Database Setup Script
# ============================================
# This script sets up the complete database schema
# and populates it with initial data
# ============================================

set -e  # Exit on error

echo "============================================"
echo "TaskNest Database Setup"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Please create .env file with DATABASE_URL"
    exit 1
fi

# Load environment variables
export $(cat ../.env | grep -v '^#' | xargs)

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ Error: DATABASE_URL not set in .env${NC}"
    exit 1
fi

echo -e "${YELLOW}📊 Database URL: ${DATABASE_URL%%@*}@***${NC}"
echo ""

# Step 1: Test database connection
echo -e "${YELLOW}🔍 Step 1: Testing database connection...${NC}"
if psql "$DATABASE_URL" -c "SELECT version();" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database connection successful${NC}"
else
    echo -e "${RED}❌ Failed to connect to database${NC}"
    echo "Please check your DATABASE_URL in .env file"
    exit 1
fi
echo ""

# Step 2: Run schema
echo -e "${YELLOW}🗄️  Step 2: Creating database schema...${NC}"
if psql "$DATABASE_URL" -f schema.sql > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database schema created successfully${NC}"
else
    echo -e "${RED}❌ Failed to create schema${NC}"
    exit 1
fi
echo ""

# Step 3: Verify tables
echo -e "${YELLOW}🔍 Step 3: Verifying tables...${NC}"
TABLES=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
echo -e "${GREEN}✅ Created $TABLES tables${NC}"
echo ""

# Step 4: Populate knowledge base
echo -e "${YELLOW}📚 Step 4: Populating knowledge base...${NC}"
if command -v python3 &> /dev/null; then
    if python3 populate_knowledge_base.py; then
        echo -e "${GREEN}✅ Knowledge base populated${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: Failed to populate knowledge base${NC}"
        echo "You can run 'python3 populate_knowledge_base.py' manually later"
    fi
else
    echo -e "${YELLOW}⚠️  Python3 not found, skipping knowledge base population${NC}"
    echo "Run 'python3 populate_knowledge_base.py' manually to populate knowledge base"
fi
echo ""

# Step 5: Show summary
echo "============================================"
echo -e "${GREEN}🎉 Database Setup Complete!${NC}"
echo "============================================"
echo ""
echo "Database Tables Created:"
psql "$DATABASE_URL" -c "\dt" 2>/dev/null || echo "  (Run '\dt' in psql to see tables)"
echo ""
echo "Next Steps:"
echo "  1. Start the API server: cd ../src && uvicorn api.main:app --reload"
echo "  2. Start the workers: cd ../src && python workers/service.py"
echo "  3. Test the API: curl http://localhost:8000/health"
echo ""
echo "============================================"

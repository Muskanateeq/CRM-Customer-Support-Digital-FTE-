#!/bin/bash

# TaskNest - UV Setup Script
# Fast Python package management with uv

set -e

echo "========================================"
echo "TaskNest - UV Setup"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}uv is not installed. Installing...${NC}"

    # Install uv
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # Windows
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    else
        # Linux/Mac
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi

    echo -e "${GREEN}✓ uv installed successfully${NC}"
else
    echo -e "${GREEN}✓ uv is already installed${NC}"
    uv --version
fi

echo ""
echo "========================================"
echo "Initializing Python Environment"
echo "========================================"
echo ""

# Create virtual environment with uv
echo "Creating virtual environment..."
uv venv

echo -e "${GREEN}✓ Virtual environment created${NC}"

echo ""
echo "========================================"
echo "Installing Dependencies"
echo "========================================"
echo ""

# Install dependencies
echo "Installing project dependencies..."
uv pip install -e .

echo -e "${GREEN}✓ Dependencies installed${NC}"

echo ""
echo "========================================"
echo "Installing Development Dependencies"
echo "========================================"
echo ""

# Install dev dependencies
echo "Installing development dependencies..."
uv pip install -e ".[dev]"

echo -e "${GREEN}✓ Development dependencies installed${NC}"

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To activate the virtual environment:"
echo ""
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "  .venv\\Scripts\\activate"
else
    echo "  source .venv/bin/activate"
fi
echo ""
echo "To install packages with uv:"
echo "  uv pip install <package>"
echo ""
echo "To sync dependencies:"
echo "  uv pip sync"
echo ""
echo "To run tests:"
echo "  python test_module1.py"
echo "  python test_module6.py"
echo "  python test_module7.py"
echo ""
echo -e "${GREEN}Ready to go!${NC}"

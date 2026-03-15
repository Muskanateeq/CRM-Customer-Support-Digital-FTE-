# TaskNest - UV Setup Script (Windows)
# Fast Python package management with uv

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TaskNest - UV Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if uv is installed
$uvInstalled = Get-Command uv -ErrorAction SilentlyContinue

if (-not $uvInstalled) {
    Write-Host "uv is not installed. Installing..." -ForegroundColor Yellow

    # Install uv
    irm https://astral.sh/uv/install.ps1 | iex

    Write-Host "✓ uv installed successfully" -ForegroundColor Green
} else {
    Write-Host "✓ uv is already installed" -ForegroundColor Green
    uv --version
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Initializing Python Environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create virtual environment with uv
Write-Host "Creating virtual environment..."
uv venv

Write-Host "✓ Virtual environment created" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installing Dependencies" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Install dependencies
Write-Host "Installing project dependencies..."
uv pip install -e .

Write-Host "✓ Dependencies installed" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installing Development Dependencies" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Install dev dependencies
Write-Host "Installing development dependencies..."
uv pip install -e ".[dev]"

Write-Host "✓ Development dependencies installed" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To activate the virtual environment:"
Write-Host "  .venv\Scripts\activate" -ForegroundColor Yellow
Write-Host ""
Write-Host "To install packages with uv:"
Write-Host "  uv pip install <package>" -ForegroundColor Yellow
Write-Host ""
Write-Host "To sync dependencies:"
Write-Host "  uv pip sync" -ForegroundColor Yellow
Write-Host ""
Write-Host "To run tests:"
Write-Host "  python test_module1.py" -ForegroundColor Yellow
Write-Host "  python test_module6.py" -ForegroundColor Yellow
Write-Host "  python test_module7.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "Ready to go!" -ForegroundColor Green

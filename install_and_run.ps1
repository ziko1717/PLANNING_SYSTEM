# File: install_and_run.ps1
# Industrial Planning System - Windows Installation Script

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Industrial Planning System Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check Python installation
Write-Host "`nChecking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion detected" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
python -m venv planning_env
.\planning_env\Scripts\Activate.ps1
Write-Host "✓ Virtual environment created" -ForegroundColor Green

# Upgrade pip
Write-Host "`nUpgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install packages
Write-Host "`nInstalling required packages..." -ForegroundColor Yellow
pip install numpy scipy pandas --quiet
Write-Host "✓ Packages installed successfully" -ForegroundColor Green

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Yellow
python -c "import numpy; import scipy; import pandas; print('All packages OK')"
Write-Host "✓ All packages verified" -ForegroundColor Green

# Run the script
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Running Industrial Planning System..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
python industrial_planner.py

# Deactivate
deactivate
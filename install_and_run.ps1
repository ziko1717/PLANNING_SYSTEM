# File: install_and_run.ps1
# Industrial Planning System - Windows Installation Script

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Industrial Planning System Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Python detected" -ForegroundColor Green
} else {
    Write-Host "ERROR: Python is not installed" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv planning_env
Write-Host "Virtual environment created" -ForegroundColor Green

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\planning_env\Scripts\Activate.ps1
Write-Host "Virtual environment activated" -ForegroundColor Green

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "Pip upgraded" -ForegroundColor Green

# Install packages
Write-Host "Installing required packages..." -ForegroundColor Yellow
pip install numpy scipy pandas --quiet
Write-Host "Packages installed successfully" -ForegroundColor Green

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Yellow
python -c "import numpy; import scipy; import pandas; print('All packages OK')"
Write-Host "All packages verified" -ForegroundColor Green

# Check if script file exists
if (-not (Test-Path "industrial_planner.py")) {
    Write-Host "ERROR: industrial_planner.py not found!" -ForegroundColor Red
    Write-Host "Please ensure the script is in the same directory" -ForegroundColor Yellow
    deactivate
    exit 1
}

# Run the script
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Running Industrial Planning System..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
python industrial_planner.py

# Deactivate virtual environment
Write-Host "Cleaning up..." -ForegroundColor Yellow
deactivate
Write-Host "Virtual environment deactivated" -ForegroundColor Green
Write-Host "Script completed!" -ForegroundColor Cyan
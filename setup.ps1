# LabWise AI - Setup Script for Windows
# This script sets up the development environment

Write-Host "🧬 LabWise AI - Setup Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.9 or higher." -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 16 or higher." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists." -ForegroundColor Cyan
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
pip install -r requirements.txt
Write-Host "✓ Python dependencies installed" -ForegroundColor Green

# Initialize database
Write-Host ""
Write-Host "Initializing database..." -ForegroundColor Yellow
python -m app.db.init_db
Write-Host "✓ Database initialized" -ForegroundColor Green

# Install frontend dependencies
Write-Host ""
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
Set-Location ..
Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green

# Check Ollama
Write-Host ""
Write-Host "Checking Ollama installation..." -ForegroundColor Yellow
try {
    $ollamaCheck = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✓ Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "⚠ Ollama not detected. Install from https://ollama.ai" -ForegroundColor Yellow
    Write-Host "  After installing, run: ollama pull phi3:mini" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. If Ollama is not installed, install it and run: ollama pull phi3:mini" -ForegroundColor White
Write-Host "2. Start the backend: .\run-backend.ps1" -ForegroundColor White
Write-Host "3. Start the frontend: .\run-frontend.ps1" -ForegroundColor White
Write-Host ""

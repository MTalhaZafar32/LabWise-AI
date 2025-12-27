# LabWise AI - Backend Server
# Runs FastAPI with EasyOCR and OpenAI integration

Write-Host "🧬 LabWise AI - Starting Backend..." -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Warning: .env file not found!" -ForegroundColor Yellow
    Write-Host "Please copy .env.example to .env and configure your OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host ""
}

# Start backend server
Write-Host "🚀 Starting FastAPI server..." -ForegroundColor Green
Write-Host "   OCR: EasyOCR" -ForegroundColor White
Write-Host "   LLM: OpenAI GPT-4o-mini" -ForegroundColor White
Write-Host ""
Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

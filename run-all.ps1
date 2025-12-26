# LabWise AI - Complete Development Environment Runner
# This script starts both backend and frontend in separate terminals

Write-Host "🧬 LabWise AI - Starting Complete Environment" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Start backend in new window
Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-File", ".\run-backend.ps1"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend in new window
Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-File", ".\run-frontend.ps1"

Write-Host ""
Write-Host "✅ Both servers are starting in separate windows" -ForegroundColor Green
Write-Host ""
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Close the terminal windows to stop the servers" -ForegroundColor Yellow

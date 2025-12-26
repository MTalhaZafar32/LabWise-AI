# LabWise AI - Frontend Development Server Runner

Write-Host "🧬 Starting LabWise AI Frontend..." -ForegroundColor Cyan
Write-Host ""

Set-Location frontend

Write-Host "Frontend server starting at http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

npm run dev

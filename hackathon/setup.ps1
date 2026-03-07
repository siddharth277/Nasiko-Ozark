# HR AI Agent Setup Script
# Run this once to initialize the project

Write-Host "=== HR AI Agent Setup ===" -ForegroundColor Cyan

# 1. Create virtual environment
Write-Host "`n[1/4] Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# 2. Activate and install requirements
Write-Host "`n[2/4] Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
.\venv\Scripts\pip install -r requirements.txt

# 3. Copy .env
if (-not (Test-Path ".env")) {
    Write-Host "`n[3/4] Creating .env from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "  --> IMPORTANT: Open .env and add your API keys before running!" -ForegroundColor Red
} else {
    Write-Host "`n[3/4] .env already exists, skipping." -ForegroundColor Green
}

Write-Host "`n[4/4] Setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:"
Write-Host "  1. Edit .env with your actual API keys"
Write-Host "  2. Run: .\venv\Scripts\Activate.ps1"
Write-Host "  3. Run: uvicorn main:app --reload --port 8000"
Write-Host "  4. Open: http://localhost:8000"
Write-Host ""

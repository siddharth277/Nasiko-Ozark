# ============================================
# NASIKO HACKATHON - AUTOMATED SETUP
# ============================================
# Run this script in PowerShell to setup everything automatically

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  NASIKO HR AI AGENT - AUTO SETUP  " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.8+" -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Step 2: Upgrade pip
Write-Host ""
Write-Host "[2/6] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "  ✓ pip upgraded" -ForegroundColor Green

# Step 3: Install dependencies
Write-Host ""
Write-Host "[3/6] Installing dependencies (this may take 2-3 minutes)..." -ForegroundColor Yellow
Write-Host "  Installing core packages..." -ForegroundColor Cyan

# Install in batches to avoid timeout
$packages1 = "fastapi uvicorn python-multipart jinja2 httpx aiofiles"
$packages2 = "groq sentence-transformers scikit-learn numpy"
$packages3 = "openai langchain langchain-openai langchain-core langgraph"
$packages4 = "google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
$packages5 = "pymupdf reportlab pillow beautifulsoup4 lxml"
$packages6 = "python-dotenv requests python-dateutil APScheduler rich"

Write-Host "  - Batch 1/6: Web framework..." -ForegroundColor Cyan
python -m pip install $packages1 --quiet

Write-Host "  - Batch 2/6: AI/ML libraries..." -ForegroundColor Cyan
python -m pip install $packages2 --quiet

Write-Host "  - Batch 3/6: LangChain..." -ForegroundColor Cyan
python -m pip install $packages3 --quiet

Write-Host "  - Batch 4/6: Google APIs..." -ForegroundColor Cyan
python -m pip install $packages4 --quiet

Write-Host "  - Batch 5/6: Document processing..." -ForegroundColor Cyan
python -m pip install $packages5 --quiet

Write-Host "  - Batch 6/6: Utilities..." -ForegroundColor Cyan
python -m pip install $packages6 --quiet

Write-Host "  ✓ All dependencies installed!" -ForegroundColor Green

# Step 4: Check for .env
Write-Host ""
Write-Host "[4/6] Checking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✓ .env file found" -ForegroundColor Green
} else {
    Write-Host "  ! .env file not found" -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Write-Host "  Creating .env from .env.example..." -ForegroundColor Cyan
        Copy-Item ".env.example" ".env"
        Write-Host "  ✓ .env created - PLEASE EDIT IT WITH YOUR API KEYS!" -ForegroundColor Yellow
        Write-Host "    Required: GROQ_API_KEY, OPENAI_API_KEY, HR_EMAIL" -ForegroundColor Yellow
    } else {
        Write-Host "  ✗ .env.example not found!" -ForegroundColor Red
    }
}

# Step 5: Check for credentials.json
Write-Host ""
Write-Host "[5/6] Checking Google Calendar credentials..." -ForegroundColor Yellow
if (Test-Path "credentials.json") {
    Write-Host "  ✓ credentials.json found" -ForegroundColor Green
} else {
    Write-Host "  ! credentials.json not found (optional for calendar)" -ForegroundColor Yellow
    Write-Host "    Download from: https://console.cloud.google.com" -ForegroundColor Cyan
}

# Step 6: Verify installation
Write-Host ""
Write-Host "[6/6] Verifying installation..." -ForegroundColor Yellow

$criticalPackages = @{
    "fastapi" = "FastAPI"
    "groq" = "Groq"
    "langchain" = "LangChain"
    "reportlab" = "ReportLab"
}

$allGood = $true
foreach ($pkg in $criticalPackages.Keys) {
    $name = $criticalPackages[$pkg]
    try {
        python -c "import $pkg" 2>$null
        Write-Host "  ✓ $name" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ $name (missing!)" -ForegroundColor Red
        $allGood = $false
    }
}

# Final status
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "  ✓ SETUP COMPLETE!" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Edit .env file with your API keys" -ForegroundColor White
    Write-Host "2. Run: python main.py" -ForegroundColor White
    Write-Host "3. Open: http://localhost:8000" -ForegroundColor White
    Write-Host ""
    Write-Host "Press any key to start the server..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Write-Host ""
    Write-Host "Starting server..." -ForegroundColor Green
    python main.py
} else {
    Write-Host "  ✗ SETUP INCOMPLETE" -ForegroundColor Red
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Some packages failed to install." -ForegroundColor Yellow
    Write-Host "Try running: pip install -r requirements.txt" -ForegroundColor White
    Write-Host ""
}

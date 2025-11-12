# Setup script for News Classifier API (Windows PowerShell)
Write-Host "News Classifier API - Setup Script (Windows)" -ForegroundColor Cyan


# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not installed. Please install Python 3.10 or higher." -ForegroundColor Red
    exit 1
}

# Install UV if not present
Write-Host "Installing dependencies with UV..." -ForegroundColor Yellow
try {
    $uvVersion = uv --version 2>&1
    Write-Host "UV found: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "UV not found. Installing UV..." -ForegroundColor Yellow
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
}

# Install dependencies
uv sync
Write-Host "Dependencies installed" -ForegroundColor Green
Write-Host ""

Write-Host "Virtual environment created at .venv" -ForegroundColor Green
Write-Host "   To activate: .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ".env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Edit .env and add your OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host "   You can get an API key from: https://platform.openai.com/api-keys" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ".env file already exists" -ForegroundColor Green
    Write-Host ""
}

# Check if PostgreSQL is installed
try {
    $pgVersion = psql --version 2>&1
    Write-Host "PostgreSQL found: $pgVersion" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "PostgreSQL not found" -ForegroundColor Yellow
    Write-Host "   Please install PostgreSQL to use the API:" -ForegroundColor White
    Write-Host "   Download from: https://www.postgresql.org/download/windows/" -ForegroundColor White
    Write-Host ""
}

Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env and add your OPENAI_API_KEY" -ForegroundColor White
Write-Host "2. Initialize Qdrant: uv run python scripts/init_vectorstore.py" -ForegroundColor White
Write-Host "3. Start the API: uv run uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "4. Visit http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Or use Docker:" -ForegroundColor Yellow
Write-Host "1. Edit .env and add your OPENAI_API_KEY" -ForegroundColor White
Write-Host "2. Run: docker-compose up -d" -ForegroundColor White
Write-Host "3. Visit http://localhost:8000/docs" -ForegroundColor White
Write-Host ""


# Setup with UV - Fast Python Package Manager

This project uses [UV](https://docs.astral.sh/uv/) for dependency management - a fast, reliable Python package manager written in Rust.

## 🚀 Why UV?

- ⚡ **10-100x faster** than pip
- 🔒 **Reproducible** builds with lock file
- 🎯 **Simple** - drop-in replacement for pip
- 📦 **All-in-one** - manages Python versions, venvs, and packages

## 📋 Prerequisites

### Install UV

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Or with pip:**
```bash
pip install uv
```

## 🎯 Quick Start

### 1. Install Dependencies

```bash
# Install all dependencies
uv sync

# Or install with dev dependencies
uv sync --extra dev
```

This creates a virtual environment and installs everything defined in `pyproject.toml`.

### 2. Activate Environment

**Windows (PowerShell):**
```powershell
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 3. Create .env File

```powershell
# Windows
@"
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://classifier_user:classifier_pass@localhost:5432/news_classifier
"@ | Out-File -FilePath .env -Encoding utf8
```

```bash
# Linux/Mac
cat > .env << 'EOF'
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://classifier_user:classifier_pass@localhost:5432/news_classifier
EOF
```

### 4. Initialize Qdrant

```bash
uv run python scripts/init_vectorstore.py
```

### 5. Start the API

```bash
uv run uvicorn app.main:app --reload
```

## 📦 UV Commands

### Install Dependencies
```bash
# Sync with lockfile
uv sync

# Install with dev dependencies
uv sync --extra dev

# Install only production dependencies
uv sync --no-dev
```

### Run Commands
```bash
# Run Python scripts
uv run python scripts/init_vectorstore.py
uv run python scripts/generate_predictions.py

# Run the API
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=app
```

### Add Dependencies
```bash
# Add a package
uv add package-name

# Add to dev dependencies
uv add --dev pytest-mock

# Add specific version
uv add "fastapi>=0.109.0"
```

### Update Dependencies
```bash
# Update all packages
uv sync --upgrade

# Update specific package
uv sync --upgrade-package openai
```

### Lock File
```bash
# Generate lock file (done automatically with sync)
uv lock

# Update lock file
uv lock --upgrade
```

## 🔄 Migration from pip

If you were using pip:

```bash
# OLD (pip)
pip install -e .
python scripts/init_vectorstore.py

# NEW (uv)
uv sync
uv run python scripts/init_vectorstore.py
```

## 🎓 Common Tasks

### Development Setup
```bash
# Complete setup for development
uv sync --extra dev
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv run python scripts/init_vectorstore.py
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_api.py -v
```

### Generate Predictions
```bash
uv run python scripts/generate_predictions.py
```

### Code Formatting
```bash
# Format code
uv run black app/ tests/

# Lint code
uv run ruff check app/ tests/
```

## 🐳 Docker with UV

The Dockerfile is already set up to use UV:

```bash
# Build and run
docker-compose up -d

# Inside container, UV is pre-installed
docker-compose exec api uv run python scripts/init_vectorstore.py
```

## 📊 Performance Comparison

| Task | pip | uv | Speedup |
|------|-----|----|---------| 
| Install from scratch | ~60s | ~5s | 12x faster |
| Install from cache | ~30s | ~1s | 30x faster |
| Resolve dependencies | ~10s | ~0.5s | 20x faster |

## 🔍 Troubleshooting

### "uv: command not found"

Install UV:
```bash
pip install uv
```

Or use the install script (see Prerequisites above).

### Virtual environment not found

```bash
# Create new environment
uv venv

# Sync dependencies
uv sync
```

### Lock file conflicts

```bash
# Regenerate lock file
rm uv.lock
uv lock
```

### Dependencies not resolving

```bash
# Clear cache and retry
uv cache clean
uv sync
```

## 📚 Learn More

- UV Documentation: https://docs.astral.sh/uv/
- UV GitHub: https://github.com/astral-sh/uv
- Migration Guide: https://docs.astral.sh/uv/guides/migration/

## ✅ Verification

Check everything is working:

```bash
# Check UV is installed
uv --version

# Check environment is activated
which python  # Should show .venv/bin/python

# Check dependencies are installed
uv run python -c "import langchain; import qdrant_client; print('✅ All dependencies installed!')"
```

---

**Summary**: UV makes dependency management faster and more reliable. Use `uv sync` instead of `pip install` and `uv run` to execute commands! 🚀


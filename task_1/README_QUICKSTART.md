# Quick Start - News Classifier with LangGraph + Qdrant

Get started in 3 simple steps using UV!

## Super Quick (5 minutes)

### 1. Install UV (if not already installed)

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Setup Project

```bash
# Run the setup script
./setup.sh          # Linux/Mac
.\setup.ps1         # Windows

# Or manually:
uv sync             # Install dependencies
```

### 3. Configure & Run

```bash
# Create .env with your OpenAI API key
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=postgresql://classifier_user:classifier_pass@localhost:5432/news_classifier
EOF

# Initialize Qdrant (ONE TIME - takes ~10-15 min)
uv run python scripts/init_vectorstore.py

# Start the API
uv run uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs

## 🧪 Test It

```bash
curl -X POST "http://localhost:8000/classify?include_examples=true" \
  -H "Content-Type: application/json" \
  -d '{"message": "Apple announces new iPhone with AI features"}'
```

## 📊 Generate Test Predictions

```bash
uv run python scripts/generate_predictions.py
```

This creates `test_predictions.csv` with all classifications.

## 🎯 Common Commands

```bash
# Install dependencies
uv sync

# Run API in development mode
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest

# Generate predictions
uv run python scripts/generate_predictions.py

# Add a new package
uv add package-name
```

## 📚 More Information

- **UV Setup**: See `SETUP_UV.md` for detailed UV usage
- **Environment**: See `CREATE_ENV.md` for .env file setup
- **Full Docs**: See `README_UPDATED.md` for complete documentation

## ⚡ Why UV?

- **10-100x faster** than pip
- **Reproducible** builds with lock file
- **Simple** - just use `uv run` before your commands
- **All-in-one** - manages everything

---

**That's it!** You now have a production-ready news classifier with LangGraph + Qdrant! 🎉


# Creating Your .env File

The `.env` file contains sensitive configuration like your OpenAI API key. Follow these steps:

## 🚀 Quick Setup

### Windows (PowerShell):
```powershell
# Create .env file
@"
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://classifier_user:classifier_pass@localhost:5432/news_classifier
POSTGRES_USER=classifier_user
POSTGRES_PASSWORD=classifier_pass
POSTGRES_DB=news_classifier
API_HOST=0.0.0.0
API_PORT=8000
"@ | Out-File -FilePath .env -Encoding utf8
```

### Linux/Mac:
```bash
# Create .env file
cat > .env << 'EOF'
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://classifier_user:classifier_pass@localhost:5432/news_classifier
POSTGRES_USER=classifier_user
POSTGRES_PASSWORD=classifier_pass
POSTGRES_DB=news_classifier
API_HOST=0.0.0.0
API_PORT=8000
EOF
```

### Or Copy Template:
```bash
# Copy the template
copy .env.template .env      # Windows
cp .env.template .env        # Linux/Mac
```

## 🔑 Get Your OpenAI API Key

1. Go to: https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)
5. Replace `your_openai_api_key_here` in `.env` with your actual key

## ✏️ Edit the .env File

Open `.env` in any text editor and replace:

```env
OPENAI_API_KEY=sk-proj-abc123...your-actual-key-here
```

## ✅ Verify

Your `.env` file should look like this:

```env
OPENAI_API_KEY=sk-proj-xyz123...
DATABASE_URL=postgresql://classifier_user:classifier_pass@localhost:5432/news_classifier
POSTGRES_USER=classifier_user
POSTGRES_PASSWORD=classifier_pass
POSTGRES_DB=news_classifier
API_HOST=0.0.0.0
API_PORT=8000
```

## 🔒 Security Notes

- ✅ `.env` is in `.gitignore` - won't be committed
- ✅ Never share your API key
- ✅ Never commit `.env` to git
- ✅ Rotate your key if it's exposed

## 🐳 Using Docker?

If using Docker Compose, you only need:

```env
OPENAI_API_KEY=sk-proj-xyz123...
```

The database is automatically configured in docker-compose.yml!

## 🧪 Test Your Setup

```bash
# Check .env exists and has your key
cat .env | grep OPENAI_API_KEY

# Should show (with your actual key):
# OPENAI_API_KEY=sk-proj-xyz...
```

## 🆘 Troubleshooting

### "OpenAI API key not found"
- Check `.env` file exists in `task_1/` directory
- Check file name is exactly `.env` (not `.env.txt`)
- Check key starts with `sk-`
- No quotes needed around the key

### "Permission denied"
```bash
chmod 600 .env  # Make it readable only by you
```

---

**Ready?** Once `.env` is created with your API key, you can:
```bash
python scripts/init_vectorstore.py
```


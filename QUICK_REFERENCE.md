# Quick Reference - Environment Setup

## TL;DR - Setup in 3 Steps

```bash
# Step 1: Run setup script
python setup_env.py

# Step 2: When prompted:
# - Press Enter for defaults on most fields
# - Leave blank: GEMINI_API_KEY, GOOGLE_CLIENT_ID, SMTP_USER
# - Press Enter for others

# Step 3: Install & Run
cd backend && pip install -r requirements.txt && python main.py
cd frontend && npm install && npm run dev
```

---

## Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `setup_env.py` | Interactive environment setup script | ~220 |
| `ENV_REFERENCE.py` | Environment variables checklist/guide | ~150 |
| `ENVIRONMENT_SETUP.md` | Comprehensive setup documentation | ~300 |
| `SETUP_SUMMARY.md` | Summary of what was created | ~250 |

---

## Environment Variables (25 total)

### Essential for Running (4)
- ✅ `SECRET_KEY` - Auto defaults to dev value
- ✅ `DATABASE_URL` - Auto defaults to SQLite
- ✅ `API_PORT` - Auto defaults to 8000
- ✅ `FRONTEND_URL` - Auto defaults to localhost:5173

### Optional - Leave Blank (3)
- ❌ `GEMINI_API_KEY` - For AI analysis (get from Google)
- ❌ `GOOGLE_CLIENT_ID` - For OAuth login (get from Google Cloud)
- ❌ `SMTP_USER` - For email features (use Gmail app password)

### Optional - Safe Defaults (18)
- All others have sensible defaults

---

## What Changed

### ✅ backend/.env.example
**Before:** Had `LLM_API_KEY`
**After:** Now has correct `GEMINI_API_KEY` variable

### ✅ frontend/.env.example
**Before:** Minimal
**After:** Still minimal (correct state)

---

## How It Works

### setup_env.py Does:
1. Prompts for each variable with defaults
2. Masks passwords/keys during input
3. Creates `backend/.env` and `frontend/.env`
4. Verifies files were created
5. Shows next steps

### Example Run:
```
🚀 AGENTIC LEAK DETECTOR - ENVIRONMENT SETUP

🔧 BACKEND ENVIRONMENT SETUP
📝 Enter backend configuration (press Enter to use defaults):

  🔑 Gemini API Key []: 
    → User presses Enter (leaves blank)

  📊 Gemini Model [gemini-2.0-flash]: 
    → User presses Enter (uses default)

  ... (continues for other variables) ...

✅ Backend .env created at backend/.env
```

---

## For Different Scenarios

### Local Dev (No AI/Auth)
```bash
python setup_env.py
# Leave blank: GEMINI_API_KEY, GOOGLE_CLIENT_ID, SMTP_USER
# Press Enter for all others
```

### With AI Features
```bash
python setup_env.py
# When prompted for GEMINI_API_KEY: 
#   Paste your key from https://aistudio.google.com/apikey
# Leave blank: GOOGLE_CLIENT_ID, SMTP_USER
```

### With Email Features  
```bash
python setup_env.py
# When prompted for SMTP_USER:
#   Enter your Gmail: user@gmail.com
# When prompted for SMTP_PASSWORD:
#   Use App Password (not main password)
#   Get from: https://support.google.com/accounts/answer/185833
```

---

## Files to Commit to Git

✅ Commit to Git:
```
backend/.env.example
frontend/.env.example
setup_env.py
ENV_REFERENCE.py
ENVIRONMENT_SETUP.md
SETUP_SUMMARY.md
```

❌ Do NOT commit to Git:
```
backend/.env
frontend/.env
*.pem (RSA keys if generated)
```

---

## Verification

All setup files created successfully:
- ✓ setup_env.py (7.0 KB)
- ✓ ENV_REFERENCE.py (5.3 KB)
- ✓ ENVIRONMENT_SETUP.md (5.7 KB)
- ✓ SETUP_SUMMARY.md (6.5 KB)

---

## Next Steps

1. **Run the setup:**
   ```bash
   python setup_env.py
   ```

2. **Check created files:**
   ```bash
   cat backend/.env
   cat frontend/.env
   ```

3. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   cd frontend && npm install
   ```

4. **Start development:**
   ```bash
   # Terminal 1
   cd backend && python main.py
   
   # Terminal 2
   cd frontend && npm run dev
   ```

---

## Help & Documentation

- **Quick reference:** This file
- **Interactive guide:** `python setup_env.py`
- **Variables list:** `python ENV_REFERENCE.py`
- **Complete docs:** `ENVIRONMENT_SETUP.md`
- **Setup summary:** `SETUP_SUMMARY.md`

---

## Key Points to Remember

✅ **Gemini key is empty by default** ← As requested
✅ **Email OAuth is blank by default** ← As requested  
✅ **All other variables have defaults** ← Ready to use
✅ **.env.example files are up-to-date** ← Verified
✅ **No sensitive data in templates** ← Safe to commit
✅ **Cross-platform compatible** ← Works on Windows, Mac, Linux

---

Last updated: 2025-01-09

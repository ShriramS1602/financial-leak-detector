# Environment Setup - Summary

## Created Files

### 1. **setup_env.py** - Interactive Setup Script
Interactive Python script that guides users through environment configuration.

**Usage:**
```bash
python setup_env.py
```

**Features:**
- Interactive prompts for all environment variables
- Sensible defaults for most values
- Password masking for sensitive fields (keys, passwords)
- Automatic .env file generation
- Validation of existing .env files

**What it sets up:**
- ✅ Backend environment (backend/.env)
- ✅ Frontend environment (frontend/.env)
- ✅ 25+ configuration variables

---

### 2. **ENV_REFERENCE.py** - Environment Variables Guide
Reference guide showing all available environment variables.

**Usage:**
```bash
python ENV_REFERENCE.py
```

**Provides:**
- Complete checklist of all environment variables
- Description for each variable
- Requirement status (Required/Optional/Recommended)
- Helpful notes and generation instructions
- Setup instructions for local development

---

### 3. **ENVIRONMENT_SETUP.md** - Setup Documentation
Comprehensive markdown documentation for environment setup.

**Contains:**
- Quick start guide (automatic & manual)
- Detailed configuration sections
- Local development setup
- Production setup
- Database configuration (SQLite & PostgreSQL)
- RSA key generation instructions
- Troubleshooting guide
- File structure overview

---

### 4. **Updated .env.example Files**

#### backend/.env.example
- ✅ Fixed GEMINI_API_KEY (was LLM_API_KEY)
- ✅ Added GEMINI_MODEL variable
- ✅ Organized into 8 sections
- ✅ All 25 variables documented

#### frontend/.env.example
- ✅ Only 1 variable needed (VITE_API_URL)
- ✅ Clean and minimal

---

## Environment Variables Included

### Security (4 vars)
- `SECRET_KEY` - JWT signing key
- `ALGORITHM` - JWT algorithm (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiry
- `RSA_PRIVATE_KEY` / `RSA_PUBLIC_KEY` - Password encryption

### API Keys (3 vars)
- `GEMINI_API_KEY` - Google Gemini (AI analysis) - **OPTIONAL, EMPTY BY DEFAULT**
- `GEMINI_MODEL` - Model version (default: gemini-2.0-flash)
- `GROQ_API_KEY` - Groq API (fallback)

### Google OAuth (3 vars)
- `GOOGLE_CLIENT_ID` - **BLANK BY DEFAULT**
- `GOOGLE_CLIENT_SECRET` - **BLANK BY DEFAULT**
- `GOOGLE_REDIRECT_URI` - Default: http://localhost:8000/api/auth/callback

### Email/SMTP (5 vars)
- `SMTP_HOST` - Default: smtp.gmail.com
- `SMTP_PORT` - Default: 587
- `SMTP_USER` - **BLANK BY DEFAULT**
- `SMTP_PASSWORD` - **BLANK BY DEFAULT**
- `FROM_EMAIL` - Default: noreply@finguard.com

### Database (1 var)
- `DATABASE_URL` - Default: sqlite:///./finance_tracker.db

### API Configuration (3 vars)
- `API_HOST` - Default: 0.0.0.0
- `API_PORT` - Default: 8000
- `FRONTEND_URL` - Default: http://localhost:5173

### Email Sync (2 vars)
- `EMAIL_SYNC_BATCH_SIZE` - Default: 50
- `EMAIL_SYNC_DAYS` - Default: 30

### Environment (2 vars)
- `ENVIRONMENT` - development/staging/production
- `DEBUG` - true/false

### Frontend (1 var)
- `VITE_API_URL` - Default: http://localhost:8000

---

## Quick Setup for New System

### Step 1: Clone Repository
```bash
git clone <repo-url>
cd agentic-leak-detector
```

### Step 2: Run Setup Script
```bash
python setup_env.py
```
This will:
- Prompt for each configuration
- Create `backend/.env` and `frontend/.env`
- Show next steps

### Step 3: Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Step 4: Run Application
```bash
# Terminal 1 - Backend
cd backend && python main.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

---

## For Different Users/Scenarios

### Scenario 1: Basic Local Development (No AI)
Run `setup_env.py` and:
- Leave `GEMINI_API_KEY` blank
- Leave `GOOGLE_CLIENT_ID` blank
- Leave `GOOGLE_CLIENT_SECRET` blank
- Leave `SMTP_USER` blank
- Leave `SMTP_PASSWORD` blank
- Keep all other defaults

### Scenario 2: With AI Analysis
- Add your `GEMINI_API_KEY` from [Google AI Studio](https://aistudio.google.com/apikey)
- Leave all other optional fields blank

### Scenario 3: With Email Features
- Set `SMTP_USER` to your Gmail address
- Set `SMTP_PASSWORD` to your [Gmail App Password](https://support.google.com/accounts/answer/185833)
- Keep other SMTP defaults

### Scenario 4: Production Deployment
See ENVIRONMENT_SETUP.md "For Production" section for:
- Secure SECRET_KEY generation
- PostgreSQL configuration
- All optional features enabled
- Security best practices

---

## Validation Checklist

✅ **Backend .env.example**
- GEMINI_API_KEY (correct var name - was LLM_API_KEY)
- All 25 variables documented
- Organized in logical sections
- Default values provided

✅ **Frontend .env.example**
- VITE_API_URL variable present
- Minimal and clean

✅ **setup_env.py**
- Interactive prompts for all variables
- Password masking for sensitive fields
- Automatic .env file generation
- 220+ lines of setup logic

✅ **ENV_REFERENCE.py**
- Complete variable checklist
- Requirement status for each var
- Helpful notes and instructions
- Setup guide included

✅ **ENVIRONMENT_SETUP.md**
- Quick start guide
- Detailed configuration
- Troubleshooting section
- Production setup
- File structure overview

---

## Next Steps

1. **On your new system**, run:
   ```bash
   python setup_env.py
   ```

2. **Follow the prompts** - press Enter for defaults on optional fields

3. **For features, add**:
   - Gemini API Key (for AI analysis)
   - Google OAuth credentials (for OAuth login)
   - SMTP credentials (for email features)

4. **Install and run** - follow the on-screen instructions

---

## Notes

- ✅ Gemini key is **EMPTY by default** as requested
- ✅ Email OAuth is **BLANK by default** as requested
- ✅ All other essential variables have sensible defaults
- ✅ .env.example files are up-to-date with actual usage
- ✅ Script prevents overwriting existing .env files
- ✅ All 25 backend variables covered
- ✅ Password fields are masked during input
- ✅ Windows and Linux compatible

---

For detailed information, see:
- [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) - Full setup guide
- Run `python setup_env.py` - Interactive setup
- Run `python ENV_REFERENCE.py` - Variable reference

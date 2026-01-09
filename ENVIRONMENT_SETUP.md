# Environment Setup Guide

This guide will help you set up the Agentic Leak Detector project on a new system.

## Quick Start

### 1. Automatic Setup (Recommended)
Run the interactive setup script:

```bash
python setup_env.py
```

This script will:
- Create `.env` files for both backend and frontend
- Prompt you for each configuration value
- Provide helpful defaults for most settings

### 2. Manual Setup
Copy the example files and edit them:

```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your values

# Frontend  
cp frontend/.env.example frontend/.env
# Edit frontend/.env with your values
```

## Environment Variables Guide

### For Local Development

**Minimal Configuration (Frontend Only):**
```bash
# backend/.env
DATABASE_URL=sqlite:///./finance_tracker.db
SECRET_KEY=dev-secret-key-change-in-production
FRONTEND_URL=http://localhost:5173
VITE_API_URL=http://localhost:8000
```

**With AI Analysis:**
```bash
# Add to backend/.env
GEMINI_API_KEY=your-api-key-from-google
GEMINI_MODEL=gemini-2.0-flash
```

**With Email Features:**
```bash
# Add to backend/.env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
```

**With OAuth (Google):**
```bash
# Add to backend/.env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/callback
```

### For Production

**Security:**
```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-with: python -c "import secrets; print(secrets.token_urlsafe(64))">
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Database:**
```bash
# Use PostgreSQL instead of SQLite
DATABASE_URL=postgresql://user:password@production-host:5432/dbname
```

**All Optional Features:**
- GEMINI_API_KEY (recommended for AI features)
- GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
- SMTP settings for email notifications
- RSA keys for password encryption

## Database Setup

SQLite (default, local development):
```bash
# Automatically created on first run
# Location: backend/finance_tracker.db
```

PostgreSQL (production):
```bash
# Create database
createdb agentic_leak_detector

# Update DATABASE_URL in backend/.env
DATABASE_URL=postgresql://user:password@localhost:5432/agentic_leak_detector
```

## RSA Key Generation

For password encryption (optional):

```bash
# Generate private key
openssl genrsa -out backend/private_key.pem 2048

# Generate public key
openssl rsa -in backend/private_key.pem -pubout -out backend/public_key.pem

# Convert to single-line format for .env
# (Python script will handle this if you use setup_env.py)
```

## Dependencies Installation

### Backend
```bash
cd backend
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

## Starting the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
# Runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

### Production Mode

```bash
# Backend
cd backend
gunicorn -w 4 -b 0.0.0.0:8000 main:app

# Frontend
cd frontend
npm run build
npm run preview
```

## Environment Variable Reference

See `ENV_REFERENCE.py` for a complete checklist:

```bash
python ENV_REFERENCE.py
```

## Troubleshooting

### API Connection Failed
- Check `VITE_API_URL` in `frontend/.env`
- Ensure backend is running on the port specified

### Database Error
- Verify `DATABASE_URL` in `backend/.env`
- For SQLite: ensure `backend/` directory is writable
- For PostgreSQL: verify connection parameters

### Email Not Sending
- SMTP_USER and SMTP_PASSWORD must be valid
- For Gmail: use an [App Password](https://support.google.com/accounts/answer/185833), not your account password
- Check firewall rules for SMTP port 587

### AI Analysis Not Working
- Verify `GEMINI_API_KEY` is set in `backend/.env`
- Get your key from [Google AI Studio](https://aistudio.google.com/apikey)
- Check that the API is enabled in Google Cloud Console

### OAuth Not Working
- Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `backend/.env`
- Ensure `GOOGLE_REDIRECT_URI` matches exactly in Google Cloud Console
- Check that OAuth2 is enabled for your Google Cloud project

## File Structure

```
project-root/
├── backend/
│   ├── .env                 # Actual config (DO NOT COMMIT)
│   ├── .env.example         # Template (commit this)
│   ├── requirements.txt      # Python dependencies
│   └── main.py             # Backend entry point
├── frontend/
│   ├── .env                 # Actual config (DO NOT COMMIT)
│   ├── .env.example         # Template (commit this)
│   ├── package.json         # NPM dependencies
│   └── src/
├── setup_env.py             # Environment setup script
└── ENV_REFERENCE.py         # Environment variables guide
```

## Notes

- **Never commit `.env` files** - They contain sensitive information
- Always commit `.env.example` files
- For team collaboration, create a `.env.template` with instructions
- Use different `SECRET_KEY` values for each environment
- Rotate secrets regularly in production
- For Gmail: Always use [App Passwords](https://support.google.com/accounts/answer/185833) instead of your main password

---

For detailed configuration options, run:
```bash
python setup_env.py
```

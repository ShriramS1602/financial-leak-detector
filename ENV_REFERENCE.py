#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Environment Variables Reference Guide
This script generates a checklist of all required environment variables
"""

import sys
import os
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')


def print_env_checklist():
    """Print environment variables checklist"""
    
    checklist = {
        "🔐 SECURITY": [
            ("SECRET_KEY", "JWT Secret Key for token signing", "Required", "Use: python -c \"import secrets; print(secrets.token_urlsafe(64))\""),
            ("ALGORITHM", "JWT Algorithm (default: HS256)", "Optional", "Default: HS256"),
            ("ACCESS_TOKEN_EXPIRE_MINUTES", "Token expiration time", "Optional", "Default: 30 minutes"),
        ],
        "🔑 API KEYS": [
            ("GEMINI_API_KEY", "Google Gemini API Key for AI analysis", "⚠️  Optional but recommended", "Get from: https://aistudio.google.com/apikey"),
            ("GEMINI_MODEL", "Gemini Model Version", "Optional", "Default: gemini-2.0-flash"),
            ("GROQ_API_KEY", "Groq API Key (fallback LLM)", "Optional", "Get from: https://console.groq.com"),
        ],
        "🔐 GOOGLE OAUTH": [
            ("GOOGLE_CLIENT_ID", "Google OAuth Client ID", "⚠️  Leave blank for now", "Get from: Google Cloud Console"),
            ("GOOGLE_CLIENT_SECRET", "Google OAuth Client Secret", "⚠️  Leave blank for now", "Get from: Google Cloud Console"),
            ("GOOGLE_REDIRECT_URI", "Google OAuth Redirect URI", "Optional", "Default: http://localhost:8000/api/auth/callback"),
        ],
        "📧 EMAIL (SMTP)": [
            ("SMTP_HOST", "SMTP Server Host", "Optional", "Default: smtp.gmail.com"),
            ("SMTP_PORT", "SMTP Server Port", "Optional", "Default: 587"),
            ("SMTP_USER", "SMTP Email Address", "⚠️  Leave blank for now", "Gmail app password required"),
            ("SMTP_PASSWORD", "SMTP App Password", "⚠️  Leave blank for now", "Use app-specific password, not account password"),
            ("FROM_EMAIL", "Sender Email Address", "Optional", "Default: noreply@finguard.com"),
        ],
        "💾 DATABASE": [
            ("DATABASE_URL", "Database Connection URL", "Optional", "Default: sqlite:///./finance_tracker.db"),
        ],
        "🌐 API CONFIGURATION": [
            ("API_HOST", "API Server Host", "Optional", "Default: 0.0.0.0"),
            ("API_PORT", "API Server Port", "Optional", "Default: 8000"),
            ("FRONTEND_URL", "Frontend URL for CORS", "Optional", "Default: http://localhost:5173"),
        ],
        "📧 EMAIL SYNC": [
            ("EMAIL_SYNC_BATCH_SIZE", "Batch size for email sync", "Optional", "Default: 50"),
            ("EMAIL_SYNC_DAYS", "Days to sync emails back", "Optional", "Default: 30"),
        ],
        "🔐 RSA ENCRYPTION": [
            ("RSA_PRIVATE_KEY", "Private key for password encryption", "⚠️  Optional", "Generate with: openssl genrsa -out private_key.pem 2048"),
            ("RSA_PUBLIC_KEY", "Public key for password encryption", "⚠️  Optional", "Generate with: openssl rsa -in private_key.pem -pubout -out public_key.pem"),
        ],
        "🌍 ENVIRONMENT": [
            ("ENVIRONMENT", "Application Environment", "Optional", "Options: development, staging, production"),
            ("DEBUG", "Debug Mode", "Optional", "Default: true (set to false in production)"),
        ],
        "🎨 FRONTEND": [
            ("VITE_API_URL", "Backend API URL for frontend", "Optional", "Default: http://localhost:8000"),
        ],
    }
    
    print("\n" + "=" * 100)
    print("📋 ENVIRONMENT VARIABLES REFERENCE GUIDE")
    print("=" * 100)
    
    for category, variables in checklist.items():
        print(f"\n{category}")
        print("-" * 100)
        
        for var_name, description, requirement, note in variables:
            print(f"\n  Variable: {var_name}")
            print(f"  Description: {description}")
            print(f"  Requirement: {requirement}")
            print(f"  Note: {note}")
    
    print("\n" + "=" * 100)
    print("🚀 SETUP INSTRUCTIONS")
    print("=" * 100)
    print("""
1. Run the setup script:
   python setup_env.py

2. Fill in the required fields (leave optional ones blank by pressing Enter)

3. For local development, you can skip:
   - GEMINI_API_KEY (unless you want AI analysis features)
   - GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET (unless you want OAuth)
   - SMTP settings (unless you want email features)
   - RSA keys (unless you want password encryption)

4. Verify your .env files were created correctly:
   - backend/.env (backend configuration)
   - frontend/.env (frontend configuration)

5. Install dependencies:
   cd backend && pip install -r requirements.txt
   cd frontend && npm install

6. Start the application:
   Terminal 1: cd backend && python main.py
   Terminal 2: cd frontend && npm run dev
""")
    print("=" * 100 + "\n")


def main():
    """Main function"""
    print_env_checklist()


if __name__ == "__main__":
    main()

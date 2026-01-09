# BACKEND IMPLEMENTATION QUICK START

**For Backend Developers Starting Fresh**

---

## 🎯 YOUR MISSION

You are a **backend developer** with **NO FRONTEND EXPERIENCE**.

You need to implement a backend API that the frontend React app will call.

This guide tells you exactly what to build and how to verify it works.

---

## 📚 DOCUMENTATION PROVIDED

You have **4 comprehensive guides**:
1. ✅ **DOCUMENTATION_INDEX.md** ← Start here
2. ✅ **FRONTEND_ANALYSIS_SUMMARY.md** ← For quick overview  
3. ✅ **FRONTEND_API_MAPPING.md** ← For API implementation specs
4. ✅ **FRONTEND_GUIDE.md** ← For technical deep dives
5. ✅ **FRONTEND_DIAGRAMS.md** ← For visual workflows

**All together**: ~5,000 lines of detailed documentation

---

## 🚀 QUICK START STEPS

### Step 1: Understand What You're Building (20 min)
Read: **FRONTEND_ANALYSIS_SUMMARY.md**

Key takeaways:
- It's a financial leak detector app
- Users upload bank statements or connect Gmail
- Backend detects "leaks" (recurring charges)
- 27 API endpoints total
- 4 main feature areas

### Step 2: Get Your Checklist (10 min)
Open: **FRONTEND_API_MAPPING.md**

Copy this checklist into a spreadsheet or doc:
```
AUTHENTICATION (12 endpoints)
☐ POST /api/auth/login
☐ POST /api/auth/signup
☐ GET /api/auth/me
... (10 more)

EMAIL (4 endpoints)
☐ POST /api/email/sync
... (3 more)

TRANSACTIONS (6 endpoints)
☐ GET /api/transactions
... (5 more)

LEAKS (4 endpoints)
☐ POST /api/leaks/detect
... (3 more)

OTHER (1 endpoint)
☐ GET /health
```

### Step 3: Understand The Flow (15 min)
Look at: **FRONTEND_DIAGRAMS.md**

Focus on:
- Complete User Flow (diagram #2)
- Authentication State Machine (diagram #3)
- Component Communication (diagram #14)

### Step 4: Start Implementation (Days 1-4)
Use: **FRONTEND_API_MAPPING.md** as your spec

For each endpoint:
1. Copy the exact request/response format
2. Implement the endpoint
3. Test with `curl` or Postman
4. Mark it as complete

### Step 5: Integration Test (Days 5-7)
Run both:
- Frontend: `cd frontend && npm run dev` (port 5173)
- Backend: `python main.py` (port 8000)

Test each flow:
1. Sign up
2. Email verification
3. Login
4. File upload
5. Gmail sync
6. View results

---

## 📋 27 ENDPOINTS YOU MUST IMPLEMENT

### Category 1: AUTHENTICATION (12 endpoints) - PRIORITY 1
**Timeline**: Days 1-3

**What the frontend needs**:
- Users to sign up with email/password
- Users to login with email/password
- Users to login with Google OAuth
- Users to reset forgotten passwords
- Users to verify their email address

**Key files to reference**:
- FRONTEND_API_MAPPING.md (Authentication section)
- FRONTEND_GUIDE.md (Authentication Flow section)

**Test with**:
- [Login.tsx](./frontend/src/pages/Login.tsx)
- [Signup.tsx](./frontend/src/pages/Signup.tsx)
- [VerifyEmail.tsx](./frontend/src/pages/VerifyEmail.tsx)
- [ResetPassword.tsx](./frontend/src/pages/ResetPassword.tsx)

**Endpoints**:
1. `POST /api/auth/login` - Email/password login
2. `POST /api/auth/signup` - Register new user
3. `GET /api/auth/me` - Get current user info
4. `POST /api/auth/logout` - Logout
5. `POST /api/auth/forgot-password` - Request password reset
6. `POST /api/auth/reset-password` - Apply password reset
7. `POST /api/auth/validate-reset-token` - Check reset token
8. `POST /api/auth/verify-email` - Verify email with token
9. `GET /api/auth/check-email` - Check if email exists
10. `POST /api/auth/change-password` - Change password (logged in)
11. `GET /api/auth/login` - Get Google OAuth URL (for login)
12. `GET /api/auth/google/signup` - Get Google OAuth URL (for signup)

**CRITICAL**: 
- Password encryption/decryption (RSA)
- JWT token generation
- Email service setup (SMTP)
- Google OAuth integration
- Password hashing (bcrypt)

---

### Category 2: FILE UPLOAD & ANALYSIS (1 endpoint) - PRIORITY 2
**Timeline**: Days 3-5

**What the frontend needs**:
- Upload CSV/Excel/PDF file
- Extract transactions
- Detect "leaks" (recurring charges)
- Generate AI insights

**Key files to reference**:
- FRONTEND_API_MAPPING.md (Transaction endpoints)
- FRONTEND_DIAGRAMS.md (File upload flow diagram #4)

**Test with**:
- [AnalysisPage.tsx](./frontend/src/pages/AnalysisPage.tsx) line 120
- [DataImport.tsx](./frontend/src/components/DataImport.tsx)

**Endpoints**:
1. `POST /api/transactions/upload-csv` - Upload and parse file

**Endpoint also expects**:
- `POST /analyze` - Direct file analysis (LEGACY - may not use)

**Must do**:
- Parse CSV/Excel/PDF files
- Extract transaction data
- Detect transaction categories
- Identify recurring charges (subscriptions)
- Generate AI-powered insights

---

### Category 3: GMAIL INTEGRATION (4 endpoints) - PRIORITY 3
**Timeline**: Days 5-7

**What the frontend needs**:
- Connect to Gmail via OAuth
- Extract transactions from emails
- Detect leaks from email patterns
- Show sync status

**Key files to reference**:
- FRONTEND_API_MAPPING.md (Email endpoints)
- FRONTEND_DIAGRAMS.md (Gmail sync flow diagram #5)

**Test with**:
- [AuthCallback.tsx](./frontend/src/pages/AuthCallback.tsx)
- [DataImport.tsx](./frontend/src/components/DataImport.tsx)

**Endpoints**:
1. `POST /api/email/sync` - Sync emails (with detailed options)
2. `POST /api/email/sync-with-range` - Sync emails (with date range)
3. `GET /api/email/preview` - Preview emails
4. `GET /api/email/status` - Get sync status

**Must do**:
- Store Gmail OAuth tokens
- Query Gmail API
- Parse transaction emails
- Extract amounts, merchants, dates
- Detect leaks
- Generate insights

---

### Category 4: TRANSACTION MANAGEMENT (6 endpoints) - PRIORITY 4
**Timeline**: Days 7-8

**What the frontend needs**:
- View all transactions
- Filter transactions
- Get monthly statistics
- Create/update/delete transactions

**Key files to reference**:
- FRONTEND_API_MAPPING.md (Transaction endpoints)

**Test with**:
- [Dashboard.tsx](./frontend/src/components/Dashboard.tsx)
- [useTransactions.ts](./frontend/src/hooks/useTransactions.ts) hook

**Endpoints**:
1. `GET /api/transactions` - List transactions with filters
2. `GET /api/transactions/stats` - Get monthly statistics
3. `POST /api/transactions` - Create transaction
4. `PUT /api/transactions/{id}` - Update transaction
5. `DELETE /api/transactions/{id}` - Delete transaction
6. (Already covered above)

**Must do**:
- Store transactions in database
- Calculate monthly totals
- Calculate savings rate
- Categorize transactions
- Support filtering by type, category, date range

---

### Category 5: LEAK DETECTION (4 endpoints) - PRIORITY 5
**Timeline**: Days 8-10

**What the frontend needs**:
- Detect leaks (recurring charges, anomalies)
- Get list of detected leaks
- Get list of detected subscriptions
- Mark leaks as resolved

**Key files to reference**:
- FRONTEND_API_MAPPING.md (Leak endpoints)

**Test with**:
- [Dashboard.tsx](./frontend/src/components/Dashboard.tsx) leak list

**Endpoints**:
1. `POST /api/leaks/detect` - Trigger leak detection
2. `GET /api/leaks` - Get all detected leaks
3. `GET /api/leaks/subscriptions` - Get subscriptions
4. `PUT /api/leaks/leaks/{id}/resolve` - Mark leak resolved

**Must do**:
- Analyze transaction patterns
- Identify recurring charges
- Calculate leak confidence score
- Predict next payment date
- Store in database

---

### Category 6: OTHER (1 endpoint) - PRIORITY 6
**Timeline**: Day 10

**Endpoints**:
1. `GET /health` - Health check

---

## 🔐 CRITICAL IMPLEMENTATION DETAILS

### 1. PASSWORD ENCRYPTION/DECRYPTION

**Frontend sends**:
```json
{
  "email": "user@example.com",
  "password": "vN2k3j/VK9d..." // RSA-OAEP encrypted, base64 encoded
}
```

**You must**:
1. Receive the base64-encoded encrypted password
2. Decode it from base64 to bytes
3. Decrypt using RSA private key
4. Get the original plain text password
5. Hash it with bcrypt for storage

**Python example**:
```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64
from passlib.context import CryptContext

# Load private key
with open('private_key.pem', 'rb') as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None,
        backend=default_backend()
    )

# Decrypt
encrypted_bytes = base64.b64decode(encrypted_password_string)
decrypted_password = private_key.decrypt(
    encrypted_bytes,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
).decode()

# Hash for storage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash(decrypted_password)
```

**⚠️ CRITICAL**: The frontend has a hardcoded RSA public key. You MUST have the matching private key!

---

### 2. JWT TOKEN GENERATION

**Frontend expects**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**You must**:
1. Generate JWT on successful login/signup
2. Token should expire in 30 minutes
3. Include user info in payload
4. Sign with SECRET_KEY

**Python example**:
```python
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

payload = {
    "sub": user_email,
    "user_id": user_id,
    "exp": datetime.utcnow() + timedelta(minutes=30)
}
token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

**Frontend checks**:
- Token stored in localStorage
- Attached to all requests as `Authorization: Bearer {token}`
- 401 response → token invalid → redirect to login

---

### 3. GOOGLE OAUTH INTEGRATION

**Frontend flow**:
1. Clicks "Login/Signup with Google"
2. Calls `GET /api/auth/login` or `GET /api/auth/google/signup`
3. You respond with `authorization_url`
4. Frontend redirects user to Google consent screen
5. User approves
6. Google redirects to your backend `/api/auth/callback`
7. You exchange code for access token
8. You redirect to `{FRONTEND_URL}/auth/callback?token=JWT&oauth_success=true`

**Environment variables needed**:
```
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/callback
FRONTEND_URL=http://localhost:5173
```

**Backend must**:
1. Generate authorization URL
2. Handle OAuth callback
3. Exchange code for Gmail access token
4. Fetch user profile
5. Create/find user in database
6. Store Gmail token (encrypted!)
7. Generate JWT for frontend

---

### 4. EMAIL SERVICE (SMTP)

**Frontend expects**:
- Verification email sent after signup
- Password reset email sent after forgot-password request
- AI insights generated and displayed

**Environment variables needed**:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=noreply@finguard.com
```

**You must**:
1. Setup SMTP connection
2. Send verification email with token link
3. Send password reset email with token link
4. Format emails as HTML
5. Include proper links to frontend

---

### 5. CORS CONFIGURATION

**Frontend runs on**: `http://localhost:5173`  
**Backend runs on**: `http://127.0.0.1:8000`

**You must allow**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ✅ IMPLEMENTATION CHECKLIST

### Pre-Implementation
- [ ] Read FRONTEND_ANALYSIS_SUMMARY.md
- [ ] Read FRONTEND_DIAGRAMS.md (the flow diagrams)
- [ ] Bookmark FRONTEND_API_MAPPING.md
- [ ] Set up development environment (Python, FastAPI, DB)
- [ ] Get RSA key pair (private key matches frontend's public key)
- [ ] Get Google Client ID & Secret
- [ ] Get SMTP credentials

### Phase 1: Authentication (Days 1-3)
- [ ] Setup FastAPI project structure
- [ ] Create User model & database
- [ ] Implement POST /api/auth/signup
- [ ] Implement POST /api/auth/login
- [ ] Implement GET /api/auth/me
- [ ] Implement POST /api/auth/logout
- [ ] Implement email verification flow
- [ ] Implement password reset flow
- [ ] Implement Google OAuth
- [ ] Test with frontend Sign up / Login flows

### Phase 2: File Upload (Days 3-5)
- [ ] Create Transaction model
- [ ] Create Leak model
- [ ] Implement CSV/Excel/PDF parsing
- [ ] Implement transaction extraction
- [ ] Implement category detection
- [ ] Implement leak detection algorithm
- [ ] Implement POST /api/transactions/upload-csv
- [ ] Implement AI insights generation (Gemini API)
- [ ] Test with frontend file upload

### Phase 3: Email Integration (Days 5-7)
- [ ] Setup Gmail API integration
- [ ] Implement OAuth token storage
- [ ] Implement email parsing
- [ ] Implement POST /api/email/sync
- [ ] Implement POST /api/email/sync-with-range
- [ ] Implement GET /api/email/preview
- [ ] Implement GET /api/email/status
- [ ] Test with frontend Gmail connection

### Phase 4: Transactions (Days 7-8)
- [ ] Implement GET /api/transactions
- [ ] Implement GET /api/transactions/stats
- [ ] Implement POST /api/transactions
- [ ] Implement PUT /api/transactions/{id}
- [ ] Implement DELETE /api/transactions/{id}
- [ ] Test with useTransactions hook

### Phase 5: Leaks (Days 8-10)
- [ ] Implement POST /api/leaks/detect
- [ ] Implement GET /api/leaks
- [ ] Implement GET /api/leaks/subscriptions
- [ ] Implement PUT /api/leaks/leaks/{id}/resolve
- [ ] Test with Dashboard component

### Phase 6: Testing & Polish (Days 10-14)
- [ ] Full integration testing
- [ ] Error handling
- [ ] Security review
- [ ] Performance testing
- [ ] Documentation
- [ ] Code review

---

## 🧪 TESTING YOUR IMPLEMENTATION

### Test 1: Sign Up Flow
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "encrypted_string",
    "username": "testuser",
    "name": "Test User",
    "terms_accepted": true,
    "privacy_accepted": true
  }'

# Expected response:
# {
#   "access_token": "eyJ...",
#   "token_type": "bearer",
#   "user": { "id": 1, "email": "test@example.com", ... }
# }
```

### Test 2: Login Flow
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "encrypted_string",
    "remember_me": false
  }'

# Expected response:
# {
#   "access_token": "eyJ...",
#   "token_type": "bearer",
#   "user": { ... }
# }
```

### Test 3: With Frontend
1. Start backend: `python main.py`
2. Start frontend: `npm run dev` (in frontend folder)
3. Navigate to `http://localhost:5173`
4. Test entire sign up → login → upload file flow
5. Fix any CORS, API contract, or data format issues

---

## 📞 WHEN YOU'RE STUCK

### "I don't understand what an endpoint should do"
→ Read FRONTEND_API_MAPPING.md - has detailed specs for each endpoint

### "I don't know how password encryption works"
→ Read FRONTEND_GUIDE.md section "Password Encryption" or FRONTEND_DIAGRAMS.md diagram #6

### "I'm not sure what response format to use"
→ Check FRONTEND_API_MAPPING.md - copy the exact response JSON format

### "Frontend is calling an endpoint I don't see documented"
→ Check FRONTEND_ANALYSIS_SUMMARY.md section "Critical Issues" - there are 2 legacy endpoints

### "I need to see the complete user flow"
→ Look at FRONTEND_DIAGRAMS.md diagram #2 (Complete User Flow)

### "I need to understand authentication"
→ Look at FRONTEND_DIAGRAMS.md diagram #3 (Authentication State Machine)

---

## 🎯 SUCCESS CRITERIA

You're done when:

1. ✅ All 27 endpoints are implemented
2. ✅ Frontend sign up / login works
3. ✅ Frontend file upload works
4. ✅ Frontend Gmail sync works
5. ✅ Frontend displays results correctly
6. ✅ No CORS errors
7. ✅ No authentication errors
8. ✅ All data flows correctly
9. ✅ AI insights are generated
10. ✅ Code is documented

---

## 📚 FINAL REMINDERS

1. **Use FRONTEND_API_MAPPING.md as your spec** - it has exact request/response formats
2. **Test frequently with frontend** - don't just test endpoints in isolation
3. **Check FRONTEND_DIAGRAMS.md for flows** - visual understanding helps
4. **Read FRONTEND_GUIDE.md for deep dives** - when you need technical details
5. **Keep documentation up to date** - help your team succeed

---

**You've got this! 🚀 Good luck with your backend implementation!**

For questions, refer back to the 4 comprehensive documentation files provided.

# FRONTEND ARCHITECTURE & WORKFLOW DIAGRAMS

**Visual Guide for Backend Developers**

---

## 1. APPLICATION ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React 18)                      │
│                    Running on port 5173                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              App.tsx (Router / Page Setup)              │   │
│  └────────────────────┬────────────────────────────────────┘   │
│                       │                                          │
│        ┌──────────────┼──────────────┐                          │
│        │              │              │                          │
│  ┌─────▼─────┐  ┌────▼────┐  ┌─────▼────────────┐              │
│  │   Public  │  │Protected │  │  OAuth Callback │              │
│  │   Pages   │  │  Pages   │  │    Handler      │              │
│  └───────────┘  └──────────┘  └─────────────────┘              │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Services Layer (API Communication)          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐   │   │
│  │  │   api.ts     │  │emailService  │  │  crypto.ts  │   │   │
│  │  │  (Main API)  │  │  (Email API) │  │ (Encryption)│   │   │
│  │  └──────────────┘  └──────────────┘  └─────────────┘   │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │                                        │
│                    Fetch API                                     │
│                         │                                        │
└─────────────────────────┼────────────────────────────────────────┘
                          │
                          │ HTTP Requests
                          │ Authorization: Bearer {JWT}
                          │
┌─────────────────────────▼────────────────────────────────────────┐
│                  BACKEND (FastAPI/Python)                        │
│                  Running on port 8000                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           API Routers (27 total endpoints)               │   │
│  │  ├─ /api/auth (12 endpoints)                            │   │
│  │  ├─ /api/email (4 endpoints)                            │   │
│  │  ├─ /api/transactions (6 endpoints)                     │   │
│  │  ├─ /api/leaks (4 endpoints)                            │   │
│  │  └─ /health (1 endpoint)                                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Core Logic & Services                          │   │
│  │  ├─ leak_analyzer.py                                    │   │
│  │  ├─ email_service.py                                    │   │
│  │  ├─ transaction_processor.py                            │   │
│  │  └─ detector.py                                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Database & External Services                   │   │
│  │  ├─ SQLAlchemy ORM                                      │   │
│  │  ├─ PostgreSQL/SQLite                                   │   │
│  │  ├─ Gmail API                                           │   │
│  │  ├─ Google OAuth                                        │   │
│  │  └─ SMTP Email Service                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. COMPLETE USER FLOW

```
START
  │
  ├─ New User?
  │  │
  │  ├─ Yes → [Signup Page]
  │  │        ├─ Enter email, password, username
  │  │        ├─ Validate password strength (5 criteria)
  │  │        ├─ POST /api/auth/signup
  │  │        ├─ Receive JWT token
  │  │        └─ Show "Check your email" message
  │  │             └─ User clicks email link
  │  │                 └─ [VerifyEmail Page]
  │  │                     ├─ GET token from URL
  │  │                     ├─ POST /api/auth/verify-email
  │  │                     └─ Redirect to [Login Page]
  │  │
  │  └─ No → [Login Page]
  │           ├─ Email or Google OAuth?
  │           │
  │           ├─ Email:
  │           │  ├─ Enter email + password
  │           │  ├─ POST /api/auth/login (password encrypted)
  │           │  └─ Receive JWT token → localStorage
  │           │
  │           └─ Google OAuth:
  │              ├─ GET /api/auth/login → authorization_url
  │              ├─ Redirect to Google consent
  │              ├─ Google redirects to /auth/callback?code=xxx
  │              ├─ Backend exchanges code for token
  │              ├─ Frontend stores JWT
  │              └─ Continue to main app
  │
  ├─ Forgot Password?
  │  │
  │  └─ Yes → [Modal in Login Page]
  │           ├─ POST /api/auth/forgot-password
  │           ├─ Backend sends reset email
  │           └─ User receives link
  │               └─ [ResetPassword Page]
  │                   ├─ POST /api/auth/validate-reset-token
  │                   ├─ Enter new password
  │                   ├─ POST /api/auth/reset-password
  │                   └─ Redirect to [Login Page]
  │
  └─ Authenticated → [AnalysisPage - MAIN APP]
                     │
                     ├─ Option 1: Upload File
                     │  ├─ Select CSV/Excel/PDF
                     │  ├─ If locked PDF:
                     │  │  └─ Enter password → POST /analyze
                     │  ├─ Else: POST /analyze
                     │  ├─ Backend analyzes transactions
                     │  ├─ Backend detects "leaks"
                     │  └─ Show results in [Dashboard]
                     │
                     ├─ Option 2: Connect Gmail
                     │  ├─ Select date range
                     │  ├─ POST /api/auth/google/signup
                     │  ├─ Get Gmail authorization_url
                     │  ├─ Redirect to Google OAuth
                     │  ├─ Grant Gmail access
                     │  ├─ Backend syncs emails
                     │  ├─ Backend extracts transactions
                     │  ├─ Backend detects "leaks"
                     │  └─ Show results in [Dashboard]
                     │
                     └─ View Results in Dashboard
                        ├─ 3 stat cards
                        ├─ Leak list
                        ├─ Spending chart
                        └─ AI insights
                            │
                            └─ Click "Back to Upload" → repeat flow

LOGOUT → Delete token → Redirect to [Login Page]
```

---

## 3. AUTHENTICATION STATE MACHINE

```
┌──────────────┐
│  UNAUTHENTI- │
│   CATED      │
└───────┬──────┘
        │
        │ Sign Up / Log In / OAuth Success
        │
        ▼
┌──────────────────────────────────────────────────┐
│  AUTHENTICATED                                   │
│  ├─ Token stored in localStorage['auth_token']  │
│  ├─ Token attached to all API requests          │
│  │  (Authorization: Bearer {token})             │
│  └─ Access to PrivateRoute pages                │
└───────┬──────────────────────────────────────────┘
        │
        │ Token Valid          │ Token Expired/Invalid
        │ (< 30 min old)       │
        │                      │
        ├─ Continue using app  ├─ API returns 401
        │                      ├─ setToken(null)
        │                      ├─ localStorage cleared
        │                      └─ Redirect to /login
        │
        │ User clicks Logout
        │
        ▼
┌──────────────────────────────────────────────────┐
│  LOGOUT ACTION                                   │
│  ├─ POST /api/auth/logout                       │
│  ├─ setToken(null)                              │
│  ├─ localStorage.removeItem('auth_token')       │
│  └─ Redirect to /login                          │
└──────────────────────────────────────────────────┘
```

---

## 4. FILE UPLOAD FLOW

```
User clicks "Upload Statement"
        │
        ▼
    [File Input]
        │
        ├─ CSV/Excel/PDF format?
        │
        ▼
   [Check file]
        │
        ├─ Is PDF locked?
        │  ├─ Yes → Show password modal
        │  │        └─ User enters password
        │  │            └─ Submit password + file
        │  │
        │  └─ No → Continue
        │
        ▼
  POST /analyze
  (Frontend sends FormData)
        │
        ▼
  [Backend Processing]
  ├─ Parse file
  ├─ Extract transactions
  ├─ Detect categories
  ├─ Identify recurring charges (LEAKS)
  └─ Generate AI insights
        │
        ▼
  Response: {
    leaks: [{...}, {...}],
    transactions: [{...}, {...}],
    ai_insights: "markdown string",
    summary: { total_spend, transaction_count }
  }
        │
        ▼
  [Dashboard Component]
  ├─ Render stats cards
  ├─ Display leak list
  ├─ Show spending chart
  └─ Display AI insights
        │
        ▼
  User sees results
  └─ Can click "Back to Upload" to try again
```

---

## 5. GMAIL SYNC FLOW

```
User clicks "Connect Gmail"
        │
        ├─ Select date range (30/60/90 days, 1 year)
        │
        ▼
sessionStorage.setItem('email_date_range', selectedRange)
        │
        ▼
Fetch GET /api/auth/google/signup
        │
        ▼
Response: {
  authorization_url: "https://accounts.google.com/o/oauth2/v2/auth?...",
  state: "random_string",
  action: "signup"
}
        │
        ▼
window.location.href = authorization_url
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  USER ON GOOGLE CONSENT SCREEN                      │
│  ├─ See permissions requested:                      │
│  │  ├─ Read Gmail messages                         │
│  │  ├─ See your email address                      │
│  │  └─ See your basic profile info                 │
│  ├─ User clicks "Allow" or "Deny"                  │
│  └─ Google redirects with auth code                │
└──────────────────────────────────────────────────────┘
        │
        ▼
Backend OAuth Callback:
  1. Exchange code for access_token + refresh_token
  2. Fetch user profile from Google
  3. Create/find user in database
  4. Store Gmail tokens (encrypted)
  5. Create JWT for frontend
  6. Redirect: /auth/callback?token=JWT&oauth_success=true
        │
        ▼
Frontend [AuthCallback Component]
  1. Retrieve JWT from URL
  2. api.setToken(JWT)
  3. emailService.setToken(JWT)
  4. sessionStorage.getItem('email_date_range')
  5. Call emailService.syncEmailsWithRange(dateRange)
        │
        ▼
POST /api/email/sync-with-range {
  date_range: "30_days",
  max_emails: 100
}
        │
        ▼
Backend Email Sync:
  1. Use stored Gmail token
  2. Query Gmail API for emails
  3. Parse each email:
     ├─ Extract amounts
     ├─ Find merchants
     ├─ Detect dates
     └─ Categorize
  4. Store transactions in DB
  5. Detect leaks
  6. Generate AI insights
        │
        ▼
Response: {
  status: "success",
  emails_processed: 45,
  transactions_found: 23,
  message: "..."
}
        │
        ▼
Frontend shows success message
        │
        ▼
Redirect to / (home)
  └─ Show results in Dashboard
```

---

## 6. PASSWORD ENCRYPTION FLOW

```
User enters password: "MyPassword123!"
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  FRONTEND ENCRYPTION (crypto.ts)                    │
│                                                     │
│  1. Load RSA public key (hardcoded in code):       │
│     ─────BEGIN PUBLIC KEY─────                    │
│     MIIBIjANBgkqhkiG...                           │
│     ─────END PUBLIC KEY─────                      │
│                                                     │
│  2. Use Web Crypto API:                            │
│     crypto.subtle.importKey(...)                   │
│                                                     │
│  3. Encrypt with RSA-OAEP:                         │
│     const encrypted = await crypto.subtle.encrypt(│
│       { name: 'RSA-OAEP' },                        │
│       publicKey,                                   │
│       encodedPassword                             │
│     )                                              │
│                                                     │
│  4. Base64 encode result:                          │
│     btoa(encrypted) → "vN2k3j/VK9d..."            │
│                                                     │
│  5. Send in request body:                          │
│     {                                              │
│       email: "user@example.com",                   │
│       password: "vN2k3j/VK9d...",                 │
│       ...                                          │
│     }                                              │
└────────┬────────────────────────────────────────────┘
         │
         │ HTTP Request
         ▼
┌─────────────────────────────────────────────────────┐
│  BACKEND DECRYPTION (crypto.py)                     │
│                                                     │
│  1. Receive encrypted password as base64 string    │
│                                                     │
│  2. Base64 decode:                                 │
│     base64.b64decode("vN2k3j/VK9d...")           │
│                                                     │
│  3. Load RSA private key:                          │
│     (Must match public key!)                       │
│                                                     │
│  4. Decrypt with RSA private key:                  │
│     decrypted = decrypt_with_private_key(         │
│       encrypted_bytes,                             │
│       private_key                                  │
│     )                                              │
│     → "MyPassword123!"                             │
│                                                     │
│  5. Hash for storage (bcrypt):                     │
│     hashed = pwd_context.hash("MyPassword123!")   │
│     → "$2b$12$abcdefgh..."                        │
│                                                     │
│  6. Store in database:                             │
│     user.hashed_password = hashed                  │
│                                                     │
└────────┬────────────────────────────────────────────┘
         │
         ▼
✅ Password securely stored
   Never stored in plain text!
```

---

## 7. API CALL PATTERN

```
ALL API CALLS follow this pattern:

Frontend Component
        │
        ▼
[Call API Service Method]
    api.auth.login(email, password)
        │
        ▼
    ┌──────────────────────────────────────────┐
    │  private async request<T>(               │
    │    endpoint: string,                     │
    │    options: RequestOptions               │
    │  ): Promise<T> {                         │
    │                                          │
    │    // 1. Build headers                   │
    │    const headers = {                     │
    │      'Content-Type': 'application/json', │
    │      ...options.headers                  │
    │    }                                      │
    │                                          │
    │    // 2. Add auth token if available     │
    │    if (this.token) {                     │
    │      headers['Authorization'] =          │
    │        `Bearer ${this.token}`            │
    │    }                                      │
    │                                          │
    │    // 3. Make fetch request              │
    │    const response = await fetch(         │
    │      `${this.baseUrl}${endpoint}`,       │
    │      { method, headers, body: ... }     │
    │    )                                      │
    │                                          │
    │    // 4. Handle errors                   │
    │    if (!response.ok) {                   │
    │      if (response.status === 401) {      │
    │        // Token expired/invalid          │
    │        this.setToken(null)               │
    │        window.location.href = '/login'   │
    │      }                                    │
    │      throw new Error(...)                │
    │    }                                      │
    │                                          │
    │    // 5. Parse and return JSON           │
    │    return response.json()                │
    │  }                                        │
    └──────────────────────────────────────────┘
        │
        ▼
   HTTP Request
   POST /api/auth/login
   Authorization: Bearer eyJhbGc...
   Content-Type: application/json
   {
     "email": "user@example.com",
     "password": "vN2k3j/VK9d...",
     "remember_me": false
   }
        │
        ▼
   Backend Processing
   ├─ Validate request
   ├─ Decrypt password
   ├─ Query database
   ├─ Verify credentials
   └─ Generate JWT token
        │
        ▼
   Response 200 OK
   {
     "access_token": "eyJhbGc...",
     "token_type": "bearer",
     "user": { ... }
   }
        │
        ▼
   Frontend Receives
        │
        ├─ api.setToken(access_token)
        │  └─ localStorage['auth_token'] = token
        │
        └─ Component updates state
           └─ Navigates to /
```

---

## 8. COMPONENT DEPENDENCY TREE

```
App.tsx
├── Login.tsx
│   ├── AuthLayout.tsx
│   ├── ForgotPasswordModal (inline)
│   └── authService
│
├── Signup.tsx
│   ├── AuthLayout.tsx
│   ├── PolicyModal.tsx
│   └── authService
│
├── AuthCallback.tsx
│   ├── ConsentModal.tsx
│   ├── emailService
│   └── api
│
├── AnalysisPage.tsx ⭐ MAIN APP
│   ├── DataImport.tsx
│   │   └── FileInput + DateRangeSelector
│   ├── Dashboard.tsx
│   │   ├── StatsCard (inline)
│   │   ├── Recharts.LineChart
│   │   └── React Markdown
│   └── authService
│
├── VerifyEmail.tsx
│   └── api.auth
│
├── ResetPassword.tsx
│   └── api.auth
│
├── TermsOfService.tsx
│
├── PrivacyPolicy.tsx
│
└── NotFound.tsx
```

---

## 9. DATA FLOW IN AnalysisPage (MAIN APP)

```
Component Mounts
    │
    ├─ useEffect → Fetch current user
    │  └─ GET /api/auth/me
    │     └─ setUserName()
    │
    ├─ useEffect → Check OAuth callback in URL
    │  ├─ if oauth_success=true && access_token
    │  ├─ api.setToken(access_token)
    │  ├─ Retrieve date_range from sessionStorage
    │  └─ Call handleEmailScrape()
    │
    └─ Render initial UI
       ├─ Header with userName + logout button
       └─ DataImport component (or Dashboard if data loaded)
              │
              ├─ Option 1: File Upload
              │  ├─ User selects file
              │  ├─ handleFileChange() → onFileUpload(file)
              │  ├─ POST /analyze
              │  ├─ If locked PDF (423): Show password modal
              │  ├─ On success: setData(result)
              │  └─ Re-render with Dashboard
              │
              ├─ Option 2: Email Connect
              │  ├─ User clicks "Connect Gmail"
              │  ├─ sessionStorage['email_date_range'] = range
              │  ├─ GET /api/auth/google/signup
              │  ├─ Redirect to Google OAuth
              │  ├─ (User returns with token in URL)
              │  ├─ handleEmailScrape(tokenInfo, dateRange)
              │  ├─ POST /api/scrape-emails ⚠️
              │  ├─ On success: setData(result)
              │  └─ Re-render with Dashboard
              │
              └─ Password Modal (if PDF locked)
                 ├─ handlePasswordSubmit()
                 ├─ Re-call POST /analyze with password
                 └─ setData(result)
```

---

## 10. STATE LIFECYCLE

```
Component loads
    │
    ├─ Initial State:
    │  ├─ data = null
    │  ├─ loading = false
    │  ├─ userName = null
    │  ├─ showPasswordInput = false
    │  └─ etc.
    │
    ├─ Fetch user info
    │  └─ setLoading(true)
    │     └─ api.getCurrentUser()
    │        └─ setUserName(result)
    │           └─ setLoading(false)
    │
    ├─ User uploads file
    │  └─ setLoading(true)
    │     └─ fetch(/analyze)
    │        ├─ If 423: 
    │        │  ├─ setShowPasswordInput(true)
    │        │  └─ setFileToRetry(file)
    │        │
    │        └─ If 200:
    │           ├─ setData(result)
    │           ├─ setShowPasswordInput(false)
    │           └─ setLoading(false)
    │
    └─ Dashboard re-renders with data
       └─ data !== null → Shows Dashboard instead of DataImport
          └─ User can click "Back to Upload"
             └─ onReset() → setData(null)
                └─ Re-shows DataImport
```

---

## 11. TOKEN LIFECYCLE

```
Login Successful
    │
    └─ Response: { access_token: "eyJhbGc..." }
        │
        └─ api.setToken(token)
            │
            ├─ this.token = token
            │
            └─ localStorage.setItem('auth_token', token)
                │
                └─ Token stored ✅
                    │
                    ├─ Valid for 30 minutes
                    ├─ Attached to all API requests:
                    │  Authorization: Bearer {token}
                    │
                    └─ Expiration Options:
                       ├─ Auto-refresh (not implemented)
                       ├─ Redirect to login (on 401)
                       └─ Manual logout
```

---

## 12. ERROR HANDLING FLOW

```
API Request
    │
    ├─ Network Error
    │  └─ catch (err)
    │     └─ setError(err.message)
    │        └─ Show error toast/modal
    │
    ├─ Response 401 (Unauthorized)
    │  └─ Token invalid/expired
    │     ├─ api.setToken(null)
    │     ├─ localStorage cleared
    │     └─ window.location.href = '/login'
    │
    ├─ Response 4xx (Client Error)
    │  └─ const error = await response.json()
    │     └─ setError(error.detail)
    │        └─ Show user-friendly error message
    │
    ├─ Response 5xx (Server Error)
    │  └─ Retry logic (not implemented)
    │     └─ Show "Server error, try again later"
    │
    └─ Success (2xx)
       └─ return response.json()
          └─ Process data
```

---

## 13. ROUTING STRUCTURE

```
App.tsx Router Configuration:

PUBLIC ROUTES (No auth required)
├── /login                  → Login.tsx
├── /signup                 → Signup.tsx
├── /forgot-password        → Modal in Login.tsx
├── /auth/callback          → AuthCallback.tsx
├── /verify-email?token=    → VerifyEmail.tsx
├── /reset-password?token=  → ResetPassword.tsx
├── /terms                  → TermsOfService.tsx
└── /privacy                → PrivacyPolicy.tsx

PROTECTED ROUTES (Auth required via PrivateRoute)
├── /                       → AnalysisPage.tsx
└── /onboarding             → AnalysisPage.tsx (same)

CATCH-ALL ROUTE
└── *                       → Navigate to /
```

---

## 14. COMPONENT COMMUNICATION PATTERN

```
Parent Component
    │
    ├─ Props down (data flow)
    │  └─ <ChildComponent 
    │       data={data}
    │       onEvent={handleEvent}
    │     />
    │
    └─ Callbacks up (event handling)
       ├─ ChildComponent triggers onEvent()
       ├─ Parent receives in callback
       ├─ Parent updates state
       └─ Parent re-renders with new props

Example: AnalysisPage → DataImport → Dashboard

AnalysisPage (has state: data, loading)
    │
    ├─ Pass props:
    │  └─ <DataImport 
    │       onFileUpload={handleUpload}
    │       onEmailConnect={handleEmailScrape}
    │       isLoading={loading}
    │     />
    │
    ├─ DataImport renders file/email options
    │  │
    │  └─ User interacts
    │     └─ Calls onFileUpload(file) or onEmailConnect(tokenInfo)
    │
    └─ AnalysisPage.handleUpload/handleEmailScrape called
       ├─ setLoading(true)
       ├─ Make API request
       ├─ setData(result)
       └─ setLoading(false)
           └─ Re-render:
              ├─ DataImport hidden (loading)
              └─ Dashboard shown (data exists)
```

---

## 15. ENVIRONMENT & CONFIGURATION

```
Frontend Configuration:
├─ Vite Config (vite.config.ts)
│  ├─ React plugin
│  ├─ Alias: @ → src/
│  └─ Build output: dist/
│
├─ TypeScript (tsconfig.json)
│  ├─ Target: ES2020
│  └─ Strict mode enabled
│
├─ Tailwind CSS (tailwind.config.js)
│  ├─ Custom colors
│  └─ Theme extensions
│
└─ Environment Variables (.env)
   ├─ VITE_API_BASE_URL=http://127.0.0.1:8000 (hardcoded)
   └─ VITE_FRONTEND_URL (for OAuth callback)

Backend Configuration (from frontend perspective):
├─ Base URL: http://127.0.0.1:8000
├─ CORS enabled for frontend origin
├─ Google OAuth configured
├─ SMTP email service setup
└─ JWT secret key configured
```

---

**All diagrams created: ✅**
These visualizations should help you understand the complete frontend architecture and data flow.

For detailed code-level information, refer to `FRONTEND_GUIDE.md` and `FRONTEND_API_MAPPING.md`.

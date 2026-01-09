# FRONTEND API CALL MAPPING - Quick Reference

**Created for**: Backend Developers  
**Purpose**: Shows every API call the frontend makes and what backend endpoint should handle it

---

## QUICK CHECKLIST: DOES YOUR BACKEND HAVE THESE ENDPOINTS?

### Authentication (8 total)
- [ ] `POST /api/auth/login` - Email/password login
- [ ] `POST /api/auth/signup` - User registration
- [ ] `GET /api/auth/me` - Get current user
- [ ] `POST /api/auth/logout` - Logout
- [ ] `POST /api/auth/forgot-password` - Request password reset email
- [ ] `POST /api/auth/reset-password` - Reset password with token
- [ ] `POST /api/auth/validate-reset-token` - Validate reset token
- [ ] `POST /api/auth/verify-email` - Verify email with token
- [ ] `GET /api/auth/check-email` - Check if email exists
- [ ] `POST /api/auth/change-password` - Change password (authenticated)
- [ ] `GET /api/auth/login` - Initiate Google login (returns OAuth URL)
- [ ] `GET /api/auth/google/signup` - Initiate Google signup (returns OAuth URL)
- [ ] `POST /api/auth/callback` - Handle OAuth callback (backend route)
- [ ] `POST /api/auth/resend-verification` - Resend verification email
- [ ] `POST /api/auth/accept-terms` - Accept terms & privacy

### Email (4 total)
- [ ] `POST /api/email/sync` - Sync emails (with days_back, max_emails, use_ai)
- [ ] `POST /api/email/sync-with-range` - Sync emails (with date_range preset)
- [ ] `GET /api/email/preview?limit=10` - Preview emails before sync
- [ ] `GET /api/email/status` - Get email sync status

### Transactions (6 total)
- [ ] `GET /api/transactions` - Get transactions (with pagination & filters)
- [ ] `GET /api/transactions/stats?month_year=2024-01` - Get monthly stats
- [ ] `POST /api/transactions` - Create transaction
- [ ] `PUT /api/transactions/{id}` - Update transaction
- [ ] `DELETE /api/transactions/{id}` - Delete transaction
- [ ] `POST /api/transactions/upload-csv` - Upload CSV file

### Leaks (4 total)
- [ ] `POST /api/leaks/detect` - Trigger leak detection
- [ ] `GET /api/leaks` - Get all leaks
- [ ] `GET /api/leaks/subscriptions` - Get detected subscriptions
- [ ] `PUT /api/leaks/leaks/{id}/resolve` - Mark leak as resolved

### Other (1 total)
- [ ] `GET /health` - Health check

### ⚠️ CRITICAL - May Not Exist (Need to check):
- [ ] `POST /analyze` - Direct file upload & analysis (legacy endpoint?)
- [ ] `POST /api/scrape-emails` - Email scraping with OAuth tokens (may be `/api/email/sync-with-range`)

---

## AUTHENTICATION ENDPOINTS - DETAILED

### 1. POST /api/auth/login
**Frontend Call**:
```typescript
authService.login(email, password, rememberMe)
```
**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "encrypted_base64_string",
  "remember_me": false
}
```
**Response Expected**:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```
**Used By**: Login.tsx  
**Storage**: Token stored in `localStorage['auth_token']`

---

### 2. POST /api/auth/signup
**Frontend Call**:
```typescript
authService.signup(email, password, username, name, termsAccepted, privacyAccepted)
```
**Request Body**:
```json
{
  "email": "newuser@example.com",
  "password": "encrypted_base64_string",
  "username": "john_doe",
  "name": "John Doe",
  "terms_accepted": true,
  "privacy_accepted": true
}
```
**Response Expected**:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "message": "Verification email sent"
}
```
**Used By**: Signup.tsx  
**Flow**: Creates user → Sends verification email → Frontend shows success

---

### 3. GET /api/auth/me
**Frontend Call**:
```typescript
authService.getCurrentUser()
```
**Request**: No body, uses Authorization header
**Response Expected**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe"
}
```
**Used By**: AnalysisPage.tsx (to display user name in header)

---

### 4. POST /api/auth/logout
**Frontend Call**:
```typescript
authService.logout()
```
**Request**: No body, empty POST  
**Response Expected**:
```json
{
  "message": "Logged out successfully"
}
```
**Used By**: AnalysisPage.tsx logout button

---

### 5. POST /api/auth/forgot-password
**Frontend Call**:
```typescript
authService.forgotPassword(email)
```
**Request Body**:
```json
{
  "email": "user@example.com"
}
```
**Response Expected**:
```json
{
  "message": "Reset link sent to email"
}
```
**Used By**: Login.tsx (in forgot password modal)

---

### 6. POST /api/auth/validate-reset-token
**Frontend Call**:
```typescript
authService.validateResetToken(token)
```
**Request Body**:
```json
{
  "token": "reset_token_from_email"
}
```
**Response Expected**:
```json
{
  "valid": true,
  "email": "user@example.com"
}
```
**Used By**: ResetPassword.tsx (validate before showing form)

---

### 7. POST /api/auth/reset-password
**Frontend Call**:
```typescript
authService.resetPassword(token, password)
```
**Request Body**:
```json
{
  "token": "reset_token_from_email",
  "password": "encrypted_base64_string"
}
```
**Response Expected**:
```json
{
  "message": "Password reset successfully"
}
```
**Used By**: ResetPassword.tsx (submit new password)

---

### 8. POST /api/auth/verify-email
**Frontend Call**:
```typescript
authService.verifyEmail(token)
```
**Request Body**:
```json
{
  "token": "verification_token_from_email"
}
```
**Response Expected**:
```json
{
  "message": "Email verified successfully"
}
```
**Used By**: VerifyEmail.tsx (when user clicks link from email)

---

### 9. GET /api/auth/check-email
**Frontend Call**:
```typescript
authService.checkEmail(email)
```
**Request**: Query string `?email=user@example.com`  
**Response Expected**:
```json
{
  "exists": false
}
```
**Used By**: Signup.tsx (real-time email existence check)

---

### 10. POST /api/auth/change-password
**Frontend Call**:
```typescript
authService.changePassword(currentPassword, newPassword)
```
**Request Body**:
```json
{
  "current_password": "encrypted_base64_string",
  "new_password": "encrypted_base64_string"
}
```
**Response Expected**:
```json
{
  "message": "Password changed successfully"
}
```
**Used By**: Not yet in UI (would be in settings page)

---

### 11. GET /api/auth/login
**Frontend Call**:
```typescript
authService.initiateGoogleLogin()
```
**Request**: No body, GET request  
**Response Expected**:
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "state": "random_state_string"
}
```
**Used By**: Login.tsx ("Login with Google" button)  
**Then**: Frontend redirects to authorization_url

---

### 12. GET /api/auth/google/signup
**Frontend Call**:
```typescript
authService.initiateGoogleSignup()
```
**Request**: No body, GET request  
**Response Expected**:
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "state": "random_state_string",
  "action": "signup"
}
```
**Used By**: Signup.tsx ("Signup with Google" button) & DataImport.tsx ("Connect Gmail" button)

---

### 13. OAuth Callback (Backend Route)
**Frontend**: After Google OAuth, Google redirects to backend callback URL  
**Backend Responsibility**:
1. Exchange authorization code for access token
2. Fetch user profile from Google
3. Create or find user in database
4. Store Gmail access token (encrypted)
5. Create JWT token for frontend
6. Redirect to: `{FRONTEND_URL}/auth/callback?token=xxx&oauth_success=true`

**Frontend Handler**: AuthCallback.tsx

---

## EMAIL ENDPOINTS - DETAILED

### 1. POST /api/email/sync
**Frontend Call**:
```typescript
api.syncEmails(daysBack, maxEmails, useAi)
```
**Request Body**:
```json
{
  "days_back": 30,
  "max_emails": 100,
  "use_ai": false
}
```
**Response Expected**:
```json
{
  "status": "success",
  "emails_processed": 45,
  "transactions_found": 23,
  "message": "Synced 45 emails and found 23 transactions"
}
```
**Used By**: AuthCallback.tsx (manual trigger)

---

### 2. POST /api/email/sync-with-range
**Frontend Call**:
```typescript
emailService.syncEmailsWithRange(dateRange, maxEmails)
// dateRange: '30_days' | '60_days' | '90_days' | '1_year'
```
**Request Body**:
```json
{
  "date_range": "30_days",
  "max_emails": 100
}
```
**Response Expected**:
```json
{
  "status": "success",
  "emails_processed": 45,
  "transactions_found": 23,
  "message": "Synced 45 emails and found 23 transactions"
}
```
**Used By**: AuthCallback.tsx (called after OAuth from DataImport)

---

### 3. GET /api/email/preview
**Frontend Call**:
```typescript
api.previewEmails(limit)
```
**Request**: Query string `?limit=10`  
**Response Expected**:
```json
{
  "total_emails": 150,
  "transactions": [
    {
      "email_id": "msg_12345",
      "date": "2024-01-15",
      "amount": 99.99,
      "trans_type": "debit",
      "merchant": "Netflix",
      "category": "Entertainment",
      "category_confidence": 0.95
    }
  ]
}
```
**Used By**: Could be used in a preview modal (not currently in UI)

---

### 4. GET /api/email/status
**Frontend Call**:
```typescript
api.getEmailSyncStatus()
```
**Request**: No body, uses Authorization header  
**Response Expected**:
```json
{
  "last_sync": "2024-01-20T15:30:00",
  "total_emails_synced": 150,
  "total_transactions": 45,
  "sync_in_progress": false
}
```
**Used By**: Could be used to show sync history (not currently in UI)

---

## TRANSACTION ENDPOINTS - DETAILED

### 1. GET /api/transactions
**Frontend Call**:
```typescript
api.getTransactions({page, page_size, trans_type, category_id, search})
```
**Request**: Query string parameters  
**Example**: `/api/transactions?page=1&page_size=20&trans_type=debit&category_id=5`

**Response Expected**:
```json
{
  "total": 125,
  "page": 1,
  "page_size": 20,
  "transactions": [
    {
      "id": 1,
      "date": "2024-01-15",
      "amount": 99.99,
      "trans_type": "debit",
      "merchant": "Netflix",
      "category_name": "Entertainment",
      "category_icon": "🎬",
      "bank_name": "Chase",
      "description": "Monthly subscription"
    }
  ]
}
```
**Used By**: Not currently in UI (for future transaction list page)

---

### 2. GET /api/transactions/stats
**Frontend Call**:
```typescript
api.getMonthlyStats(monthYear)
// monthYear: '2024-01' or undefined (current month)
```
**Request**: Query string `?month_year=2024-01` or no params  
**Response Expected**:
```json
{
  "month_year": "2024-01",
  "total_income": 5000.00,
  "total_expenses": 3200.50,
  "net_savings": 1799.50,
  "savings_rate": 0.36,
  "category_breakdown": [
    {
      "category_id": 1,
      "category_name": "Entertainment",
      "category_icon": "🎬",
      "category_color": "#FF6B6B",
      "total_amount": 299.98,
      "transaction_count": 3,
      "percentage": 9.4
    }
  ]
}
```
**Used By**: Not currently in UI (for statistics page)

---

### 3. POST /api/transactions
**Frontend Call**:
```typescript
api.createTransaction({date, amount, trans_type, merchant, category_id, description})
```
**Request Body**:
```json
{
  "date": "2024-01-15",
  "amount": 99.99,
  "trans_type": "debit",
  "merchant": "Netflix",
  "category_id": 5,
  "description": "Monthly subscription"
}
```
**Response Expected**:
```json
{
  "id": 42,
  "date": "2024-01-15",
  "amount": 99.99,
  "trans_type": "debit",
  "merchant": "Netflix",
  "category_id": 5
}
```
**Used By**: Not currently in UI (would be in manual transaction add)

---

### 4. PUT /api/transactions/{id}
**Frontend Call**:
```typescript
api.updateTransaction(id, {category_id, merchant, description})
```
**Request Body**:
```json
{
  "category_id": 6,
  "merchant": "Netflix Updated",
  "description": "Updated description"
}
```
**Response Expected**:
```json
{
  "message": "Transaction updated"
}
```
**Used By**: Not currently in UI (would be in transaction edit)

---

### 5. DELETE /api/transactions/{id}
**Frontend Call**:
```typescript
api.deleteTransaction(id)
```
**Request**: No body, uses Authorization header  
**Response Expected**:
```json
{
  "message": "Transaction deleted"
}
```
**Used By**: Not currently in UI (would be in transaction delete)

---

### 6. POST /api/transactions/upload-csv
**Frontend Call**:
```typescript
api.uploadCsv(file)
```
**Request**: FormData with file  
```
Content-Type: multipart/form-data
Body: {
  file: <File object>
}
```

**Response Expected**:
```json
{
  "status": "success",
  "transactions_created": 23,
  "duplicates_skipped": 2,
  "message": "Processed 23 transactions"
}
```
**Used By**: Not directly called in current UI (file upload uses `/analyze` endpoint instead)

---

## LEAK ENDPOINTS - DETAILED

### 1. POST /api/leaks/detect
**Frontend Call**:
```typescript
api.detectLeaks()
```
**Request**: No body  
**Response Expected**:
```json
{
  "message": "Leak detection completed"
}
```
**Used By**: Could be called to manually trigger detection (not in UI)

---

### 2. GET /api/leaks
**Frontend Call**:
```typescript
api.getLeaks()
```
**Request**: No body, uses Authorization header  
**Response Expected**:
```json
[
  {
    "id": 1,
    "leak_type": "Subscription",
    "title": "Netflix",
    "description": "Monthly recurring charge",
    "severity": "medium",
    "detected_amount": 99.99,
    "frequency": "monthly",
    "created_at": "2024-01-15T10:30:00"
  },
  {
    "id": 2,
    "leak_type": "Spending Anomaly",
    "title": "High Amazon spending",
    "description": "Unusual spending pattern detected",
    "severity": "low",
    "detected_amount": 450.00,
    "frequency": "one-time",
    "created_at": "2024-01-18T14:45:00"
  }
]
```
**Used By**: Dashboard.tsx (leak list display)

---

### 3. GET /api/leaks/subscriptions
**Frontend Call**:
```typescript
api.getSubscriptions()
```
**Request**: No body, uses Authorization header  
**Response Expected**:
```json
[
  {
    "id": 1,
    "name": "Netflix",
    "amount": 99.99,
    "interval_days": 30,
    "next_expected_date": "2024-02-15",
    "merchant": "Netflix Inc.",
    "is_active": true
  },
  {
    "id": 2,
    "name": "Gym Membership",
    "amount": 49.99,
    "interval_days": 30,
    "next_expected_date": "2024-02-01",
    "merchant": "FitnessPro",
    "is_active": true
  }
]
```
**Used By**: Not currently in UI (could be used in subscriptions page)

---

### 4. PUT /api/leaks/leaks/{id}/resolve
**Frontend Call**:
```typescript
api.resolveLeak(id)
```
**Request**: No body  
**Response Expected**:
```json
{
  "message": "Leak marked as resolved"
}
```
**Used By**: Could be called when user resolves a leak (not in UI)

---

## OTHER ENDPOINTS

### GET /health
**Frontend Call**:
```typescript
api.healthCheck()
```
**Request**: No body  
**Response Expected**:
```json
{
  "status": "healthy",
  "service": "Financial Leak Detector",
  "version": "1.0.0"
}
```
**Used By**: Can be used to verify backend is running

---

## ⚠️ LEGACY/UNCERTAIN ENDPOINTS

### POST /analyze
**Where it's called**: AnalysisPage.tsx, line ~120
```typescript
const response = await fetch('http://localhost:8000/analyze', {
    method: 'POST',
    body: formData,
});
```
**What frontend expects**:
```json
{
  "leaks": [...],
  "transactions": [...],
  "ai_insights": "string",
  "summary": {
    "total_spend": 0,
    "transaction_count": 0
  }
}
```
**Status**: ⚠️ **Need to verify if this endpoint exists**  
**Possible Fix**: This should probably be `/api/transactions/upload-csv`

---

### POST /api/scrape-emails
**Where it's called**: AnalysisPage.tsx, line ~75
```typescript
const response = await fetch('http://localhost:8000/api/scrape-emails', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        token: accessToken,
        refresh_token: refreshToken,
        email: email,
        date_range: dateRange
    }),
});
```
**What frontend expects**:
```json
{
  "leaks": [...],
  "transactions": [...],
  "ai_insights": "string"
}
```
**Status**: ⚠️ **Need to verify if this endpoint exists**  
**Possible Fix**: This should probably be `/api/email/sync-with-range`

---

## PASSWORD ENCRYPTION - CRITICAL

### Frontend (crypto.ts)
```typescript
// Password is encrypted using RSA-OAEP before sending
const encryptedPassword = await encryptPassword(password);
// Sent as base64-encoded string in request body
```

**Public Key Used**:
```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLfHCozMxH2Mo
4lgOP+IJEPh5/G9y93Mid7t3VNcyyYDS7lbOaUvZ9/tv0t8vCeniRBwgnrxFgGio
8BQI2N1U0A8lSsDyJOwV5HCaRFqYhVtn9WSW6oMYD8b2F7y5wFTKc+q6xllq+DLg
iT5eaSocROi5BvCvUVNRxCeW0KkGb7R1Yb6lfA5NKd2IwWVbxFfvM+CkyR/CwNGq
JbFl2L6SL1OeEA8RZSflQXDkVr0bWGSI3mVPQmVVo8+tqn/BwQxEX+oY1dFBBp5y
XxGtJLe7LIRIMLnJ6hWM9fNpNQk3q8DfXwdvpTKhL2kJ0mP7KxQXQfr1OiEhDILp
/8dHdWQjAgMBAAE=
-----END PUBLIC KEY-----
```

### Backend (crypto.py)
**Must decrypt** using matching private key:
1. Decode base64 to bytes
2. Decrypt with RSA private key
3. Verify matches public key

**Then hash** for storage:
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash(decrypted_password)
```

---

## AUTHENTICATION FLOW SUMMARY

```
1. User submits form
   ↓
2. Frontend encrypts password with RSA public key
   ↓
3. Sends POST request with encrypted password
   ↓
4. Backend decrypts with RSA private key
   ↓
5. Backend hashes with bcrypt
   ↓
6. Backend stores hash in database
   ↓
7. Backend returns JWT token
   ↓
8. Frontend stores token in localStorage['auth_token']
   ↓
9. All subsequent requests include Authorization: Bearer {token}
```

---

## STATUS REPORT TEMPLATE

Use this to verify your backend implementation:

```
✅ = Implemented & tested
⚠️  = Implemented but not tested with frontend
❌ = Not implemented

AUTHENTICATION:
[ ] POST /api/auth/login
[ ] POST /api/auth/signup
[ ] GET /api/auth/me
[ ] POST /api/auth/logout
[ ] POST /api/auth/forgot-password
[ ] POST /api/auth/reset-password
[ ] POST /api/auth/validate-reset-token
[ ] POST /api/auth/verify-email
[ ] GET /api/auth/check-email
[ ] POST /api/auth/change-password
[ ] GET /api/auth/login (OAuth initiate)
[ ] GET /api/auth/google/signup (OAuth initiate)
[ ] OAuth callback handler
[ ] POST /api/auth/resend-verification
[ ] POST /api/auth/accept-terms

EMAIL:
[ ] POST /api/email/sync
[ ] POST /api/email/sync-with-range
[ ] GET /api/email/preview
[ ] GET /api/email/status

TRANSACTIONS:
[ ] GET /api/transactions
[ ] GET /api/transactions/stats
[ ] POST /api/transactions
[ ] PUT /api/transactions/{id}
[ ] DELETE /api/transactions/{id}
[ ] POST /api/transactions/upload-csv

LEAKS:
[ ] POST /api/leaks/detect
[ ] GET /api/leaks
[ ] GET /api/leaks/subscriptions
[ ] PUT /api/leaks/leaks/{id}/resolve

OTHER:
[ ] GET /health

CRITICAL ISSUES:
[ ] Password encryption/decryption implemented
[ ] JWT token generation & validation
[ ] CORS configured for frontend
[ ] OAuth Google integration
[ ] Email service setup (SMTP)
[ ] Database migrations
```

---

## TESTING CHECKLIST

```
Frontend Running: npm run dev (port 5173)
Backend Running: python main.py (port 8000)

Test Suite:
1. [ ] Sign up new user
2. [ ] Verify email
3. [ ] Log in with email/password
4. [ ] Log out
5. [ ] Forgot password flow
6. [ ] Reset password
7. [ ] Log in with Google
8. [ ] Connect Gmail & sync emails
9. [ ] Upload CSV file
10. [ ] View results dashboard
11. [ ] Check token refreshing (if implemented)
12. [ ] Verify CORS works
13. [ ] Test password encryption/decryption
14. [ ] Test leak detection
15. [ ] Test AI insights generation (if using Gemini)
```

---

**Last Updated**: January 2025  
**Frontend Version**: React 18 with TypeScript 5  
**Backend API Version**: 1.0.0

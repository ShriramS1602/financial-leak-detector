# FRONTEND COMPLETE GUIDE - Agentic Leak Detector

> **For Backend Developers**: Complete understanding of frontend architecture, data flow, API integration, and workflow.

---

## TABLE OF CONTENTS
1. [Tech Stack & Libraries](#tech-stack--libraries)
2. [Project Structure](#project-structure)
3. [Core Files Explained](#core-files-explained)
4. [Page Navigation Flow](#page-navigation-flow)
5. [Component Breakdown](#component-breakdown)
6. [API Service Layer](#api-service-layer)
7. [Data Flow & State Management](#data-flow--state-management)
8. [Authentication Flow](#authentication-flow)
9. [Email Sync Workflow](#email-sync-workflow)
10. [API-to-Backend Mapping](#api-to-backend-mapping)

---

## TECH STACK & LIBRARIES

### Core Framework
- **React 18.2.0** - UI library
- **TypeScript 5.2.2** - Type safety
- **Vite 5.0.8** - Build tool & dev server
- **React Router DOM 6.30.2** - Client-side routing

### UI & Styling
- **Tailwind CSS 3.3.6** - Utility-first CSS framework
- **Lucide React 0.292.0** - Icon library (used for all icons: Mail, Lock, Shield, etc.)
- **Recharts 2.15.4** - Chart/graph visualization library
- **React Markdown 9.0.0** - Render markdown content (for AI insights)

### Utilities
- **Axios 1.6.0** - HTTP client (installed but using fetch API instead)
- **Date-fns 2.30.0** - Date manipulation
- **Clsx 2.1.1** - Conditional CSS class merging
- **Tailwind Merge 3.4.0** - Intelligent Tailwind class merging
- **Terser 5.44.1** - Code minification

### Key Configuration Files
- **tsconfig.json** - TypeScript configuration
- **vite.config.ts** - Vite build configuration
- **tailwind.config.js** - Tailwind CSS customization
- **postcss.config.js** - PostCSS processing for Tailwind

---

## PROJECT STRUCTURE

```
frontend/
├── src/
│   ├── App.tsx                 # Main routing component
│   ├── main.tsx                # Entry point
│   ├── index.css               # Global styles
│   ├── vite-env.d.ts          # Vite type definitions
│   ├── components/             # Reusable UI components
│   │   ├── AuthLayout.tsx      # Left-side form container, right-side hero
│   │   ├── Dashboard.tsx       # Results display with leaks, stats, charts
│   │   ├── DataImport.tsx      # CSV upload & email sync options
│   │   ├── LoginPage.tsx       # Legacy (unused)
│   │   ├── DataSourceSelection.tsx  # (unused)
│   │   ├── Upload.tsx          # (unused)
│   │   ├── ConsentModal.tsx    # Gmail consent modal
│   │   └── PolicyModal.tsx     # Terms/Privacy policy modal
│   ├── pages/                  # Full page components
│   │   ├── Login.tsx           # Email/password login + forgot password modal
│   │   ├── Signup.tsx          # Registration with validation
│   │   ├── AuthCallback.tsx    # OAuth callback handler
│   │   ├── AnalysisPage.tsx    # Main app page (file upload & results)
│   │   ├── VerifyEmail.tsx     # Email verification from link
│   │   ├── ResetPassword.tsx   # Password reset from email link
│   │   ├── ForgotPassword.tsx  # (likely unused - modal in Login)
│   │   ├── TermsOfService.tsx  # Static terms page
│   │   ├── PrivacyPolicy.tsx   # Static privacy page
│   │   ├── LeakDashboard.tsx   # (unused/alternative)
│   │   ├── Subscriptions.tsx   # (unused)
│   │   ├── Onboarding.tsx      # (unused)
│   │   └── NotFound.tsx        # 404 page
│   ├── services/               # API communication
│   │   ├── api.ts              # Main API service class + authService export
│   │   └── emailService.ts     # Email-specific API calls
│   ├── hooks/                  # Custom React hooks
│   │   └── useTransactions.ts  # useTransactions, useMonthlyStats, useAuth
│   ├── types/                  # TypeScript type definitions
│   │   └── index.ts            # Transaction, Category, User, etc.
│   ├── utils/                  # Utility functions
│   │   └── crypto.ts           # RSA password encryption
│   └── lib/                    # (referenced but not in workspace)
│       └── utils.ts            # cn() function for class merging
├── index.html                  # HTML entry point
├── package.json                # Dependencies
├── tailwind.config.js          # Tailwind theme
├── vite.config.ts              # Vite config
└── tsconfig.json               # TypeScript config
```

---

## CORE FILES EXPLAINED

### 1. **index.html** - HTML Entry Point
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Money Manager - Personal Finance Tracker</title>
    <meta name="description" content="Track expenses and get smart insights from financial emails" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```
- **What it shows**: Just the mount point
- **Key elements**: `<div id="root">` - React mounts here

### 2. **main.tsx** - Entry Point
```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
);
```
- **What it does**: Initializes React and renders the App component
- **Flow**: React boots up → renders App.tsx

### 3. **App.tsx** - Main Routing Component
```typescript
function App() {
    return (
        <Router>
            <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />
                <Route path="/auth/callback" element={<AuthCallback />} />
                <Route path="/terms" element={<TermsOfService />} />
                <Route path="/privacy" element={<PrivacyPolicy />} />
                <Route path="/verify-email" element={<VerifyEmail />} />
                <Route path="/reset-password" element={<ResetPassword />} />
                
                {/* Protected Routes */}
                <Route path="/" element={<PrivateRoute><AnalysisPage /></PrivateRoute>} />
                <Route path="/onboarding" element={<PrivateRoute><AnalysisPage /></PrivateRoute>} />
            </Routes>
        </Router>
    );
}
```

**What it does**:
- Sets up all routes
- Defines `PrivateRoute` component that checks `localStorage.auth_token`
- Redirects unauthenticated users to `/login`

**All Routes**:
| Path | Component | Auth Required | Description |
|------|-----------|---------------|-------------|
| `/login` | Login | ❌ | Email/password login |
| `/signup` | Signup | ❌ | Registration |
| `/forgot-password` | ForgotPassword | ❌ | Password reset request |
| `/auth/callback` | AuthCallback | ❌ | OAuth callback handler |
| `/verify-email` | VerifyEmail | ❌ | Email verification |
| `/reset-password` | ResetPassword | ❌ | Password reset form |
| `/terms` | TermsOfService | ❌ | Static terms page |
| `/privacy` | PrivacyPolicy | ❌ | Static privacy page |
| `/` | AnalysisPage | ✅ | Main app (file upload & results) |
| `/onboarding` | AnalysisPage | ✅ | Same as `/` |
| `*` | Navigate to `/` | - | 404 redirect |

### 4. **types/index.ts** - Type Definitions
```typescript
export interface Transaction {
  id: number;
  date: string;
  amount: number;
  trans_type: 'credit' | 'debit';
  merchant: string;
  category_id?: number;
  category_name?: string;
  category_icon?: string;
  description?: string;
  bank_name?: string;
  email_id?: string;
  created_at: string;
}

export interface MonthlyStats {
  month_year: string;
  total_income: number;
  total_expenses: number;
  net_savings: number;
  savings_rate: number;
  category_breakdown: CategoryBreakdown[];
}

export interface User {
  id: number;
  email: string;
  name?: string;
  last_email_sync?: string;
  created_at: string;
}

export interface EmailSyncStatus {
  last_sync: string | null;
  total_emails_synced: number;
  total_transactions: number;
  sync_in_progress: boolean;
}
```

**Key Types Used Throughout App**:
- `Transaction` - Individual transaction from CSV/email
- `MonthlyStats` - Monthly summary statistics
- `User` - Current logged-in user
- `EmailSyncStatus` - Email sync progress/status
- `Category` - Transaction category with icon/color
- `Insight` - AI insight messages
- `PaginatedResponse<T>` - Generic paginated API responses

---

## PAGE NAVIGATION FLOW

```
Initial Load
    ↓
[Check localStorage.auth_token]
    ↓
    ├─→ Token Exists? → /
    └─→ No Token? → /login

┌─────────────────────────────────────────┐
│              AUTHENTICATION FLOW         │
└─────────────────────────────────────────┘

/login (Login.tsx)
  ├─ Enter email + password
  ├─ Or click "Login with Google"
  │  → Calls authService.initiateGoogleLogin()
  │  → Redirects to Google consent
  │  → Google redirects to /auth/callback
  ├─ On success → Navigate to /
  └─ On error → Show error message

/signup (Signup.tsx)
  ├─ Enter email, password, username, name
  ├─ Validate password strength (5 criteria)
  ├─ Validate email not exists
  ├─ Accept terms + privacy
  ├─ Or click "Signup with Google"
  └─ On success → Show success, prompt to verify email

/verify-email (VerifyEmail.tsx)
  ├─ Get token from URL query ?token=xxx
  ├─ Call api.auth.verifyEmail(token)
  ├─ Show status (loading/success/error)
  └─ On success → Redirect to /login

/forgot-password (Login.tsx - Modal)
  ├─ Enter email
  ├─ Call authService.forgotPassword(email)
  └─ Show success message

/reset-password (ResetPassword.tsx)
  ├─ Get token from URL query ?token=xxx
  ├─ Validate token → api.auth.validateResetToken(token)
  ├─ Enter new password (with validation)
  ├─ Call api.auth.resetPassword(token, password)
  └─ Redirect to /login

/auth/callback (AuthCallback.tsx)
  ├─ OAuth callback from Google
  ├─ Get token from URL query ?token=xxx
  ├─ Set token → api.setToken(token)
  ├─ Check if needs consent
  ├─ Sync emails → emailService.syncEmailsWithRange()
  └─ Redirect to /

┌─────────────────────────────────────────┐
│            MAIN APP FLOW                 │
└─────────────────────────────────────────┘

/ (AnalysisPage.tsx) - MAIN PAGE
  ├─ Fetch current user info
  ├─ Show "Upload file or Connect Gmail"
  │
  ├─ Option 1: CSV Upload
  │  ├─ Click "Upload Statement"
  │  ├─ Select CSV/Excel/PDF file
  │  ├─ POST /analyze (to backend)
  │  ├─ Show password modal if file locked
  │  └─ Show results in Dashboard
  │
  ├─ Option 2: Connect Gmail
  │  ├─ Click "Connect Gmail"
  │  ├─ Select date range (30/60/90 days, 1 year)
  │  ├─ Call authService.initiateGoogleSignup()
  │  ├─ Redirect to Google OAuth
  │  ├─ After OAuth → /auth/callback
  │  ├─ Call emailService.syncEmailsWithRange()
  │  └─ Show results
  │
  └─ Results Shown in Dashboard Component
     ├─ Stats cards (total spend, transaction count, leaks)
     ├─ Leak list with details
     ├─ Spending trend chart
     └─ AI insights (right sidebar)
```

---

## COMPONENT BREAKDOWN

### **1. AuthLayout.tsx** - Form Container Component
**Purpose**: Wraps login/signup pages with consistent styling

**What it shows**:
- **Left side (55% width)**:
  - Form container with glassmorphic design
  - Logo "FinGuard" with icon
  - Title + Subtitle from props
  - Children content (form)
  - Footer with Terms/Privacy links
  
- **Right side (45% width)** - Hidden on mobile:
  - Gradient background (indigo → slate)
  - Mock dashboard preview
  - Feature highlights:
    - Real-time Monitoring
    - Visual Analytics
    - AI-Powered Insights

**Key Props**:
```typescript
interface AuthLayoutProps {
    children: React.ReactNode;  // Form content
    title: string;              // "Login" or "Create Account"
    subtitle: string;           // Descriptive text
}
```

**Events/Buttons**:
- Privacy link → Opens PolicyModal (type: 'privacy')
- Terms link → Opens PolicyModal (type: 'terms')

**CSS Classes Used**:
- Tailwind gradient backgrounds
- Glassmorphism effects (backdrop-blur, backdrop blur)
- Responsive: `lg:w-[55%]` for left, `hidden lg:block` for right
- Animated blobs in background

---

### **2. DataImport.tsx** - Upload/Email Sync Selector
**Purpose**: Allows user to choose CSV upload or Gmail sync

**What it shows**:
- **Benefits section** (3 cards):
  - Detect Leaks icon
  - AI Insights icon
  - Secure & Private icon
  
- **Import options** (2 large cards):
  - **Left card**: CSV Upload
    - File input for `.csv`, `.xlsx`, `.pdf`
    - Click or drag-drop
    - Shows selected filename
    
  - **Right card**: Email Sync
    - Date range selector (30/60/90 days, 1 year)
    - "Connect Gmail" button
    - OAuth flow

**Key Props**:
```typescript
interface DataImportProps {
    onFileUpload: (file: File) => void;
    onEmailConnect: (tokenResponse: any, dateRange: DateRangeOption) => void;
    isLoading: boolean;
    isGoogleConfigured: boolean;
}
```

**Events**:
| Event | Handler | Does What |
|-------|---------|-----------|
| File selected | `handleFileChange()` | Sets filename, calls `onFileUpload(file)` |
| "Connect Gmail" click | `handleEmailSync()` | Stores dateRange in sessionStorage, redirects to OAuth |
| Loading | Shows spinner | Disables both options |

**State Variables**:
```typescript
const [selectedMethod, setSelectedMethod] = useState<'csv' | 'email' | null>(null);
const [fileName, setFileName] = useState('');
const [error, setError] = useState('');
const [dateRange, setDateRange] = useState<DateRangeOption>('30_days');
```

**OAuth Flow Here**:
```typescript
sessionStorage.setItem('email_date_range', dateRange);  // Save for after redirect
const response = await fetch('http://localhost:8000/api/auth/google/signup');
const data = await response.json();
window.location.href = data.authorization_url;  // Redirect to Google
```

---

### **3. Dashboard.tsx** - Results Display
**Purpose**: Shows analysis results (leaks, stats, insights, charts)

**What it shows**:
- **Back button** - Returns to upload screen
  
- **Stats Grid** (3 cards):
  - Total Spend: `$amount`
  - Transactions: `count` with avg per txn
  - Potential Leaks: `count` with severity warning
  
- **Left column (2/3 width)**:
  - **Leaks Section**:
    - List of detected leaks with:
      - Icon (subscription or alert)
      - Description
      - Type + Frequency
      - Amount
      - Confidence score
  - **Spending Trend Chart** (Recharts LineChart):
    - Mock data showing 4 weeks
    - X-axis: Week labels
    - Y-axis: Spending amounts
    - Blue line with dots
  
- **Right column (1/3 width)** - Sticky:
  - **AI Insights Section**:
    - Rendered from markdown
    - React Markdown component
    - Styled with prose classes

**Key Props**:
```typescript
interface DashboardProps {
    data: any;
    onReset: () => void;  // Back button callback
}
```

**Data Structure Expected**:
```typescript
{
  summary: {
    total_spend: number,
    transaction_count: number
  },
  leaks: [
    {
      type: 'Subscription' | 'Spending',
      frequency: string,
      description: string,
      amount: number,
      confidence: string
    }
  ],
  ai_insights: string,  // Markdown content
  raw_data_preview: []  // Unused
}
```

**StatsCard Sub-component**:
```typescript
function StatsCard({ title, value, icon, trend, color }) {
    // Renders single stat card with icon, value, trend
    // Colors: 'primary', 'accent', 'danger'
}
```

---

### **4. ConsentModal.tsx** - Gmail Consent Dialog
**Purpose**: Request user to accept Gmail data collection

**What it shows**:
- Modal overlay
- "Gmail Sync Consent" title
- Checkboxes to accept:
  - Read Gmail messages
  - Analyze for financial transactions
  - Store encrypted copies
- "Decline" and "Accept & Sync" buttons

**Key Props**:
```typescript
interface ConsentModalProps {
    isOpen: boolean;
    onSuccess: () => void;  // Called after acceptance
}
```

**Events**:
- "Accept" → Calls `onSuccess()`, syncs emails
- "Decline" → Closes modal, redirects to home

---

### **5. PolicyModal.tsx** - Terms/Privacy Modal
**Purpose**: Display Terms of Service or Privacy Policy

**What it shows**:
- Scrollable modal with policy content
- "Close" button
- Type: 'terms' or 'privacy'

**Key Props**:
```typescript
interface PolicyModalProps {
    isOpen: boolean;
    onClose: () => void;
    type: 'terms' | 'privacy';
}
```

---

## API SERVICE LAYER

### **services/api.ts** - Main API Service Class

**Base URL**: `http://127.0.0.1:8000`

**Token Management**:
```typescript
class ApiService {
    private token: string | null = null;
    
    setToken(token: string | null) {
        this.token = token;
        if (token) {
            localStorage.setItem('auth_token', token);
        } else {
            localStorage.removeItem('auth_token');
        }
    }
    
    // Adds Bearer token to all requests automatically
    private async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        // ... fetch call ...
    }
}
```

#### **Authentication Endpoints**

| Method | Endpoint | Request | Response | Notes |
|--------|----------|---------|----------|-------|
| POST | `/api/auth/login` | `{email, password (encrypted), remember_me}` | `{access_token, ...user data}` | Password encrypted via RSA before sending |
| POST | `/api/auth/signup` | `{email, password (encrypted), username, name, terms_accepted, privacy_accepted}` | `{access_token, ...user data}` | Same encryption, validates email uniqueness |
| POST | `/api/auth/logout` | `{}` | `{message}` | Clears token from localStorage |
| GET | `/api/auth/me` | Headers only | `{id, email, name}` | Current user info |
| POST | `/api/auth/forgot-password` | `{email}` | `{message}` | Sends reset link to email |
| POST | `/api/auth/reset-password` | `{token, password (encrypted)}` | `{message}` | Reset password using token |
| POST | `/api/auth/validate-reset-token` | `{token}` | `{valid: bool, email}` | Verify token before showing form |
| POST | `/api/auth/verify-email` | `{token}` | `{message}` | Verify email after signup |
| POST | `/api/auth/resend-verification` | `{email}` | `{message}` | Resend verification email |
| POST | `/api/auth/accept-terms` | `{}` | `{message}` | Accept terms/privacy |
| GET | `/api/auth/check-email` | Query: `?email=...` | `{exists: bool}` | Check if email already registered |
| POST | `/api/auth/change-password` | `{current_password (encrypted), new_password (encrypted)}` | `{message}` | Change password while logged in |

**OAuth Endpoints**:
```typescript
initiateGoogleLogin() → GET /api/auth/login → {authorization_url, state}
initiateGoogleSignup() → GET /api/auth/google/signup → {authorization_url, state, action}
```

**Location**: `/auth/callback` handles OAuth response

---

#### **Email Endpoints**

| Method | Endpoint | Request | Response | Notes |
|--------|----------|---------|----------|-------|
| POST | `/api/email/sync` | `{days_back, max_emails, use_ai}` | `{status, emails_processed, transactions_found, message}` | Sync emails from Gmail |
| POST | `/api/email/sync-with-range` | `{date_range, max_emails}` | `{status, emails_processed, transactions_found}` | Same but with preset date ranges |
| GET | `/api/email/preview` | Query: `?limit=10` | `{total_emails, transactions: [...]}` | Preview before full sync |
| GET | `/api/email/status` | Headers only | `{last_sync, total_emails_synced, total_transactions, sync_in_progress}` | Email sync status |

---

#### **Transaction Endpoints**

| Method | Endpoint | Request | Response | Notes |
|--------|----------|---------|----------|-------|
| GET | `/api/transactions` | Query: `?page=1&page_size=20&trans_type=debit&category_id=5&search=amazon` | `{total, page, page_size, transactions: [...]}` | Fetch transactions with filters |
| GET | `/api/transactions/stats` | Query: `?month_year=2024-01` | `{month_year, total_income, total_expenses, net_savings, savings_rate, category_breakdown: [...]}` | Monthly statistics |
| POST | `/api/transactions` | `{date, amount, trans_type, merchant, category_id, description}` | `{id, ...transaction}` | Create manual transaction |
| PUT | `/api/transactions/{id}` | `{category_id, merchant, description}` | `{message}` | Update transaction |
| DELETE | `/api/transactions/{id}` | Headers only | `{message}` | Delete transaction |
| POST | `/api/transactions/upload-csv` | FormData: `{file}` | `{transactions_created, ...}` | Upload CSV file |

---

#### **Leak Detection Endpoints**

| Method | Endpoint | Request | Response | Notes |
|--------|----------|---------|----------|-------|
| POST | `/api/leaks/detect` | `{}` | `{message}` | Trigger leak detection |
| GET | `/api/leaks` | Headers only | `[{id, leak_type, title, description, severity, detected_amount, frequency, created_at}, ...]` | Get all detected leaks |
| GET | `/api/leaks/subscriptions` | Headers only | `[{id, name, amount, interval_days, next_expected_date, merchant, is_active}, ...]` | Get detected subscriptions |
| PUT | `/api/leaks/leaks/{id}/resolve` | `{}` | `{message}` | Mark leak as resolved |

---

#### **Other Endpoints**

| Method | Endpoint | Response | Notes |
|--------|----------|----------|-------|
| GET | `/health` | `{status, service, version}` | Health check |

---

### **services/emailService.ts** - Email-Specific Service

```typescript
class EmailService {
    // Same token management as ApiService
    
    async syncEmailsWithRange(
        dateRange: DateRangeOption = '30_days',  // '30_days' | '60_days' | '90_days' | '1_year'
        maxEmails: number = 100
    ): Promise<EmailSyncResponse>
}
```

**Used in**: AuthCallback.tsx and DataImport.tsx

---

## DATA FLOW & STATE MANAGEMENT

### State Management Pattern (No Redux)
React uses **local component state** with `useState` hook.

#### **Global State (localStorage)**
- `auth_token` - JWT token for API requests
- `email_date_range` - Temporarily stores selected date range during OAuth redirect

#### **Component State Examples**

**Login.tsx**:
```typescript
const [email, setEmail] = useState('');
const [password, setPassword] = useState('');
const [rememberMe, setRememberMe] = useState(false);
const [error, setError] = useState('');
const [loading, setLoading] = useState(false);
const [showPassword, setShowPassword] = useState(false);
const [showForgotModal, setShowForgotModal] = useState(false);
```

**Signup.tsx**:
```typescript
const [formData, setFormData] = useState({
    username: '', name: '', email: '', password: '', confirmPassword: ''
});
const [termsAccepted, setTermsAccepted] = useState(false);
const [privacyAccepted, setPrivacyAccepted] = useState(false);
const [emailExists, setEmailExists] = useState(false);
const [passwordStrength, setPasswordStrength] = useState({ score: 0, label: '', color: '' });
```

**AnalysisPage.tsx**:
```typescript
const [data, setData] = useState<any>(null);           // Results data
const [loading, setLoading] = useState(false);         // Loading state
const [userName, setUserName] = useState<string | null>(null);  // Current user name
const [showPasswordInput, setShowPasswordInput] = useState(false); // PDF password modal
const [fileToRetry, setFileToRetry] = useState<File | null>(null);
const [password, setPassword] = useState("");
```

### Data Flow from User Input to UI

```
User Types Email & Password
    ↓
onClick handleSubmit() → setLoading(true)
    ↓
Call authService.login(email, password)
    ↓
API Request: POST /api/auth/login
    ↓
Response: {access_token, user_data}
    ↓
api.setToken(token) → localStorage.setItem('auth_token', token)
    ↓
navigate(redirectPath)
    ↓
PrivateRoute checks localStorage.auth_token → ✅ Allows access
    ↓
Show AnalysisPage
```

---

## AUTHENTICATION FLOW

### Complete Auth Lifecycle

```
┌──────────────────────────────────────────────┐
│        EMAIL/PASSWORD AUTHENTICATION         │
└──────────────────────────────────────────────┘

1. SIGNUP
   /signup page
   ├─ User enters: email, password, username, name
   ├─ Validations:
   │  ├─ Email format + uniqueness check
   │  ├─ Password strength (5 criteria)
   │  ├─ Terms & privacy checkboxes
   │  └─ Username required
   ├─ Frontend encrypts password (RSA)
   ├─ POST /api/auth/signup {email, password (encrypted), ...}
   ├─ Backend:
   │  ├─ Hash password (bcrypt)
   │  ├─ Create user
   │  ├─ Send verification email
   │  └─ Return access_token
   ├─ Frontend shows success message
   └─ User receives verification email

2. EMAIL VERIFICATION
   /verify-email?token=xxx
   ├─ User clicks link from email
   ├─ Frontend extracts token from URL
   ├─ POST /api/auth/verify-email {token}
   ├─ Backend verifies token + marks email as verified
   ├─ Frontend shows success + redirects to /login

3. LOGIN
   /login page
   ├─ User enters: email, password
   ├─ Optional: check "Remember Me"
   ├─ Frontend encrypts password (RSA)
   ├─ POST /api/auth/login {email, password (encrypted), remember_me}
   ├─ Backend:
   │  ├─ Find user by email
   │  ├─ Verify password
   │  ├─ Check email verified
   │  └─ Return access_token
   ├─ Frontend stores token in localStorage
   └─ Navigates to /

4. PASSWORD RESET
   /forgot-password (modal in /login)
   ├─ User enters email
   ├─ POST /api/auth/forgot-password {email}
   ├─ Backend:
   │  ├─ Find user
   │  ├─ Create reset token
   │  └─ Send reset link via email
   ├─ Frontend shows confirmation
   │
   /reset-password?token=xxx (from email link)
   ├─ User opens link from email
   ├─ Frontend validates token
   ├─ POST /api/auth/validate-reset-token {token}
   ├─ If valid, show password form
   ├─ User enters new password
   ├─ POST /api/auth/reset-password {token, password (encrypted)}
   ├─ Backend:
   │  ├─ Verify token
   │  ├─ Hash + update password
   │  └─ Invalidate token
   └─ Redirect to /login

┌──────────────────────────────────────────────┐
│           OAUTH AUTHENTICATION               │
└──────────────────────────────────────────────┘

1. GOOGLE LOGIN
   /login → Click "Login with Google"
   ├─ authService.initiateGoogleLogin()
   ├─ GET /api/auth/login → {authorization_url}
   ├─ window.location.href = authorization_url
   ├─ Redirects to Google consent screen
   └─ User grants permission
   
   Google redirects to /auth/callback?code=xxx
   ├─ Backend exchanges code for access_token
   ├─ Gets user profile from Google
   ├─ Finds or creates user
   ├─ Redirects to frontend: /auth/callback?token=xxx&oauth_success=true
   
   AuthCallback.tsx
   ├─ api.setToken(token)
   ├─ emailService.setToken(token)
   ├─ Checks if needs_consent=true
   ├─ If yes: show ConsentModal
   ├─ If no: sync emails (optional)
   └─ Navigate to /

2. GOOGLE SIGNUP
   /signup → Click "Signup with Google"
   ├─ Requires: terms_accepted=true, privacy_accepted=true
   ├─ authService.initiateGoogleSignup()
   ├─ GET /api/auth/google/signup → {authorization_url}
   ├─ Same flow as login
   └─ Creates new user account

TOKEN FLOW:
┌─────────────────────┐
│   JWT Access Token  │
├─────────────────────┤
│ Stored in:          │
│ localStorage        │
│                     │
│ Sent in all         │
│ requests as:        │
│ Authorization:      │
│ Bearer {token}      │
│                     │
│ Expires: 30 min     │
│ (or configured)     │
└─────────────────────┘

LOGOUT:
/anywhere
├─ Click logout button
├─ POST /api/auth/logout {}
├─ Frontend removes token
├─ localStorage.removeItem('auth_token')
└─ Redirect to /login

PASSWORD ENCRYPTION:
┌──────────────────────────────────────────┐
│ Frontend (utils/crypto.ts)               │
├──────────────────────────────────────────┤
│ 1. Load RSA public key (hardcoded)       │
│ 2. Encrypt password with RSA-OAEP       │
│ 3. Base64 encode encrypted password    │
│ 4. Send in JSON body                   │
│                                         │
│ Backend (app/crypto.py)                 │
│ 1. Receive base64 encrypted password    │
│ 2. Base64 decode                       │
│ 3. Decrypt with RSA private key         │
│ 4. Hash with bcrypt                    │
│ 5. Store hash in database              │
└──────────────────────────────────────────┘
```

---

## EMAIL SYNC WORKFLOW

```
USER INITIATES EMAIL SYNC:

1. DataImport Component
   ├─ User clicks "Connect Gmail"
   ├─ Selects date range (30/60/90 days, 1 year)
   ├─ sessionStorage.setItem('email_date_range', dateRange)
   ├─ handleEmailSync() called
   └─ Fetches: GET /api/auth/google/signup
              → {authorization_url, state, action}
   
2. Google OAuth
   ├─ Redirects to Google consent screen
   ├─ User grants:
   │  ├─ gmail.readonly - Read Gmail
   │  ├─ userinfo.email - Get email
   │  └─ userinfo.profile - Get profile
   ├─ Google redirects back with auth code
   
3. Backend OAuth Callback
   ├─ Exchanges code for access_token + refresh_token
   ├─ Fetches user profile from Google
   ├─ Finds or creates user account
   ├─ Stores Gmail tokens in database (encrypted)
   ├─ Creates JWT access_token for frontend
   └─ Redirects: /auth/callback?token=xxx&oauth_success=true
   
4. Frontend AuthCallback Component
   ├─ Receives JWT token from URL
   ├─ api.setToken(token)
   ├─ emailService.setToken(token)
   ├─ Retrieves dateRange from sessionStorage
   ├─ Calls: emailService.syncEmailsWithRange(dateRange, maxEmails)
   │         → POST /api/email/sync-with-range
   │            {date_range, max_emails}
   │         ← {status, emails_processed, transactions_found, message}
   ├─ Shows success message
   ├─ Cleans up URL
   └─ Navigates to /

5. Backend Email Sync
   ├─ Uses stored Gmail token
   ├─ Queries Gmail API for emails in date range
   ├─ Parses each email:
   │  ├─ Extract transaction details (regex or AI)
   │  ├─ Detect amounts, merchants, dates
   │  ├─ Categorize transactions
   │  └─ Store in database
   ├─ Returns count of processed emails + found transactions
   └─ Frontend shows results in Dashboard

EMAIL PARSING:
┌──────────────────────────────────────────────┐
│          Email Transaction Extraction        │
├──────────────────────────────────────────────┤
│ Input: Raw email subject + body              │
│                                              │
│ Method 1: Regex Patterns                     │
│ ├─ Match amount patterns: $123.45            │
│ ├─ Match dates: YYYY-MM-DD                   │
│ ├─ Match merchant keywords                   │
│ └─ Extract from common email templates       │
│                                              │
│ Method 2: AI Parsing (if enabled)           │
│ ├─ Send email to Gemini API                  │
│ ├─ Request structured extraction             │
│ └─ Return parsed JSON                        │
│                                              │
│ Output: Transaction object                   │
│ ├─ amount: float                             │
│ ├─ date: datetime                            │
│ ├─ merchant: string                          │
│ ├─ category: string                          │
│ └─ trans_type: 'debit' | 'credit'           │
└──────────────────────────────────────────────┘

AVAILABLE EMAIL SYNC ENDPOINTS:

GET /api/email/preview?limit=10
├─ Returns: {total_emails, transactions: [...]}
├─ Used for: Preview before full sync

GET /api/email/status
├─ Returns: {last_sync, total_emails_synced, total_transactions, sync_in_progress}
├─ Used for: Check sync progress/history

POST /api/email/sync
├─ Body: {days_back, max_emails, use_ai}
├─ Returns: {status, emails_processed, transactions_found, message}
├─ Used for: Full manual email sync (with fine control)

POST /api/email/sync-with-range
├─ Body: {date_range: '30_days'|'60_days'|'90_days'|'1_year', max_emails}
├─ Returns: {status, emails_processed, transactions_found, message}
└─ Used for: Called after OAuth from DataImport component
```

---

## API-TO-BACKEND MAPPING

### Summary of All Frontend API Calls & Backend Endpoints

#### **AUTHENTICATION API CALLS**

```typescript
// Login
authService.login(email, password, rememberMe)
→ POST /api/auth/login
  Request: {email, password (encrypted), remember_me}
  Response: {access_token, user}

// Signup
authService.signup(email, password, username, name, termsAccepted, privacyAccepted)
→ POST /api/auth/signup
  Request: {email, password (encrypted), username, name, terms_accepted, privacy_accepted}
  Response: {access_token, user}

// Get Current User
authService.getCurrentUser()
→ GET /api/auth/me
  Response: {id, email, name}

// Logout
authService.logout()
→ POST /api/auth/logout
  Response: {message}

// Forgot Password
authService.forgotPassword(email)
→ POST /api/auth/forgot-password
  Request: {email}
  Response: {message}

// Reset Password
authService.resetPassword(token, password)
→ POST /api/auth/reset-password
  Request: {token, password (encrypted)}
  Response: {message}

// Validate Reset Token
authService.validateResetToken(token)
→ POST /api/auth/validate-reset-token
  Request: {token}
  Response: {valid, email}

// Verify Email
authService.verifyEmail(token)
→ POST /api/auth/verify-email
  Request: {token}
  Response: {message}

// Check Email Exists
authService.checkEmail(email)
→ GET /api/auth/check-email?email=user@example.com
  Response: {exists}

// Change Password
authService.changePassword(currentPassword, newPassword)
→ POST /api/auth/change-password
  Request: {current_password (encrypted), new_password (encrypted)}
  Response: {message}

// Google Login (Initiate)
authService.initiateGoogleLogin()
→ GET /api/auth/login
  Response: {authorization_url, state}

// Google Signup (Initiate)
authService.initiateGoogleSignup()
→ GET /api/auth/google/signup
  Response: {authorization_url, state, action}
```

#### **EMAIL API CALLS**

```typescript
// Sync Emails (Main call after OAuth)
emailService.syncEmailsWithRange(dateRange, maxEmails)
→ POST /api/email/sync-with-range
  Request: {date_range: '30_days'|'60_days'|'90_days'|'1_year', max_emails}
  Response: {status, emails_processed, transactions_found, message}

// Manual Sync
api.syncEmails(daysBack, maxEmails, useAi)
→ POST /api/email/sync
  Request: {days_back, max_emails, use_ai}
  Response: {status, emails_processed, transactions_found, message}

// Preview Emails
api.previewEmails(limit)
→ GET /api/email/preview?limit=10
  Response: {total_emails, transactions: [...]}

// Email Sync Status
api.getEmailSyncStatus()
→ GET /api/email/status
  Response: {last_sync, total_emails_synced, total_transactions, sync_in_progress}
```

#### **TRANSACTION API CALLS**

```typescript
// Get All Transactions
api.getTransactions({page, page_size, trans_type, category_id, search})
→ GET /api/transactions?page=1&page_size=20&trans_type=debit&...
  Response: {total, page, page_size, transactions: [...]}

// Get Monthly Stats
api.getMonthlyStats(monthYear)
→ GET /api/transactions/stats?month_year=2024-01
  Response: {month_year, total_income, total_expenses, net_savings, savings_rate, category_breakdown}

// Create Transaction
api.createTransaction({date, amount, trans_type, merchant, category_id, description})
→ POST /api/transactions
  Request: {date, amount, trans_type, merchant, category_id, description}
  Response: {id, ...transaction}

// Update Transaction
api.updateTransaction(id, {category_id, merchant, description})
→ PUT /api/transactions/{id}
  Request: {category_id, merchant, description}
  Response: {message}

// Delete Transaction
api.deleteTransaction(id)
→ DELETE /api/transactions/{id}
  Response: {message}

// Upload CSV
api.uploadCsv(file)
→ POST /api/transactions/upload-csv (FormData)
  Request: FormData with file
  Response: {transactions_created, ...}
```

#### **LEAK DETECTION API CALLS**

```typescript
// Detect Leaks
api.detectLeaks()
→ POST /api/leaks/detect
  Response: {message}

// Get All Leaks
api.getLeaks()
→ GET /api/leaks
  Response: [{id, leak_type, title, description, severity, detected_amount, frequency, created_at}, ...]

// Get Subscriptions
api.getSubscriptions()
→ GET /api/leaks/subscriptions
  Response: [{id, name, amount, interval_days, next_expected_date, merchant, is_active}, ...]

// Resolve Leak
api.resolveLeak(id)
→ PUT /api/leaks/leaks/{id}/resolve
  Response: {message}
```

#### **OTHER API CALLS**

```typescript
// Health Check
api.healthCheck()
→ GET /health
  Response: {status, service, version}
```

#### **DIRECT FETCH CALLS (NOT USING API SERVICE CLASS)**

These are legacy or special cases:

```typescript
// File Upload (from AnalysisPage.tsx)
fetch('http://localhost:8000/analyze', {
    method: 'POST',
    body: formData  // Contains PDF/file
})
Response: {leaks, transactions, ai_insights, ...}
Note: 📌 THIS ENDPOINT MAY NOT EXIST IN BACKEND!

// Email Scrape (from AnalysisPage.tsx)
fetch('http://localhost:8000/api/scrape-emails', {
    method: 'POST',
    body: {token, refresh_token, email, date_range}
})
Response: {leaks, transactions, ai_insights, ...}
Note: 📌 THIS ENDPOINT MAY NOT EXIST IN BACKEND!

// Google Signup
fetch('http://localhost:8000/api/auth/google/signup')
Note: ✅ This is correctly using the api service in DataImport.tsx
```

---

## CRITICAL ISSUES TO INVESTIGATE

### ⚠️ Missing or Incorrect Backend Endpoints

Based on the frontend code, check if these endpoints exist in your backend:

1. **`POST /analyze`** (AnalysisPage.tsx, line ~120)
   - Frontend calls this for file upload analysis
   - Expected endpoint: `/api/transactions/upload-csv` or similar
   - **Status**: Need to verify

2. **`POST /api/scrape-emails`** (AnalysisPage.tsx, line ~75)
   - Frontend calls this with OAuth tokens
   - Expected behavior: Parse emails and detect leaks
   - **Status**: Need to verify if this exists or if it should be `/api/email/sync`

3. **`GET /api/auth/login`** (should return OAuth URL)
   - Used for initiating Google login
   - **Status**: Should exist in auth.py

4. **`GET /api/auth/google/signup`** (should return OAuth URL)
   - Used for initiating Google signup
   - **Status**: Should exist in auth.py

5. **Leak Detection Endpoints**
   - `/api/leaks/detect` - POST to trigger detection
   - `/api/leaks` - GET to fetch all leaks
   - `/api/leaks/subscriptions` - GET to fetch subscriptions
   - `/api/leaks/leaks/{id}/resolve` - PUT to mark resolved
   - **Status**: May be in `leak_analyzer.py`

### 🔐 Password Encryption

**Frontend Implementation** (`utils/crypto.ts`):
- Uses RSA-OAEP with hardcoded public key
- Encrypts password before sending
- Sends base64-encoded encrypted password

**Backend Requirements** (`app/crypto.py` should exist):
- Decrypt using matching RSA private key
- Hash with bcrypt for storage
- **Verify this matches!**

### 🔑 Token Management

- Frontend stores JWT in `localStorage['auth_token']`
- All authenticated requests use: `Authorization: Bearer {token}`
- Token is set via `api.setToken(token)`
- **Check**: Does backend issue JWT tokens?

---

## KEY PATTERNS & CONVENTIONS

### Component File Naming
- Pages: PascalCase.tsx (e.g., `Login.tsx`)
- Components: PascalCase.tsx (e.g., `Dashboard.tsx`)
- Hooks: camelCase.ts (e.g., `useTransactions.ts`)
- Services: camelCase.ts (e.g., `api.ts`)
- Utils: camelCase.ts (e.g., `crypto.ts`)

### Import Aliases
- `@/` resolves to `src/` (configured in vite.config.ts)
- Used throughout for clean imports

### Color Scheme
- Primary: Indigo (#6366f1)
- Accent: Purple (#a855f7)
- Danger: Red (#ef4444)
- Success: Green (#22c55e)
- Background: Slate colors

### Tailwind Classes Used
- `bg-gradient-to-r` - Horizontal gradients
- `backdrop-blur-md` - Glassmorphism
- `animate-spin` - Loading spinners
- `transition-all` - Smooth animations
- Responsive: `md:`, `lg:`, `xl:` prefixes

---

## COMPLETE COMPONENT DEPENDENCY TREE

```
App.tsx (Router setup)
├── Login.tsx (Public)
│   ├── AuthLayout.tsx
│   ├── ForgotPasswordModal (embedded)
│   └── authService
├── Signup.tsx (Public)
│   ├── AuthLayout.tsx
│   ├── PolicyModal.tsx
│   └── authService
├── AuthCallback.tsx (Public)
│   ├── emailService
│   ├── ConsentModal.tsx
│   └── api
├── AnalysisPage.tsx (Protected)
│   ├── DataImport.tsx
│   ├── Dashboard.tsx
│   └── authService
├── VerifyEmail.tsx (Public)
│   └── api.auth.verifyEmail
├── ResetPassword.tsx (Public)
│   └── api.auth.*
├── TermsOfService.tsx (Public)
├── PrivacyPolicy.tsx (Public)
└── NotFound.tsx (404)

DataImport.tsx
└── Calls: onFileUpload, onEmailConnect

Dashboard.tsx
├── StatsCard (embedded)
├── Recharts (LineChart)
└── React Markdown

PolicyModal.tsx
└── Terms/Privacy content

ConsentModal.tsx
└── Consent UI
```

---

## SUMMARY: WHAT THE FRONTEND DOES

### High-Level Purpose
A financial leak detector that helps users:
1. **Upload bank statements** (CSV/Excel/PDF) to analyze spending
2. **Connect Gmail** to auto-extract transactions from emails
3. **Detect hidden leaks** (subscriptions, recurring charges, spending anomalies)
4. **Get AI insights** from Gemini about their finances

### User Journey
```
Anonymous User
  ↓
Sign Up / Log In (Email or Google OAuth)
  ↓
Verify Email
  ↓
Upload Bank Statement OR Connect Gmail
  ↓
Backend analyzes and detects "leaks" (suspicious recurring charges)
  ↓
View Dashboard with:
  - Total spend summary
  - Leak list with amounts
  - Spending trends (chart)
  - AI-generated insights
  ↓
Can manage leaks, update transactions, etc.
```

### Key Technologies
- **React + TypeScript** - Type-safe UI
- **Tailwind CSS** - Beautiful styling
- **Lucide Icons** - Clean icon set
- **Recharts** - Data visualization
- **Fetch API** - HTTP requests
- **localStorage** - Client-side auth token storage
- **React Router** - Page navigation

---

## TESTING THE FRONTEND LOCALLY

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
# Runs on http://localhost:5173

# Build for production
npm run build

# Preview production build
npm run preview
```

**Important**: Backend must be running on `http://127.0.0.1:8000` for API calls to work.

---

## NEXT STEPS FOR YOU (BACKEND DEVELOPER)

1. ✅ **Review this guide** and understand the flow
2. ✅ **Map all frontend API calls** to your backend endpoints
3. ✅ **Check password encryption/decryption** matches
4. ✅ **Verify OAuth implementation** returns correct data
5. ✅ **Test email sync flow** end-to-end
6. ✅ **Implement missing endpoints** if any
7. ✅ **Add proper error handling** for all cases
8. ✅ **Test with frontend** running simultaneously

---

**Document Created**: 2024-2025  
**Framework Version**: React 18, Vite 5, Tailwind CSS 3  
**API Base URL**: `http://127.0.0.1:8000`

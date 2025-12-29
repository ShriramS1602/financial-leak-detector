# 💸 Financial Leak Detector

> **Built a Personal Financial Leak Detector that identifies forgotten subscriptions and hidden spending habits by analyzing transaction patterns. The system detects recurring payments, small high-frequency expenses, and price creep, helping users save money without manual budgeting.**

## 🎯 Problem Statement

People don't realize small recurring charges and irregular spending habits that silently drain money.

### What This App Answers:
- ❓ Where is my money leaking without my awareness?
- ❓ What subscriptions did I forget?
- ❓ Which expenses look harmless individually but are expensive monthly?

## 🔍 Leak Types Detected

### Type A — Hidden Subscriptions
- Netflix, Spotify, Amazon Prime
- App subscriptions, Cloud services
- **Pattern:** Same merchant + Same amount + Fixed interval (30/7/365 days)

### Type B — Small Repeating Expenses
- ₹99 daily coffee, ₹149 Swiggy late-night orders
- **Pattern:** Amount < ₹300 + High frequency (>8/month)

### Type C — Irregular but Habitual Spending
- Weekend party spends, Random Amazon buys
- **Pattern:** Irregular dates + Similar category + Time clusters

### Type D — Price Increases / Silent Upgrades
- Subscription increased from ₹199 → ₹249
- **Pattern:** Same merchant + Slowly increasing amount

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Access
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 📊 Data Sources

### Phase 1 (Current)
✅ **Manual CSV Upload** - Upload bank statement CSV
✅ **Gmail Parsing** - Auto-detect "Payment successful", "Subscription renewed" emails

### Phase 2 (Future)
- Account Aggregator integration for real-time sync

## 🧠 Core Detection Algorithms

### 1. Subscription Detector
```
Group by merchant + amount
IF same transaction appears >= 3 times
AND interval ≈ 30/7/365 days
→ Mark as Subscription
```

### 2. Small Leak Accumulator
```
IF amount < ₹300
AND frequency > 8 per month
→ Flag as "Silent Leak"
```

### 3. Irregular Pattern Detector
```
Cluster spending by:
- Time (weekend/night)
- Category
- Merchant
```

### 4. Price Creep Detector
```
Same merchant + Increasing amount over time
→ Alert user
```

## 🏗️ Tech Stack

### Backend
- **Framework:** FastAPI
- **Database:** SQLite
- **Data Processing:** Pandas, NumPy
- **AI:** Google Gemini API (transaction parsing)
- **Email:** Google Gmail API

### Frontend
- **Framework:** React + TypeScript
- **Charts:** Recharts
- **Styling:** Tailwind CSS
- **Routing:** React Router

## 📁 Project Structure

```
v1/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── requirements.txt        # Python dependencies
│   └── app/
│       ├── models.py           # SQLAlchemy models
│       ├── database.py         # DB connection
│       ├── email_service.py    # Gmail parsing + AI
│       ├── schema.py           # Pydantic schemas
│       ├── api/
│       │   ├── auth.py         # Authentication
│       │   ├── email.py        # Email sync endpoints
│       │   ├── transactions.py # Transaction CRUD
│       │   └── leaks.py        # Leak detection endpoints
│       └── core/
│           └── detector.py     # Leak detection algorithms
├── frontend/
│   ├── package.json
│   └── src/
│       ├── App.tsx
│       ├── pages/
│       │   ├── LeakDashboard.tsx
│       │   ├── Subscriptions.tsx
│       │   └── Onboarding.tsx
│       └── services/
│           └── api.ts
└── README.md
```

## 🎨 Key Features

1. **Leak Overview Dashboard** - See all detected financial leaks at a glance
2. **Subscription Tracker** - Monitor active subscriptions with next charge dates
3. **CSV Upload** - Import bank statements easily
4. **Gmail Integration** - Auto-parse financial emails
5. **AI-Powered Parsing** - Gemini API for smart transaction extraction
6. **Cancel Reminders** - Get notified before subscriptions renew

## 📈 Example Insights

- 🔔 "You have 3 active subscriptions you haven't used recently"
- ⚠️ "You spent ₹2,430 on Swiggy in the last 30 days — mostly after 10 PM"
- 💸 "Small daily spends added up to ₹4,800 this month"
- 📈 "Netflix price increased by 25% in the last 6 months"

## 🔐 Environment Variables

Create `.env` file in `backend/`:

```env
# Database
DATABASE_URL=sqlite:///./finance_tracker.db

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google OAuth (for Gmail)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/callback

# Gemini AI
LLM_API_KEY=your-gemini-api-key

# Frontend URL
FRONTEND_URL=http://localhost:5173
```

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/login` | Login with email/password |
| GET | `/api/auth/login` | Initiate Google OAuth |
| POST | `/api/transactions/upload-csv` | Upload CSV file |
| GET | `/api/transactions` | List transactions |
| GET | `/api/transactions/stats` | Monthly statistics |
| POST | `/api/leaks/detect` | Run leak detection |
| GET | `/api/leaks` | Get detected leaks |
| GET | `/api/leaks/subscriptions` | Get subscriptions |

## 🎤 How to Pitch This Project

> "Built a Personal Financial Leak Detector that identifies forgotten subscriptions and hidden spending habits by analyzing transaction patterns. The system detects recurring payments, small high-frequency expenses, and price creep, helping users save money without manual budgeting."

This sounds **product-driven**, not just CRUD.

## 📄 License

MIT License

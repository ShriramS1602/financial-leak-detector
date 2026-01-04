# Financial Leak Detector - UI API Integration Guide

This guide explains which API endpoints to call at each step of the user journey, from a frontend UI perspective.

---

## User Journey Flow

### 1. Dashboard / Home Page

**What the user sees:**
- Welcome screen with "Upload Transactions" button
- View existing patterns (if any)
- View identified leaks (if any)

**API calls to make:**

```
GET /api/transactions/patterns
├─ Purpose: Fetch all spending patterns
├─ Used by: Display spending summary on dashboard
├─ Response: List of patterns with evidence (txn_count, amounts, frequency)
└─ Display: Show top merchants, spending frequency, trends
```

```
POST /api/leaks/analyze  (if patterns exist)
├─ Purpose: Run AI analysis on patterns
├─ Used by: Get leak recommendations
├─ Condition: Only call if patterns exist (txn_count >= 2)
├─ Response: List of leaks with probability, reasoning, savings
└─ Display: Show leak cards with actionable steps
```

---

### 2. Upload Transaction File

**What the user sees:**
- File upload form (CSV/Excel)
- Progress indicator
- Upload success message with statistics

**API call to make:**

```
POST /api/transactions/upload
├─ Input:
│  ├─ File: CSV or Excel (.csv, .xlsx, .xls)
│  ├─ Required columns: Date, Narration, Withdrawal Amt., Deposit Amt.
│  └─ Max file size: 5MB
│
├─ Response:
│  ├─ status: "success" or "error"
│  ├─ upload_id: Unique batch identifier
│  └─ statistics:
│     ├─ total_rows: Rows in file
│     ├─ clean_rows: Valid rows after cleaning
│     ├─ transactions_stored: Rows in Transaction table
│     ├─ patterns_aggregated: Distinct merchants
│     └─ pattern_stats_stored: Patterns stored
│
├─ Usage: 
│  ├─ Show upload progress to user
│  ├─ Display statistics after success
│  └─ Trigger automatic pattern refresh
│
└─ Error handling:
   ├─ 400: Invalid file or missing columns
   ├─ 413: File too large
   └─ Display error message to user
```

**Frontend flow:**
```
1. User selects file
   ↓
2. POST /api/transactions/upload (with file)
   ↓
3. Show uploading... spinner
   ↓
4. Receive response
   ├─ If success:
   │  ├─ Show "Upload successful!" message
   │  ├─ Display: "X transactions stored, Y patterns found"
   │  └─ Auto-refresh patterns list
   │
   └─ If error:
      ├─ Show error message
      └─ Allow retry
```

---

### 3. View All Transactions

**What the user sees:**
- List of transactions
- Filter options (date range, merchant, amount)
- Pagination (load more)

**API calls to make:**

```
GET /api/transactions/raw-transactions?limit=50&skip=0
├─ Purpose: Fetch enriched transaction records
├─ Query params:
│  ├─ limit: Number of records (default: 100)
│  └─ skip: Offset for pagination (default: 0)
│
├─ Response:
│  ├─ total: Total transaction count
│  ├─ skip: Current skip value
│  ├─ limit: Current limit
│  └─ transactions[]:
│     ├─ txn_date: Date of transaction
│     ├─ narration: Description (raw)
│     ├─ withdrawal_amount: Expense amount
│     ├─ deposit_amount: Income amount
│     ├─ money_flow: INCOME/EXPENSE/TRANSFER
│     ├─ level_1/2/3_tag: Categories
│     └─ merchant_hint: Extracted merchant
│
├─ Usage:
│  ├─ Display as table/list
│  ├─ Show category badges (level_3_tag)
│  ├─ Color-code by money_flow (red=expense, green=income)
│  └─ Implement pagination with skip parameter
│
└─ Frontend pagination:
   ├─ Initial load: skip=0, limit=50
   ├─ Load more: skip=50, limit=50
   ├─ Load more: skip=100, limit=50
   └─ Continue until loaded transactions == total
```

**Display example:**
```
Transaction List:
├─ Date: 2026-01-01
├─ Description: STARBUCKS COFFEE
├─ Amount: -$50.00 (red, expense)
├─ Category: COFFEE_SHOP (badge)
└─ Merchant: starbucks

[Load More] button to fetch next 50
```

---

### 4. View Spending Patterns

**What the user sees:**
- List of merchants with aggregated data
- Frequency (how often)
- Amount information (total, average)
- Category tags
- Trend indicators

**API call to make:**

```
GET /api/transactions/patterns
├─ Purpose: Get all spending patterns for user
├─ Response:
│  └─ patterns[]:
│     ├─ id: Pattern database ID
│     ├─ merchant_hint: Merchant name (grouping key)
│     ├─ level_1_tag: High-level category
│     ├─ level_2_tag: Mid-level category
│     ├─ level_3_tag: Specific category
│     │
│     └─ evidence (aggregated statistics):
│        ├─ txn_count: Number of transactions
│        ├─ total_amount: Total spent
│        ├─ avg_amount: Average per transaction
│        ├─ gap_mean_days: Average days between transactions
│        ├─ gap_std_days: Consistency (low = regular)
│        ├─ gap_min_days: Shortest gap
│        ├─ gap_max_days: Longest gap
│        ├─ recency_days: Days since last transaction
│        └─ level_3_confidence: Category confidence (0.0-1.0)
│
└─ Usage:
   ├─ Display as cards or rows
   ├─ Show merchant name + category
   ├─ Display: "X transactions, $Y total, $Z average"
   ├─ Show frequency indicator (e.g., "every 6.8 days")
   └─ Highlight: "Last transaction X days ago"
```

**Display example:**
```
STARBUCKS
├─ Category: COFFEE_SHOP
├─ Transactions: 54
├─ Total Spent: $810.00
├─ Average: $15.00 per transaction
├─ Frequency: Every 6.8 days (±2.1 days)
└─ Last transaction: 1 day ago ✓ Active
```

---

### 5. View Leak Recommendations

**What the user sees:**
- List of identified leaks
- Leak type (subscription, habit, impulse)
- Confidence score
- AI reasoning
- Actionable steps
- Potential annual savings

**API call to make:**

```
POST /api/leaks/analyze
├─ Input: {} (empty JSON)
├─ Prerequisite: User must have patterns (run upload first)
│
├─ Response:
│  ├─ leaks[]:
│  │  ├─ pattern_id: ID of the spending pattern
│  │  ├─ merchant_hint: What spending is for
│  │  ├─ leak_probability: Confidence 0.0-1.0
│  │  ├─ leak_category: Type of leak
│  │  ├─ reasoning: Why it's a leak
│  │  ├─ actionable_step: What to do
│  │  └─ estimated_annual_saving: Potential savings
│  │
│  ├─ total_estimated_annual_saving: Sum of all savings
│  ├─ analysis_timestamp: When analysis ran
│  └─ confidence_level: high/medium/low
│
└─ Usage:
   ├─ Sort by estimated_annual_saving (highest first)
   ├─ Color-code by leak_probability:
   │  ├─ 0.9-1.0: Red (high confidence leak)
   │  ├─ 0.7-0.9: Orange (medium-high)
   │  ├─ 0.5-0.7: Yellow (medium)
   │  └─ <0.5: Gray (low confidence)
   ├─ Show breakdown of leak types
   └─ Display total savings potential
```

**Display example:**
```
💰 Potential Annual Savings: $5,380

🔴 MONTHLY AUTOPAY (Confidence: 95%)
   Leak Type: Unused Subscription
   Category: OTT_STREAMING
   Monthly Cost: $199.00
   Annual Saving: $2,388
   AI Says: "Perfectly consistent monthly payment suggests 
            recurring subscription that may be unused."
   Action: "Review and cancel if not using"
   
   [Dismiss] [Mark as Resolved] [View Pattern]

🟠 STARBUCKS (Confidence: 85%)
   Leak Type: Excessive Habit
   Category: COFFEE_SHOP
   Monthly Cost: ~$135
   Annual Saving: $400
   AI Says: "54 frequent transactions every 6.8 days suggests
            regular discretionary spending habit."
   Action: "Consider reducing frequency or bringing beverages
           from home"
   
   [Dismiss] [Mark as Resolved] [View Pattern]
```

---

### 6. Leak Detail View

**What the user sees:**
- Full leak details
- AI reasoning explained
- Related transactions
- Optional: Mark as resolved

**API calls to make:**

```
1. GET /api/transactions/patterns
   ├─ Purpose: Get the pattern details for this leak
   └─ Use: Display pattern statistics

2. GET /api/transactions/raw-transactions?limit=10&skip=0
   ├─ Purpose: Show last 10 transactions for this merchant
   ├─ Filter client-side: merchant_hint matches leak pattern
   └─ Use: Show user's actual spending with this merchant
```

**Display example:**
```
← Back to Leaks

NETFLIX SUBSCRIPTION

Leak Analysis
├─ Confidence: 95% (Very High)
├─ Potential Annual Saving: $1,200
└─ Risk Level: High ⚠️

Pattern Evidence
├─ Transactions: 12
├─ Time Period: 355 days
├─ Average Gap: 30.0 days (very consistent)
├─ Gap Variance: 0.5 days (predictable)
├─ Average Amount: $100.00
├─ Last Transaction: 3 days ago

AI Analysis
"This is a very strong leak signal: explicitly labeled 'monthly 
autopay', categorized as 'OTT' (streaming service), with a 
perfectly consistent monthly amount (99.0) and regular monthly 
gaps. Unused or underutilized subscriptions are common 
financial leaks."

Recommended Action
"Review this OTT subscription. If you are not using it 
frequently, consider canceling or downgrading to save money."

Recent Transactions
├─ Jan 05: Netflix         -$99.00   [OTT_STREAMING]
├─ Dec 05: Netflix         -$99.00   [OTT_STREAMING]
├─ Nov 05: Netflix         -$99.00   [OTT_STREAMING]
└─ [View all 12 transactions]

[Mark as Resolved] [Dismiss Leak] [View All Patterns]
```

---

## API Call Sequence by Feature

### Feature: "Dashboard Summary"
```
1. GET /api/transactions/patterns
   └─ Display top 5 merchants by spending

2. POST /api/leaks/analyze
   └─ Display top 3 leaks by savings potential
```

### Feature: "Upload & Auto-refresh"
```
1. POST /api/transactions/upload
   └─ Wait for response

2. GET /api/transactions/patterns
   └─ Refresh patterns list

3. POST /api/leaks/analyze (if patterns exist)
   └─ Show new leaks
```

### Feature: "Transaction Search/Filter"
```
1. GET /api/transactions/raw-transactions?limit=100&skip=0
   └─ Initial load

2. Loop: GET /api/transactions/raw-transactions?limit=100&skip=100
   └─ Load more on pagination

3. Client-side filtering:
   ├─ Filter by date range
   ├─ Filter by category (level_3_tag)
   ├─ Filter by money_flow (INCOME/EXPENSE)
   └─ Search in narration
```

### Feature: "Spending Analytics"
```
1. GET /api/transactions/patterns
   └─ Use evidence fields:
      ├─ txn_count for frequency chart
      ├─ gap_mean_days for regularity
      ├─ total_amount for spending trends
      └─ recency_days for "active" indicator
```

### Feature: "Leak Tracking"
```
1. POST /api/leaks/analyze
   └─ Get all leaks

2. For each leak:
   ├─ GET /api/transactions/patterns (get pattern by ID)
   └─ GET /api/transactions/raw-transactions (get related txns)

3. Optional: [Mark as Resolved] - store locally in frontend
   (No backend endpoint needed currently)
```

---

## API Response Fields Quick Reference

### Transaction Object
```json
{
  "id": 1,
  "txn_date": "2026-01-01",
  "narration": "STARBUCKS COFFEE",
  "withdrawal_amount": 50.00,
  "deposit_amount": null,
  "money_flow": "EXPENSE",
  "level_1_tag": "FOOD_AND_DINING",
  "level_2_tag": "COFFEE",
  "level_3_tag": "COFFEE_SHOP",
  "merchant_hint": "starbucks",
  "file_upload_id": "uuid"
}
```

### Pattern Object
```json
{
  "id": 1,
  "merchant_hint": "starbucks",
  "level_1_tag": "FOOD_AND_DINING",
  "level_2_tag": "COFFEE",
  "level_3_tag": "COFFEE_SHOP",
  "evidence": {
    "txn_count": 54,
    "total_amount": 810.00,
    "avg_amount": 15.00,
    "gap_mean_days": 6.8,
    "gap_std_days": 2.1,
    "gap_min_days": 3,
    "gap_max_days": 14,
    "recency_days": 1
  }
}
```

### Leak Object
```json
{
  "pattern_id": 1,
  "merchant_hint": "netflix",
  "leak_probability": 0.95,
  "leak_category": "unused_subscription",
  "reasoning": "...",
  "actionable_step": "...",
  "estimated_annual_saving": 1200.00
}
```

---

## Frontend Implementation Tips

### 1. Caching Strategy
```javascript
// Cache patterns to avoid repeated API calls
const patternsCache = {}
const leaksCache = {}

// Only refresh on:
├─ File upload completion
├─ Manual refresh button click
└─ Time-based (e.g., every 5 minutes)
```

### 2. Error Handling
```javascript
// All API calls should handle:
├─ 400: Show form validation errors
├─ 401: Redirect to login
├─ 500: Show "Something went wrong" message
└─ Network: Show "Check connection" message
```

### 3. Loading States
```javascript
// Show loading spinner during:
├─ POST /api/transactions/upload
├─ POST /api/leaks/analyze
└─ GET /api/transactions/raw-transactions (on pagination)
```

### 4. Pagination Implementation
```javascript
const [skip, setSkip] = useState(0)
const [limit, setLimit] = useState(50)
const [hasMore, setHasMore] = useState(true)

async function loadMoreTransactions() {
  const response = await fetch(
    `/api/transactions/raw-transactions?limit=${limit}&skip=${skip}`
  )
  
  if (response.transactions.length < limit) {
    setHasMore(false)  // No more data
  }
  
  setSkip(skip + limit)  // Increment for next call
}
```

### 5. Category Color Coding
```javascript
const categoryColors = {
  "FOOD_AND_DINING": "#FF6B6B",
  "UTILITIES": "#4ECDC4",
  "TRANSPORTATION": "#45B7D1",
  "ENTERTAINMENT": "#FFA07A",
  "SHOPPING": "#DDA0DD",
  "HEALTHCARE": "#98D8C8",
  "INVESTMENT": "#F7DC6F"
}

const moneyFlowColors = {
  "EXPENSE": "#FF6B6B",     // Red
  "INCOME": "#51CF66",      // Green
  "TRANSFER": "#4ECDC4"     // Blue
}
```

### 6. Leak Probability Badges
```javascript
function getLeakBadge(probability) {
  if (probability >= 0.9) return "🔴 Very High Risk"
  if (probability >= 0.7) return "🟠 High Risk"
  if (probability >= 0.5) return "🟡 Medium Risk"
  return "⚪ Low Risk"
}
```

---

## Common UI Patterns

### "No Data" States
```
// After upload but before analysis
"No patterns found yet. Upload more transactions to identify patterns."

// Before first upload
"Upload a transaction file to get started"

// API error
"Unable to load data. Please try again."
```

### Success Messages
```
"✓ File uploaded successfully!
  • 145 transactions stored
  • 23 spending patterns identified
  • Ready for analysis"
```

### Confirmation Dialogs
```
Before DELETE or "Mark as Resolved":
"Are you sure? This action cannot be undone."
[Cancel] [Confirm]
```

---

## Performance Considerations

### Optimize API Calls
1. **Debounce search** - Wait 300ms after user stops typing
2. **Lazy load** - Only fetch patterns when user clicks "Patterns" tab
3. **Paginate** - Don't load all 5000 transactions at once
4. **Cache** - Store patterns/leaks until user uploads new file

### Optimize Rendering
1. **Virtual lists** - For large transaction lists (1000+ items)
2. **Memoization** - Prevent re-renders of transaction rows
3. **Code splitting** - Load leak analysis feature on demand

---

## Testing Checklist

- [ ] Upload file → See statistics appear
- [ ] View patterns → See all merchants with stats
- [ ] View transactions → Can scroll/paginate through all
- [ ] Run analysis → See leaks with confidence scores
- [ ] Click leak → See details and related transactions
- [ ] No data states → Shown when appropriate
- [ ] Error messages → Clear and actionable
- [ ] Mobile responsive → Works on all screen sizes

---

Last Updated: January 5, 2026

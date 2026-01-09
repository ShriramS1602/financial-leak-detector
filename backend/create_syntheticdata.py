import pandas as pd
import random
from datetime import datetime, timedelta

# =========================
# CONFIG
# =========================
INPUT_CSV = r"C:\Users\SHRIRAM\Downloads\Acct_Statement_XXXXXXXX9888_01012026 - Copy.csv"
OUTPUT_CSV = "synthetic_account_statement.csv"

START_DATE = datetime(2025, 10, 1)
NUM_DAYS = 180
START_BALANCE = 6000.0

random.seed(42)

# =========================
# LOAD REAL DATA
# =========================
df = pd.read_csv(INPUT_CSV)

def to_float(x):
    try:
        return float(x)
    except:
        return None

df["Withdrawal Amt."] = df["Withdrawal Amt."].apply(to_float)
df["Deposit Amt."] = df["Deposit Amt."].apply(to_float)

# =========================
# LEARN FROM REAL DATA
# =========================

# Frequent debit narrations (human habits)
debit_df = df[df["Withdrawal Amt."].notna()]
common_narrations = (
    debit_df["Narration"]
    .value_counts()
    .head(30)
    .index
    .tolist()
)

# Realistic debit amounts
debit_amounts = debit_df["Withdrawal Amt."].dropna().tolist()

# =========================
# GENERATE SYNTHETIC DATA
# =========================
rows = []
balance = START_BALANCE

current_date = START_DATE

for day in range(NUM_DAYS):

    date = current_date + timedelta(days=day)

    # ---- Monthly salary (simple realism) ----
    if date.day == 1:
        balance += 45000
        rows.append({
            "Date": date.strftime("%d/%m/%y"),
            "Narration": "NEFT-SALARY-CREDIT",
            "Chq./Ref.No.": str(random.randint(10**15, 10**16 - 1)),
            "Value Dt": date.strftime("%d/%m/%y"),
            "Withdrawal Amt.": None,
            "Deposit Amt.": "45000.00",
            "Closing Balance": f"{balance:.2f}"
        })

    # ---- Regular debit (most days) ----
    if random.random() < 0.75:
        narration = random.choice(common_narrations)
        amt = max(5, random.choice(debit_amounts) + random.choice([-5, 0, 5]))

        if balance - amt > 0:
            balance -= amt
            rows.append({
                "Date": date.strftime("%d/%m/%y"),
                "Narration": narration,
                "Chq./Ref.No.": str(random.randint(10**15, 10**16 - 1)),
                "Value Dt": date.strftime("%d/%m/%y"),
                "Withdrawal Amt.": f"{amt:.2f}",
                "Deposit Amt.": None,
                "Closing Balance": f"{balance:.2f}"
            })

    # ---- Weekly coffee leak ----
    if date.weekday() == 2:  # Wednesday habit
        amt = random.choice([120, 140, 160])
        if balance - amt > 0:
            balance -= amt
            rows.append({
                "Date": date.strftime("%d/%m/%y"),
                "Narration": "UPI-STARBUCKS-COFFEE",
                "Chq./Ref.No.": str(random.randint(10**15, 10**16 - 1)),
                "Value Dt": date.strftime("%d/%m/%y"),
                "Withdrawal Amt.": f"{amt:.2f}",
                "Deposit Amt.": None,
                "Closing Balance": f"{balance:.2f}"
            })

    # ---- Monthly OTT leak ----
    if date.day == 5:
        amt = 199
        if balance - amt > 0:
            balance -= amt
            rows.append({
                "Date": date.strftime("%d/%m/%y"),
                "Narration": "UPI-NETFLIX-SUBSCRIPTION",
                "Chq./Ref.No.": str(random.randint(10**15, 10**16 - 1)),
                "Value Dt": date.strftime("%d/%m/%y"),
                "Withdrawal Amt.": f"{amt:.2f}",
                "Deposit Amt.": None,
                "Closing Balance": f"{balance:.2f}"
            })

# =========================
# FINALIZE
# =========================
synthetic_df = pd.DataFrame(rows)
synthetic_df = synthetic_df.sort_values("Date").reset_index(drop=True)
synthetic_df.to_csv(OUTPUT_CSV, index=False)

print(f"Synthetic data generated: {OUTPUT_CSV}")
print(f"Rows: {len(synthetic_df)}")

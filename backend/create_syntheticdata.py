import pandas as pd
import random
from datetime import datetime, timedelta

# =========================
# CONFIG
# =========================
OUTPUT_CSV = "synthetic_account_statement_60_days.csv"

NUM_DAYS = 60
END_DATE = datetime.today()
START_DATE = END_DATE - timedelta(days=NUM_DAYS)

START_BALANCE = 25000.0
SALARY_AMOUNT = 65000.0

random.seed(42)

# =========================
# HELPERS
# =========================
def rrn():
    return str(random.randint(10**11, 10**12 - 1))

def ref_no():
    return str(random.randint(10**15, 10**16 - 1))

# =========================
# REALISTIC NARRATION POOLS
# =========================

P2P_NAMES = [
    "GOPALAKRISHNAN S",
    "HABIB RAHMAN",
    "KALISHNATHAN",
    "ANANDA RAJ C",
    "GAYATHRI ELUMALAI",
    "CHINNAMANI V VIJAYAS"
]

MERCHANTS = [
    ("RISHI S KITCHEN", "HDFC0MERUPI"),
    ("ZAVIAN RESTAURANT", "YESB0PTMUPI"),
    ("MYNTRA DESIGNS PRIVA", "INDB0MERCHA"),
    ("STARBUCKS", "SBIP0123456")
]

OTT = [
    ("UPI-NETFLIX-SUBSCRIPTION", 199),
]

BANK_HANDLES = [
    "YBL",
    "SBIPAY",
    "PTYS",
    "HDFCBANK",
    "INDUS"
]

# =========================
# NARRATION GENERATORS
# =========================
def p2p_upi():
    name = random.choice(P2P_NAMES)
    handle = random.choice(BANK_HANDLES)
    return f"UPI-{name}-Q{random.randint(100000000,999999999)}@{handle}-YESB0YBLUPI-{rrn()}-UPI"

def merchant_upi():
    merchant, bankcode = random.choice(MERCHANTS)
    return f"UPI-{merchant}-PAYTMQR{random.randint(100000,999999)}@PTYS-{bankcode}-{rrn()}-UPI"

def self_bank_transfer():
    return f"IMPS-SELF-{random.choice(['HDFC','SBI','ICICI'])}-{rrn()}"

# =========================
# GENERATE DATA
# =========================
rows = []
balance = START_BALANCE
current_date = START_DATE

while current_date <= END_DATE:

    date_str = current_date.strftime("%d/%m/%y")

    # ---- Salary ----
    if current_date.day == 1:
        balance += SALARY_AMOUNT
        rows.append({
            "Date": date_str,
            "Narration": "NEFT-SALARY-CREDIT",
            "Chq./Ref.No.": ref_no(),
            "Value Dt": date_str,
            "Withdrawal Amt.": None,
            "Deposit Amt.": f"{SALARY_AMOUNT:.2f}",
            "Closing Balance": f"{balance:.2f}"
        })

    # ---- Daily transactions ----
    for _ in range(random.randint(2, 6)):

        txn_type = random.choices(
            ["p2p", "merchant", "self"],
            weights=[0.4, 0.45, 0.15]
        )[0]

        if txn_type == "p2p":
            narration = p2p_upi()
            amt = random.choice([300, 500, 750, 1000])

        elif txn_type == "merchant":
            narration = merchant_upi()
            amt = random.randint(120, 900)

        else:
            narration = self_bank_transfer()
            amt = random.choice([2000, 3000, 5000])

        if balance - amt <= 0:
            continue

        balance -= amt
        rows.append({
            "Date": date_str,
            "Narration": narration,
            "Chq./Ref.No.": ref_no(),
            "Value Dt": date_str,
            "Withdrawal Amt.": f"{amt:.2f}",
            "Deposit Amt.": None,
            "Closing Balance": f"{balance:.2f}"
        })

    # ---- OTT ----
    if current_date.day == 5:
        for narration, amt in OTT:
            if balance - amt > 0:
                balance -= amt
                rows.append({
                    "Date": date_str,
                    "Narration": narration,
                    "Chq./Ref.No.": ref_no(),
                    "Value Dt": date_str,
                    "Withdrawal Amt.": f"{amt:.2f}",
                    "Deposit Amt.": None,
                    "Closing Balance": f"{balance:.2f}"
                })

    current_date += timedelta(days=1)

# =========================
# FINALIZE
# =========================
df = pd.DataFrame(rows)
df = df.sort_values("Date").reset_index(drop=True)
df.to_csv(OUTPUT_CSV, index=False)

print("Generated:", OUTPUT_CSV)
print("Rows:", len(df))

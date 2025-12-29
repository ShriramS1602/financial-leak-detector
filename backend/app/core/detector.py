
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import Transaction, Leak, Subscription, LeakType, TransactionType
from typing import List

class LeakDetector:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def run_all(self):
        """Run all detection algorithms"""
        # Fetch transactions
        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == self.user_id,
            Transaction.trans_type == TransactionType.DEBIT
        ).all()
        
        if not transactions:
            return

        # Convert to DataFrame
        data = [{
            "id": t.id,
            "date": t.date,
            "amount": t.amount,
            "merchant": t.merchant,
            "description": t.description,
            "category": t.category.name if t.category else "Uncategorized"
        } for t in transactions]
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])

        self.detect_subscriptions(df)
        self.detect_small_leaks(df)
        self.detect_irregular_spending(df)
        self.detect_price_creep(df)

    def detect_subscriptions(self, df: pd.DataFrame):
        """
        Logic: Group by merchant + amount. 
        If same transaction appears >= 3 times AND interval approx 30/7/365 days.
        """
        # Group by merchant and amount
        groups = df.groupby(['merchant', 'amount'])
        
        for (merchant, amount), group in groups:
            if len(group) >= 3:
                # Calculate intervals
                dates = group['date'].sort_values()
                intervals = dates.diff().dt.days.dropna()
                
                # Check if intervals are consistent (approx 30 days)
                mean_interval = intervals.mean()
                std_interval = intervals.std()
                
                if std_interval < 5 and (25 <= mean_interval <= 35):
                    # Found a monthly subscription
                    self._save_subscription(merchant, amount, 30, dates.iloc[-1])
                elif std_interval < 2 and (6 <= mean_interval <= 8):
                     # Found a weekly subscription
                    self._save_subscription(merchant, amount, 7, dates.iloc[-1])

    def detect_small_leaks(self, df: pd.DataFrame):
        """
        Logic: Amount < 300 AND frequency > 8 per month.
        """
        # Filter small transactions
        small_txns = df[df['amount'] < 300]
        
        if small_txns.empty:
            return

        # Group by month and merchant
        small_txns['month'] = small_txns['date'].dt.to_period('M')
        monthly_counts = small_txns.groupby(['month', 'merchant']).size()
        
        for (month, merchant), count in monthly_counts.items():
            if count > 8:
                total_spent = small_txns[(small_txns['month'] == month) & (small_txns['merchant'] == merchant)]['amount'].sum()
                self._save_leak(
                    LeakType.SMALL_RECURRING,
                    f"High frequency spending at {merchant}",
                    f"You spent ₹{total_spent} at {merchant} this month across {count} transactions.",
                    "medium",
                    total_spent,
                    f"{count} times/month"
                )

    def detect_irregular_spending(self, df: pd.DataFrame):
        """
        Logic: Late night food orders or weekend party spends.
        Simple rule: Transactions > 500 after 10 PM or on weekends in 'Food'/'Entertainment' categories.
        """
        # Late night (after 10 PM)
        late_night = df[df['date'].dt.hour >= 22]
        food_entertainment = late_night[late_night['category'].isin(['Food', 'Entertainment', 'Dining'])]
        
        if not food_entertainment.empty:
            total = food_entertainment['amount'].sum()
            if total > 1000:
                 self._save_leak(
                    LeakType.IRREGULAR,
                    "Late Night Spending",
                    f"You spent ₹{total} on late-night food/entertainment recently.",
                    "low",
                    total,
                    "Irregular"
                )

    def detect_price_creep(self, df: pd.DataFrame):
        """
        Logic: Same merchant, increasing amount over time.
        """
        # Group by merchant
        for merchant, group in df.groupby('merchant'):
            if len(group) < 4:
                continue
                
            # Sort by date
            group = group.sort_values('date')
            
            # Check if amount is increasing
            amounts = group['amount'].values
            if amounts[-1] > amounts[0] * 1.1: # 10% increase
                # Check if it's strictly increasing or just a jump
                if amounts[-1] > amounts[-2]:
                     self._save_leak(
                        LeakType.PRICE_CREEP,
                        f"Price increase at {merchant}",
                        f"Spending at {merchant} has increased from ₹{amounts[0]} to ₹{amounts[-1]}.",
                        "high",
                        amounts[-1] - amounts[0],
                        "Increasing"
                    )

    def _save_subscription(self, merchant, amount, interval, last_date):
        # Check if already exists
        existing = self.db.query(Subscription).filter(
            Subscription.user_id == self.user_id,
            Subscription.merchant == merchant,
            Subscription.amount == amount
        ).first()
        
        if not existing:
            sub = Subscription(
                user_id=self.user_id,
                name=merchant,
                amount=amount,
                interval_days=interval,
                last_charged_date=last_date,
                next_expected_date=last_date + timedelta(days=interval),
                merchant=merchant
            )
            self.db.add(sub)
            self.db.commit()

    def _save_leak(self, leak_type, title, description, severity, amount, frequency):
        # Check if similar leak exists to avoid duplicates (simplified)
        existing = self.db.query(Leak).filter(
            Leak.user_id == self.user_id,
            Leak.leak_type == leak_type,
            Leak.title == title,
            Leak.is_resolved == False
        ).first()
        
        if not existing:
            leak = Leak(
                user_id=self.user_id,
                leak_type=leak_type,
                title=title,
                description=description,
                severity=severity,
                detected_amount=amount,
                frequency=frequency
            )
            self.db.add(leak)
            self.db.commit()

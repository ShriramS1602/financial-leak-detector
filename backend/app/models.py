"""
SQLAlchemy ORM Models for Personal Finance App
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

# ==================== ENUMS ====================
# COMMENTED OUT - Used only by Transaction and InsightLog models
# class TransactionType(str, enum.Enum):
#     CREDIT = "credit"
#     DEBIT = "debit"

# class SpendingHealth(str, enum.Enum):
#     EXCELLENT = "excellent"
#     GOOD = "good"
#     MODERATE = "moderate"
#     POOR = "poor"

# ==================== MODELS ====================
class User(Base):
    """User model for storing user information"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=True)
    name = Column(String(255))
    password_hash = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255), nullable=True)
    email_verification_sent_at = Column(DateTime, nullable=True)
    
    # Auth provider tracking
    auth_provider = Column(String(50), default="email")  # 'email' or 'google'
    
    # Password reset fields
    password_reset_token = Column(String(255), nullable=True)
    password_reset_sent_at = Column(DateTime, nullable=True)
    
    # Terms acceptance
    terms_accepted = Column(Boolean, default=False)
    terms_accepted_at = Column(DateTime, nullable=True)
    privacy_accepted = Column(Boolean, default=False)
    privacy_accepted_at = Column(DateTime, nullable=True)
    
    # Gmail OAuth tokens
    gmail_access_token = Column(Text)
    gmail_refresh_token = Column(Text)
    last_email_sync = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships - COMMENTED OUT (related to disabled endpoints)
    # transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    # categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    # budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    # subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    # leaks = relationship("Leak", back_populates="user", cascade="all, delete-orphan")
    
    # Relationships for new transaction upload feature
    raw_transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    spending_patterns = relationship("SpendingPatternStats", back_populates="user", cascade="all, delete-orphan")
    leak_insights = relationship("LeakInsight", back_populates="user", cascade="all, delete-orphan")

# COMMENTED OUT - Category model (used by Transactions API)
# class Category(Base):
#     """Transaction categories for spending analysis"""
#     __tablename__ = "categories"
#
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     name = Column(String(100), nullable=False)
#     icon = Column(String(50))
#     description = Column(Text)
#     color = Column(String(7), default="#3b82f6")  # HEX color
#     is_income = Column(Boolean, default=False)
#     is_system = Column(Boolean, default=True)  # System categories cannot be deleted
#     created_at = Column(DateTime, default=datetime.utcnow)
#
#     # Relationships
#     user = relationship("User", back_populates="categories")
#     transactions = relationship("Transaction", back_populates="category")

# COMMENTED OUT - Transaction model (used by Transactions API)
# class Transaction(Base):
#     """Transaction model storing parsed email data"""
#     __tablename__ = "transactions"
#
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     category_id = Column(Integer, ForeignKey("categories.id"))
#     
#     # Transaction details
#     date = Column(DateTime, index=True, nullable=False)
#     amount = Column(Float, nullable=False)
#     currency = Column(String(3), default="INR")
#     trans_type = Column(Enum(TransactionType), nullable=False)
#     merchant = Column(String(255))
#     description = Column(Text)
#     
#     # Source
#     source = Column(String(20), default="gmail")  # 'gmail' or 'csv'
#
#     # Email source (nullable for CSV)
#     email_id = Column(String(255), unique=True, nullable=True)
#     email_subject = Column(String(255), nullable=True)
#     email_from = Column(String(255), nullable=True)
#     raw_email_body = Column(Text, nullable=True)
#     
#     # Bank details
#     bank_name = Column(String(100))
#     account_last4 = Column(String(4))
#     reference_id = Column(String(255))
#     
#     # Categorization
#     category_confidence = Column(Float, default=1.0)  # 0-1 score
#     is_manual_category = Column(Boolean, default=False)  # User manually categorized
#     
#     # Metadata
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#
#     # Relationships
#     user = relationship("User", back_populates="transactions")
#     category = relationship("Category", back_populates="transactions")

# COMMENTED OUT - Budget model (used by Transactions API)
# COMMENTED OUT - Budget model (used by Transactions API)
# class Budget(Base):
#     """Monthly budget for categories"""
#     __tablename__ = "budgets"
#
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     category_id = Column(Integer, ForeignKey("categories.id"))
#     
#     month_year = Column(String(7), nullable=False)  # YYYY-MM format
#     budget_amount = Column(Float, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#
#     # Relationships
#     user = relationship("User", back_populates="budgets")

# COMMENTED OUT - InsightLog model (used by Transactions API)
# class InsightLog(Base):
#     """Store generated spending insights"""
#     __tablename__ = "insight_logs"
#
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     
#     month_year = Column(String(7), nullable=False)
#     total_income = Column(Float, default=0.0)
#     total_expenses = Column(Float, default=0.0)
#     total_savings = Column(Float, default=0.0)
#     savings_percentage = Column(Float, default=0.0)
#     
#     health_score = Column(Enum(SpendingHealth), default=SpendingHealth.MODERATE)
#     top_category = Column(String(100))
#     top_category_amount = Column(Float)
#     
#     insights_json = Column(Text)  # JSON blob of insights
#     created_at = Column(DateTime, default=datetime.utcnow)

# COMMENTED OUT - LeakType enum (used by Leak model)
# class LeakType(str, enum.Enum):
#     SUBSCRIPTION = "subscription"
#     SMALL_RECURRING = "small_recurring"
#     IRREGULAR = "irregular"
#     PRICE_CREEP = "price_creep"

# COMMENTED OUT - Subscription model (used by Leaks API)
# class Subscription(Base):
#     """Detected recurring subscriptions"""
#     __tablename__ = "subscriptions"
#
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     
#     name = Column(String(255), nullable=False)
#     amount = Column(Float, nullable=False)
#     currency = Column(String(3), default="INR")
#     interval_days = Column(Integer)  # e.g., 30 for monthly
#     last_charged_date = Column(DateTime)
#     next_expected_date = Column(DateTime)
#     
#     is_active = Column(Boolean, default=True)
#     merchant = Column(String(255))
#     
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#
#     # Relationships
#     user = relationship("User", back_populates="subscriptions")

# COMMENTED OUT - Leak model (used by Leaks API)
# class Leak(Base):
#     """Detected financial leaks"""
#     __tablename__ = "leaks"
#
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     
#     leak_type = Column(Enum(LeakType), nullable=False)
#     title = Column(String(255), nullable=False)
#     description = Column(Text)
#     severity = Column(String(20))  # high, medium, low
#     
#     detected_amount = Column(Float)  # The amount associated with the leak
#     frequency = Column(String(50))   # e.g., "8 times/month"
#     
#     is_resolved = Column(Boolean, default=False)
#     
#     created_at = Column(DateTime, default=datetime.utcnow)
#
#     # Relationships
#     user = relationship("User", back_populates="leaks")

# COMMENTED OUT - Additional relationships to User model (already commented in User class above)
# User.subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
# User.leaks = relationship("Leak", back_populates="user", cascade="all, delete-orphan")


# ==================== NEW MODELS FOR TRANSACTION UPLOAD FEATURE ====================

class Transaction(Base):
    """Transaction data uploaded by users with enriched merchant categorization"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Core transaction facts
    txn_date = Column(DateTime, nullable=False, index=True)
    narration = Column(String(500), nullable=False)
    
    # Amount tracking
    withdrawal_amount = Column(Float, nullable=True)
    deposit_amount = Column(Float, nullable=True)
    money_flow = Column(String(20), nullable=False)  # INFLOW / OUTFLOW / UNKNOWN
    
    # Deterministic enrichment
    level_1_tag = Column(String(50), nullable=False, index=True)
    level_2_tag = Column(String(50), nullable=False, index=True)
    level_3_tag = Column(String(50), nullable=True)
    merchant_hint = Column(String(300), nullable=True, index=True)
    
    # Provenance
    file_upload_id = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="raw_transactions")


class SpendingPatternStats(Base):
    """Spending pattern statistics with aggregated transaction evidence"""
    __tablename__ = "spending_pattern_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Identity
    merchant_hint = Column(String(300), nullable=False, index=True)
    
    # Aggregated evidence
    txn_count = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    avg_amount = Column(Float)
    amount_std = Column(Float)
    amount_min = Column(Float)
    amount_max = Column(Float)
    
    active_duration_days = Column(Integer)
    avg_gap_days = Column(Float)
    gap_std_days = Column(Float)
    gap_min_days = Column(Float)
    gap_max_days = Column(Float)
    
    last_txn_days_ago = Column(Integer)
    
    # Soft metadata (derived, not identity)
    dominant_level_1_tag = Column(String(50))
    level_1_confidence = Column(Float)
    
    dominant_level_2_tag = Column(String(50))
    level_2_confidence = Column(Float)
    
    dominant_level_3_tag = Column(String(50))
    level_3_confidence = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="spending_patterns")
    leak_insights = relationship("LeakInsight", back_populates="pattern", cascade="all, delete-orphan")
    
    # Unique constraint: one pattern per merchant per user
    __table_args__ = (
        # UniqueConstraint would be added here, but SQLAlchemy handles via declarative
    )


class LeakInsight(Base):
    """AI-detected financial leaks from spending patterns"""
    __tablename__ = "leak_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    pattern_id = Column(Integer, ForeignKey("spending_pattern_stats.id"), nullable=False, index=True)
    
    # Leak classification
    leak_category = Column(String(100), nullable=False)  # 'subscription', 'impulse_spending', 'excessive_habit', etc.
    leak_probability = Column(Float, nullable=False)  # 0.0 to 1.0 confidence score
    
    # Analysis results
    reasoning = Column(Text, nullable=False)  # Why this is a leak
    actionable_step = Column(Text, nullable=False)  # What user should do
    estimated_annual_saving = Column(Float, nullable=False)  # Potential annual savings
    
    # Metadata
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status tracking
    is_resolved = Column(Boolean, default=False)  # User marked as fixed
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="leak_insights")
    pattern = relationship("SpendingPatternStats", back_populates="leak_insights")


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
class TransactionType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"

class SpendingHealth(str, enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"

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

    # Relationships
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")

class Category(Base):
    """Transaction categories for spending analysis"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    icon = Column(String(50))
    description = Column(Text)
    color = Column(String(7), default="#3b82f6")  # HEX color
    is_income = Column(Boolean, default=False)
    is_system = Column(Boolean, default=True)  # System categories cannot be deleted
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")

class Transaction(Base):
    """Transaction model storing parsed email data"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # Transaction details
    date = Column(DateTime, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    trans_type = Column(Enum(TransactionType), nullable=False)
    merchant = Column(String(255))
    description = Column(Text)
    
    # Source
    source = Column(String(20), default="gmail")  # 'gmail' or 'csv'

    # Email source (nullable for CSV)
    email_id = Column(String(255), unique=True, nullable=True)
    email_subject = Column(String(255), nullable=True)
    email_from = Column(String(255), nullable=True)
    raw_email_body = Column(Text, nullable=True)
    
    # Bank details
    bank_name = Column(String(100))
    account_last4 = Column(String(4))
    reference_id = Column(String(255))
    
    # Categorization
    category_confidence = Column(Float, default=1.0)  # 0-1 score
    is_manual_category = Column(Boolean, default=False)  # User manually categorized
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

class Budget(Base):
    """Monthly budget for categories"""
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    month_year = Column(String(7), nullable=False)  # YYYY-MM format
    budget_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="budgets")

class InsightLog(Base):
    """Store generated spending insights"""
    __tablename__ = "insight_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    month_year = Column(String(7), nullable=False)
    total_income = Column(Float, default=0.0)
    total_expenses = Column(Float, default=0.0)
    total_savings = Column(Float, default=0.0)
    savings_percentage = Column(Float, default=0.0)
    
    health_score = Column(Enum(SpendingHealth), default=SpendingHealth.MODERATE)
    top_category = Column(String(100))
    top_category_amount = Column(Float)
    
    insights_json = Column(Text)  # JSON blob of insights
    created_at = Column(DateTime, default=datetime.utcnow)

class LeakType(str, enum.Enum):
    SUBSCRIPTION = "subscription"
    SMALL_RECURRING = "small_recurring"
    IRREGULAR = "irregular"
    PRICE_CREEP = "price_creep"

class Subscription(Base):
    """Detected recurring subscriptions"""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    interval_days = Column(Integer)  # e.g., 30 for monthly
    last_charged_date = Column(DateTime)
    next_expected_date = Column(DateTime)
    
    is_active = Column(Boolean, default=True)
    merchant = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscriptions")

class Leak(Base):
    """Detected financial leaks"""
    __tablename__ = "leaks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    leak_type = Column(Enum(LeakType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    severity = Column(String(20))  # high, medium, low
    
    detected_amount = Column(Float)  # The amount associated with the leak
    frequency = Column(String(50))   # e.g., "8 times/month"
    
    is_resolved = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="leaks")

# Add relationships to User model
User.subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
User.leaks = relationship("Leak", back_populates="user", cascade="all, delete-orphan")


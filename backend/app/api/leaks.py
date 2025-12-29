
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Leak, Subscription
from app.core.detector import LeakDetector
from app.api.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# --- Schemas ---
class LeakOut(BaseModel):
    id: int
    leak_type: str
    title: str
    description: str
    severity: str
    detected_amount: float
    frequency: str
    created_at: datetime

class SubscriptionOut(BaseModel):
    id: int
    name: str
    amount: float
    interval_days: int
    next_expected_date: datetime
    merchant: str
    is_active: bool

# --- Endpoints ---

@router.post("/detect")
def detect_leaks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run the leak detection algorithms for the current user"""
    detector = LeakDetector(db, current_user.id)
    detector.run_all()
    return {"message": "Detection complete"}

@router.get("/", response_model=List[LeakOut])
def get_leaks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all detected leaks"""
    return db.query(Leak).filter(Leak.user_id == current_user.id, Leak.is_resolved == False).all()

@router.get("/subscriptions", response_model=List[SubscriptionOut])
def get_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all detected subscriptions"""
    return db.query(Subscription).filter(Subscription.user_id == current_user.id, Subscription.is_active == True).all()

@router.put("/leaks/{leak_id}/resolve")
def resolve_leak(
    leak_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a leak as resolved"""
    leak = db.query(Leak).filter(Leak.id == leak_id, Leak.user_id == current_user.id).first()
    if not leak:
        raise HTTPException(status_code=404, detail="Leak not found")
    
    leak.is_resolved = True
    db.commit()
    return {"message": "Leak resolved"}

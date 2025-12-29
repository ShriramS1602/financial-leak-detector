"""
Transactions API Routes
"""

from typing import List, Optional
from datetime import datetime
import csv
import io
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from pydantic import BaseModel, Field
from app.models import Transaction, Category, User
from app.database import get_db

router = APIRouter()

# ==================== SCHEMAS ====================
class TransactionBase(BaseModel):
    date: datetime
    amount: float
    trans_type: str  # 'credit' or 'debit'
    merchant: str
    category_id: Optional[int] = None
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    merchant: Optional[str] = None
    description: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: int
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    bank_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    transactions: List[TransactionResponse]

class CategorySummary(BaseModel):
    category_id: int
    category_name: str
    category_icon: str
    category_color: str
    total_amount: float
    transaction_count: int
    percentage: float

class MonthlyStats(BaseModel):
    month_year: str
    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate: float
    category_breakdown: List[CategorySummary]

# ==================== ROUTES ====================
@router.get("/", response_model=TransactionListResponse)
async def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    trans_type: Optional[str] = None,
    category_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List transactions with filtering and pagination
    """
    query = db.query(Transaction)
    
    if trans_type:
        query = query.filter(Transaction.trans_type == trans_type)
    
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
        
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    if search:
        search_lower = f"%{search.lower()}%"
        query = query.filter(
            (func.lower(Transaction.merchant).like(search_lower)) | 
            (func.lower(Transaction.description).like(search_lower))
        )
    
    # Pagination
    total = query.count()
    transactions = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # Enrich with category info (if not eager loaded)
    # Ideally use joinedload in query
    
    return TransactionListResponse(
        total=total,
        page=page,
        page_size=page_size,
        transactions=[
            TransactionResponse(
                id=t.id,
                date=t.date,
                amount=t.amount,
                trans_type=t.trans_type,
                merchant=t.merchant,
                category_id=t.category_id,
                description=t.description,
                category_name=t.category.name if t.category else "Uncategorized",
                category_icon=t.category.icon if t.category else "📝",
                bank_name=t.bank_name,
                created_at=t.created_at
            ) for t in transactions
        ]
    )

@router.get("/stats", response_model=MonthlyStats)
async def get_monthly_stats(
    month_year: Optional[str] = None,  # Format: YYYY-MM
    db: Session = Depends(get_db)
):
    """
    Get monthly spending statistics
    """
    target_date = datetime.now()
    if month_year:
        try:
            target_date = datetime.strptime(month_year, "%Y-%m")
        except ValueError:
            pass
            
    # Calculate totals
    income = db.query(func.sum(Transaction.amount)).filter(
        extract('year', Transaction.date) == target_date.year,
        extract('month', Transaction.date) == target_date.month,
        Transaction.trans_type == 'credit'
    ).scalar() or 0.0
    
    expenses = db.query(func.sum(Transaction.amount)).filter(
        extract('year', Transaction.date) == target_date.year,
        extract('month', Transaction.date) == target_date.month,
        Transaction.trans_type == 'debit'
    ).scalar() or 0.0
    
    net_savings = income - expenses
    savings_rate = (net_savings / income * 100) if income > 0 else 0
    
    # Category breakdown
    category_stats = db.query(
        Transaction.category_id,
        func.sum(Transaction.amount).label('total')
    ).filter(
        extract('year', Transaction.date) == target_date.year,
        extract('month', Transaction.date) == target_date.month,
        Transaction.trans_type == 'debit'
    ).group_by(Transaction.category_id).all()
    
    breakdown = []
    for cat_id, total in category_stats:
        cat = db.query(Category).filter(Category.id == cat_id).first()
        breakdown.append(CategorySummary(
            category_id=cat_id or 0,
            category_name=cat.name if cat else "Uncategorized",
            category_icon=cat.icon if cat else "📝",
            category_color=cat.color if cat else "#6b7280",
            total_amount=total,
            transaction_count=0, # Simplified for now
            percentage=(total / expenses * 100) if expenses > 0 else 0
        ))
    
    return MonthlyStats(
        month_year=target_date.strftime("%Y-%m"),
        total_income=income,
        total_expenses=expenses,
        net_savings=net_savings,
        savings_rate=savings_rate,
        category_breakdown=breakdown
    )

@router.get("/{transaction_id}", response_model=TransactionResponse)

async def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """
    Get a single transaction by ID
    """
    t = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not t:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found"
        )
    
    return TransactionResponse(
        id=t.id,
        date=t.date,
        amount=t.amount,
        trans_type=t.trans_type,
        merchant=t.merchant,
        category_id=t.category_id,
        description=t.description,
        category_name=t.category.name if t.category else "Uncategorized",
        category_icon=t.category.icon if t.category else "📝",
        bank_name=t.bank_name,
        created_at=t.created_at
    )

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)

async def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """
    Create a new transaction manually
    """
    # TODO: Get actual user ID from auth
    user = db.query(User).first()
    if not user:
        # Create default user if none exists (temporary fix)
        user = User(email="default@example.com", name="Default User")
        db.add(user)
        db.commit()
        db.refresh(user)

    new_transaction = Transaction(
        user_id=user.id,
        date=transaction.date,
        amount=transaction.amount,
        trans_type=transaction.trans_type,
        merchant=transaction.merchant,
        category_id=transaction.category_id,
        description=transaction.description,
        source="manual"
    )
    
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    
    return TransactionResponse(
        id=new_transaction.id,
        date=new_transaction.date,
        amount=new_transaction.amount,
        trans_type=new_transaction.trans_type,
        merchant=new_transaction.merchant,
        category_id=new_transaction.category_id,
        description=new_transaction.description,
        category_name=new_transaction.category.name if new_transaction.category else "Uncategorized",
        category_icon=new_transaction.category.icon if new_transaction.category else "📝",
        bank_name=new_transaction.bank_name,
        created_at=new_transaction.created_at
    )

@router.put("/{transaction_id}", response_model=TransactionResponse)

async def update_transaction(transaction_id: int, update: TransactionUpdate, db: Session = Depends(get_db)):
    """
    Update a transaction
    """
    t = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not t:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found"
        )
    
    if update.category_id is not None:
        t.category_id = update.category_id
    if update.merchant is not None:
        t.merchant = update.merchant
    if update.description is not None:
        t.description = update.description
        
    db.commit()
    db.refresh(t)
    
    return TransactionResponse(
        id=t.id,
        date=t.date,
        amount=t.amount,
        trans_type=t.trans_type,
        merchant=t.merchant,
        category_id=t.category_id,
        description=t.description,
        category_name=t.category.name if t.category else "Uncategorized",
        category_icon=t.category.icon if t.category else "📝",
        bank_name=t.bank_name,
        created_at=t.created_at
    )

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)

async def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """
    Delete a transaction
    """
    t = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not t:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found"
        )
    
    db.delete(t)
    db.commit()
    return

@router.post("/upload-csv", response_model=TransactionListResponse)

async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a CSV file of transactions
    Expected columns: date, description, amount, type, category (optional)
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")
    
    # TODO: Get actual user ID from auth
    user = db.query(User).first()
    if not user:
        user = User(email="default@example.com", name="Default User")
        db.add(user)
        db.commit()
        db.refresh(user)

    content = await file.read()
    decoded_content = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded_content))
    
    new_transactions = []
    
    # Normalize headers to lowercase
    if csv_reader.fieldnames:
        csv_reader.fieldnames = [name.lower() for name in csv_reader.fieldnames]
    
    for row in csv_reader:
        try:
            # Basic mapping logic
            date_str = row.get('date') or row.get('transaction date')
            amount_str = row.get('amount') or row.get('debit') or row.get('credit')
            desc = row.get('description') or row.get('narration') or row.get('particulars')
            trans_type = row.get('type') or ('credit' if row.get('credit') else 'debit')
            category = row.get('category')
            
            if not date_str or not amount_str:
                continue
                
            # Parse date (try a few formats)
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                except ValueError:
                    date_obj = datetime.now() # Fallback
            
            # Parse amount
            amount = float(amount_str.replace(',', '').replace('₹', ''))
            
            transaction = Transaction(
                user_id=user.id,
                date=date_obj,
                amount=abs(amount),
                trans_type=trans_type.lower() if trans_type else 'debit',
                merchant=desc.split()[0] if desc else "Unknown",
                description=desc,
                source="csv",
                bank_name="CSV Upload"
            )
            
            db.add(transaction)
            new_transactions.append(transaction)
            
        except Exception as e:
            print(f"Skipping row due to error: {e}")
            continue
            
    db.commit()
    
    # Refresh to get IDs
    for t in new_transactions:
        db.refresh(t)
    
    return TransactionListResponse(
        total=len(new_transactions),
        page=1,
        page_size=len(new_transactions),
        transactions=[
            TransactionResponse(
                id=t.id,
                date=t.date,
                amount=t.amount,
                trans_type=t.trans_type,
                merchant=t.merchant,
                category_id=t.category_id,
                description=t.description,
                category_name=t.category.name if t.category else "Uncategorized",
                category_icon=t.category.icon if t.category else "📝",
                bank_name=t.bank_name,
                created_at=t.created_at
            ) for t in new_transactions
        ]
    )

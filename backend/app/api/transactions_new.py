"""
Transaction Upload API
Endpoints for uploading and processing transaction files
"""

from fastapi import APIRouter, UploadFile, File, Depends, status, HTTPException, Form
from sqlalchemy.orm import Session
import logging
import json

from app.database import get_db
from app.api.auth import get_current_user
from app.core.transaction_processor import TransactionUploadProcessor
from app.models import User

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/transactions",
    tags=["transactions"],
)


@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_transactions(
    file: UploadFile = File(...),
    column_mapping: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload transaction file (CSV/Excel) and process for pattern detection
    
    - **file**: CSV or Excel file (.csv, .xlsx, .xls)
    - **column_mapping**: Optional JSON string mapping file columns to expected columns
      Example: {"Date": "date_field", "Narration": "desc_field", ...}
    - Returns: Upload statistics, detected patterns, and invalid rows
    """
    try:
        logger.info(f"Received transaction upload from user {current_user.id}")
        
        # Parse column mapping if provided
        column_mapping_dict = None
        if column_mapping:
            try:
                column_mapping_dict = json.loads(column_mapping)
                logger.info(f"Column mapping provided: {column_mapping_dict}")
            except json.JSONDecodeError:
                logger.error(f"Invalid column_mapping JSON: {column_mapping}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid column_mapping format. Must be valid JSON."
                )
        
        # Process the upload
        result = await TransactionUploadProcessor.process_upload(
            file=file,
            user_id=current_user.id,
            db=db,
            column_mapping=column_mapping_dict
        )
        
        # Handle errors
        if result.get("status") == "error":
            logger.warning(f"Upload failed: {result.get('detail')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("detail")
            )
        
        txn_count = result['statistics']['transactions_stored']
        pattern_count = result['statistics']['pattern_stats_stored']
        logger.info(f"Upload successful: {txn_count} transactions stored, {pattern_count} patterns aggregated")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process transaction file"
        )


@router.get("/patterns")
async def get_user_patterns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all spending pattern statistics for the current user
    """
    try:
        from app.models import SpendingPatternStats
        
        patterns = db.query(SpendingPatternStats).filter(
            SpendingPatternStats.user_id == current_user.id
        ).all()
        
        logger.info(f"Retrieved {len(patterns)} pattern statistics for user {current_user.id}")
        
        return {
            "status": "success",
            "patterns": [
                {
                    "id": p.id,
                    "merchant_hint": p.merchant_hint,
                    "level_1_tag": p.level_1_tag,
                    "level_2_tag": p.level_2_tag,
                    "level_3_tag": p.level_3_tag,
                    "evidence": {
                        "txn_count": p.txn_count,
                        "total_amount": p.total_amount,
                        "avg_amount": p.avg_amount,
                        "dominant_level_3_tag": p.dominant_level_3_tag,
                        "level_3_confidence": p.level_3_confidence,
                        "gap_mean_days": p.gap_mean_days,
                        "gap_std_days": p.gap_std_days,
                        "gap_min_days": p.gap_min_days,
                        "gap_max_days": p.gap_max_days,
                        "recency_days": p.recency_days
                    },
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                    "updated_at": p.updated_at.isoformat() if p.updated_at else None
                }
                for p in patterns
            ]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving patterns: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patterns"
        )


@router.get("/raw-transactions")
async def get_user_raw_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 100,
    skip: int = 0
):
    """
    Get raw uploaded transactions for the current user
    """
    try:
        from app.models import Transaction
        
        transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id
        ).order_by(Transaction.txn_date.desc()).offset(skip).limit(limit).all()
        
        total = db.query(Transaction).filter(
            Transaction.user_id == current_user.id
        ).count()
        
        logger.info(f"Retrieved {len(transactions)} transactions for user {current_user.id}")
        
        return {
            "status": "success",
            "total": total,
            "skip": skip,
            "limit": limit,
            "transactions": [
                {
                    "id": t.id,
                    "txn_date": t.txn_date.isoformat() if isinstance(t.txn_date, str) else str(t.txn_date),
                    "narration": t.narration,
                    "withdrawal_amount": t.withdrawal_amount,
                    "deposit_amount": t.deposit_amount,
                    "money_flow": t.money_flow,
                    "level_1_tag": t.level_1_tag,
                    "level_2_tag": t.level_2_tag,
                    "level_3_tag": t.level_3_tag,
                    "merchant_hint": t.merchant_hint,
                    "file_upload_id": t.file_upload_id,
                    "created_at": t.created_at.isoformat() if hasattr(t.created_at, 'isoformat') else str(t.created_at)
                }
                for t in transactions
            ]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving transactions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transactions"
        )

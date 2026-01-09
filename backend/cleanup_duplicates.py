"""
Cleanup script to remove duplicate transactions from database
Keeps only the first occurrence of each duplicate set
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import Transaction, SpendingPatternStats
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finance_tracker.db")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def cleanup_duplicates(user_id: int = None):
    """
    Remove duplicate transactions, keeping the first occurrence
    Duplicates = same user_id, txn_date, narration, withdrawal_amount, deposit_amount
    """
    db = Session()
    try:
        # Query to find duplicates
        if user_id:
            duplicates_query = text("""
                SELECT id, txn_date, narration, withdrawal_amount, deposit_amount, user_id
                FROM transactions
                WHERE user_id = :user_id
                ORDER BY user_id, txn_date, narration, withdrawal_amount, deposit_amount, id
            """)
            result = db.execute(duplicates_query, {"user_id": user_id})
        else:
            # All users
            duplicates_query = text("""
                SELECT id, txn_date, narration, withdrawal_amount, deposit_amount, user_id
                FROM transactions
                ORDER BY user_id, txn_date, narration, withdrawal_amount, deposit_amount, id
            """)
            result = db.execute(duplicates_query)
        
        rows = result.fetchall()
        
        seen = set()
        ids_to_delete = []
        duplicates_count = 0
        
        for row in rows:
            txn_id, txn_date, narration, withdrawal, deposit, user = row
            
            # Create a key for this transaction
            key = (user, txn_date, narration, withdrawal, deposit)
            
            if key in seen:
                # This is a duplicate - mark for deletion
                ids_to_delete.append(txn_id)
                duplicates_count += 1
                logger.info(f"Found duplicate: ID {txn_id} - {narration} on {txn_date}")
            else:
                # First occurrence - keep it
                seen.add(key)
        
        if not ids_to_delete:
            logger.info("No duplicates found!")
            return
        
        logger.info(f"\nFound {duplicates_count} duplicates. Deleting {len(ids_to_delete)} rows...")
        
        # Delete duplicates
        for txn_id in ids_to_delete:
            db.execute(text("DELETE FROM transactions WHERE id = :id"), {"id": txn_id})
        
        db.commit()
        logger.info(f"✓ Successfully deleted {len(ids_to_delete)} duplicate transactions")
        
        # Show before/after stats
        if user_id:
            total = db.query(Transaction).filter(Transaction.user_id == user_id).count()
            logger.info(f"\nUser {user_id}: Now has {total} transactions (was {total + duplicates_count})")
        else:
            total = db.query(Transaction).count()
            logger.info(f"\nDatabase now has {total} total transactions (was {total + duplicates_count})")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    user_id = None
    if len(sys.argv) > 1:
        try:
            user_id = int(sys.argv[1])
            logger.info(f"Cleaning duplicates for user {user_id}...")
        except ValueError:
            logger.error("Usage: python cleanup_duplicates.py [user_id]")
            sys.exit(1)
    else:
        logger.info("Cleaning duplicates for ALL users...")
    
    cleanup_duplicates(user_id)

"""
Email Sync API Routes
"""

import os
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from pydantic import BaseModel
from jose import jwt

from ..email_service import GmailService, EmailParser, TransactionCategorizer, AITransactionParser

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# ==================== SCHEMAS ====================
class EmailSyncRequest(BaseModel):
    days_back: int = 30
    max_emails: int = 100
    use_ai: bool = False

class EmailSyncResponse(BaseModel):
    status: str
    emails_processed: int
    transactions_found: int
    message: str

class ParsedTransaction(BaseModel):
    email_id: str
    date: datetime
    amount: float
    trans_type: str
    merchant: str
    category: str
    category_confidence: float
    bank_name: Optional[str] = None

# ==================== HELPERS ====================
def get_gmail_token(request: Request) -> str:
    """Extract Gmail token from JWT - requires authentication."""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please login with Google first."
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        gmail_token = payload.get("gmail_token")
        if not gmail_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Gmail token not found. Please re-authenticate with Google."
            )
        return gmail_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired. Please login again."
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token. Please login again."
        )

# ==================== ROUTES ====================
@router.post("/sync", response_model=EmailSyncResponse)
async def sync_emails(
    request: Request,
    sync_request: EmailSyncRequest,
    background_tasks: BackgroundTasks
):
    """
    Sync emails from Gmail and extract transactions.
    Requires Google OAuth authentication.
    """
    print("Syncing emails...")
    try:
        gmail_token = get_gmail_token(request)
        
        # Initialize services
        gmail = GmailService(gmail_token)
        categorizer = TransactionCategorizer()
        ai_parser = AITransactionParser(api_key=os.getenv("LLM_API_KEY"))

        # Build Gmail search query
        date_from = (datetime.now() - timedelta(days=sync_request.days_back)).strftime('%Y/%m/%d')
        print(f"DEBUG: Syncing emails from {date_from}")
        
        # Use a broader query for debugging, or the specific one
        query = f"after:{date_from} (subject:(transaction OR payment OR debited OR credited) OR from:(bank OR hdfc OR icici OR axis))"
        print(f"DEBUG: Query: {query}")

        # Fetch messages
        messages = gmail.get_messages(query=query, max_results=sync_request.max_emails)
        print(f"DEBUG: Found {len(messages)} messages")
        
        transactions_found = 0
        for msg in messages:
            message_content = gmail.get_message_content(msg['id'])
            snippet = message_content.get('snippet', '')
            print(f"DEBUG: Processing Email - ID: {msg['id']}, Snippet: {snippet}")
            
            transaction = None
            if sync_request.use_ai and ai_parser.api_key:
                try:
                    # AI Parsing
                    snippet = message_content.get('snippet', '')
                    
                    ai_result = ai_parser.parse_email_content(snippet)
                    print(ai_result)
                    if ai_result and ai_result.get('amount'):
                        # Parse date safely
                        date_val = datetime.now()
                        if ai_result.get('date'):
                            try:
                                date_val = datetime.strptime(ai_result.get('date'), '%Y-%m-%d')
                            except:
                                pass
                                
                        transaction = {
                            'email_id': msg['id'],
                            'email_subject': snippet,
                            'email_from': headers.get('from', ''),
                            'raw_email_body': snippet[:500],
                            'date': date_val,
                            'amount': float(ai_result.get('amount')),
                            'trans_type': ai_result.get('type', 'debit').lower(),
                            'merchant': ai_result.get('merchant', 'Unknown'),
                            'description': ai_result.get('description', subject),
                            'bank_name': None,
                            'category_suggestion': ai_result.get('category')
                        }
                except Exception as e:
                    print(f"AI parsing error: {e}")
                    # Fallback to regex
                    transaction = EmailParser.parse_transaction(message_content, msg['id'])
            
            if not transaction:
                # Regex Parsing Fallback
                transaction = EmailParser.parse_transaction(message_content, msg['id'])
            
            if transaction:
                # Categorize transaction
                category, confidence = categorizer.categorize(transaction)
                transaction['category'] = category
                transaction['category_confidence'] = confidence
                transactions_found += 1
                
                # TODO: Save to database
        
        return EmailSyncResponse(
            status="success",
            emails_processed=len(messages),
            transactions_found=transactions_found,
            message=f"Successfully processed {len(messages)} emails, found {transactions_found} transactions"
        )
    
    except HTTPException:
        print("HTTPException")
        raise
    except Exception as e:
        print("Exception")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync emails: {str(e)}"
        )

@router.get("/preview")
async def preview_emails(request: Request, limit: int = 10):
    """
    Preview recent financial emails without saving.
    Requires Google OAuth authentication.
    """
    try:
        gmail_token = get_gmail_token(request)
        
        query = "subject:(transaction OR payment OR debited OR credited) OR from:(bank OR hdfc OR icici)"
        
        gmail = GmailService(gmail_token)
        categorizer = TransactionCategorizer()
        
        messages = gmail.get_messages(query=query, max_results=limit)
        
        parsed_transactions: List[dict] = []
        for msg in messages:
            message_content = gmail.get_message_content(msg['id'])
            transaction = EmailParser.parse_transaction(message_content, msg['id'])
            
            if transaction:
                category, confidence = categorizer.categorize(transaction)
                parsed_transactions.append({
                    "email_id": transaction['email_id'],
                    "date": transaction['date'].isoformat(),
                    "amount": transaction['amount'],
                    "trans_type": transaction['trans_type'],
                    "merchant": transaction['merchant'],
                    "category": category,
                    "category_confidence": confidence,
                    "bank_name": transaction.get('bank_name'),
                    "subject": transaction.get('email_subject', '')
                })
        
        return {
            "total_emails": len(messages),
            "transactions": parsed_transactions
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview emails: {str(e)}"
        )

@router.get("/status")
async def email_sync_status(request: Request):
    """
    Get email sync status for current user
    """
    # TODO: Implement actual status tracking
    return {
        "last_sync": None,
        "total_emails_synced": 0,
        "total_transactions": 0,
        "sync_in_progress": False
    }

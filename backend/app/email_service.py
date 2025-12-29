"""
Email Parsing & Transaction Extraction Service
Handles Gmail API integration and email content parsing
"""

import base64
import re
from datetime import datetime
from email.mime.text import MIMEText
from typing import Optional, Dict, List, Tuple
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

# ==================== GMAIL SERVICE ====================
class GmailService:
    """Wrapper around Gmail API"""
    
    def __init__(self, access_token: str, refresh_token: str = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.credentials = Credentials(token=access_token, refresh_token=refresh_token)
        self.service = build('gmail', 'v1', credentials=self.credentials)
    
    def get_messages(self, query: str = "", max_results: int = 100) -> List[Dict]:
        """Fetch messages from Gmail with optional query"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=min(max_results, 100)
            ).execute()
            return results.get('messages', [])
        except RefreshError:
            logger.error("Token refresh failed. User needs to re-authenticate.")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch messages: {str(e)}")
            raise

    def get_message_content(self, message_id: str) -> Dict:
        """Get full message content by ID"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            return message
        except Exception as e:
            logger.error(f"Failed to get message {message_id}: {str(e)}")
            return {}

# ==================== EMAIL PARSER ====================
class EmailParser:
    """Parse and extract transaction data from emails"""
    
    # Bank patterns for detection
    BANK_PATTERNS = {
        'HDFC': r'hdfc.*?bank',
        'ICICI': r'icici.*?bank',
        'Axis': r'axis.*?bank',
        'SBI': r'sbi|state.*?bank',
        'Citi': r'citi.*?bank',
        'AMEX': r'american.*?express|amex',
    }
    
    # Insurance patterns
    INSURANCE_PATTERNS = {
        'LIC': r'\blic\b|life.*?insurance',
        'Health Insurance': r'health.*?insurance|arogya',
        'Vehicle Insurance': r'vehicle.*?insurance|motor.*?insurance|car.*?insurance',
    }
    
    # Merchant patterns
    MERCHANT_PATTERNS = {
        'Food & Dining': r'swiggy|zomato|dominos|pizza|restaurant|cafe|diner|burger',
        'Shopping': r'amazon|flipkart|myntra|ajio|snapdeal|fashion|clothing|dress',
        'Utility Bills': r'electricity|water|gas|broadband|mobile.*?bill',
        'Subscriptions': r'netflix|amazon.*?prime|hotstar|spotify|youtube',
        'Fuel': r'petrol|diesel|fuel|gas.*?station|iocl|bharat|reliance',
    }
    
    @staticmethod
    def extract_amount(text: str) -> Optional[float]:
        """Extract monetary amount from text"""
        # Patterns: "INR 543.00", "₹543", "Rs. 543", "543.00"
        patterns = [
            r'(?:INR|Rs\.?|₹)\s*(?:,)?(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(?:amount|credited|debited).*?(?:INR|Rs\.?|₹)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        return None
    
    @staticmethod
    def extract_date(text: str) -> Optional[datetime]:
        """Extract date from email text"""
        date_patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',  # DD-MM-YYYY or MM-DD-YYYY
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # YYYY-MM-DD
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4}',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1)
                    for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%B %d, %Y', '%b %d, %Y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except Exception as e:
                    logger.debug(f"Date parsing error: {str(e)}")
                    continue
        
        return None
    
    @staticmethod
    def extract_merchant(text: str) -> Optional[str]:
        """Extract merchant/vendor name from text"""
        merchants = [
            r'(?:merchant|vendor|biller|payee)\s*:?\s*([A-Za-z0-9\s&\.]+)',
            r'at\s+([A-Za-z0-9\s&\.]+?)(?:\s|$)',
            r'from\s+([A-Za-z0-9\s&\.]+?)(?:\s|$)',
        ]
        
        for pattern in merchants:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                merchant = match.group(1).strip()
                if len(merchant) > 3 and len(merchant) < 100:
                    return merchant
        
        return None

    @staticmethod
    def decode_email_body(message: Dict) -> str:
        """Decode email body from Gmail message format"""
        try:
            payload = message.get('payload', {})
            
            # Try to get plain text part
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8')
            
            # Fallback to main body
            elif 'body' in payload:
                data = payload['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
        
        except Exception as e:
            logger.error(f"Failed to decode email body: {str(e)}")
        
        return ""

    @staticmethod
    def get_email_headers(message: Dict) -> Dict[str, str]:
        """Extract key headers from Gmail message"""
        headers = message.get('payload', {}).get('headers', [])
        header_dict = {}
        
        for header in headers:
            name = header.get('name', '').lower()
            value = header.get('value', '')
            header_dict[name] = value
        
        return header_dict

    @classmethod
    def parse_transaction(cls, message: Dict, message_id: str) -> Optional[Dict]:
        """
        Parse a single email message and extract transaction data
        Returns dict with transaction info or None if not financial
        """
        try:
            headers = cls.get_email_headers(message)
            body = cls.decode_email_body(message)
            subject = headers.get('subject', '')
            sender = headers.get('from', '')
            
            # Combine for analysis
            full_text = f"{subject} {body}"
            
            # Extract amount
            amount = cls.extract_amount(full_text)
            if not amount:
                return None  # Not a financial email
            
            # Extract date (default to today if not found)
            trans_date = cls.extract_date(full_text) or datetime.now()
            
            # Detect transaction type
            is_credit = bool(re.search(r'credit|received|deposit|refund|income', full_text, re.IGNORECASE))
            trans_type = 'credit' if is_credit else 'debit'
            
            # Extract merchant
            merchant = cls.extract_merchant(full_text)
            
            # Detect bank
            bank_name = None
            for bank, pattern in cls.BANK_PATTERNS.items():
                if re.search(pattern, sender, re.IGNORECASE):
                    bank_name = bank
                    break
            
            return {
                'email_id': message_id,
                'email_subject': subject,
                'email_from': sender,
                'raw_email_body': body[:500],  # Store first 500 chars
                'date': trans_date,
                'amount': amount,
                'trans_type': trans_type,
                'merchant': merchant or 'Unknown',
                'description': subject,
                'bank_name': bank_name,
                'category_suggestion': None,  # Will be filled by categorizer
            }
        
        except Exception as e:
            logger.error(f"Error parsing transaction: {str(e)}")
            return None

# ==================== CATEGORIZER ====================
class TransactionCategorizer:
    """Categorize transactions based on content"""
    
    DEFAULT_CATEGORIES = {
        'Income': {'icon': '💰', 'color': '#10b981', 'is_income': True},
        'Salary': {'icon': '💼', 'color': '#10b981', 'is_income': True},
        'Insurance': {'icon': '🛡️', 'color': '#8b5cf6'},
        'Food & Dining': {'icon': '🍔', 'color': '#f59e0b'},
        'Shopping': {'icon': '🛍️', 'color': '#ec4899'},
        'Bills & Utilities': {'icon': '💡', 'color': '#6366f1'},
        'Travel & Transport': {'icon': '🚗', 'color': '#06b6d4'},
        'Entertainment': {'icon': '🎬', 'color': '#a855f7'},
        'Investments': {'icon': '📈', 'color': '#14b8a6'},
        'Loan & EMI': {'icon': '📊', 'color': '#ef4444'},
        'Cash Withdrawal': {'icon': '💸', 'color': '#78350f'},
        'Education': {'icon': '🎓', 'color': '#3b82f6'},
        'Health & Medical': {'icon': '⚕️', 'color': '#ef4444'},
        'Others': {'icon': '📝', 'color': '#6b7280'},
    }
    
    @classmethod
    def get_default_categories(cls) -> Dict:
        """Return default category definitions"""
        return cls.DEFAULT_CATEGORIES
    
    @classmethod
    def categorize(cls, transaction: Dict) -> Tuple[str, float]:
        """
        Categorize a transaction based on content
        Returns (category_name, confidence_score)
        """
        text = f"{transaction.get('merchant', '')} {transaction.get('description', '')}".lower()
        
        # Insurance detection
        if any(pattern in text for pattern in ['lic', 'insurance', 'premium', 'policy']):
            return ('Insurance', 0.95)
        
        # Food & Dining
        if any(pattern in text for pattern in ['swiggy', 'zomato', 'dominos', 'restaurant', 'cafe']):
            return ('Food & Dining', 0.98)
        
        # Shopping
        if any(pattern in text for pattern in ['amazon', 'flipkart', 'myntra', 'shopping']):
            return ('Shopping', 0.97)
        
        # Bills & Utilities
        if any(pattern in text for pattern in ['electricity', 'water', 'internet', 'mobile', 'broadband']):
            return ('Bills & Utilities', 0.95)
        
        # Travel
        if any(pattern in text for pattern in ['uber', 'ola', 'travel', 'fuel', 'petrol', 'taxi']):
            return ('Travel & Transport', 0.90)
        
        # Investments
        if any(pattern in text for pattern in ['mutual fund', 'sip', 'stock', 'investment', 'nse', 'bse']):
            return ('Investments', 0.93)
        
        # Subscriptions
        if any(pattern in text for pattern in ['netflix', 'spotify', 'prime', 'hotstar', 'youtube']):
            return ('Entertainment', 0.92)
        
        # Cash Withdrawal
        if 'atm' in text or 'cash withdrawal' in text or 'cash' in text:
            return ('Cash Withdrawal', 0.98)
        
        # Health & Medical
        if any(pattern in text for pattern in ['hospital', 'medical', 'doctor', 'pharmacy', 'health']):
            return ('Health & Medical', 0.90)
        
        # Default
        return ('Others', 0.3)

# ==================== AI PARSER ====================
class AITransactionParser:
    """
    AI-powered transaction parser using LLM (Gemini/OpenAI)
    Falls back to regex parser if API key is missing or fails
    """
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "gemini"):
        self.api_key = api_key
        self.provider = provider
        
    def parse_email_content(self, email_text: str) -> Dict:
        """
        Use AI to extract transaction details from email text
        Returns dict with: amount, merchant, date, category, etc.
        """
        if not self.api_key:
            logger.warning("No AI API key provided. Skipping AI parsing.")
            return {}
            
        prompt = f'''
        Analyze the following financial email snippet and extract transaction details.
        
        Snippet: "{email_text}"
        
        Return ONLY a valid JSON object with the following keys:
        - amount: (number) The transaction amount.
        - currency: (string) Currency code (e.g., "INR").
        - date: (string) Date in YYYY-MM-DD format.
        - merchant: (string) The name of the merchant or receiver (e.g., "Cumta", "UBER INDIA", "Amazon Pay").
        - type: (string) "debit" or "credit".
        - ref_number: (string) The transaction reference number.
        - risk_score: (number) 1-10 (10 = high risk/wasteful).
        - tip: (string) A brief financial tip.
        - description: (string) A brief summary of the transaction.
        - category: (string) Choose from: Food, Travel, Shopping, Bills, Insurance, Investment, Salary, Medical, Other.

        If any field cannot be found, use null.
        '''
        
        try:
            import requests
            import json
            
            if self.provider == "gemini":
                # Use Gemini 1.5 Flash for speed and cost
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                headers = {'Content-Type': 'application/json'}
                data = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "response_mime_type": "application/json"
                    }
                }
                
                response = requests.post(url, headers=headers, json=data)
                print(response)
                
                if response.status_code != 200:
                    logger.error(f"Gemini API Error: {response.text}")
                    return {}
                
                result = response.json()
                
                try:
                    # Extract text from Gemini response
                    text_response = result['candidates'][0]['content']['parts'][0]['text']
                    return json.loads(text_response)
                except (KeyError, IndexError, json.JSONDecodeError) as e:
                    logger.error(f"Failed to parse Gemini response: {e}")
                    return {}
            
            return {} 
            
        except Exception as e:
            logger.error(f"AI parsing failed: {str(e)}")
            return {}

    def enhance_transaction(self, transaction: Dict) -> Dict:
        """
        Enhance an already parsed transaction with AI insights (Category, Risk, Tips)
        """
        if not self.api_key:
            return transaction
            
        # This would be a lighter call just for categorization/insights
        return transaction

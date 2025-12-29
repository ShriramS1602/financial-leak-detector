"""
Authentication API Routes - OAuth with Gmail & Email/Password Auth
Complete authentication system with email verification and password reset
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models import User
from app.schema import UserCreate, UserResponse, Token
from app.database import get_db
from app.crypto import decrypt_password
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# ==================== CONFIG ====================
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/callback")

# Email settings
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@finguard.com")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Allow scope change (Google adds 'openid' automatically)
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==================== PYDANTIC MODELS ====================
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class UserSignup(BaseModel):
    email: EmailStr
    password: str
    username: str
    name: Optional[str] = None
    terms_accepted: bool = False
    privacy_accepted: bool = False


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class GoogleSignupData(BaseModel):
    terms_accepted: bool
    privacy_accepted: bool


# ==================== EMAIL HELPERS ====================
def send_email(to_email: str, subject: str, html_content: str):
    """Send email using SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        if SMTP_USER and SMTP_PASSWORD:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(FROM_EMAIL, to_email, msg.as_string())
            logger.info(f"Email sent successfully to {to_email}")
        else:
            # Log email for development
            logger.info(f"[DEV MODE] Email to {to_email}: {subject}")
            logger.info(f"[DEV MODE] Content: {html_content}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        raise


def get_email_verification_template(name: str, verification_link: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verify Your Email</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc;">
        <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; border-radius: 16px 16px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 700;">🛡️ FinGuard</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 14px;">Smart Insights for Smarter Spending</p>
            </div>
            <div style="background: white; padding: 40px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #1e293b; margin: 0 0 20px 0; font-size: 24px;">Welcome, {name or 'there'}! 👋</h2>
                <p style="color: #64748b; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                    Thank you for signing up for FinGuard. Please verify your email address to activate your account and start your journey to financial freedom.
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_link}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; padding: 14px 40px; border-radius: 8px; font-weight: 600; font-size: 16px;">
                        Verify Email Address
                    </a>
                </div>
                <p style="color: #94a3b8; font-size: 14px; line-height: 1.6; margin: 20px 0 0 0;">
                    This link will expire in 24 hours. If you didn't create an account with FinGuard, you can safely ignore this email.
                </p>
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                <p style="color: #94a3b8; font-size: 12px; text-align: center; margin: 0;">
                    If the button doesn't work, copy and paste this link into your browser:<br>
                    <a href="{verification_link}" style="color: #667eea; word-break: break-all;">{verification_link}</a>
                </p>
            </div>
            <p style="color: #94a3b8; font-size: 12px; text-align: center; margin: 20px 0 0 0;">
                © {datetime.now().year} FinGuard. All rights reserved.
            </p>
        </div>
    </body>
    </html>
    """


def get_password_reset_template(name: str, reset_link: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reset Your Password</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc;">
        <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; border-radius: 16px 16px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 700;">🛡️ FinGuard</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 14px;">Smart Insights for Smarter Spending</p>
            </div>
            <div style="background: white; padding: 40px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #1e293b; margin: 0 0 20px 0; font-size: 24px;">Reset Your Password 🔐</h2>
                <p style="color: #64748b; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                    Hi {name or 'there'}, we received a request to reset your password. Click the button below to create a new password.
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; padding: 14px 40px; border-radius: 8px; font-weight: 600; font-size: 16px;">
                        Reset Password
                    </a>
                </div>
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; border-radius: 4px; margin: 20px 0;">
                    <p style="color: #92400e; font-size: 14px; margin: 0;">
                        ⚠️ <strong>Security Notice:</strong> This link will expire in 1 hour. If you didn't request a password reset, please ignore this email or contact support.
                    </p>
                </div>
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                <p style="color: #94a3b8; font-size: 12px; text-align: center; margin: 0;">
                    If the button doesn't work, copy and paste this link into your browser:<br>
                    <a href="{reset_link}" style="color: #667eea; word-break: break-all;">{reset_link}</a>
                </p>
            </div>
            <p style="color: #94a3b8; font-size: 12px; text-align: center; margin: 20px 0 0 0;">
                © {datetime.now().year} FinGuard. All rights reserved.
            </p>
        </div>
    </body>
    </html>
    """


# ==================== TOKEN HELPERS ====================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_verification_token(email: str) -> str:
    """Create email verification token valid for 24 hours"""
    return create_access_token(
        data={"sub": email, "type": "email_verification"},
        expires_delta=timedelta(hours=24)
    )


def create_password_reset_token(email: str) -> str:
    """Create password reset token valid for 1 hour"""
    return create_access_token(
        data={"sub": email, "type": "password_reset"},
        expires_delta=timedelta(hours=1)
    )


def verify_token(token: str, expected_type: str) -> Optional[str]:
    """Verify a JWT token and return the email if valid"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        token_type = payload.get("type")
        if email is None or token_type != expected_type:
            return None
        return email
    except JWTError:
        return None


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_google_flow() -> Flow:
    """Create OAuth flow for Google"""
    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [GOOGLE_REDIRECT_URI],
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    return flow


def get_current_user_from_token(request: Request, db: Session) -> User:
    """Extract and validate user from Authorization header"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """FastAPI dependency to get current authenticated user"""
    return get_current_user_from_token(request, db)


# ==================== ROUTES ====================

# ----- Google OAuth -----
@router.get("/login")
async def initiate_google_login():
    """Initiate OAuth login with Google"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
        )
    
    flow = get_google_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    return {"authorization_url": authorization_url, "state": state}


@router.get("/google/signup")
async def initiate_google_signup():
    """Initiate OAuth signup with Google (same as login but returns different state for frontend tracking)"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured."
        )
    
    flow = get_google_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    return {"authorization_url": authorization_url, "state": state, "action": "signup"}


@router.get("/callback")
async def oauth_callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """Handle OAuth callback from Google"""
    if error:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error={error}")
    
    if not code:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=no_code")
    
    try:
        flow = get_google_flow()
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Get user info from Google
        from googleapiclient.discovery import build
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        email = user_info['email']
        # Get first name and last name from Google and combine them
        given_name = user_info.get('given_name', '')
        family_name = user_info.get('family_name', '')
        full_name = f"{given_name} {family_name}".strip() or user_info.get('name', '')
        
        user = db.query(User).filter(User.email == email).first()
        is_new_user = user is None
        
        if not user:
            # Create new user with Google data
            # Use email prefix as username if not provided (or generate unique)
            base_username = email.split('@')[0]
            username = base_username
            
            # Ensure username uniqueness
            counter = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1

            user = User(
                email=email,
                username=username,
                name=full_name,  # Store combined first and last name
                gmail_access_token=credentials.token,
                gmail_refresh_token=credentials.refresh_token,
                is_active=True,  # Google-verified users are automatically active
                is_email_verified=True,  # Email verified by Google
                auth_provider="google",
                terms_accepted=False,  # Will be set when user accepts on frontend
                privacy_accepted=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update tokens
            user.gmail_access_token = credentials.token
            if credentials.refresh_token:
                user.gmail_refresh_token = credentials.refresh_token
            # Update name if not set
            if not user.name and full_name:
                user.name = full_name
            # Update username if not set (for existing users)
            if not user.username:
                base_username = email.split('@')[0]
                username = base_username
                counter = 1
                while db.query(User).filter(User.username == username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
                user.username = username
                
            db.commit()

        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email},
            expires_delta=access_token_expires
        )
        
        # Check if user needs to accept terms (for new Google users)
        if is_new_user or (not user.terms_accepted or not user.privacy_accepted):
            return RedirectResponse(
                url=f"{FRONTEND_URL}/auth/callback?token={access_token}&needs_consent=true"
            )
        
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?token={access_token}"
        )
    
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=oauth_failed")


# ----- Email/Password Auth -----
@router.post("/signup", response_model=dict)
async def signup(user: UserSignup, db: Session = Depends(get_db)):
    """Register a new user with email and password"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Validate terms acceptance
    if not user.terms_accepted or not user.privacy_accepted:
        raise HTTPException(
            status_code=400,
            detail="You must accept the Terms of Service and Privacy Policy"
        )
    
    # Decrypt the password from frontend encryption
    plain_password = decrypt_password(user.password)
    
    # Validate password strength and length
    if len(plain_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if len(plain_password) > 64:
        raise HTTPException(status_code=400, detail="Password cannot be longer than 64 characters")
    
    # Create verification token
    verification_token = create_verification_token(user.email)
    
    # Hash the password with bcrypt for secure storage
    hashed_password = get_password_hash(plain_password)
    
    # Create new user with bcrypt-hashed password
    new_user = User(
        email=user.email,
        username=user.username,
        name=user.name,
        password_hash=hashed_password,
        is_active=False,  # Will be activated after email verification
        is_email_verified=False,
        email_verification_token=verification_token,
        email_verification_sent_at=datetime.utcnow(),
        gmail_access_token="",
        gmail_refresh_token="",
        last_email_sync=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send verification email
    verification_link = f"{FRONTEND_URL}/verify-email?token={verification_token}"
    try:
        send_email(
            to_email=user.email,
            subject="Verify your FinGuard account",
            html_content=get_email_verification_template(user.name, verification_link)
        )
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
    
    return {
        "message": "Account created successfully. Please check your email to verify your account.",
        "email": user.email,
        "requires_verification": True
    }


@router.post("/login", response_model=Token)
async def login_with_email(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password"""
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Decrypt the password from frontend encryption
    plain_password = decrypt_password(user_credentials.password)
    
    # Verify against the bcrypt hash stored in database
    if not verify_password(plain_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if email is verified
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address before logging in"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not active. Please contact support."
        )
    
    # Determine token expiry
    token_expires_minutes = 120 if user_credentials.remember_me else 30
    
    access_token_expires = timedelta(minutes=token_expires_minutes)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": token_expires_minutes * 60
    }


# ----- Email Verification -----
@router.post("/verify-email")
async def verify_email(data: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Verify user's email address"""
    email = verify_token(data.token, "email_verification")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification link"
        )
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_email_verified:
        return {"message": "Email already verified"}
    
    # Mark user as verified and active
    user.is_email_verified = True
    user.is_active = True
    user.email_verification_token = None
    db.commit()
    
    return {"message": "Email verified successfully. You can now log in."}


@router.post("/resend-verification")
async def resend_verification(data: ResendVerificationRequest, db: Session = Depends(get_db)):
    """Resend verification email"""
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user:
        # Don't reveal if user exists
        return {"message": "If this email is registered, you will receive a verification email."}
    
    if user.is_email_verified:
        return {"message": "Email already verified"}
    
    # Rate limiting: don't send if last email was less than 1 minute ago
    if user.email_verification_sent_at:
        time_since_last = datetime.utcnow() - user.email_verification_sent_at
        if time_since_last.total_seconds() < 60:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Please wait before requesting another verification email"
            )
    
    # Create new verification token
    verification_token = create_verification_token(data.email)
    user.email_verification_token = verification_token
    user.email_verification_sent_at = datetime.utcnow()
    db.commit()
    
    # Send verification email
    verification_link = f"{FRONTEND_URL}/verify-email?token={verification_token}"
    try:
        send_email(
            to_email=data.email,
            subject="Verify your FinGuard account",
            html_content=get_email_verification_template(user.name, verification_link)
        )
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
    
    return {"message": "If this email is registered, you will receive a verification email."}


# ----- Password Reset -----
@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request password reset email"""
    user = db.query(User).filter(User.email == data.email).first()
    
    # Always return same message to prevent email enumeration
    response_message = "If this email is registered, you will receive a password reset link."
    
    if not user:
        return {"message": response_message}
    
    # Check if user signed up with Google
    if user.auth_provider == "google" and not user.password_hash:
        return {"message": response_message}
    
    # Rate limiting
    if user.password_reset_sent_at:
        time_since_last = datetime.utcnow() - user.password_reset_sent_at
        if time_since_last.total_seconds() < 60:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Please wait before requesting another reset email"
            )
    
    # Create password reset token
    reset_token = create_password_reset_token(data.email)
    user.password_reset_token = reset_token
    user.password_reset_sent_at = datetime.utcnow()
    db.commit()
    
    # Send reset email
    reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token}"
    try:
        send_email(
            to_email=data.email,
            subject="Reset your FinGuard password",
            html_content=get_password_reset_template(user.name, reset_link)
        )
    except Exception as e:
        logger.error(f"Failed to send reset email: {str(e)}")
    
    # Log link for development
    logger.info(f"[DEV] Password reset link for {data.email}: {reset_link}")
    
    return {"message": response_message}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using token from email"""
    email = verify_token(data.token, "password_reset")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset link"
        )
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Decrypt the password from frontend encryption
    plain_password = decrypt_password(data.password)
    
    # Validate password strength and length
    if len(plain_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if len(plain_password) > 64:
        raise HTTPException(status_code=400, detail="Password cannot be longer than 64 characters")
    
    # Update password with bcrypt hash
    user.password_hash = get_password_hash(plain_password)
    user.password_reset_token = None
    user.password_reset_sent_at = None
    
    # If user wasn't active, activate them now
    if not user.is_active:
        user.is_active = True
    if not user.is_email_verified:
        user.is_email_verified = True
    
    db.commit()
    
    return {"message": "Password reset successfully. You can now log in with your new password."}


@router.post("/validate-reset-token")
async def validate_reset_token(data: dict, db: Session = Depends(get_db)):
    """Validate if a reset token is still valid"""
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token required")
    
    email = verify_token(token, "password_reset")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset link"
        )
    
    return {"valid": True, "email": email}


# ----- User Management -----
@router.get("/me", response_model=UserResponse)
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get current authenticated user"""
    user = get_current_user_from_token(request, db)
    return user


@router.post("/logout")
async def logout():
    """Logout user (client should discard token)"""
    return {"message": "Logged out successfully"}


@router.post("/accept-terms")
async def accept_terms(request: Request, db: Session = Depends(get_db)):
    """Accept terms and privacy policy (for Google signup users)"""
    user = get_current_user_from_token(request, db)
    
    user.terms_accepted = True
    user.terms_accepted_at = datetime.utcnow()
    user.privacy_accepted = True
    user.privacy_accepted_at = datetime.utcnow()
    user.is_active = True
    db.commit()
    
    return {"message": "Terms accepted successfully"}


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Change password for logged-in user"""
    user = get_current_user_from_token(request, db)
    
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password for Google-authenticated accounts"
        )
    
    # Decrypt passwords from frontend encryption
    plain_current_password = decrypt_password(data.current_password)
    plain_new_password = decrypt_password(data.new_password)
    
    if not verify_password(plain_current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    if len(plain_new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if len(plain_new_password) > 64:
        raise HTTPException(status_code=400, detail="Password cannot be longer than 64 characters")
    
    # Store with bcrypt hash
    user.password_hash = get_password_hash(plain_new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/check-email")
async def check_email(email: str, db: Session = Depends(get_db)):
    """Check if email is already registered"""
    user = db.query(User).filter(User.email == email).first()
    return {"exists": user is not None}

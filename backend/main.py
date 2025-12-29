"""
Financial Leak Detector - Backend API
Detects forgotten subscriptions, hidden spending habits, and price creep
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Config & Environment
from dotenv import load_dotenv
load_dotenv()

# Import Models & Database
from app.models import Base
from app.database import engine
from app.api.auth import router as auth_router
from app.api.email import router as email_router
from app.api.transactions import router as transaction_router
from app.api.leaks import router as leaks_router

# Create tables
Base.metadata.create_all(bind=engine)

# ==================== FASTAPI APP ====================
app = FastAPI(
    title="Financial Leak Detector API",
    description="Detect forgotten subscriptions, hidden spending habits, and price creep",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ROUTES ====================
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(email_router, prefix="/api/email", tags=["Email"])
app.include_router(transaction_router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(leaks_router, prefix="/api/leaks", tags=["Leaks"])

# ==================== HEALTH CHECK ====================
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Financial Leak Detector",
        "version": "1.0.0"
    }

# ==================== ROOT ====================
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Financial Leak Detector API",
        "description": "Detect forgotten subscriptions, hidden spending habits, and price creep",
        "endpoints": {
            "docs": "/docs",
            "auth": "/api/auth",
            "email": "/api/email",
            "transactions": "/api/transactions",
            "leaks": "/api/leaks"
        }
    }

# ==================== RUN ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )

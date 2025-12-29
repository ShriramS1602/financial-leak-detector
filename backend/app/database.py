import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ==================== DATABASE CONFIG ====================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./finance_tracker.db"  # Default SQLite for dev
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ==================== DEPENDENCY ====================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

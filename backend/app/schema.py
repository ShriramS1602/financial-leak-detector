from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

# Minimal Pydantic schemas expected by the REST API


class UserCreate(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    password: str
    name: Optional[str] = None
    terms_accepted: bool = False
    privacy_accepted: bool = False


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: Optional[str] = None
    name: Optional[str] = None
    is_active: bool = False
    is_email_verified: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None


# Minimal Strawberry GraphQL schema so `main.py` can mount a GraphQL endpoint.
# Keep it tiny to avoid creating heavy dependencies in code paths that only need the schema variable.
try:
    import strawberry

    @strawberry.type
    class Query:
        @strawberry.field
        def hello(self) -> str:
            return "Hello from GraphQL"

    schema = strawberry.Schema(query=Query)
except Exception:
    # If strawberry is not installed in the environment where this import runs,
    # provide a fallback `schema` value to avoid ImportError at import-time.
    schema = None

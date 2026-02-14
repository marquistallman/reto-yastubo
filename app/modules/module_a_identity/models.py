from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class Role(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    roles: List[Role] = []
    mfa_secret: Optional[str] = None  # For TOTP (Time-based One-Time Password)
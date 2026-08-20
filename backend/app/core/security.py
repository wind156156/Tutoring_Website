from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
secret_key = settings.secret_key
algorithm = settings.algorithm


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class UserInfo(BaseModel):
    id: int
    role: str
    phone: str
    nickname: str = ""
    avatar: str = ""
    status: str


class RegisterRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=20)
    password: str = Field(..., min_length=6, max_length=128)
    role: str = Field(..., pattern="^(parent|teacher|student|admin)$")


class LoginRequest(BaseModel):
    phone: str
    password: str


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=128)


class ProfileUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    # Ensure sub is string (jose requirement)
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def decode_access_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return TokenData(
            user_id=int(payload.get("sub", 0)) if payload.get("sub") else None,
            role=payload.get("role"),
        )
    except JWTError:
        return None

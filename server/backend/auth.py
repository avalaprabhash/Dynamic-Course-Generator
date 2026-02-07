"""
Authentication Service

Handles user authentication, JWT token generation/validation, and password hashing.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth_models import User, RegisterRequest, LoginRequest, UserResponse

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-please")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# HTTP Bearer token scheme
security = HTTPBearer()

# Storage path
STORAGE_DIR = Path(__file__).parent / "data"
USERS_FILE = STORAGE_DIR / "users.json"


def ensure_users_file():
    """Ensure users.json file exists"""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)


def load_users() -> list[dict]:
    """Load all users from storage"""
    ensure_users_file()
    with open(USERS_FILE, 'r') as f:
        return json.load(f)


def save_users(users: list[dict]):
    """Save users to storage"""
    ensure_users_file()
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2, default=str)


def get_user_by_email(email: str) -> Optional[dict]:
    """Find user by email"""
    users = load_users()
    for user in users:
        if user['email'].lower() == email.lower():
            return user
    return None


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def create_user(email: str, password: str) -> User:
    """Create a new user with hashed password"""
    users = load_users()
    
    # Check if user already exists
    if get_user_by_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=email,
        password_hash=get_password_hash(password)
    )
    
    users.append(user.model_dump())
    save_users(users)
    
    return user


def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Authenticate user with email and password"""
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user['password_hash']):
        return None
    return user


def create_access_token(data: dict) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get current authenticated user from JWT token.
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user_id": user["id"]}
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from storage
    users = load_users()
    user = next((u for u in users if u['id'] == user_id), None)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

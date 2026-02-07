"""
Authentication Models for User Management

This module defines user authentication models and request/response schemas.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid


class User(BaseModel):
    """
    User model for authentication
    
    Fields:
        id: Unique user identifier
        email: User's email address (unique)
        password_hash: Hashed password (bcrypt)
        created_at: Account creation timestamp
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.now)


class RegisterRequest(BaseModel):
    """Request model for user registration"""
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)


class LoginRequest(BaseModel):
    """Request model for user login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response model for successful authentication"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Response model for user information (without password)"""
    id: str
    email: str
    created_at: datetime

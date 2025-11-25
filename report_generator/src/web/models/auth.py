"""
Authentication Models
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class EmailRequest(BaseModel):
    """Request to send OTP to email"""
    email: EmailStr


class OTPVerifyRequest(BaseModel):
    """Request to verify OTP"""
    email: EmailStr
    otp: str


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserInfo(BaseModel):
    """User information"""
    email: str

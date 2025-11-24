"""
Authentication Models
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class OTPRequest(BaseModel):
    """Request OTP code"""
    email: EmailStr = Field(..., description="User email address")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@company.com"
            }
        }


class OTPVerifyRequest(BaseModel):
    """Verify OTP code"""
    email: EmailStr = Field(..., description="User email address")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@company.com",
                "otp_code": "123456"
            }
        }


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }


class UserInfo(BaseModel):
    """User information from JWT token"""
    email: str = Field(..., description="User email address")
    domain: str = Field(..., description="Email domain")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@company.com",
                "domain": "company.com"
            }
        }


class OTPSession(BaseModel):
    """OTP session stored in memory"""
    email: str = Field(..., description="User email")
    secret: str = Field(..., description="TOTP secret key")
    otp_code: str = Field(..., description="Generated OTP code (for logging/display)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    attempts: int = Field(default=0, description="Number of verification attempts")
    is_verified: bool = Field(default=False, description="Whether OTP is verified")

    def is_expired(self, expiration_seconds: int) -> bool:
        """Check if OTP is expired"""
        elapsed = (datetime.utcnow() - self.created_at).total_seconds()
        return elapsed > expiration_seconds

    def increment_attempts(self) -> int:
        """Increment and return attempt count"""
        self.attempts += 1
        return self.attempts


class OTPResponse(BaseModel):
    """Response after requesting OTP"""
    message: str = Field(..., description="Response message")
    email: str = Field(..., description="Email where OTP was sent")
    expires_in: int = Field(..., description="OTP expiration time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "OTP code sent to your email",
                "email": "user@company.com",
                "expires_in": 300
            }
        }

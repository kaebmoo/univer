"""
Authentication Router
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.auth import (
    OTPRequest,
    OTPVerifyRequest,
    TokenResponse,
    UserInfo,
    OTPResponse
)
from app.services.auth_service import auth_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme
security = HTTPBearer()


# Dependency to get current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInfo:
    """
    Dependency to extract and verify user from JWT token

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        UserInfo with email and domain

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    return auth_service.verify_token(token)


@router.post("/request-otp", response_model=OTPResponse)
async def request_otp(request: OTPRequest):
    """
    Request OTP code

    Send a 6-digit OTP code to the user's email address.
    The OTP will expire after 5 minutes.

    Args:
        request: OTP request with email

    Returns:
        OTPResponse with message and expiration time

    Raises:
        HTTPException 403: If email domain is not allowed
        HTTPException 500: If email sending fails
    """
    logger.info(f"OTP request for email: {request.email}")
    return auth_service.request_otp(request.email)


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(request: OTPVerifyRequest):
    """
    Verify OTP code and get access token

    Verify the OTP code sent to the user's email.
    If valid, returns a JWT access token.

    Args:
        request: OTP verification request with email and OTP code

    Returns:
        TokenResponse with JWT access token

    Raises:
        HTTPException 404: If no OTP session found
        HTTPException 400: If OTP is expired
        HTTPException 429: If max attempts exceeded
        HTTPException 401: If OTP code is invalid
    """
    logger.info(f"OTP verification for email: {request.email}")
    return auth_service.verify_otp(request.email, request.otp_code)


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: UserInfo = Depends(get_current_user)
):
    """
    Get current user information

    Returns information about the currently authenticated user.
    Requires a valid JWT token in the Authorization header.

    Args:
        current_user: Current user from JWT token (injected by dependency)

    Returns:
        UserInfo with email and domain
    """
    logger.info(f"User info requested for: {current_user.email}")
    return current_user


@router.post("/logout")
async def logout(current_user: UserInfo = Depends(get_current_user)):
    """
    Logout current user

    Note: Since we're using stateless JWT tokens, this endpoint
    mainly serves as a signal for the client to delete their token.
    In production, you might want to implement token blacklisting.

    Args:
        current_user: Current user from JWT token (injected by dependency)

    Returns:
        Success message
    """
    logger.info(f"User logged out: {current_user.email}")
    return {
        "message": "Logged out successfully",
        "email": current_user.email
    }


@router.get("/health")
async def auth_health_check():
    """
    Health check for authentication service

    Returns:
        Service status
    """
    return {
        "status": "healthy",
        "service": "Authentication",
        "active_sessions": len(auth_service.otp_sessions)
    }

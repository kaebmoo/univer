"""
Authentication Routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from config.settings import settings
from src.web.models.auth import (
    EmailRequest,
    OTPVerifyRequest,
    TokenResponse,
    UserInfo
)
from src.web.utils.otp import otp_manager
from src.web.utils.email import create_email_sender
from src.web.utils.jwt import initialize_jwt_manager

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Initialize JWT manager
jwt_manager = initialize_jwt_manager(settings)

# Initialize email sender
email_sender = create_email_sender(settings)


@router.post("/request-otp")
async def request_otp(request: EmailRequest):
    """
    Request OTP for email login

    Args:
        request: Email request

    Returns:
        Success message (OTP included in dev mode)
    """
    email = request.email.lower()

    # Check if email domain is allowed
    if not settings.is_email_allowed(email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Email domain not allowed. Allowed domains: {settings.allowed_email_domains}"
        )

    # Generate OTP
    otp = otp_manager.generate_otp(email)

    # Send OTP via email (if configured)
    if email_sender and settings.app_env == "production":
        success = email_sender.send_otp_email(email, otp)
        if not success:
            logger.error(f"Failed to send OTP email to {email}")
            # Don't fail the request, user can still get OTP in dev mode

    # In development mode, return OTP in response
    response = {
        "message": "OTP sent successfully",
        "email": email,
        "expires_in": settings.otp_expiration
    }

    if settings.app_env == "development" or settings.debug:
        response["otp"] = otp  # Include OTP in response for dev mode
        response["dev_mode"] = True

    logger.info(f"OTP requested for {email}")

    return response


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(request: OTPVerifyRequest):
    """
    Verify OTP and get JWT token

    Args:
        request: OTP verification request

    Returns:
        JWT token
    """
    email = request.email.lower()
    otp = request.otp

    # Validate OTP
    is_valid = otp_manager.validate_otp(email, otp)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )

    # Create JWT token
    token, expires_in = jwt_manager.create_token(email)

    logger.info(f"OTP verified successfully for {email}")

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInfo:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP bearer credentials

    Returns:
        User info

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials

    # Verify token
    email = jwt_manager.verify_token(token)

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserInfo(email=email)


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: UserInfo = Depends(get_current_user)):
    """
    Get current user information

    Args:
        current_user: Current authenticated user

    Returns:
        User info
    """
    return current_user

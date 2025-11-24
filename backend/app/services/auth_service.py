"""
Authentication Service
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.config import settings
from app.models.auth import (
    OTPRequest,
    OTPVerifyRequest,
    TokenResponse,
    UserInfo,
    OTPSession,
    OTPResponse
)
from app.utils.otp import generate_secret, generate_totp, verify_totp, get_remaining_time
from app.utils.email import send_otp_email

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for OTP and JWT token management"""

    def __init__(self):
        # In-memory storage for OTP sessions
        # In production, use Redis or similar
        self.otp_sessions: Dict[str, OTPSession] = {}

    def request_otp(self, email: str) -> OTPResponse:
        """
        Generate and send OTP code to user email

        Args:
            email: User email address

        Returns:
            OTPResponse with message and expiration time

        Raises:
            HTTPException: If email domain is not allowed or email sending fails
        """
        # Check if email domain is allowed
        if not settings.is_email_allowed(email):
            logger.warning(f"Unauthorized email domain: {email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Email domain not allowed. Allowed domains: {', '.join(settings.allowed_domains_list)}"
            )

        # Generate TOTP secret and code
        secret = generate_secret()
        otp_code, totp = generate_totp(secret, interval=settings.otp_expiration)

        # Send OTP via email
        logger.info(f"Sending OTP to {email}")
        email_sent = send_otp_email(email, otp_code)

        if not email_sent:
            logger.error(f"Failed to send OTP email to {email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP email. Please try again later."
            )

        # Store OTP session with TOTP secret
        self.otp_sessions[email] = OTPSession(
            email=email,
            secret=secret,
            otp_code=otp_code,
            created_at=datetime.utcnow(),
            attempts=0,
            is_verified=False
        )

        logger.info(f"OTP generated and sent successfully to {email}")

        return OTPResponse(
            message="OTP code sent to your email",
            email=email,
            expires_in=settings.otp_expiration
        )

    def verify_otp(self, email: str, otp_code: str) -> TokenResponse:
        """
        Verify OTP code and generate JWT token

        Args:
            email: User email address
            otp_code: OTP code to verify

        Returns:
            TokenResponse with access token

        Raises:
            HTTPException: If OTP is invalid, expired, or max attempts exceeded
        """
        # Check if OTP session exists
        session = self.otp_sessions.get(email)
        if not session:
            logger.warning(f"No OTP session found for {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No OTP request found. Please request a new OTP."
            )

        # Check if OTP is expired
        if session.is_expired(settings.otp_expiration):
            logger.warning(f"OTP expired for {email}")
            del self.otp_sessions[email]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired. Please request a new one."
            )

        # Check max attempts
        if session.attempts >= settings.otp_max_attempts:
            logger.warning(f"Max OTP attempts exceeded for {email}")
            del self.otp_sessions[email]
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Maximum verification attempts exceeded. Please request a new OTP."
            )

        # Increment attempts
        session.increment_attempts()

        # Verify OTP code using TOTP
        is_valid = verify_totp(
            secret=session.secret,
            otp_code=otp_code,
            interval=settings.otp_expiration,
            valid_window=1  # Accept codes from previous, current, and next interval
        )

        if not is_valid:
            logger.warning(f"Invalid OTP for {email} (attempt {session.attempts}/{settings.otp_max_attempts})")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid OTP code. {settings.otp_max_attempts - session.attempts} attempts remaining."
            )

        # Mark as verified
        session.is_verified = True

        # Generate JWT token
        token = self._create_access_token(email)

        # Clean up OTP session
        del self.otp_sessions[email]

        logger.info(f"OTP verified successfully for {email}")

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.jwt_expiration * 60  # Convert minutes to seconds
        )

    def verify_token(self, token: str) -> UserInfo:
        """
        Verify JWT token and extract user info

        Args:
            token: JWT access token

        Returns:
            UserInfo with email and domain

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Decode token
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm]
            )

            # Extract email
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing email"
                )

            # Extract domain
            domain = email.split("@")[-1]

            return UserInfo(email=email, domain=domain)

        except JWTError as e:
            logger.warning(f"JWT verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

    def _create_access_token(self, email: str) -> str:
        """
        Create JWT access token

        Args:
            email: User email address

        Returns:
            JWT access token string
        """
        # Token expiration
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration)

        # Create payload
        payload = {
            "sub": email,
            "domain": email.split("@")[-1],
            "exp": expire,
            "iat": datetime.utcnow()
        }

        # Encode token
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )

        return token

    def cleanup_expired_sessions(self):
        """Clean up expired OTP sessions"""
        current_time = datetime.utcnow()
        expired_emails = [
            email for email, session in self.otp_sessions.items()
            if session.is_expired(settings.otp_expiration)
        ]

        for email in expired_emails:
            del self.otp_sessions[email]
            logger.info(f"Cleaned up expired OTP session for {email}")


# Create global auth service instance
auth_service = AuthService()

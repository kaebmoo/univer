"""
OTP (One-Time Password) Generator and Validator
"""
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class OTPManager:
    """Manage OTP generation and validation"""

    def __init__(
        self,
        length: int = 6,
        expiration: int = 300,  # seconds
        max_attempts: int = 3
    ):
        """
        Initialize OTP Manager

        Args:
            length: Length of OTP
            expiration: Expiration time in seconds
            max_attempts: Maximum validation attempts
        """
        self.length = length
        self.expiration = expiration
        self.max_attempts = max_attempts

        # In-memory storage (in production, use Redis or database)
        self.otp_storage: Dict[str, Dict] = {}

    def generate_otp(self, email: str) -> str:
        """
        Generate OTP for email

        Args:
            email: Email address

        Returns:
            Generated OTP
        """
        # Generate random numeric OTP
        otp = ''.join(random.choices(string.digits, k=self.length))

        # Store OTP with metadata
        self.otp_storage[email] = {
            'otp': otp,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(seconds=self.expiration),
            'attempts': 0,
            'used': False
        }

        logger.info(f"Generated OTP for {email}: {otp} (expires in {self.expiration}s)")

        return otp

    def validate_otp(self, email: str, otp: str) -> bool:
        """
        Validate OTP for email

        Args:
            email: Email address
            otp: OTP to validate

        Returns:
            True if OTP is valid, False otherwise
        """
        # Check if OTP exists
        if email not in self.otp_storage:
            logger.warning(f"No OTP found for {email}")
            return False

        otp_data = self.otp_storage[email]

        # Check if already used
        if otp_data['used']:
            logger.warning(f"OTP for {email} already used")
            return False

        # Check expiration
        if datetime.now() > otp_data['expires_at']:
            logger.warning(f"OTP for {email} expired")
            del self.otp_storage[email]
            return False

        # Check max attempts
        if otp_data['attempts'] >= self.max_attempts:
            logger.warning(f"Max attempts exceeded for {email}")
            del self.otp_storage[email]
            return False

        # Increment attempts
        otp_data['attempts'] += 1

        # Validate OTP
        if otp_data['otp'] == otp:
            # Mark as used
            otp_data['used'] = True
            logger.info(f"OTP validated successfully for {email}")
            return True
        else:
            logger.warning(f"Invalid OTP for {email} (attempt {otp_data['attempts']})")
            return False

    def get_otp_for_dev(self, email: str) -> Optional[str]:
        """
        Get OTP for development mode (to display on screen)

        Args:
            email: Email address

        Returns:
            OTP string or None
        """
        if email in self.otp_storage:
            return self.otp_storage[email]['otp']
        return None

    def cleanup_expired(self):
        """Clean up expired OTPs"""
        now = datetime.now()
        expired = [
            email for email, data in self.otp_storage.items()
            if now > data['expires_at']
        ]

        for email in expired:
            del self.otp_storage[email]

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired OTPs")


# Global OTP manager instance
otp_manager = OTPManager()

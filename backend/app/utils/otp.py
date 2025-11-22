"""
OTP (One-Time Password) Generator using PyOTP
Uses TOTP (Time-based One-Time Password) for secure OTP generation and verification
"""

import pyotp
import secrets
import base64
from typing import Tuple


def generate_secret() -> str:
    """
    Generate a random secret key for TOTP

    Returns:
        Base32-encoded secret key

    Example:
        >>> secret = generate_secret()
        >>> print(secret)
        'JBSWY3DPEHPK3PXP'
    """
    # Generate 20 random bytes and encode as base32
    random_bytes = secrets.token_bytes(20)
    secret = base64.b32encode(random_bytes).decode('utf-8')
    return secret


def generate_totp(secret: str, interval: int = 300) -> Tuple[str, pyotp.TOTP]:
    """
    Generate a TOTP code using the secret key

    Args:
        secret: Base32-encoded secret key
        interval: Time interval in seconds (default: 300 = 5 minutes)

    Returns:
        Tuple of (OTP code, TOTP instance)

    Example:
        >>> secret = generate_secret()
        >>> otp_code, totp = generate_totp(secret)
        >>> print(otp_code)
        '123456'
    """
    # Create TOTP instance with 6-digit code and 5-minute interval
    totp = pyotp.TOTP(secret, digits=6, interval=interval)

    # Generate current OTP code
    otp_code = totp.now()

    return otp_code, totp


def verify_totp(secret: str, otp_code: str, interval: int = 300, valid_window: int = 1) -> bool:
    """
    Verify a TOTP code

    Args:
        secret: Base32-encoded secret key
        otp_code: OTP code to verify
        interval: Time interval in seconds (default: 300 = 5 minutes)
        valid_window: Number of intervals to check before/after current time (default: 1)

    Returns:
        True if OTP is valid, False otherwise

    Example:
        >>> secret = generate_secret()
        >>> otp_code, _ = generate_totp(secret)
        >>> verify_totp(secret, otp_code)
        True
        >>> verify_totp(secret, '000000')
        False
    """
    # Create TOTP instance
    totp = pyotp.TOTP(secret, digits=6, interval=interval)

    # Verify OTP with time window
    # valid_window=1 means it will accept OTP from:
    # - 1 interval before (5 min ago)
    # - current interval
    # - 1 interval after (5 min future)
    return totp.verify(otp_code, valid_window=valid_window)


def get_remaining_time(secret: str, interval: int = 300) -> int:
    """
    Get remaining time in seconds until current OTP expires

    Args:
        secret: Base32-encoded secret key
        interval: Time interval in seconds (default: 300 = 5 minutes)

    Returns:
        Remaining time in seconds

    Example:
        >>> secret = generate_secret()
        >>> remaining = get_remaining_time(secret)
        >>> print(f"OTP expires in {remaining} seconds")
    """
    totp = pyotp.TOTP(secret, digits=6, interval=interval)

    # Calculate remaining time
    import time
    current_time = int(time.time())
    time_in_interval = current_time % interval
    remaining = interval - time_in_interval

    return remaining


# Backward compatibility: simple OTP generation for testing
def generate_otp(length: int = 6) -> str:
    """
    Generate a simple numeric OTP (for backward compatibility)

    Note: This is kept for backward compatibility with tests.
    For production, use generate_totp() instead.

    Args:
        length: Length of OTP code (default: 6)

    Returns:
        String of random digits
    """
    import string
    digits = string.digits
    otp = ''.join(secrets.choice(digits) for _ in range(length))
    return otp

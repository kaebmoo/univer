"""
OTP (One-Time Password) Generator
"""

import random
import string
import hashlib
import secrets


def generate_otp(length: int = 6) -> str:
    """
    Generate a random numeric OTP code

    Args:
        length: Length of OTP code (default: 6)

    Returns:
        String of random digits

    Example:
        >>> otp = generate_otp(6)
        >>> print(otp)
        '123456'
    """
    # Use secrets for cryptographically strong random numbers
    digits = string.digits
    otp = ''.join(secrets.choice(digits) for _ in range(length))
    return otp


def generate_alphanumeric_otp(length: int = 6) -> str:
    """
    Generate a random alphanumeric OTP code

    Args:
        length: Length of OTP code (default: 6)

    Returns:
        String of random uppercase letters and digits

    Example:
        >>> otp = generate_alphanumeric_otp(6)
        >>> print(otp)
        'A1B2C3'
    """
    characters = string.ascii_uppercase + string.digits
    otp = ''.join(secrets.choice(characters) for _ in range(length))
    return otp


def hash_otp(otp: str) -> str:
    """
    Hash OTP code for secure storage

    Args:
        otp: OTP code to hash

    Returns:
        SHA-256 hash of OTP

    Example:
        >>> hashed = hash_otp('123456')
        >>> print(hashed)
        '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'
    """
    return hashlib.sha256(otp.encode()).hexdigest()


def verify_otp(input_otp: str, stored_otp: str, use_hash: bool = False) -> bool:
    """
    Verify OTP code

    Args:
        input_otp: OTP code entered by user
        stored_otp: OTP code stored in system (plain or hashed)
        use_hash: Whether stored_otp is hashed

    Returns:
        True if OTP matches, False otherwise

    Example:
        >>> verify_otp('123456', '123456')
        True
        >>> verify_otp('123456', hash_otp('123456'), use_hash=True)
        True
    """
    if use_hash:
        return hash_otp(input_otp) == stored_otp
    return input_otp == stored_otp

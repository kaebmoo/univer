"""
JWT Token Management
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import logging

logger = logging.getLogger(__name__)


class JWTManager:
    """Manage JWT token creation and validation"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        expiration_minutes: int = 1440  # 24 hours
    ):
        """
        Initialize JWT Manager

        Args:
            secret_key: Secret key for JWT
            algorithm: JWT algorithm
            expiration_minutes: Token expiration in minutes
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_minutes = expiration_minutes

    def create_token(self, email: str) -> tuple[str, int]:
        """
        Create JWT token for user

        Args:
            email: User email

        Returns:
            Tuple of (token, expires_in_seconds)
        """
        expires_delta = timedelta(minutes=self.expiration_minutes)
        expire = datetime.utcnow() + expires_delta

        to_encode = {
            "sub": email,
            "exp": expire,
            "iat": datetime.utcnow()
        }

        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )

        expires_in = int(expires_delta.total_seconds())

        logger.info(f"Created JWT token for {email}, expires in {expires_in}s")

        return encoded_jwt, expires_in

    def verify_token(self, token: str) -> Optional[str]:
        """
        Verify JWT token and extract email

        Args:
            token: JWT token

        Returns:
            Email if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            email: str = payload.get("sub")

            if email is None:
                return None

            return email

        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None


# Global JWT manager (will be initialized with settings)
jwt_manager = None


def initialize_jwt_manager(settings):
    """Initialize global JWT manager"""
    global jwt_manager
    jwt_manager = JWTManager(
        secret_key=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
        expiration_minutes=settings.jwt_expiration
    )
    return jwt_manager

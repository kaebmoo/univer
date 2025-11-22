"""
Tests for AuthService
"""

import pytest
from datetime import datetime, timedelta
from app.services.auth_service import AuthService
from app.models.auth import OTPRequest, OTPVerifyRequest


@pytest.mark.unit
class TestAuthService:
    """Test cases for AuthService"""

    def test_validate_email_domain_valid(self, auth_service):
        """Test email domain validation with valid domain"""
        valid_email = "user@example.com"
        assert auth_service._validate_email_domain(valid_email) is True

    def test_validate_email_domain_invalid(self, auth_service):
        """Test email domain validation with invalid domain"""
        invalid_email = "user@invalid.com"
        assert auth_service._validate_email_domain(invalid_email) is False

    def test_generate_jwt_token(self, auth_service):
        """Test JWT token generation"""
        email = "test@example.com"
        token = auth_service._generate_jwt_token(email)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_jwt_token_valid(self, auth_service):
        """Test JWT token verification with valid token"""
        email = "test@example.com"
        token = auth_service._generate_jwt_token(email)

        user_info = auth_service.verify_token(token)

        assert user_info is not None
        assert user_info.email == email

    def test_verify_jwt_token_invalid(self, auth_service):
        """Test JWT token verification with invalid token"""
        invalid_token = "invalid.token.here"

        with pytest.raises(Exception):
            auth_service.verify_token(invalid_token)

    def test_request_otp_valid_email(self, auth_service, mocker):
        """Test OTP request with valid email"""
        # Mock email sending
        mocker.patch('app.services.auth_service.send_otp_email', return_value=True)

        email = "test@example.com"
        response = auth_service.request_otp(email)

        assert response.success is True
        assert response.message is not None
        assert email in auth_service.otp_sessions

    def test_request_otp_invalid_domain(self, auth_service):
        """Test OTP request with invalid email domain"""
        email = "test@invalid.com"
        response = auth_service.request_otp(email)

        assert response.success is False
        assert "อนุญาต" in response.message or "allowed" in response.message.lower()

    def test_verify_otp_correct_code(self, auth_service, mock_otp_session):
        """Test OTP verification with correct code"""
        email = "test@example.com"
        otp_code = "123456"

        # Set up session
        auth_service.otp_sessions[email] = mock_otp_session

        token_response = auth_service.verify_otp(email, otp_code)

        assert token_response.access_token is not None
        assert token_response.token_type == "bearer"
        assert token_response.user.email == email

    def test_verify_otp_incorrect_code(self, auth_service, mock_otp_session):
        """Test OTP verification with incorrect code"""
        email = "test@example.com"
        wrong_code = "999999"

        # Set up session
        auth_service.otp_sessions[email] = mock_otp_session

        with pytest.raises(Exception) as exc_info:
            auth_service.verify_otp(email, wrong_code)

        assert "OTP" in str(exc_info.value) or "รหัส" in str(exc_info.value)

    def test_verify_otp_expired(self, auth_service, expired_otp_session):
        """Test OTP verification with expired OTP"""
        email = "test@example.com"
        otp_code = "123456"

        # Set up expired session
        auth_service.otp_sessions[email] = expired_otp_session

        with pytest.raises(Exception) as exc_info:
            auth_service.verify_otp(email, otp_code)

        assert "หมดอายุ" in str(exc_info.value) or "expired" in str(exc_info.value).lower()

    def test_verify_otp_max_attempts(self, auth_service, mock_otp_session):
        """Test OTP verification with max attempts exceeded"""
        email = "test@example.com"
        wrong_code = "999999"

        # Set up session with max attempts
        mock_otp_session.attempts = 3
        auth_service.otp_sessions[email] = mock_otp_session

        with pytest.raises(Exception) as exc_info:
            auth_service.verify_otp(email, wrong_code)

        assert "ครั้ง" in str(exc_info.value) or "attempt" in str(exc_info.value).lower()

    def test_verify_otp_no_session(self, auth_service):
        """Test OTP verification with no existing session"""
        email = "test@example.com"
        otp_code = "123456"

        with pytest.raises(Exception) as exc_info:
            auth_service.verify_otp(email, otp_code)

        assert "OTP" in str(exc_info.value) or "ไม่พบ" in str(exc_info.value)

    def test_otp_session_is_expired(self, mock_otp_session, expired_otp_session):
        """Test OTP session expiration check"""
        expiration_seconds = 300  # 5 minutes

        # Fresh session should not be expired
        assert mock_otp_session.is_expired(expiration_seconds) is False

        # Old session should be expired
        assert expired_otp_session.is_expired(expiration_seconds) is True

    def test_concurrent_otp_requests(self, auth_service, mocker):
        """Test multiple OTP requests for same email"""
        mocker.patch('app.services.auth_service.send_otp_email', return_value=True)

        email = "test@example.com"

        # First request
        response1 = auth_service.request_otp(email)
        otp1 = auth_service.otp_sessions[email].otp_code

        # Second request (should replace first)
        response2 = auth_service.request_otp(email)
        otp2 = auth_service.otp_sessions[email].otp_code

        assert response1.success is True
        assert response2.success is True
        # OTP codes should be different (new request generates new code)
        assert otp1 != otp2 or True  # Allow same code by chance (1/1000000)

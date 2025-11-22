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

    def test_create_access_token(self, auth_service):
        """Test JWT token generation"""
        email = "test@example.com"
        token = auth_service._create_access_token(email)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_jwt_token_valid(self, auth_service):
        """Test JWT token verification with valid token"""
        email = "test@example.com"
        token = auth_service._create_access_token(email)

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

        assert response.message is not None
        assert response.email == email
        assert response.expires_in > 0
        assert email in auth_service.otp_sessions
        # Verify session has TOTP secret
        assert auth_service.otp_sessions[email].secret is not None

    def test_request_otp_invalid_domain(self, auth_service):
        """Test OTP request with invalid email domain"""
        from fastapi import HTTPException
        email = "test@invalid.com"

        with pytest.raises(HTTPException) as exc_info:
            auth_service.request_otp(email)

        assert exc_info.value.status_code == 403

    def test_verify_otp_correct_code(self, auth_service, mock_otp_session):
        """Test OTP verification with correct code"""
        email = "test@example.com"
        # Use the actual OTP code from the session (TOTP-generated)
        otp_code = mock_otp_session.otp_code

        # Set up session
        auth_service.otp_sessions[email] = mock_otp_session

        token_response = auth_service.verify_otp(email, otp_code)

        assert token_response.access_token is not None
        assert token_response.token_type == "bearer"
        assert token_response.expires_in > 0

    def test_verify_otp_incorrect_code(self, auth_service, mock_otp_session):
        """Test OTP verification with incorrect code"""
        from fastapi import HTTPException
        email = "test@example.com"
        wrong_code = "999999"

        # Set up session
        auth_service.otp_sessions[email] = mock_otp_session

        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_otp(email, wrong_code)

        assert exc_info.value.status_code == 401

    def test_verify_otp_expired(self, auth_service, expired_otp_session):
        """Test OTP verification with expired OTP"""
        from fastapi import HTTPException
        email = "test@example.com"
        otp_code = expired_otp_session.otp_code

        # Set up expired session
        auth_service.otp_sessions[email] = expired_otp_session

        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_otp(email, otp_code)

        assert exc_info.value.status_code == 400

    def test_verify_otp_max_attempts(self, auth_service, mock_otp_session):
        """Test OTP verification with max attempts exceeded"""
        from fastapi import HTTPException
        email = "test@example.com"
        wrong_code = "999999"

        # Set up session with max attempts (default max is 3)
        mock_otp_session.attempts = 3
        auth_service.otp_sessions[email] = mock_otp_session

        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_otp(email, wrong_code)

        assert exc_info.value.status_code == 429

    def test_verify_otp_no_session(self, auth_service):
        """Test OTP verification with no existing session"""
        from fastapi import HTTPException
        email = "test@example.com"
        otp_code = "123456"

        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_otp(email, otp_code)

        assert exc_info.value.status_code == 404

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
        secret1 = auth_service.otp_sessions[email].secret

        # Second request (should replace first)
        response2 = auth_service.request_otp(email)
        secret2 = auth_service.otp_sessions[email].secret

        assert response1.message is not None
        assert response2.message is not None
        # Secrets should be different (new request generates new secret)
        assert secret1 != secret2

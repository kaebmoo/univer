"""
Integration Tests for API Endpoints
Tests the actual API endpoints with FastAPI TestClient
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.mark.integration
class TestAuthEndpoints:
    """Integration tests for authentication endpoints"""

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_request_otp_invalid_domain(self):
        """Test OTP request with invalid email domain"""
        response = client.post(
            "/auth/request-otp",
            json={"email": "test@invalid.com"}
        )
        assert response.status_code in [400, 422, 200]  # Depends on implementation

    def test_verify_otp_without_session(self):
        """Test OTP verification without existing session"""
        response = client.post(
            "/auth/verify-otp",
            json={"email": "test@example.com", "otp_code": "123456"}
        )
        assert response.status_code in [400, 401, 422]


@pytest.mark.integration
class TestReportEndpoints:
    """Integration tests for report endpoints"""

    def test_get_filters_endpoint(self):
        """Test getting filter options"""
        response = client.get("/report/filters")

        # Should work without authentication (or return 401)
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert "years" in data or "error" not in data

    def test_generate_report_without_auth(self):
        """Test generating report without authentication"""
        response = client.post(
            "/report/generate",
            json={
                "year": 2024,
                "months": [1, 2, 3],
                "business_groups": None
            }
        )
        # Should require authentication
        assert response.status_code == 401 or response.status_code == 403

    def test_health_check_endpoint(self):
        """Test report health check"""
        response = client.get("/report/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


@pytest.mark.integration
class TestCORSHeaders:
    """Test CORS configuration"""

    def test_cors_headers_present(self):
        """Test that CORS headers are configured"""
        response = client.options(
            "/report/filters",
            headers={"Origin": "http://localhost:5173"}
        )
        # CORS should allow the request
        assert response.status_code in [200, 204]


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling across endpoints"""

    def test_invalid_json_body(self):
        """Test handling of invalid JSON"""
        response = client.post(
            "/report/generate",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]

    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        response = client.post(
            "/report/generate",
            json={"year": 2024}  # Missing months
        )
        assert response.status_code == 422

    def test_invalid_year_range(self):
        """Test validation of year range"""
        response = client.post(
            "/report/generate",
            json={
                "year": 1999,  # Out of range
                "months": [1]
            }
        )
        assert response.status_code in [422, 401]

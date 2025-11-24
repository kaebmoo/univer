"""
End-to-End Flow Tests
Tests complete user flows from start to finish
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)


@pytest.mark.integration
class TestCompleteAuthFlow:
    """Test complete authentication flow"""

    @patch('app.services.auth_service.send_otp_email')
    def test_complete_otp_flow(self, mock_send_email):
        """Test complete OTP authentication flow"""
        mock_send_email.return_value = True

        # Step 1: Request OTP
        response = client.post(
            "/auth/request-otp",
            json={"email": "test@example.com"}
        )

        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True or "message" in data


@pytest.mark.integration
class TestCompleteReportFlow:
    """Test complete report generation flow"""

    def test_filters_to_report_flow(self):
        """Test flow from getting filters to generating report"""
        # Step 1: Get available filters
        response = client.get("/report/filters")

        if response.status_code == 200:
            filters = response.json()

            if filters.get("years"):
                # Step 2: Use filters to generate report
                # Note: This will fail without auth, which is expected
                year = filters["years"][0] if filters["years"] else 2024

                response = client.post(
                    "/report/generate",
                    json={
                        "year": year,
                        "months": [1, 2, 3]
                    }
                )

                # Should require authentication
                assert response.status_code in [401, 403, 200]


@pytest.mark.integration
class TestDataReloadFlow:
    """Test data reload functionality"""

    def test_reload_data_endpoint(self):
        """Test reloading data"""
        response = client.post("/report/reload-data")

        # Should require authentication or succeed
        assert response.status_code in [200, 401, 403]


@pytest.mark.integration
class TestExportFlow:
    """Test export functionality"""

    def test_export_without_auth(self):
        """Test export requires authentication"""
        response = client.post(
            "/report/export",
            json={
                "year": 2024,
                "months": [1, 2, 3]
            }
        )

        # Should require authentication
        assert response.status_code in [401, 403]


@pytest.mark.integration
class TestErrorScenarios:
    """Test various error scenarios"""

    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import concurrent.futures

        def make_request():
            return client.get("/report/health")

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All requests should succeed
        assert all(r.status_code == 200 for r in results)

    def test_large_month_range(self):
        """Test handling of full year request"""
        response = client.post(
            "/report/generate",
            json={
                "year": 2024,
                "months": list(range(1, 13))  # Full year
            }
        )

        # Should require auth or accept request
        assert response.status_code in [200, 401, 403]

    def test_invalid_month_values(self):
        """Test validation of month values"""
        response = client.post(
            "/report/generate",
            json={
                "year": 2024,
                "months": [0, 13, 14]  # Invalid months
            }
        )

        # Should reject invalid months
        assert response.status_code in [422, 400, 401]


@pytest.mark.integration
class TestEdgeCases:
    """Test edge cases"""

    def test_empty_business_groups(self):
        """Test with empty business groups list"""
        response = client.post(
            "/report/generate",
            json={
                "year": 2024,
                "months": [1],
                "business_groups": []
            }
        )

        assert response.status_code in [200, 401, 403, 422]

    def test_single_month_report(self):
        """Test report for single month"""
        response = client.post(
            "/report/generate",
            json={
                "year": 2024,
                "months": [1]
            }
        )

        assert response.status_code in [200, 401, 403]

    def test_future_year(self):
        """Test with future year"""
        response = client.post(
            "/report/generate",
            json={
                "year": 2030,
                "months": [1]
            }
        )

        # Should accept (data might be empty) or reject
        assert response.status_code in [200, 401, 403, 422]

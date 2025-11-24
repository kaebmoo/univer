"""
Tests for ReportCalculator
"""

import pytest
from app.services.report_calculator import ReportCalculator


@pytest.mark.unit
class TestReportCalculator:
    """Test cases for ReportCalculator"""

    def test_calculate_revenue(self, report_calculator):
        """Test revenue calculation"""
        # Use actual data from CSV
        revenue = report_calculator.calculate_revenue(
            year=2024,
            months=[1, 2, 3],
            business_groups=None
        )

        assert revenue is not None
        assert isinstance(revenue, dict)
        assert 'Total' in revenue

        # Total should be sum of all items
        if len(revenue) > 1:
            calculated_total = sum(v for k, v in revenue.items() if k != 'Total')
            assert abs(revenue['Total'] - calculated_total) < 0.01  # Allow small floating point difference

    def test_calculate_cost_by_type(self, report_calculator):
        """Test cost calculation by type"""
        cost_of_service = report_calculator.calculate_cost_by_type(
            year=2024,
            months=[1, 2, 3],
            cost_type='ต้นทุนบริการและต้นทุนขาย',
            business_groups=None
        )

        assert cost_of_service is not None
        assert isinstance(cost_of_service, dict)
        assert 'Total' in cost_of_service

    def test_calculate_ytd(self, report_calculator):
        """Test YTD (Year-to-Date) calculation"""
        # Calculate YTD for month 3 (should include Jan, Feb, Mar)
        ytd_revenue = report_calculator.calculate_ytd(
            year=2024,
            month=3,
            metric_name='revenue',
            business_groups=None
        )

        assert ytd_revenue >= 0

        # YTD for month 1 should equal month 1 value
        ytd_m1 = report_calculator.calculate_ytd(
            year=2024,
            month=1,
            metric_name='revenue',
            business_groups=None
        )

        assert ytd_m1 >= 0

    def test_calculate_profit_metrics(self, report_calculator):
        """Test profit metrics calculation"""
        metrics = report_calculator.calculate_profit_metrics(
            revenue=10000000,
            cost_of_service=6000000,
            selling_expenses=1000000,
            admin_expenses=1500000,
            depreciation=800000,
            amortization=200000
        )

        assert metrics is not None
        assert 'gross_profit' in metrics
        assert 'ebit' in metrics
        assert 'ebitda' in metrics
        assert 'gross_margin' in metrics
        assert 'ebit_margin' in metrics
        assert 'ebitda_margin' in metrics

        # Check calculations
        assert metrics['gross_profit'] == 4000000  # 10M - 6M
        assert metrics['ebit'] == 1500000  # 10M - 6M - 1M - 1.5M
        assert metrics['ebitda'] == 2500000  # EBIT + depreciation + amortization

        # Check margins
        assert abs(metrics['gross_margin'] - 40.0) < 0.01
        assert abs(metrics['ebit_margin'] - 15.0) < 0.01
        assert abs(metrics['ebitda_margin'] - 25.0) < 0.01

    def test_calculate_profit_metrics_with_zero_revenue(self, report_calculator):
        """Test profit metrics calculation with zero revenue"""
        metrics = report_calculator.calculate_profit_metrics(
            revenue=0,
            cost_of_service=1000000,
            selling_expenses=500000,
            admin_expenses=300000,
            depreciation=100000,
            amortization=50000
        )

        assert metrics is not None
        # Margins should be 0 when revenue is 0
        assert metrics['gross_margin'] == 0
        assert metrics['ebit_margin'] == 0
        assert metrics['ebitda_margin'] == 0

    def test_calculate_profit_metrics_negative_values(self, report_calculator):
        """Test profit metrics calculation with negative results"""
        metrics = report_calculator.calculate_profit_metrics(
            revenue=1000000,
            cost_of_service=2000000,  # Cost > Revenue
            selling_expenses=500000,
            admin_expenses=300000,
            depreciation=100000,
            amortization=50000
        )

        assert metrics is not None
        assert metrics['gross_profit'] < 0
        assert metrics['ebit'] < 0
        # EBITDA might still be negative even with depreciation added back

    def test_generate_full_report(self, report_calculator):
        """Test full report generation"""
        report = report_calculator.generate_full_report(
            year=2024,
            months=[1, 2, 3],
            business_groups=None
        )

        assert report is not None
        assert 'data' in report
        assert 'revenue' in report['data']
        assert 'cost_of_service' in report['data']
        assert 'metrics' in report['data']

        # Check revenue
        assert 'Total' in report['data']['revenue']

        # Check cost of service
        assert 'Total' in report['data']['cost_of_service']

        # Check metrics
        metrics = report['data']['metrics']
        assert 'gross_profit' in metrics
        assert 'ebit' in metrics
        assert 'ebitda' in metrics

    def test_generate_full_report_with_business_group_filter(self, report_calculator):
        """Test full report generation with business group filter"""
        report = report_calculator.generate_full_report(
            year=2024,
            months=[1, 2, 3],
            business_groups=['Hard Infrastructure']
        )

        assert report is not None
        assert 'data' in report

    def test_generate_full_report_single_month(self, report_calculator):
        """Test full report generation for single month"""
        report = report_calculator.generate_full_report(
            year=2024,
            months=[1],
            business_groups=None
        )

        assert report is not None
        assert 'data' in report

    def test_generate_full_report_full_year(self, report_calculator):
        """Test full report generation for full year"""
        report = report_calculator.generate_full_report(
            year=2024,
            months=list(range(1, 13)),
            business_groups=None
        )

        assert report is not None
        assert 'data' in report

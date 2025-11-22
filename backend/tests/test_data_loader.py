"""
Tests for DataLoader
"""

import pytest
import pandas as pd
from app.services.data_loader import DataLoader


@pytest.mark.unit
class TestDataLoader:
    """Test cases for DataLoader"""

    def test_load_profit_loss_data(self, data_loader):
        """Test loading profit and loss data"""
        df = data_loader.load_profit_loss_data()

        assert df is not None
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

        # Check required columns
        required_columns = ['วันที่', 'ปี', 'เดือน', 'กลุ่มธุรกิจ', 'บริการ', 'หมวดบัญชี', 'จำนวนเงิน']
        for col in required_columns:
            assert col in df.columns

    def test_load_profit_loss_data_caching(self, data_loader):
        """Test that data is cached after first load"""
        # First load
        df1 = data_loader.load_profit_loss_data()

        # Second load (should use cache)
        df2 = data_loader.load_profit_loss_data()

        # Should be same object (cached)
        assert df1 is df2

    def test_load_profit_loss_data_force_reload(self, data_loader):
        """Test forcing reload of data"""
        # First load
        df1 = data_loader.load_profit_loss_data()

        # Force reload
        df2 = data_loader.load_profit_loss_data(force_reload=True)

        # Should not be same object
        assert df1 is not df2

    def test_filter_data_by_year(self, data_loader):
        """Test filtering data by year"""
        df = data_loader.load_profit_loss_data()

        # Get unique years
        years = df['ปี'].unique()
        if len(years) > 0:
            test_year = int(years[0])

            filtered_df = data_loader.filter_data(
                year=test_year,
                months=list(range(1, 13)),
                business_groups=None
            )

            assert len(filtered_df) > 0
            assert all(filtered_df['ปี'] == test_year)

    def test_filter_data_by_months(self, data_loader):
        """Test filtering data by specific months"""
        df = data_loader.load_profit_loss_data()

        years = df['ปี'].unique()
        if len(years) > 0:
            test_year = int(years[0])
            test_months = [1, 2, 3]  # Q1

            filtered_df = data_loader.filter_data(
                year=test_year,
                months=test_months,
                business_groups=None
            )

            assert len(filtered_df) >= 0
            if len(filtered_df) > 0:
                assert all(filtered_df['เดือน'].isin(test_months))

    def test_filter_data_by_business_groups(self, data_loader):
        """Test filtering data by business groups"""
        df = data_loader.load_profit_loss_data()

        years = df['ปี'].unique()
        groups = df['กลุ่มธุรกิจ'].unique()

        if len(years) > 0 and len(groups) > 0:
            test_year = int(years[0])
            test_groups = [groups[0]]

            filtered_df = data_loader.filter_data(
                year=test_year,
                months=list(range(1, 13)),
                business_groups=test_groups
            )

            assert len(filtered_df) >= 0
            if len(filtered_df) > 0:
                assert all(filtered_df['กลุ่มธุรกิจ'].isin(test_groups))

    def test_get_available_filters(self, data_loader):
        """Test getting available filter options"""
        filter_options = data_loader.get_available_filters()

        assert filter_options is not None
        assert len(filter_options.years) > 0
        assert len(filter_options.business_groups) > 0
        assert len(filter_options.services) > 0

        # Check that years are integers
        assert all(isinstance(year, int) for year in filter_options.years)

        # Check that years are sorted
        assert filter_options.years == sorted(filter_options.years)

    def test_data_validation_numeric_columns(self, data_loader):
        """Test that numeric columns are properly converted"""
        df = data_loader.load_profit_loss_data()

        # Check that จำนวนเงิน is numeric
        assert pd.api.types.is_numeric_dtype(df['จำนวนเงิน'])

    def test_data_validation_date_columns(self, data_loader):
        """Test that date columns are properly converted"""
        df = data_loader.load_profit_loss_data()

        # Check that วันที่ is datetime
        assert pd.api.types.is_datetime64_any_dtype(df['วันที่'])

    def test_empty_filter_result(self, data_loader):
        """Test filtering with criteria that returns no results"""
        filtered_df = data_loader.filter_data(
            year=9999,  # Year that doesn't exist
            months=[1],
            business_groups=None
        )

        assert len(filtered_df) == 0

    def test_load_other_income_expense_data(self, data_loader):
        """Test loading other income/expense data"""
        df = data_loader.load_other_income_expense_data()

        assert df is not None
        assert isinstance(df, pd.DataFrame)

        if len(df) > 0:
            # Should have some expected columns
            assert 'วันที่' in df.columns or 'หมวดบัญชี' in df.columns

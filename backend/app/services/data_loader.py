"""
Data Loader Service
Load and cache CSV data files
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from functools import lru_cache

from app.config import settings
from app.models.report import FilterOptions

logger = logging.getLogger(__name__)


class DataLoader:
    """Service for loading and caching CSV data"""

    def __init__(self):
        self._profit_loss_df: Optional[pd.DataFrame] = None
        self._other_income_expense_df: Optional[pd.DataFrame] = None
        self._last_load_time: Optional[datetime] = None

    def load_profit_loss_data(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Load profit & loss data from CSV

        Args:
            force_reload: Force reload data even if cached

        Returns:
            DataFrame with profit & loss data

        Raises:
            FileNotFoundError: If CSV file not found
            pd.errors.EmptyDataError: If CSV file is empty
        """
        if self._profit_loss_df is None or force_reload:
            logger.info(f"Loading profit & loss data from {settings.profit_loss_path}")

            # Check if file exists
            if not settings.profit_loss_path.exists():
                raise FileNotFoundError(
                    f"Profit & loss CSV file not found: {settings.profit_loss_path}"
                )

            # Load CSV
            self._profit_loss_df = pd.read_csv(
                settings.profit_loss_path,
                encoding='utf-8-sig'
            )

            # Convert date column to datetime
            if 'DATE' in self._profit_loss_df.columns:
                self._profit_loss_df['DATE'] = pd.to_datetime(
                    self._profit_loss_df['DATE']
                )

            # Ensure numeric columns
            numeric_columns = ['REVENUE_VALUE', 'EXPENSE_VALUE', 'AMOUNT', 'YEAR', 'MONTH']
            for col in numeric_columns:
                if col in self._profit_loss_df.columns:
                    self._profit_loss_df[col] = pd.to_numeric(
                        self._profit_loss_df[col],
                        errors='coerce'
                    ).fillna(0)

            self._last_load_time = datetime.now()
            logger.info(f"Loaded {len(self._profit_loss_df)} rows of profit & loss data")

        return self._profit_loss_df

    def load_other_income_expense_data(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Load other income/expense data from CSV

        Args:
            force_reload: Force reload data even if cached

        Returns:
            DataFrame with other income/expense data

        Raises:
            FileNotFoundError: If CSV file not found
            pd.errors.EmptyDataError: If CSV file is empty
        """
        if self._other_income_expense_df is None or force_reload:
            logger.info(f"Loading other income/expense data from {settings.other_income_expense_path}")

            # Check if file exists
            if not settings.other_income_expense_path.exists():
                raise FileNotFoundError(
                    f"Other income/expense CSV file not found: {settings.other_income_expense_path}"
                )

            # Load CSV
            self._other_income_expense_df = pd.read_csv(
                settings.other_income_expense_path,
                encoding='utf-8-sig'
            )

            # Ensure numeric columns
            numeric_columns = [
                'YEAR', 'MONTH',
                'financial_income_month', 'financial_income_ytd',
                'other_income_month', 'other_income_ytd',
                'other_expense_month', 'other_expense_ytd',
                'financial_cost_month', 'financial_cost_ytd',
                'corporate_tax_month', 'corporate_tax_ytd'
            ]
            for col in numeric_columns:
                if col in self._other_income_expense_df.columns:
                    self._other_income_expense_df[col] = pd.to_numeric(
                        self._other_income_expense_df[col],
                        errors='coerce'
                    ).fillna(0)

            logger.info(f"Loaded {len(self._other_income_expense_df)} rows of other income/expense data")

        return self._other_income_expense_df

    def get_available_filters(self) -> FilterOptions:
        """
        Get available filter options from data

        Returns:
            FilterOptions with available years, business groups, services, and date range
        """
        # Load data
        df = self.load_profit_loss_data()

        # Get available years
        available_years = sorted(df['YEAR'].unique().tolist())

        # Get available business groups
        available_business_groups = sorted(
            df['BUSINESS_GROUP'].dropna().unique().tolist()
        )

        # Get available services
        available_services = sorted(
            df['SERVICE_GROUP'].dropna().unique().tolist()
        )

        # Get date range
        min_date = df['DATE'].min().strftime('%Y-%m-%d') if 'DATE' in df.columns else None
        max_date = df['DATE'].max().strftime('%Y-%m-%d') if 'DATE' in df.columns else None

        logger.info(f"Filter options: {len(available_years)} years, {len(available_business_groups)} business groups")

        return FilterOptions(
            available_years=available_years,
            available_business_groups=available_business_groups,
            available_services=available_services,
            min_date=min_date or "",
            max_date=max_date or ""
        )

    def filter_data(
        self,
        year: int,
        months: List[int],
        business_groups: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Filter profit & loss data by year, months, and business groups

        Args:
            year: Year to filter
            months: List of months (1-12)
            business_groups: Optional list of business groups (None = all)

        Returns:
            Filtered DataFrame
        """
        df = self.load_profit_loss_data()

        # Filter by year and months
        filtered = df[
            (df['YEAR'] == year) &
            (df['MONTH'].isin(months))
        ].copy()

        # Filter by business groups if specified
        if business_groups:
            filtered = filtered[filtered['BUSINESS_GROUP'].isin(business_groups)]

        logger.info(
            f"Filtered data: {len(filtered)} rows "
            f"(year={year}, months={months}, groups={business_groups})"
        )

        return filtered

    def reload_data(self):
        """Reload all data from CSV files"""
        logger.info("Reloading all data from CSV files")
        self.load_profit_loss_data(force_reload=True)
        self.load_other_income_expense_data(force_reload=True)

    def clear_cache(self):
        """Clear cached data"""
        logger.info("Clearing data cache")
        self._profit_loss_df = None
        self._other_income_expense_df = None
        self._last_load_time = None

    @property
    def is_data_loaded(self) -> bool:
        """Check if data is loaded"""
        return self._profit_loss_df is not None

    @property
    def last_load_time(self) -> Optional[datetime]:
        """Get last data load time"""
        return self._last_load_time


# Create global data loader instance
data_loader = DataLoader()

"""
Data Processor - Process and transform loaded CSV data
"""
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


import re


class DataProcessor:
    """Process and aggregate P&L data"""

    @staticmethod
    def _natural_sort_key(s: str) -> list:
        """
        Create a sort key for natural sorting of strings like '1.10', '1.2'.
        Example: '1.10. some text' -> [1, 10]

        Handles edge cases:
        - NaN values (converted to string 'nan' on Windows)
        - Empty strings
        - Non-numeric strings
        """
        # Handle None, NaN, and empty string cases
        if not s or s == 'nan' or (isinstance(s, float) and pd.isna(s)):
            return [float('inf')]  # Sort NaN values to the end

        # Convert to string if not already
        s = str(s).strip()

        # Extracts numbers at the beginning of the string, separated by dots.
        match = re.match(r'^[0-9\.]+', s)
        if not match:
            return [s]  # Return the string itself if no numeric prefix

        # Split by dot and convert to int for numerical sorting
        # Use try-except to handle any unexpected conversion errors
        result = []
        for text in match.group(0).split('.'):
            if text.isdigit():
                try:
                    result.append(int(text))
                except ValueError:
                    result.append(text)

        return result if result else [s]

    def __init__(self):
        """Initialize data processor"""
        pass

    def process_data(
        self,
        df: pd.DataFrame,
        report_type: str = "costtype"
    ) -> pd.DataFrame:
        """
        Process raw CSV data

        Args:
            df: Raw dataframe from CSV
            report_type: Type of report (costtype or glgroup)

        Returns:
            Processed dataframe
        """
        if df.empty:
            return df

        # Clean and standardize column names
        df = df.copy()

        # Parse TIME_KEY if exists
        if 'TIME_KEY' in df.columns:
            # Handle NaN values by filtering them out before conversion
            # On Windows, pandas may convert NaN to string 'nan' which causes int() conversion to fail
            time_key_str = df['TIME_KEY'].astype(str)

            # Convert to int, using pd.to_numeric to handle 'nan' strings gracefully
            df['YEAR'] = pd.to_numeric(time_key_str.str[:4], errors='coerce').fillna(0).astype(int)
            df['MONTH'] = pd.to_numeric(time_key_str.str[4:6], errors='coerce').fillna(0).astype(int)

        # Ensure VALUE column is numeric
        if 'VALUE' in df.columns:
            df['VALUE'] = pd.to_numeric(df['VALUE'], errors='coerce').fillna(0)

        # Convert categorical columns
        categorical_cols = ['GROUP', 'SUB_GROUP', 'BU', 'SERVICE_GROUP', 'PRODUCT_NAME']
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].astype(str)

        # Split SATELLITE service group (if enabled)
        df = self._split_satellite_service_group(df)

        return df

    def create_pivot_by_bu_service(
        self,
        df: pd.DataFrame,
        value_column: str = 'VALUE'
    ) -> pd.DataFrame:
        """
        Create pivot table with BU and SERVICE_GROUP as columns

        Args:
            df: Processed dataframe
            value_column: Column to aggregate

        Returns:
            Pivot table with rows as categories and columns as BU/SERVICE_GROUP
        """
        if df.empty:
            return pd.DataFrame()

        # Group by relevant columns
        index_cols = []
        if 'GROUP' in df.columns:
            index_cols.append('GROUP')
        if 'SUB_GROUP' in df.columns:
            index_cols.append('SUB_GROUP')

        if not index_cols:
            logger.error("No grouping columns found in dataframe")
            return pd.DataFrame()

        # Create pivot
        try:
            pivot = pd.pivot_table(
                df,
                values=value_column,
                index=index_cols,
                columns=['BU', 'SERVICE_GROUP'],
                aggfunc='sum',
                fill_value=0
            )
            return pivot
        except Exception as e:
            logger.error(f"Error creating pivot table: {e}")
            return pd.DataFrame()

    def aggregate_by_bu(
        self,
        df: pd.DataFrame,
        group_cols: List[str],
        value_col: str = 'VALUE'
    ) -> pd.DataFrame:
        """
        Aggregate data by Business Unit

        Args:
            df: Dataframe to aggregate
            group_cols: Columns to group by
            value_col: Column to sum

        Returns:
            Aggregated dataframe
        """
        if df.empty:
            return df

        agg_df = df.groupby(group_cols, as_index=False)[value_col].sum()
        return agg_df

    def calculate_totals(
        self,
        df: pd.DataFrame,
        group_level: str = 'BU'
    ) -> pd.DataFrame:
        """
        Calculate subtotals and grand totals

        Args:
            df: Dataframe with data
            group_level: Level to calculate totals (BU, SERVICE_GROUP)

        Returns:
            Dataframe with totals added
        """
        # This will be implemented when building the Excel generator
        # as it needs to add rows for subtotals
        pass

    def get_unique_business_units(self, df: pd.DataFrame) -> List[str]:
        """
        Get unique business units, sorted naturally.

        Args:
            df: Dataframe with BU column

        Returns:
            Ordered list of unique business units
        """
        if df.empty or 'BU' not in df.columns:
            return []

        unique_bus = df['BU'].dropna().unique().tolist()
        
        # Sort the list using the natural sort key
        return sorted(unique_bus, key=self._natural_sort_key)

    def get_unique_service_groups(
        self,
        df: pd.DataFrame,
        bu: Optional[str] = None
    ) -> List[str]:
        """
        Get unique service groups for a given BU, sorted naturally.

        Args:
            df: Dataframe with SERVICE_GROUP column
            bu: Business unit to filter (None = all)

        Returns:
            List of unique service groups
        """
        if df.empty or 'SERVICE_GROUP' not in df.columns:
            return []

        if bu:
            df = df[df['BU'] == bu]

        unique_sgs = df['SERVICE_GROUP'].dropna().unique().tolist()
        
        # Sort the list using the natural sort key
        return sorted(unique_sgs, key=self._natural_sort_key)

    def filter_by_period(
        self,
        df: pd.DataFrame,
        year: Optional[int] = None,
        months: Optional[List[int]] = None
    ) -> pd.DataFrame:
        """
        Filter data by year and months

        Args:
            df: Dataframe to filter
            year: Year to filter (None = all years)
            months: List of months to filter (None = all months)

        Returns:
            Filtered dataframe
        """
        if df.empty:
            return df

        filtered = df.copy()

        if year and 'YEAR' in filtered.columns:
            filtered = filtered[filtered['YEAR'] == year]

        if months and 'MONTH' in filtered.columns:
            filtered = filtered[filtered['MONTH'].isin(months)]

        return filtered

    def get_period_description(
        self,
        df: pd.DataFrame,
        report_type: str
    ) -> Tuple[str, List[int]]:
        """
        Get period description from data

        Args:
            df: Dataframe with date information
            report_type: Type of report (MTH or YTD)

        Returns:
            Tuple of (period_description, months_list)
        """
        if df.empty:
            return ("", [])

        # Get months from data
        months = sorted(df['MONTH'].unique().tolist()) if 'MONTH' in df.columns else []

        # Determine if YTD or MTH
        is_ytd = 'YTD' in report_type.upper() or len(months) > 1

        if is_ytd:
            # สำหรับงวด 9 เดือน สิ้นสุดวันที่ 30 กันยายน 2568
            last_month = max(months) if months else 12
            year = df['YEAR'].iloc[0] if 'YEAR' in df.columns else 2568

            # Convert to Buddhist year
            buddhist_year = year + 543 if year < 2100 else year

            month_names_thai = [
                "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
            ]
            month_name = month_names_thai[last_month] if last_month <= 12 else ""

            # Get last day of month
            import calendar
            last_day = calendar.monthrange(year, last_month)[1]

            period_desc = f"สำหรับงวด {last_month} เดือน สิ้นสุดวันที่ {last_day} {month_name} {buddhist_year}"
        else:
            # ประจำเดือน กันยายน 2568
            month = months[0] if months else 1
            year = df['YEAR'].iloc[0] if 'YEAR' in df.columns else 2568

            buddhist_year = year + 543 if year < 2100 else year

            month_names_thai = [
                "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
            ]
            month_name = month_names_thai[month] if month <= 12 else ""

            period_desc = f"ประจำเดือน {month_name} {buddhist_year}"

        return period_desc, months

    def _split_satellite_service_group(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Split SATELLITE service group into sub-groups based on PRODUCT_KEY

        This splits '4.5 กลุ่มบริการ SATELLITE' into:
        - 4.5.1 กลุ่มบริการ Satellite-NT
        - 4.5.2 กลุ่มบริการ Satellite-ไทยคม

        Works for BOTH COSTTYPE and GLGROUP report types.

        Args:
            df: DataFrame with SERVICE_GROUP and PRODUCT_KEY columns

        Returns:
            DataFrame with updated SERVICE_GROUP column
        """
        import sys
        from pathlib import Path

        # Add config path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from config.satellite_config import (
            ENABLE_SATELLITE_SPLIT,
            SATELLITE_SOURCE_NAME,
            get_service_group_for_product_key
        )

        # Check if feature is enabled
        if not ENABLE_SATELLITE_SPLIT:
            logger.info("SATELLITE split is disabled in config")
            return df

        # Check required columns
        if 'SERVICE_GROUP' not in df.columns:
            logger.warning("SERVICE_GROUP column not found - skipping SATELLITE split")
            return df

        if 'PRODUCT_KEY' not in df.columns:
            logger.warning("PRODUCT_KEY column not found - skipping SATELLITE split")
            return df

        # Find SATELLITE rows
        satellite_mask = df['SERVICE_GROUP'] == SATELLITE_SOURCE_NAME

        if not satellite_mask.any():
            logger.info(f"No '{SATELLITE_SOURCE_NAME}' found - skipping split")
            return df

        logger.info(f"Found {satellite_mask.sum()} SATELLITE rows - splitting...")

        # Split based on PRODUCT_KEY
        updated_count = 0
        unmatched_count = 0
        unmatched_keys = set()

        for idx in df[satellite_mask].index:
            product_key = df.loc[idx, 'PRODUCT_KEY']
            new_sg = get_service_group_for_product_key(product_key)

            if new_sg:
                df.loc[idx, 'SERVICE_GROUP'] = new_sg
                updated_count += 1
            else:
                unmatched_count += 1
                unmatched_keys.add(str(product_key))

        # Log results
        logger.info(f"SATELLITE split complete:")
        logger.info(f"  ✓ Updated: {updated_count} rows")

        if unmatched_count > 0:
            logger.warning(f"  ⚠ Unmatched: {unmatched_count} rows")
            logger.warning(f"    Product keys: {sorted(unmatched_keys)}")

        # Count by new groups
        from config.satellite_config import get_satellite_service_group_names
        for sg_name in get_satellite_service_group_names():
            count = (df['SERVICE_GROUP'] == sg_name).sum()
            logger.info(f"  → {sg_name}: {count} rows")

        return df

"""
Data Processor - Process and transform loaded CSV data
"""
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and aggregate P&L data"""

    # Business Group order
    BU_ORDER = [
        "กลุ่มธุรกิจ HARD INFRASTRUCTURE",
        "กลุ่มธุรกิจ INTERNATIONAL",
        "กลุ่มธุรกิจ MOBILE",
        "กลุ่มธุรกิจ FIXED LINE & BROADBAND",
        "กลุ่มธุรกิจ DIGITAL",
        "กลุ่มธุรกิจ ICT SOLUTION",
        "กลุ่มบริการอื่นไม่ใช่โทรคมนาคม",
        "รายได้อื่น/ค่าใช้จ่ายอื่น",
    ]

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
            df['YEAR'] = df['TIME_KEY'].astype(str).str[:4].astype(int)
            df['MONTH'] = df['TIME_KEY'].astype(str).str[4:6].astype(int)

        # Ensure VALUE column is numeric
        if 'VALUE' in df.columns:
            df['VALUE'] = pd.to_numeric(df['VALUE'], errors='coerce').fillna(0)

        # Convert categorical columns
        categorical_cols = ['GROUP', 'SUB_GROUP', 'BU', 'SERVICE_GROUP', 'PRODUCT_NAME']
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].astype(str)

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
        Get unique business units in order

        Args:
            df: Dataframe with BU column

        Returns:
            Ordered list of unique business units
        """
        if df.empty or 'BU' not in df.columns:
            return []

        unique_bus = df['BU'].dropna().unique().tolist()

        # Sort according to predefined order
        ordered_bus = []
        for bu in self.BU_ORDER:
            if bu in unique_bus:
                ordered_bus.append(bu)

        # Add any remaining BUs not in the predefined order
        for bu in unique_bus:
            if bu not in ordered_bus:
                ordered_bus.append(bu)

        return ordered_bus

    def get_unique_service_groups(
        self,
        df: pd.DataFrame,
        bu: Optional[str] = None
    ) -> List[str]:
        """
        Get unique service groups for a given BU

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

        return sorted(df['SERVICE_GROUP'].dropna().unique().tolist())

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

            period_desc = f"สำหรับงวด {len(months)} เดือน สิ้นสุดวันที่ {last_day} {month_name} {buddhist_year}"
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

"""
Excel Calculator - Financial calculations for P&L report
"""
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ExcelCalculator:
    """Calculate financial metrics for P&L report"""

    def __init__(self):
        """Initialize calculator"""
        pass

    def safe_divide(self, numerator: float, denominator: float) -> Optional[float]:
        """
        Safely divide two numbers, return None for division by zero

        Args:
            numerator: Number to divide
            denominator: Number to divide by

        Returns:
            Result of division or None if division by zero
        """
        if denominator == 0 or abs(denominator) < 1e-9:
            return None
        return numerator / denominator

    def calculate_gross_profit(
        self,
        revenue: float,
        cost_of_service: float
    ) -> float:
        """
        Calculate gross profit = Revenue - Cost of Service

        Args:
            revenue: Total revenue
            cost_of_service: Total cost of service

        Returns:
            Gross profit
        """
        return revenue - cost_of_service

    def calculate_ebit(
        self,
        gross_profit: float,
        selling_expense: float,
        admin_expense: float,
        finance_cost_operating: float
    ) -> float:
        """
        Calculate EBIT = Gross Profit - Selling Expense - Admin Expense - Finance Cost (Operating)

        Args:
            gross_profit: Gross profit
            selling_expense: Selling and marketing expense
            admin_expense: Administrative expense
            finance_cost_operating: Finance cost from operations

        Returns:
            EBIT (Earnings Before Interest and Tax)
        """
        return gross_profit - selling_expense - admin_expense - finance_cost_operating

    def calculate_ebt(
        self,
        ebit: float,
        financial_income: float,
        other_income: float,
        other_expense: float,
        finance_cost_funding: float
    ) -> float:
        """
        Calculate EBT = EBIT + Financial Income + Other Income - Other Expense - Finance Cost (Funding)

        Args:
            ebit: Earnings before interest and tax
            financial_income: Financial income
            other_income: Other income
            other_expense: Other expense
            finance_cost_funding: Finance cost from funding

        Returns:
            EBT (Earnings Before Tax)
        """
        return ebit + financial_income + other_income - other_expense - finance_cost_funding

    def calculate_net_profit(
        self,
        ebt: float,
        corporate_tax: float
    ) -> float:
        """
        Calculate Net Profit = EBT - Corporate Tax

        Args:
            ebt: Earnings before tax
            corporate_tax: Corporate income tax

        Returns:
            Net profit
        """
        return ebt - corporate_tax

    def calculate_ebitda(
        self,
        ebit: float,
        depreciation: float,
        amortization_right_of_use: float
    ) -> float:
        """
        Calculate EBITDA = EBIT + Depreciation + Amortization (Right of Use)

        Args:
            ebit: Earnings before interest and tax
            depreciation: Depreciation expense
            amortization_right_of_use: Amortization of right-of-use assets

        Returns:
            EBITDA
        """
        return ebit + depreciation + amortization_right_of_use

    def calculate_total_revenue(self, revenue_items: Dict[str, float]) -> float:
        """
        Calculate total revenue from all revenue items

        Args:
            revenue_items: Dictionary of revenue items

        Returns:
            Total revenue
        """
        return sum(revenue_items.values())

    def calculate_total_expense(
        self,
        cost_of_service: float,
        selling_expense: float,
        admin_expense: float,
        include_finance_cost: bool = False,
        finance_cost_operating: float = 0,
        finance_cost_funding: float = 0
    ) -> float:
        """
        Calculate total expense

        Args:
            cost_of_service: Cost of service
            selling_expense: Selling expense
            admin_expense: Administrative expense
            include_finance_cost: Whether to include finance costs
            finance_cost_operating: Finance cost from operations
            finance_cost_funding: Finance cost from funding

        Returns:
            Total expense
        """
        total = cost_of_service + selling_expense + admin_expense

        if include_finance_cost:
            total += finance_cost_operating + finance_cost_funding

        return total

    def calculate_service_cost_ratio(
        self,
        service_revenue: float,
        total_service_cost: float,
        depreciation: float = 0,
        amortization: float = 0,
        personnel_cost: float = 0,
        calculation_type: str = "total"
    ) -> Tuple[float, Optional[float]]:
        """
        Calculate service cost to revenue ratio

        Args:
            service_revenue: Service revenue
            total_service_cost: Total service cost
            depreciation: Depreciation expense
            amortization: Amortization expense
            personnel_cost: Personnel cost
            calculation_type: Type of calculation
                - "total": Total service cost
                - "no_depreciation": Exclude depreciation and amortization
                - "no_personnel_depreciation": Exclude personnel, depreciation, and amortization

        Returns:
            Tuple of (adjusted_cost, ratio)
            ratio is None if division by zero
        """
        adjusted_cost = total_service_cost

        if calculation_type == "no_depreciation":
            adjusted_cost = total_service_cost - depreciation - amortization
        elif calculation_type == "no_personnel_depreciation":
            adjusted_cost = total_service_cost - depreciation - amortization - personnel_cost

        ratio = self.safe_divide(adjusted_cost, service_revenue)

        return adjusted_cost, ratio

    def aggregate_by_category(
        self,
        df: pd.DataFrame,
        category_column: str,
        value_column: str = 'VALUE',
        categories: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Aggregate data by category

        Args:
            df: Dataframe with data
            category_column: Column to group by
            value_column: Column to sum
            categories: List of categories to filter (None = all)

        Returns:
            Dictionary mapping category to total value
        """
        if df.empty:
            return {}

        if categories:
            df = df[df[category_column].isin(categories)]

        result = df.groupby(category_column)[value_column].sum().to_dict()
        return result

    def sum_categories(
        self,
        category_values: Dict[str, float],
        category_names: List[str]
    ) -> float:
        """
        Sum values for specified categories

        Args:
            category_values: Dictionary of category values
            category_names: List of category names to sum

        Returns:
            Sum of category values
        """
        total = 0
        for cat in category_names:
            total += category_values.get(cat, 0)
        return total

    def calculate_column_totals(
        self,
        data: Dict[str, Dict[str, float]],
        columns: List[str]
    ) -> Dict[str, float]:
        """
        Calculate totals for each column

        Args:
            data: Nested dictionary {row_name: {column_name: value}}
            columns: List of column names

        Returns:
            Dictionary mapping column names to totals
        """
        totals = {col: 0 for col in columns}

        for row_data in data.values():
            for col in columns:
                totals[col] += row_data.get(col, 0)

        return totals

    def calculate_row_total(
        self,
        row_data: Dict[str, float]
    ) -> float:
        """
        Calculate total for a single row

        Args:
            row_data: Dictionary of {column_name: value}

        Returns:
            Row total
        """
        return sum(row_data.values())

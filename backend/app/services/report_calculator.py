"""
Report Calculator Service
คำนวณรายงานผลดำเนินงาน (P&L Report)
"""

import pandas as pd
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.services.data_loader import data_loader
from app.models.report import ReportFilter, ReportMetrics, ReportData, ReportRow

logger = logging.getLogger(__name__)


class ReportCalculator:
    """Class สำหรับคำนวณรายงานผลดำเนินงาน"""

    def __init__(self):
        """Initialize calculator - data loaded from data_loader"""
        self.data_loader = data_loader

    def calculate_revenue(
        self,
        year: int,
        months: List[int],
        business_groups: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        คำนวณรายได้แยกตามกลุ่มธุรกิจ

        Args:
            year: ปี
            months: รายการเดือน
            business_groups: รายการกลุ่มธุรกิจ (ถ้าเป็น None = ทั้งหมด)

        Returns:
            Dict with business group as key and revenue as value
        """
        # Load and filter data
        df = self.data_loader.filter_data(year, months, business_groups)

        # Filter only revenue rows
        df = df[df['REVENUE_VALUE'] > 0]

        # Group by business group and sum revenue
        revenue_by_group = df.groupby('BUSINESS_GROUP')['REVENUE_VALUE'].sum()

        # Get available business groups from data
        available_groups = sorted(revenue_by_group.index.tolist())

        result = {}
        for group in available_groups:
            result[group] = revenue_by_group.get(group, 0.0)

        # รายได้รวม
        result['Total'] = sum(result.values())

        logger.info(f"Calculated revenue for {len(available_groups)} groups: Total = {result['Total']:,.2f}")

        return result

    def calculate_cost_by_type(
        self,
        year: int,
        months: List[int],
        cost_type: str,
        business_groups: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        คำนวณต้นทุน/ค่าใช้จ่ายตาม TYPE

        Args:
            year: ปี
            months: รายการเดือน
            cost_type: ประเภทต้นทุน
                - '02 ต้นทุนบริการ'
                - '03 ค่าใช้จ่ายขายและการตลาด'
                - '04 ค่าใช้จ่ายสนับสนุน'
            business_groups: รายการกลุ่มธุรกิจ

        Returns:
            Dict with account category as key and amount as value
        """
        # Load and filter data
        df = self.data_loader.filter_data(year, months, business_groups)

        # Filter by cost type
        df = df[df['TYPE'] == cost_type]

        # Group by account category
        cost_by_category = df.groupby('หมวดบัญชี')['EXPENSE_VALUE'].sum()

        # Get categories from actual data
        result = {}
        for category in cost_by_category.index:
            result[category] = cost_by_category[category]

        # Total
        result['Total'] = sum(result.values())

        logger.info(f"Calculated {cost_type}: {len(result)-1} categories, Total = {result['Total']:,.2f}")

        return result

    def calculate_ytd(
        self,
        year: int,
        month: int,
        metric_name: str,
        business_groups: Optional[List[str]] = None
    ) -> float:
        """
        คำนวณยอดสะสม (Year-to-Date)

        Args:
            year: ปี
            month: เดือน
            metric_name: ชื่อตัวชี้วัด (revenue, cost, etc.)
            business_groups: รายการกลุ่มธุรกิจ

        Returns:
            ยอดสะสมตั้งแต่ต้นปีถึงเดือนที่ระบุ
        """
        # สำหรับข้อมูลหลัก ให้บวกสะสมจากเดือน 1 ถึงเดือนที่ระบุ
        months = list(range(1, month + 1))

        if metric_name == 'revenue':
            revenue = self.calculate_revenue(year, months, business_groups)
            return revenue['Total']
        elif metric_name.startswith('cost_'):
            cost_type = metric_name.replace('cost_', '')
            cost = self.calculate_cost_by_type(year, months, cost_type, business_groups)
            return cost['Total']
        else:
            # สำหรับ other income/expense ใช้ค่าจาก data loader
            df = self.data_loader.load_other_income_expense_data()
            df = df[(df['YEAR'] == year) & (df['MONTH'] == month)]

            column_map = {
                'other_income': 'other_income_ytd',
                'other_expense': 'other_expense_ytd',
                'financial_income': 'financial_income_ytd',
                'financial_cost': 'financial_cost_ytd',
                'corporate_tax': 'corporate_tax_ytd',
            }

            col = column_map.get(metric_name)
            if col and not df.empty:
                return df[col].iloc[0]

        return 0.0

    def calculate_profit_metrics(
        self,
        revenue: float,
        cost_of_service: float,
        selling_expense: float,
        admin_expense: float,
        operating_financial_cost: float = 0,
        depreciation_amortization: float = 0,
        other_income: float = 0,
        other_expense: float = 0,
        financial_cost: float = 0,
        corporate_tax: float = 0
    ) -> Dict[str, float]:
        """
        คำนวณตัวชี้วัดกำไรต่างๆ

        Returns:
            Dict containing:
            - gross_profit: กำไรขั้นต้น
            - profit_after_selling: กำไรหลังหักค่าใช้จ่ายขาย
            - ebit: Earnings Before Interest and Tax
            - ebitda: EBIT + Depreciation + Amortization
            - ebt: Earnings Before Tax
            - net_profit: กำไรสุทธิ
        """
        # กำไรขั้นต้น
        gross_profit = revenue - cost_of_service

        # กำไรหลังหักค่าใช้จ่ายขาย
        profit_after_selling = gross_profit - selling_expense

        # EBIT
        ebit = profit_after_selling - admin_expense - operating_financial_cost

        # EBITDA
        ebitda = ebit + depreciation_amortization

        # EBT
        ebt = ebit + other_income - other_expense - financial_cost

        # กำไรสุทธิ
        net_profit = ebt - corporate_tax

        return {
            'gross_profit': gross_profit,
            'profit_after_selling': profit_after_selling,
            'ebit': ebit,
            'ebitda': ebitda,
            'ebt': ebt,
            'net_profit': net_profit
        }

    def calculate_common_size(
        self,
        amount: float,
        base_revenue: float
    ) -> float:
        """
        คำนวณ Common Size (เปอร์เซ็นต์เทียบกับรายได้)

        Args:
            amount: จำนวนเงิน
            base_revenue: รายได้ฐาน

        Returns:
            เปอร์เซ็นต์ (0-100)
        """
        if base_revenue == 0:
            return 0.0

        return (amount / base_revenue) * 100

    def calculate_cost_to_revenue_ratio(
        self,
        total_cost: float,
        depreciation: float,
        labor_cost: float,
        service_revenue: float
    ) -> Dict[str, Dict[str, float]]:
        """
        คำนวณอัตราส่วนต้นทุนบริการต่อรายได้

        Returns:
            Dict containing ratios
        """
        # ต้นทุนบริการรวม
        total_ratio = (total_cost / service_revenue * 100) if service_revenue > 0 else 0

        # ต้นทุนบริการ - ค่าเสื่อมราคา
        cost_without_depreciation = total_cost - depreciation
        without_depreciation_ratio = (
            cost_without_depreciation / service_revenue * 100
        ) if service_revenue > 0 else 0

        # ต้นทุนบริการ - ไม่รวมค่าใช้จ่ายบุคลากรและค่าเสื่อมราคา
        cost_without_labor_depreciation = total_cost - labor_cost - depreciation
        without_labor_depreciation_ratio = (
            cost_without_labor_depreciation / service_revenue * 100
        ) if service_revenue > 0 else 0

        return {
            'total_cost': {
                'amount': total_cost,
                'ratio': total_ratio
            },
            'without_depreciation': {
                'amount': cost_without_depreciation,
                'ratio': without_depreciation_ratio
            },
            'without_labor_depreciation': {
                'amount': cost_without_labor_depreciation,
                'ratio': without_labor_depreciation_ratio
            }
        }

    def generate_full_report(
        self,
        year: int,
        months: List[int],
        business_groups: Optional[List[str]] = None,
        view_type: str = 'monthly',  # 'monthly', 'quarterly', 'yearly'
        display_type: str = 'actual',  # 'actual', 'ytd', 'both'
        show_common_size: bool = False
    ) -> Dict[str, Any]:
        """
        สร้างรายงานผลดำเนินงานแบบเต็ม

        Returns:
            Dict containing complete P&L report structure
        """
        # Implementation will be in next iteration
        # This is the main method that orchestrates all calculations
        # and returns data in the format needed for Univer snapshot conversion

        report = {
            'metadata': {
                'year': year,
                'months': months,
                'business_groups': business_groups or 'All',
                'view_type': view_type,
                'display_type': display_type,
                'show_common_size': show_common_size,
                'generated_at': datetime.now().isoformat()
            },
            'data': {
                'revenue': {},
                'cost_of_service': {},
                'selling_expense': {},
                'admin_expense': {},
                'metrics': {},
                'ratios': {}
            }
        }

        # คำนวณรายได้
        report['data']['revenue'] = self.calculate_revenue(year, months, business_groups)

        # คำนวณต้นทุนบริการ
        report['data']['cost_of_service'] = self.calculate_cost_by_type(
            year, months, '02 ต้นทุนบริการ', business_groups
        )

        # คำนวณค่าใช้จ่ายขาย
        report['data']['selling_expense'] = self.calculate_cost_by_type(
            year, months, '03 ค่าใช้จ่ายขายและการตลาด', business_groups
        )

        # คำนวณค่าใช้จ่ายบริหาร
        report['data']['admin_expense'] = self.calculate_cost_by_type(
            year, months, '04 ค่าใช้จ่ายสนับสนุน', business_groups
        )

        # คำนวณ profit metrics
        report['data']['metrics'] = self.calculate_profit_metrics(
            revenue=report['data']['revenue']['Total'],
            cost_of_service=report['data']['cost_of_service']['Total'],
            selling_expense=report['data']['selling_expense']['Total'],
            admin_expense=report['data']['admin_expense']['Total']
        )

        # คำนวณ Common Size ถ้าต้องการ
        if show_common_size:
            base_revenue = report['data']['revenue']['Total']
            report['data']['common_size'] = {
                'revenue': {
                    k: self.calculate_common_size(v, base_revenue)
                    for k, v in report['data']['revenue'].items()
                },
                'cost_of_service': {
                    k: self.calculate_common_size(v, base_revenue)
                    for k, v in report['data']['cost_of_service'].items()
                }
            }

        return report


# Create global report calculator instance
report_calculator = ReportCalculator()

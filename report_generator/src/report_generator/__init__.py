"""
Report Generator Module
Modern modular architecture for P&L report generation

This module provides flexible report generation with multiple detail levels:
- BU Only: รายงานระดับกลุ่มธุรกิจ
- BU + SG: รายงานระดับกลุ่มธุรกิจ + กลุ่มบริการ
- BU + SG + Products: รายงานระดับกลุ่มธุรกิจ + กลุ่มบริการ + บริการ

Supports both:
- มิติต้นทุน (COSTTYPE)
- มิติหมวดบัญชี (GLGROUP)

Usage:
    from src.report_generator import ReportBuilder, ReportConfig
    
    config = ReportConfig(
        report_type="COSTTYPE",
        period_type="MTH",
        detail_level="BU_SG_PRODUCT"
    )
    
    builder = ReportBuilder(config)
    builder.generate_report(data, output_path, remark_content)
"""

from .core.config import (
    ReportConfig,
    ReportType,
    PeriodType,
    DetailLevel
)
from .core.report_builder import ReportBuilder

__version__ = '2.0.0'
__author__ = 'NT P&L Report Team'

__all__ = [
    'ReportBuilder',
    'ReportConfig',
    'ReportType',
    'PeriodType',
    'DetailLevel',
]

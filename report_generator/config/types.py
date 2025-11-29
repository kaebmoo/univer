"""
Type definitions for report generator
"""
from enum import Enum


class ReportType(Enum):
    """Report type dimension"""
    COSTTYPE = "COSTTYPE"  # มิติประเภทต้นทุน
    GLGROUP = "GLGROUP"    # มิติหมวดบัญชี


class DetailLevel(Enum):
    """Detail level for report columns"""
    BU_ONLY = "BU_ONLY"              # BU Total only
    BU_SG = "BU_SG"                  # BU + Service Group
    BU_SG_PRODUCT = "BU_SG_PRODUCT"  # BU + Service Group + Products


class PeriodType(Enum):
    """Period type for report"""
    MTH = "MTH"  # Monthly
    YTD = "YTD"  # Year to Date

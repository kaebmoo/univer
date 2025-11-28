"""
Report Configuration
Define report structure and settings
"""
from dataclasses import dataclass, field
from typing import Optional, Dict
from enum import Enum


class ReportType(str, Enum):
    """Report type enumeration"""
    COSTTYPE = "COSTTYPE"
    GLGROUP = "GLGROUP"


class PeriodType(str, Enum):
    """Period type enumeration"""
    MTH = "MTH"
    YTD = "YTD"


class DetailLevel(str, Enum):
    """Report detail level enumeration"""
    BU_ONLY = "BU_ONLY"                    # กลุ่มธุรกิจเท่านั้น
    BU_SG = "BU_SG"                        # กลุ่มธุรกิจ + กลุ่มบริการ
    BU_SG_PRODUCT = "BU_SG_PRODUCT"        # กลุ่มธุรกิจ + กลุ่มบริการ + บริการ (current default)


@dataclass
class ReportConfig:
    """
    Report configuration settings
    
    Attributes:
        report_type: Report type (COSTTYPE or GLGROUP)
        period_type: Period type (MTH or YTD)
        detail_level: Level of detail in report columns
        
        include_bu_total: Include BU total columns
        include_sg_total: Include Service Group total columns
        include_products: Include product-level columns
        
        show_info_box: Show info box at top right
        show_remarks: Show remarks section at bottom
        
        font_name: Font name for report
        font_size: Default font size
        header_font_size: Font size for headers
        remark_font_size: Font size for remarks
        
        bu_colors: BU color mapping (hex colors without #)
        row_colors: Row color mapping
    """
    
    # Required settings
    report_type: ReportType
    period_type: PeriodType
    detail_level: DetailLevel = DetailLevel.BU_SG_PRODUCT
    
    # Column inclusion flags
    include_bu_total: bool = True
    include_sg_total: bool = True
    include_products: bool = True
    
    # Display settings
    show_info_box: bool = True
    show_remarks: bool = True
    
    # Font settings
    font_name: str = "TH Sarabun New"
    font_size: int = 18
    header_font_size: int = 18
    remark_font_size: int = 14
    
    # Color settings
    bu_colors: Dict[str, str] = field(default_factory=lambda: {
        '1.กลุ่มธุรกิจ HARD INFRASTRUCTURE': 'E2EFDA',
        '2.กลุ่มธุรกิจ INTERNATIONAL': 'DDEBF7',
        '3.กลุ่มธุรกิจ MOBILE': 'DBD3E5',
        '4.กลุ่มธุรกิจ FIXED LINE & BROADBAND': 'FCE4D6',
        '5.กลุ่มธุรกิจ DIGITAL': 'D9E1F2',
        '6.กลุ่มธุรกิจ ICT SOLUTION': 'C6E0B4',
        '7.กลุ่มบริการอื่นไม่ใช่โทรคมนาคม': 'BDD7EE',
        '8.รายได้อื่น/ค่าใช้จ่ายอื่น': 'EAC1C0',
    })
    
    row_colors: Dict[str, str] = field(default_factory=lambda: {
        'section_header': 'F8CBAD',      # Section headers (1.รายได้, 2.ต้นทุน, etc.)
        'info_box': 'F8CBAD',            # Info box background
        'grand_total': 'FFD966',         # Grand total column
        'detail_label': 'F4DEDC',        # รายละเอียด column
        'gray_none': 'A6A6A6',           # Gray for None values
    })
    
    # Excel structure settings
    start_row: int = 5                   # 0-indexed (Row 6 in Excel)
    start_col: int = 1                   # 0-indexed (Column B in Excel)
    header_row: int = 1                  # 0-indexed (Row 2 in Excel)
    info_box_col: int = 6                # 0-indexed (Column G in Excel)
    info_box_row: int = 0                # 0-indexed (Row 1 in Excel)
    header_rows: int = 4                 # Number of header rows for columns
    
    def __post_init__(self):
        """Validate and adjust settings based on detail_level"""
        
        # Validate enums
        if isinstance(self.report_type, str):
            self.report_type = ReportType(self.report_type)
        if isinstance(self.period_type, str):
            self.period_type = PeriodType(self.period_type)
        if isinstance(self.detail_level, str):
            self.detail_level = DetailLevel(self.detail_level)
        
        # Adjust flags based on detail level
        if self.detail_level == DetailLevel.BU_ONLY:
            self.include_sg_total = False
            self.include_products = False
        elif self.detail_level == DetailLevel.BU_SG:
            self.include_products = False
        # BU_SG_PRODUCT keeps all flags as is
    
    @property
    def report_type_thai(self) -> str:
        """Get Thai name for report type"""
        return "มิติประเภทต้นทุน" if self.report_type == ReportType.COSTTYPE else "มิติหมวดบัญชี"
    
    @property
    def detail_level_thai(self) -> str:
        """Get Thai description of detail level"""
        if self.detail_level == DetailLevel.BU_ONLY:
            return "กลุ่มธุรกิจ"
        elif self.detail_level == DetailLevel.BU_SG:
            return "กลุ่มธุรกิจ/กลุ่มบริการ"
        else:
            return "กลุ่มธุรกิจ/กลุ่มบริการ/รายบริการ"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for backward compatibility"""
        return {
            'report_type': self.report_type.value,
            'period_type': self.period_type.value,
            'detail_level': self.detail_level.value,
            'font_name': self.font_name,
            'font_size': self.font_size,
            'header_font_size': self.header_font_size,
            'remark_font_size': self.remark_font_size,
            'bu_colors': self.bu_colors,
            'row_colors': self.row_colors,
            'start_row': self.start_row,
            'start_col': self.start_col,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ReportConfig':
        """Create config from dictionary"""
        return cls(
            report_type=ReportType(data.get('report_type', 'COSTTYPE')),
            period_type=PeriodType(data.get('period_type', 'MTH')),
            detail_level=DetailLevel(data.get('detail_level', 'BU_SG_PRODUCT')),
            font_name=data.get('font_name', 'TH Sarabun New'),
            font_size=data.get('font_size', 18),
            bu_colors=data.get('bu_colors', {}),
            row_colors=data.get('row_colors', {}),
        )
    
    @classmethod
    def create_default(
        cls,
        report_type: str = "COSTTYPE",
        period_type: str = "MTH",
        detail_level: str = "BU_SG_PRODUCT"
    ) -> 'ReportConfig':
        """
        Create config with default settings
        
        Args:
            report_type: Report type (COSTTYPE or GLGROUP)
            period_type: Period type (MTH or YTD)
            detail_level: Detail level (BU_ONLY, BU_SG, BU_SG_PRODUCT)
        
        Returns:
            ReportConfig with default settings
        """
        return cls(
            report_type=ReportType(report_type),
            period_type=PeriodType(period_type),
            detail_level=DetailLevel(detail_level)
        )

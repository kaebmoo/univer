"""
Report Configuration
Central config for report generation
"""
from dataclasses import dataclass
from .types import ReportType, DetailLevel, PeriodType


@dataclass
class ReportConfig:
    """Configuration for report generation"""
    
    # Report dimensions
    report_type: ReportType = ReportType.COSTTYPE
    detail_level: DetailLevel = DetailLevel.BU_SG_PRODUCT
    period_type: PeriodType = PeriodType.MTH
    
    # Excel positioning
    start_row: int = 5  # 0-indexed: row 6
    start_col: int = 1  # 0-indexed: column B
    header_rows: int = 4
    
    # Font settings
    font_name: str = "TH Sarabun New"
    font_size: int = 18
    header_font_size: int = 18
    
    # Colors
    bu_colors: dict = None
    sg_colors: dict = None
    row_colors: dict = None
    
    def __post_init__(self):
        """Initialize default colors if not provided"""
        if self.bu_colors is None:
            self.bu_colors = {
                '1.กลุ่มธุรกิจ HARD INFRASTRUCTURE': 'E2EFDA',
                '2.กลุ่มธุรกิจ INTERNATIONAL': 'DDEBF7',
                '3.กลุ่มธุรกิจ MOBILE': 'DBD3E5',
                '4.กลุ่มธุรกิจ FIXED LINE & BROADBAND': 'FCE4D6',
                '5.กลุ่มธุรกิจ DIGITAL': 'D9E1F2',
                '6.กลุ่มธุรกิจ ICT SOLUTION': 'C6E0B4',
                '7.กลุ่มบริการอื่นไม่ใช่โทรคมนาคม': 'BDD7EE',
                '8.รายได้อื่น/ค่าใช้จ่ายอื่น': 'EAC1C0',
            }
        
        if self.sg_colors is None:
            self.sg_colors = {
                'SG1': 'FFE699',
                'SG2': 'C6E0B4',
                'SG3': 'BDD7EE',
            }
        
        if self.row_colors is None:
            self.row_colors = {
                'section_header': 'F8CBAD',
                'label': 'F8CBAD',
                'gray_none': 'A6A6A6',
            }

"""
Row Builder
Build row structure from ROW_ORDER configuration
Supports both COSTTYPE and GLGROUP report types
"""
from typing import List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RowDef:
    """
    Row definition
    
    Attributes:
        level: Indentation level (0, 1, 2, 3, ...)
        label: Row label text
        is_calculated: Whether this is a calculated row
        formula: Formula for calculation (if applicable)
        is_bold: Whether text should be bold
        color: Background color (hex without #) for section headers
    """
    level: int
    label: str
    is_calculated: bool
    formula: str
    is_bold: bool
    color: str = None
    
    def __repr__(self) -> str:
        return f"RowDef(label='{self.label}', level={self.level}, bold={self.is_bold})"


class RowBuilder:
    """Build row structure from ROW_ORDER"""
    
    def __init__(self, config):
        """
        Initialize row builder
        
        Args:
            config: ReportConfig instance
        """
        self.config = config
    
    def build_rows(self) -> List[RowDef]:
        """
        Build row structure from ROW_ORDER configuration
        Selects appropriate ROW_ORDER based on report type
        
        Returns:
            List of RowDef objects
        """
        # Select ROW_ORDER based on report type
        if self.config.report_type.value == "GLGROUP":
            from config.row_order_glgroup import ROW_ORDER_GLGROUP
            ROW_ORDER = ROW_ORDER_GLGROUP
            logger.info("Using GLGROUP row order")
        else:
            from config.row_order import ROW_ORDER
            logger.info("Using COSTTYPE row order")
        
        rows = []
        
        for level, label, is_calc, formula, is_bold in ROW_ORDER:
            # Determine color for section headers
            color = None
            if is_bold and level == 0 and label:
                # All section headers use same color (F8CBAD)
                color = self.config.row_colors.get('section_header', 'F8CBAD')
            
            row = RowDef(
                level=level,
                label=label,
                is_calculated=is_calc,
                formula=formula,
                is_bold=is_bold,
                color=color
            )
            rows.append(row)
        
        logger.info(f"Built {len(rows)} rows from ROW_ORDER ({self.config.report_type.value})")
        return rows
    
    def get_data_rows(self, rows: List[RowDef]) -> List[RowDef]:
        """
        Get only data rows (exclude empty rows)
        
        Args:
            rows: List of all rows
        
        Returns:
            List of data rows only
        """
        return [row for row in rows if row.label]
    
    def get_section_headers(self, rows: List[RowDef]) -> List[RowDef]:
        """
        Get only section header rows (level 0, bold)
        
        Args:
            rows: List of all rows
        
        Returns:
            List of section headers
        """
        return [
            row for row in rows 
            if row.label and row.level == 0 and row.is_bold
        ]
    
    def find_row_by_label(self, rows: List[RowDef], label: str) -> RowDef:
        """
        Find row by label
        
        Args:
            rows: List of rows
            label: Label to search for
        
        Returns:
            RowDef if found, None otherwise
        """
        for row in rows:
            if row.label == label:
                return row
        return None

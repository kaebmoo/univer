"""
Remark Writer
Write remarks section at bottom of report
"""
import logging

logger = logging.getLogger(__name__)


class RemarkWriter:
    """Write remarks section"""
    
    def __init__(self, config, formatter):
        """
        Initialize remark writer
        
        Args:
            config: ReportConfig instance
            formatter: CellFormatter instance
        """
        self.config = config
        self.formatter = formatter
    
    def write(self, ws, remark_content: str, start_row: int):
        """
        Write remarks section
        
        Args:
            ws: Worksheet
            remark_content: Remark text content
            start_row: Starting row (0-indexed)
        """
        if not self.config.show_remarks or not remark_content:
            return
        
        col = self.config.start_col
        current_row = start_row
        
        # Title: "หมายเหตุ"
        title_cell = ws.cell(row=current_row + 1, column=col + 1)
        self.formatter.format_remark_cell(
            title_cell,
            "หมายเหตุ:",
            is_title=True
        )
        current_row += 1
        
        # Content lines
        lines = remark_content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            
            cell = ws.cell(row=current_row + 1, column=col + 1)
            self.formatter.format_remark_cell(cell, line, is_title=False)
            current_row += 1
        
        logger.info(f"Wrote remarks section ({len(lines)} lines)")

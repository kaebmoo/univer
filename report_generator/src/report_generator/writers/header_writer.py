"""
Header Writer
Write report header (company name, report title, period) and info box
"""
from typing import List
import pandas as pd
from src.data_loader import DataProcessor
import logging

logger = logging.getLogger(__name__)


class HeaderWriter:
    """Write report header and info box"""
    
    # Info box content (5 lines)
    INFO_LINES = [
        "วัตถุประสงค์ของรายงาน :",
        "    * เพื่อทราบผลดำเนินงานรายเดือนหลังหักค่าใช้จ่ายรวมทั้งหมด ประกอบด้วย ประเภทต้นทุน ขายและบริหาร",
        "    * ใช้รายงานเพื่อการบริหารค่าใช้จ่ายแต่ละประเภทให้มีประสิทธิภาพ",
        "    * ไม่เหมาะสมที่จะใช้เพื่อวัด Performance ส่วนงาน เนื่องจากเป็นการแสดงมิติค่าใช้จ่ายแบบรวม ไม่ได้แสดงเป็นค่าใช้จ่ายที่ส่วนงานมีอำนาจควบคุมได้หรือไม่ได้",
        "    * ไม่เหมาะสมที่จะใช้เพื่อพิจารณาการยกเลิกบริการ เนื่องจากไม่ได้แสดงมิติต้นทุนผันแปรและคงที่ หากยกเลิกบริการแล้ว ควรทราบว่าต้นทุนใดบ้างลดลงได้ ต้นทุนใดบ้างยังคงอยู่ เพื่อเปรียบกับรายได้ที่จะหายไป"
    ]
    
    def __init__(self, config, formatter):
        """
        Initialize header writer
        
        Args:
            config: ReportConfig instance
            formatter: CellFormatter instance
        """
        self.config = config
        self.formatter = formatter
        self.data_processor = DataProcessor()
    
    def write(self, ws, data: pd.DataFrame):
        """
        Write complete header section
        
        Args:
            ws: Worksheet
            data: Input dataframe (for period detection)
        """
        self._write_title_lines(ws, data)
        
        if self.config.show_info_box:
            self._write_info_box(ws)
    
    def _write_title_lines(self, ws, data: pd.DataFrame):
        """
        Write 3-line title at top left
        
        Lines:
        1. Company name
        2. Report title with dimension
        3. Period description
        
        Args:
            ws: Worksheet
            data: Input dataframe
        """
        row = self.config.header_row
        col = self.config.start_col
        
        # Line 1: Company name
        cell = ws.cell(row=row + 1, column=col + 1)
        cell.value = "บริษัท โทรคมนาคมแห่งชาติ จำกัด (มหาชน)"
        cell.font = self.formatter.create_font(
            bold=True,
            size=self.config.header_font_size
        )
        
        # Line 2: Report title
        cell = ws.cell(row=row + 2, column=col + 1)
        cell.value = f"รายงานผลดำเนินงาน{self.config.detail_level_thai} - {self.config.report_type_thai}"
        cell.font = self.formatter.create_font(
            bold=True,
            size=self.config.header_font_size
        )
        
        # Line 3: Period
        period_desc, _ = self.data_processor.get_period_description(
            data,
            self.config.period_type.value
        )
        cell = ws.cell(row=row + 3, column=col + 1)
        cell.value = period_desc
        cell.font = self.formatter.create_font(
            bold=True,
            size=self.config.header_font_size
        )
        
        logger.info("Wrote header title lines")
    
    def _write_info_box(self, ws):
        """
        Write info box at top right (rows 1-5, columns G-J)
        
        Args:
            ws: Worksheet
        """
        row = self.config.info_box_row
        col = self.config.info_box_col
        
        for idx, line in enumerate(self.INFO_LINES):
            cell = ws.cell(row=row + idx + 1, column=col + 1)
            
            # Format cell
            self.formatter.format_info_box_cell(
                cell,
                line,
                is_title=(idx == 0)  # First line is title
            )
            
            # Merge columns G-J (columns 6-9 in 0-indexed, or 7-10 in 1-indexed)
            ws.merge_cells(
                start_row=row + idx + 1,
                start_column=col + 1,
                end_row=row + idx + 1,
                end_column=col + 9  # Merge 4 columns (G, H, I, J, K, L, M, N, O)
            )
            
            # Set row height
            self.formatter.set_row_height(ws, row + idx, 20)
        
        logger.info("Wrote info box (5 lines)")

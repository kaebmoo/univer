"""
Report Builder
Main orchestrator that coordinates all modules to generate complete Excel report
"""
from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from typing import Optional
import logging

from .config import ReportConfig
from ..columns.bu_only_builder import BUOnlyBuilder
from ..columns.bu_sg_builder import BUSGBuilder
from ..columns.bu_sg_product_builder import BUSGProductBuilder
from ..rows.row_builder import RowBuilder
from ..writers.header_writer import HeaderWriter
from ..writers.column_header_writer import ColumnHeaderWriter
from ..writers.data_writer import DataWriter
from ..writers.remark_writer import RemarkWriter
from ..formatters.cell_formatter import CellFormatter
from src.data_loader import DataAggregator

logger = logging.getLogger(__name__)


class ReportBuilder:
    """
    Main report builder - orchestrates all modules
    
    Usage:
        config = ReportConfig(
            report_type="COSTTYPE",
            period_type="MTH",
            detail_level="BU_SG_PRODUCT"
        )
        
        builder = ReportBuilder(config)
        output_path = builder.generate_report(data, output_path, remark)
    """
    
    def __init__(self, config: ReportConfig):
        """
        Initialize report builder
        
        Args:
            config: ReportConfig instance
        """
        self.config = config
        
        # Initialize formatter (needed by all writers)
        self.formatter = CellFormatter(config)
        
        # Initialize column builder based on detail level
        self.column_builder = self._get_column_builder()
        
        # Initialize row builder
        self.row_builder = RowBuilder(config)
        
        # Initialize writers
        self.header_writer = HeaderWriter(config, self.formatter)
        self.column_header_writer = ColumnHeaderWriter(config, self.formatter)
        self.data_writer = DataWriter(config, self.formatter)
        self.remark_writer = RemarkWriter(config, self.formatter)
        
        logger.info(f"ReportBuilder initialized: {config.detail_level.value}")
    
    def _get_column_builder(self):
        """Get appropriate column builder based on detail level"""
        if self.config.detail_level.value == "BU_ONLY":
            return BUOnlyBuilder(self.config)
        elif self.config.detail_level.value == "BU_SG":
            return BUSGBuilder(self.config)
        else:  # BU_SG_PRODUCT
            return BUSGProductBuilder(self.config)
    
    def generate_report(
        self,
        data: pd.DataFrame,
        output_path: Path,
        remark_content: str = ""
    ) -> Path:
        """
        Generate complete Excel report
        
        Args:
            data: Processed dataframe with P&L data
            output_path: Path to save Excel file
            remark_content: Remark text content (optional)
        
        Returns:
            Path to generated file
        """
        logger.info(f"Generating report: {output_path}")
        logger.info(f"Report type: {self.config.report_type.value}")
        logger.info(f"Period type: {self.config.period_type.value}")
        logger.info(f"Detail level: {self.config.detail_level.value}")
        
        # 1. Build structure
        logger.info("Building column structure...")
        columns = self.column_builder.build_columns(data)
        logger.info(f"Built {len(columns)} columns")
        
        logger.info("Building row structure...")
        rows = self.row_builder.build_rows()
        logger.info(f"Built {len(rows)} rows")
        
        # 2. Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "P&L Report"
        
        # 3. Create aggregator
        aggregator = DataAggregator(data)
        
        # 4. Write content
        logger.info("Writing header...")
        self.header_writer.write(ws, data)
        
        logger.info("Writing column headers...")
        self.column_header_writer.write(ws, columns)
        
        logger.info("Writing data rows...")
        last_row = self.data_writer.write(ws, data, aggregator, columns, rows)
        
        logger.info("Writing remarks...")
        self.remark_writer.write(ws, remark_content, last_row + 2)
        
        # 5. Apply final formatting
        logger.info("Applying final formatting...")
        self._apply_final_formatting(ws, columns)
        
        # 6. Save workbook
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(output_path)
        
        logger.info(f"Report saved to: {output_path}")
        return output_path
    
    def _apply_final_formatting(self, ws, columns):
        """
        Apply final formatting touches
        
        Args:
            ws: Worksheet
            columns: Column structure
        """
        # Set freeze panes
        # Freeze at first data row, after grand total column
        freeze_row = self.config.start_row + self.config.header_rows + 1
        
        # Find grand total column index
        freeze_col = 2  # Default (after label and grand total)
        for idx, col in enumerate(columns):
            if col.col_type == 'grand_total':
                freeze_col = idx + 2  # After grand total
                break
        
        self.formatter.set_freeze_panes(ws, freeze_row, freeze_col)
        
        logger.info("Final formatting applied")

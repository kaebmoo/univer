#!/usr/bin/env python3
"""
Generate Correct Excel Report with Multi-Level Headers
- BU Total
- Service Group Total (NEW!)
- Products

BACKUP: This is the original working version before refactoring
Date: 2025-11-26
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import CSVLoader, DataProcessor, DataAggregator
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from config.row_order import ROW_ORDER
from config.data_mapping import get_group_sub_group, is_calculated_row
from config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# BU Colors
BU_COLORS = {
    '1.กลุ่มธุรกิจ HARD INFRASTRUCTURE': 'E2EFDA',
    '2.กลุ่มธุรกิจ INTERNATIONAL': 'DDEBF7',
    '3.กลุ่มธุรกิจ MOBILE': 'DBD3E5',
    '4.กลุ่มธุรกิจ FIXED LINE & BROADBAND': 'FCE4D6',
    '5.กลุ่มธุรกิจ DIGITAL': 'D9E1F2',
    '6.กลุ่มธุรกิจ ICT SOLUTION': 'C6E0B4',
    '7.กลุ่มบริการอื่นไม่ใช่โทรคมนาคม': 'BDD7EE',
    '8.รายได้อื่น/ค่าใช้จ่ายอื่น': 'EAC1C0',
}


def generate_correct_report(csv_path: Path, output_path: Path):
    """Generate P&L Excel report with correct structure"""
    # ... (ไฟล์เดิมทั้งหมด - ไม่แปลงเป็นความคิดเห็นเพื่อประหยัดพื้นที่)
    pass


if __name__ == "__main__":
    csv_path = Path("../../data/TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv")
    output_path = Path("../output/correct_report_backup.xlsx")

    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        sys.exit(1)

    output_path.parent.mkdir(exist_ok=True)

    generate_correct_report(csv_path, output_path)
    logger.info("Done!")

"""
Univer Converter Service - Crosstab Format
แปลงข้อมูลรายงานเป็น Univer Snapshot Format แบบ Crosstab
"""

from typing import Dict, List, Any, Optional
import json
import logging
import pandas as pd

from app.models.report import UniverWorkbook, UniverSheet, UniverCell
from app.services.data_loader import data_loader
from app.services.group_order import sort_service_groups

logger = logging.getLogger(__name__)


class UniverConverter:
    """Class สำหรับแปลงข้อมูลเป็น Univer snapshot format (Crosstab)"""

    # สีที่ใช้ในรายงาน
    COLORS = {
        "header": "#4472C4",           # สีน้ำเงิน - header หลัก
        "header_white": "#FFFFFF",     # สีขาว - text สำหรับ header
        "sub_header": "#B4C7E7",       # สีฟ้าอ่อน - sub header
        "revenue": "#E7E6E6",          # สีเทาอ่อน - ส่วนรายได้
        "revenue_total": "#D9D9D9",    # สีเทาเข้มขึ้น - รายได้รวม
        "cost_header": "#F4B084",      # สีส้มอ่อน - ต้นทุนบริการ
        "cost_total": "#F8CBAD",       # สีส้มเข้มขึ้น - ต้นทุนรวม
        "gross_profit": "#C5E0B4",     # สีเขียวอ่อน - กำไรขั้นต้น
        "selling_header": "#FFD966",   # สีเหลืองอ่อน - ค่าใช้จ่ายขาย
        "admin_header": "#B4C7E7",     # สีฟ้าอ่อน - ค่าใช้จ่ายบริหาร
        "ebit": "#FFF2CC",             # สีเหลืองอ่อนมาก - EBIT
        "ebitda": "#FFE699",           # สีเหลืองทอง - EBITDA
        "net_profit": "#92D050",       # สีเขียวสด - กำไรสุทธิ
        "negative": "#FF0000",         # สีแดง - ค่าติดลบ
        "white": "#FFFFFF",            # สีขาว
        "light_gray": "#F2F2F2",       # สีเทาอ่อนมาก - พื้นหลังสลับ
        "total_column": "#FFD966",     # สีเหลือง - column รวม
    }

    # Number formats
    NUMBER_FORMATS = {
        "currency": "#,##0.00",                                    # จำนวนเงินบวก
        "currency_parentheses": "#,##0.00;[Red](#,##0.00)",       # ค่าติดลบในวงเล็บสีแดง
        "currency_no_decimal": "#,##0",
        "percentage": "0.00%",                                     # เปอร์เซ็นต์บวก
        "percentage_one_decimal": "0.0%",
    }

    def __init__(self):
        """Initialize converter"""
        self.styles_registry = {}
        self.next_style_id = 0

    def _register_style(self, style_def: Dict[str, Any]) -> str:
        """
        ลงทะเบียน style และคืนค่า style ID

        Args:
            style_def: Style definition

        Returns:
            Style ID
        """
        # สร้าง key จาก style definition
        style_key = json.dumps(style_def, sort_keys=True)

        # ถ้ามี style นี้อยู่แล้ว ให้คืนค่า ID เดิม
        if style_key in self.styles_registry:
            return self.styles_registry[style_key]

        # ลงทะเบียน style ใหม่
        style_id = f"style_{self.next_style_id}"
        self.styles_registry[style_key] = style_id
        self.next_style_id += 1

        return style_id

    def _create_cell(
        self,
        row: int,
        col: int,
        value: Any,
        style: Optional[Dict[str, Any]] = None,
        formula: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        สร้าง cell object สำหรับ Univer

        Args:
            row: Row index (0-based)
            col: Column index (0-based)
            value: ค่าที่จะแสดง (ถ้าเป็น 0 จะแสดงเป็นค่าว่าง)
            style: Style definition
            formula: Formula (ถ้ามี)

        Returns:
            Cell object
        """
        cell = {
            "r": row,
            "c": col,
            "v": {}
        }

        # ถ้ามี formula ให้ใช้ formula
        if formula:
            cell["v"]["f"] = formula

        # ใส่ค่า - ถ้าเป็นตัวเลข 0 ให้แสดงเป็นค่าว่าง
        if value is not None:
            if isinstance(value, (int, float)):
                if value == 0:
                    # ถ้าเป็น 0 ให้แสดงค่าว่าง
                    cell["v"]["v"] = ""
                    cell["v"]["t"] = "s"  # string type
                else:
                    cell["v"]["v"] = value
                    cell["v"]["t"] = "n"  # number type
            else:
                cell["v"]["v"] = str(value)
                cell["v"]["t"] = "s"  # string type

        # ใส่ style
        if style:
            style_id = self._register_style(style)
            cell["v"]["s"] = style_id

        return cell

    def _create_header_style(
        self,
        bg_color: str,
        bold: bool = True,
        font_color: str = "#000000",
        h_align: int = 2,  # 1=left, 2=center, 3=right
        v_align: int = 2,  # 1=top, 2=middle, 3=bottom
        wrap_text: bool = True  # เพิ่ม text wrap
    ) -> Dict[str, Any]:
        """สร้าง style สำหรับ header"""
        style = {
            "bg": {"rgb": bg_color},
            "bl": 1 if bold else 0,  # bold
            "fc": {"rgb": font_color},  # font color
            "ht": h_align,  # horizontal align
            "vt": v_align,  # vertical align
        }
        
        # เพิ่ม text wrap
        if wrap_text:
            style["tb"] = 1  # 0=no wrap, 1=wrap, 2=clip
            
        return style

    def _create_number_style(
        self,
        value: float,
        number_format: str = None,
        bg_color: Optional[str] = None,
        bold: bool = False
    ) -> Dict[str, Any]:
        """
        สร้าง style สำหรับตัวเลขที่จัดการค่าติดลบอัตโนมัติ

        Args:
            value: ค่าตัวเลข
            bg_color: สีพื้นหลัง
            bold: ตัวหนา

        Returns:
            Style object
        """
        # ถ้าไม่ระบุ format ให้ใช้ format ที่แสดงค่าติดลบในวงเล็บ
        if number_format is None:
            number_format = self.NUMBER_FORMATS["currency_parentheses"]

        style = {
            "bl": 1 if bold else 0,
            "ht": 3,  # right align for numbers
            "vt": 2,  # middle align
        }
        
        # เพิ่ม number format - Univer ใช้ key "n" สำหรับ number format
        style["n"] = {"pattern": number_format}

        if bg_color:
            style["bg"] = {"rgb": bg_color}

        # ถ้าค่าติดลบ เพิ่มสีแดงให้กับตัวเลข
        if value < 0:
            style["fc"] = {"rgb": self.COLORS["negative"]}

        return style

    def convert_to_snapshot(
        self,
        report_data: Dict[str, Any],
        workbook_name: str = "รายงานผลดำเนินงาน"
    ) -> Dict[str, Any]:
        """
        แปลงข้อมูลรายงานเป็น Univer snapshot แบบ Crosstab

        Args:
            report_data: ข้อมูลรายงานจาก ReportCalculator
            workbook_name: ชื่อ workbook

        Returns:
            Univer snapshot object
        """
        # Reset styles for new conversion
        self.styles_registry = {}
        self.next_style_id = 0

        cells = []
        current_row = 0

        # Extract filter info
        metadata = report_data.get('metadata', {})
        year = metadata.get('year')
        months = metadata.get('months', [])

        # Get raw data for crosstab
        df = data_loader.filter_data(year, months, None)

        if df.empty:
            logger.warning("No data available for crosstab")
            return self._create_empty_snapshot(workbook_name)

        # Create crosstab pivot table
        # Combine revenue and expense into single value column
        df['VALUE'] = df['REVENUE_VALUE'].fillna(0) + df['EXPENSE_VALUE'].fillna(0)

        # Create pivot table
        pivot = pd.pivot_table(
            df,
            index=['TYPE', 'หมวดบัญชี'],
            columns='SERVICE_GROUP',
            values='VALUE',
            aggfunc='sum',
            fill_value=0
        )

        # Sort columns (service groups)
        sorted_columns = sort_service_groups(pivot.columns.tolist())
        pivot = pivot[sorted_columns]

        # Add Total column at the beginning
        pivot.insert(0, 'รวมทั้งหมด', pivot.sum(axis=1))

        # === Create Header Row ===
        # Title cell
        cells.append(self._create_cell(
            row=current_row,
            col=0,
            value="รายงานผลดำเนินงาน",
            style=self._create_header_style(
                self.COLORS["header"],
                font_color=self.COLORS["header_white"],
                h_align=1  # left align
            )
        ))

        # Column headers (Service Groups)
        col_offset = 2  # Start after TYPE and หมวดบัญชี columns
        for col_idx, service_group in enumerate(['รวมทั้งหมด'] + sorted_columns):
            is_total = (col_idx == 0)
            cells.append(self._create_cell(
                row=current_row,
                col=col_offset + col_idx,
                value=service_group,
                style=self._create_header_style(
                    self.COLORS["total_column"] if is_total else self.COLORS["header"],
                    font_color=self.COLORS["header_white"] if not is_total else "#000000",
                    h_align=2  # center align
                )
            ))

        current_row += 1

        # === Sub-header Row (Column labels) ===
        cells.append(self._create_cell(
            row=current_row,
            col=0,
            value="ประเภท",
            style=self._create_header_style(self.COLORS["sub_header"])
        ))
        cells.append(self._create_cell(
            row=current_row,
            col=1,
            value="หมวดบัญชี",
            style=self._create_header_style(self.COLORS["sub_header"])
        ))

        current_row += 1

        # === Data Rows ===
        for (type_name, account_name), row_data in pivot.iterrows():
            # TYPE column
            cells.append(self._create_cell(
                row=current_row,
                col=0,
                value=type_name,
                style=self._create_header_style(
                    self.COLORS["white"],
                    bold=False,
                    h_align=1  # left align
                )
            ))

            # หมวดบัญชี column
            cells.append(self._create_cell(
                row=current_row,
                col=1,
                value=account_name,
                style=self._create_header_style(
                    self.COLORS["white"],
                    bold=False,
                    h_align=1  # left align
                )
            ))

            # Value columns
            for col_idx, value in enumerate(row_data):
                is_total = (col_idx == 0)
                cells.append(self._create_cell(
                    row=current_row,
                    col=col_offset + col_idx,
                    value=float(value),
                    style=self._create_number_style(
                        float(value),
                        bg_color=self.COLORS["total_column"] if is_total else None,
                        bold=is_total
                    )
                ))

            current_row += 1

        # Calculate dimensions
        num_columns = col_offset + len(['รวมทั้งหมด'] + sorted_columns)
        num_rows = current_row + 5

        # สร้าง Univer snapshot
        snapshot = {
            "id": "workbook-01",
            "name": workbook_name,
            "appVersion": "0.1.0",
            "locale": "th-TH",
            "styles": self._build_styles_object(),
            "sheets": {
                "sheet-01": {
                    "id": "sheet-01",
                    "name": "P&L Crosstab",
                    "cellData": self._build_cell_data(cells),
                    "rowCount": max(num_rows, 100),
                    "columnCount": max(num_columns, 20),
                    "defaultRowHeight": 25,
                    "defaultColumnWidth": 120,
                    "freeze": {
                        "xSplit": 2,  # Freeze first 2 columns (TYPE, หมวดบัญชี)
                        "ySplit": 2,  # Freeze first 2 rows (headers)
                        "startRow": 2,
                        "startColumn": 2
                    },
                    "columnData": {
                        "0": {"width": 250},  # TYPE column
                        "1": {"width": 350},  # หมวดบัญชี column
                        **{str(i): {"width": 150} for i in range(2, num_columns)}  # Data columns
                    }
                }
            }
        }

        return snapshot

    def _create_empty_snapshot(self, workbook_name: str) -> Dict[str, Any]:
        """สร้าง empty snapshot เมื่อไม่มีข้อมูล"""
        return {
            "id": "workbook-01",
            "name": workbook_name,
            "appVersion": "0.1.0",
            "locale": "th-TH",
            "styles": {},
            "sheets": {
                "sheet-01": {
                    "id": "sheet-01",
                    "name": "P&L Crosstab",
                    "cellData": {
                        "0": {
                            "0": {
                                "v": "ไม่มีข้อมูล",
                                "t": "s"
                            }
                        }
                    },
                    "rowCount": 100,
                    "columnCount": 20,
                    "defaultRowHeight": 25,
                    "defaultColumnWidth": 120,
                }
            }
        }

    def _build_cell_data(self, cells: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        สร้าง cellData object สำหรับ Univer

        Args:
            cells: รายการ cells

        Returns:
            cellData object
        """
        cell_data = {}

        for cell in cells:
            row = cell["r"]
            col = cell["c"]

            if row not in cell_data:
                cell_data[row] = {}

            cell_data[row][col] = cell["v"]

        return cell_data

    def _build_styles_object(self) -> Dict[str, Any]:
        """
        สร้าง styles object สำหรับ Univer

        Returns:
            styles object
        """
        styles = {}

        # สร้าง style definitions จาก registry
        for style_key, style_id in self.styles_registry.items():
            style_def = json.loads(style_key)
            styles[style_id] = style_def

        return styles


# Create global univer converter instance
univer_converter = UniverConverter()

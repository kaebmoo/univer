"""
Enhanced Univer Converter - Crosstab Format
แปลงข้อมูลรายงานเป็น Univer Snapshot แบบ Crosstab ตาม PDF Report
"""

from typing import Dict, List, Any, Optional, Tuple
import json
import logging
import pandas as pd

from app.services.data_loader import data_loader

logger = logging.getLogger(__name__)


class UniverConverterCrosstab:
    """Class สำหรับแปลงข้อมูลเป็น Univer snapshot format แบบ Crosstab"""

    # สีที่ใช้ในรายงาน (ตาม PDF)
    COLORS = {
        "header_main": "#4472C4",      # สีน้ำเงินเข้ม - header หลัก
        "header_text": "#FFFFFF",       # สีขาว - text ใน header
        "revenue_header": "#E7E6E6",    # สีเทาอ่อน - ส่วนรายได้
        "revenue_total": "#D9D9D9",     # สีเทา - รายได้รวม
        "cost_header": "#F4B084",       # สีส้มอ่อน - ต้นทุนบริการ
        "selling_header": "#FFD966",    # สีเหลือง - ค่าใช้จ่ายขาย
        "admin_header": "#B4C7E7",      # สีฟ้าอ่อน - ค่าใช้จ่ายบริหาร
        "gross_profit": "#C5E0B4",      # สีเขียวอ่อน - กำไรขั้นต้น
        "ebit": "#FFF2CC",              # สีเหลืองอ่อน - EBIT
        "net_profit": "#92D050",        # สีเขียวสด - กำไรสุทธิ
        "negative": "#FF0000",          # สีแดง - ค่าติดลบ
        "white": "#FFFFFF",             # สีขาว
        "light_gray": "#F2F2F2",        # สีเทาอ่อน - สลับแถว
    }

    # Number formats
    NUMBER_FORMATS = {
        "currency": "#,##0.00",
        "currency_negative": "#,##0.00;[Red](#,##0.00)",  # บวก: comma separated, ลบ: วงเล็บแดง
        "percentage": "0.00%",
    }

    # TYPE prefixes for display (01=รายได้, 02=ต้นทุนบริการ, etc.)
    TYPE_DISPLAY = {
        "รายได้": "01 รายได้",
        "ต้นทุนบริการ": "02 ต้นทุนบริการ",
        "ค่าใช้จ่ายขายและการตลาด": "03 ค่าใช้จ่ายขายและการตลาด",
        "ค่าใช้จ่ายสนับสนุน": "04 ค่าใช้จ่ายสนับสนุน",
        "ค่าใช้จ่ายอื่น": "05 ค่าใช้จ่ายอื่น",
    }

    def __init__(self):
        """Initialize converter"""
        self.styles_registry = {}
        self.next_style_id = 0

    def _register_style(self, style_def: Dict[str, Any]) -> str:
        """ลงทะเบียน style และคืนค่า style ID"""
        style_key = json.dumps(style_def, sort_keys=True)
        if style_key in self.styles_registry:
            return self.styles_registry[style_key]

        style_id = f"style_{self.next_style_id}"
        self.styles_registry[style_key] = style_id
        self.next_style_id += 1
        return style_id

    def _create_cell(
        self,
        row: int,
        col: int,
        value: Any,
        style: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """สร้าง cell object สำหรับ Univer"""
        cell = {
            "r": row,
            "c": col,
            "v": {}
        }

        # Set value - ไม่มี manual check สำหรับ 0 ให้ number format จัดการเอง
        if isinstance(value, (int, float)):
            # Round เพื่อป้องกัน floating point errors เช่น -1.4E-14
            rounded_value = round(value, 10)  # ปัดเศษที่ทศนิยม 10 ตำแหน่ง
            if abs(rounded_value) < 1e-9:  # ถ้าใกล้ 0 มากๆ ให้เป็น 0
                rounded_value = 0
            cell["v"]["v"] = rounded_value
            cell["v"]["t"] = "n"  # number type (string "n" ตามมาตรฐาน Univer)
        elif value is not None:
            cell["v"]["v"] = str(value)
            cell["v"]["t"] = "s"  # string type (string "s" ตามมาตรฐาน Univer)

        # Set style
        if style:
            style_id = self._register_style(style)
            cell["v"]["s"] = style_id

        return cell

    def _create_header_style(
        self,
        bg_color: str,
        bold: bool = True,
        font_color: str = "#000000",
        align_center: bool = True,
        wrap_text: bool = True  # เพิ่ม text wrap parameter
    ) -> Dict[str, Any]:
        """สร้าง style สำหรับ header"""
        style = {
            "bg": {"rgb": bg_color},
            "bl": 1 if bold else 0,
            "fc": {"rgb": font_color},
        }
        if align_center:
            style["ht"] = 2  # horizontal align: center
            style["vt"] = 2  # vertical align: middle
        
        # เพิ่ม text wrap
        if wrap_text:
            style["tb"] = 1  # 1 = wrap text, 0 = no wrap
        
        return style

    def _create_number_style(
        self,
        value: float,
        bg_color: Optional[str] = None,
        bold: bool = False
    ) -> Dict[str, Any]:
        """สร้าง style สำหรับตัวเลข (จัดการค่าติดลบอัตโนมัติ)"""
        style = {
            "n": {"pattern": self.NUMBER_FORMATS["currency_negative"]},
            "bl": 1 if bold else 0,
            "ht": 3,  # horizontal align: right
            "vt": 2,  # vertical align: middle
        }

        if bg_color:
            style["bg"] = {"rgb": bg_color}

        # Note: สีแดงสำหรับค่าลบจะถูกกำหนดโดย [Red] ใน pattern แล้ว
        # ไม่ต้องตั้ง fc แยกเพราะจะทับกัน

        return style

    def create_crosstab_data(
        self,
        year: int,
        months: List[int],
        business_groups: Optional[List[str]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        สร้างข้อมูล Crosstab สำหรับรายงาน P&L

        Returns:
            Dict containing:
            - revenue_crosstab: รายได้แยกตาม Business Group
            - cost_crosstab: ต้นทุนบริการ
            - selling_crosstab: ค่าใช้จ่ายขาย
            - admin_crosstab: ค่าใช้จ่ายบริหาร
            - business_groups: รายการ Business Groups
        """
        # Load data
        df = data_loader.filter_data(year, months, business_groups)

        # Define business group order (ตามลำดับที่ต้องการแสดง)
        all_bgs = df['BUSINESS_GROUP'].unique()
        business_group_order = [
            'Hard Infrastructure',
            'Fixed Line & Broadband',
            'Mobile',
            'International',
            'Digital',
            'ICT Solution',
            'กลุ่มบริการอื่นไม่ใช่โทรคมนาคม',
            'รายได้อื่น',
        ]
        # เอาเฉพาะที่มีในข้อมูลจริง
        business_groups_list = [bg for bg in business_group_order if bg in all_bgs]

        # สร้าง crosstab สำหรับรายได้
        df_revenue = df[df['TYPE'] == 'รายได้'].copy()
        revenue_crosstab = pd.pivot_table(
            df_revenue,
            index='หมวดบัญชี',
            columns='BUSINESS_GROUP',
            values='AMOUNT',
            aggfunc='sum',
            fill_value=0,
            observed=True
        )
        # Filter เอาเฉพาะ R categories และ reorder columns
        revenue_crosstab = revenue_crosstab[
            [col for col in business_groups_list if col in revenue_crosstab.columns]
        ]
        revenue_crosstab = revenue_crosstab[
            revenue_crosstab.index.str.startswith('R', na=False)
        ]

        # Fix floating point errors
        revenue_crosstab = revenue_crosstab.round(10)
        revenue_crosstab = revenue_crosstab.applymap(lambda x: 0 if abs(x) < 1e-9 else x)

        # สร้าง crosstab สำหรับต้นทุนบริการ
        df_cost = df[df['TYPE'] == 'ต้นทุนบริการ'].copy()
        cost_crosstab = self._create_cost_crosstab(df_cost, business_groups_list)

        # สร้าง crosstab สำหรับค่าใช้จ่ายขาย
        df_selling = df[df['TYPE'] == 'ค่าใช้จ่ายขายและการตลาด'].copy()
        selling_crosstab = self._create_cost_crosstab(df_selling, business_groups_list)

        # สร้าง crosstab สำหรับค่าใช้จ่ายบริหาร
        df_admin = df[df['TYPE'] == 'ค่าใช้จ่ายสนับสนุน'].copy()
        admin_crosstab = self._create_cost_crosstab(df_admin, business_groups_list)

        return {
            'revenue_crosstab': revenue_crosstab,
            'cost_crosstab': cost_crosstab,
            'selling_crosstab': selling_crosstab,
            'admin_crosstab': admin_crosstab,
            'business_groups': business_groups_list,
        }

    def _create_cost_crosstab(
        self,
        df: pd.DataFrame,
        business_groups_list: List[str]
    ) -> pd.DataFrame:
        """สร้าง crosstab สำหรับต้นทุน/ค่าใช้จ่าย"""
        if df.empty:
            # Return empty dataframe with correct structure
            return pd.DataFrame(
                0,
                index=[],
                columns=business_groups_list
            )

        crosstab = pd.pivot_table(
            df,
            index='หมวดบัญชี',
            columns='BUSINESS_GROUP',
            values='AMOUNT',
            aggfunc='sum',
            fill_value=0,
            observed=True
        )

        # Reorder columns และเพิ่ม missing columns
        result = pd.DataFrame(0, index=crosstab.index, columns=business_groups_list)
        for col in crosstab.columns:
            if col in result.columns:
                result[col] = crosstab[col]

        # Fix floating point errors - round และเปลี่ยนค่าที่ใกล้ 0 ให้เป็น 0
        result = result.round(10)  # ปัดเศษที่ทศนิยม 10 ตำแหน่ง
        result = result.applymap(lambda x: 0 if abs(x) < 1e-9 else x)  # ค่าใกล้ 0 ให้เป็น 0

        # Filter เอาเฉพาะ C categories
        result = result[result.index.str.startswith('C', na=False)]

        return result

    def convert_to_snapshot(
        self,
        year: int,
        months: List[int],
        business_groups: Optional[List[str]] = None,
        workbook_name: str = "รายงานผลดำเนินงาน"
    ) -> Dict[str, Any]:
        """
        แปลงข้อมูลรายงานเป็น Univer snapshot แบบ Crosstab

        Args:
            year: ปี
            months: รายการเดือน
            business_groups: รายการกลุ่มธุรกิจ (None = ทั้งหมด)
            workbook_name: ชื่อ workbook

        Returns:
            Univer snapshot object
        """
        # Reset styles for new conversion
        self.styles_registry = {}
        self.next_style_id = 0

        # สร้าง crosstab data
        crosstab_data = self.create_crosstab_data(year, months, business_groups)

        revenue_ct = crosstab_data['revenue_crosstab']
        cost_ct = crosstab_data['cost_crosstab']
        selling_ct = crosstab_data['selling_crosstab']
        admin_ct = crosstab_data['admin_crosstab']
        bgs = crosstab_data['business_groups']

        cells = []
        current_row = 0
        num_cols = len(bgs) + 2  # รายการ + Business Groups + Total

        # === Main Header ===
        cells.append(self._create_cell(
            row=current_row,
            col=0,
            value=f"รายงานผลดำเนินงาน {year} ({len(months)} เดือน)",
            style=self._create_header_style(
                self.COLORS["header_main"],
                font_color=self.COLORS["header_text"]
            )
        ))
        current_row += 2

        # === Column Headers ===
        # รายการ
        cells.append(self._create_cell(
            row=current_row,
            col=0,
            value="รายการ",
            style=self._create_header_style(self.COLORS["header_main"], font_color=self.COLORS["header_text"])
        ))

        # Business Group headers
        for idx, bg in enumerate(bgs):
            cells.append(self._create_cell(
                row=current_row,
                col=idx + 1,
                value=bg,
                style=self._create_header_style(self.COLORS["header_main"], font_color=self.COLORS["header_text"])
            ))

        # Total header
        cells.append(self._create_cell(
            row=current_row,
            col=len(bgs) + 1,
            value="รวม",
            style=self._create_header_style(self.COLORS["header_main"], font_color=self.COLORS["header_text"])
        ))
        current_row += 1

        # === รายได้ (Revenue) Section ===
        current_row = self._add_section(
            cells, current_row, revenue_ct, bgs,
            section_title="01 รายได้",
            header_color=self.COLORS["revenue_header"],
            total_label="รายได้รวม",
            total_color=self.COLORS["revenue_total"]
        )

        # === ต้นทุนบริการ Section ===
        current_row = self._add_section(
            cells, current_row, cost_ct, bgs,
            section_title="02 ต้นทุนบริการ",
            header_color=self.COLORS["cost_header"],
            total_label="ต้นทุนบริการรวม",
            total_color=self.COLORS["cost_header"]
        )

        # === กำไรขั้นต้น (Gross Profit) ===
        current_row = self._add_calculated_row(
            cells, current_row, revenue_ct, cost_ct, bgs,
            label="กำไร(ขาดทุน)ขั้นต้น",
            bg_color=self.COLORS["gross_profit"],
            is_subtraction=True
        )
        current_row += 1

        # === ค่าใช้จ่ายขายและการตลาด Section ===
        current_row = self._add_section(
            cells, current_row, selling_ct, bgs,
            section_title="03 ค่าใช้จ่ายขายและการตลาด",
            header_color=self.COLORS["selling_header"],
            total_label="ค่าใช้จ่ายขายและการตลาดรวม",
            total_color=self.COLORS["selling_header"]
        )

        # === ค่าใช้จ่ายสนับสนุน Section ===
        current_row = self._add_section(
            cells, current_row, admin_ct, bgs,
            section_title="04 ค่าใช้จ่ายสนับสนุน",
            header_color=self.COLORS["admin_header"],
            total_label="ค่าใช้จ่ายสนับสนุนรวม",
            total_color=self.COLORS["admin_header"]
        )

        # Build cellData properly (merge cells in same row)
        cellData = {}
        for cell in cells:
            row_key = str(cell["r"])
            col_key = str(cell["c"])
            if row_key not in cellData:
                cellData[row_key] = {}
            cellData[row_key][col_key] = cell["v"]

        # Build Univer snapshot structure
        snapshot = {
            "id": "workbook-01",
            "name": workbook_name,
            "sheetOrder": ["sheet-01"],
            "sheets": {
                "sheet-01": {
                    "id": "sheet-01",
                    "name": "P&L Report",
                    "cellData": cellData,
                    "rowCount": current_row + 10,
                    "columnCount": num_cols + 5,
                    "defaultRowHeight": 25,
                    "defaultColumnWidth": 120,
                }
            },
            "styles": self._build_styles_object(),
        }

        logger.info(f"Generated Univer crosstab snapshot with {len(cells)} cells, {current_row} rows")

        return snapshot

    def _add_section(
        self,
        cells: List[Dict],
        start_row: int,
        crosstab: pd.DataFrame,
        business_groups: List[str],
        section_title: str,
        header_color: str,
        total_label: str,
        total_color: str
    ) -> int:
        """เพิ่ม section (รายได้/ต้นทุน/ค่าใช้จ่าย) ลงใน cells"""
        current_row = start_row

        # Section header
        cells.append(self._create_cell(
            row=current_row,
            col=0,
            value=section_title,
            style=self._create_header_style(header_color, bold=True)
        ))
        current_row += 1

        # Detail rows
        for category, row_data in crosstab.iterrows():
            # Category name
            cells.append(self._create_cell(
                row=current_row,
                col=0,
                value=f"  {category}"  # Indent
            ))

            # Values for each business group
            row_total = 0
            for idx, bg in enumerate(business_groups):
                value = row_data.get(bg, 0)
                row_total += value
                cells.append(self._create_cell(
                    row=current_row,
                    col=idx + 1,
                    value=value,
                    style=self._create_number_style(value)
                ))

            # Total for this row
            cells.append(self._create_cell(
                row=current_row,
                col=len(business_groups) + 1,
                value=row_total,
                style=self._create_number_style(row_total, bold=True)
            ))
            current_row += 1

        # Section total row
        cells.append(self._create_cell(
            row=current_row,
            col=0,
            value=total_label,
            style=self._create_header_style(total_color, bold=True)
        ))

        # Calculate totals for each business group
        for idx, bg in enumerate(business_groups):
            total = crosstab[bg].sum() if bg in crosstab.columns else 0
            cells.append(self._create_cell(
                row=current_row,
                col=idx + 1,
                value=total,
                style=self._create_number_style(total, bg_color=total_color, bold=True)
            ))

        # Grand total
        grand_total = crosstab.sum().sum()
        cells.append(self._create_cell(
            row=current_row,
            col=len(business_groups) + 1,
            value=grand_total,
            style=self._create_number_style(grand_total, bg_color=total_color, bold=True)
        ))
        current_row += 2

        return current_row

    def _add_calculated_row(
        self,
        cells: List[Dict],
        current_row: int,
        ct1: pd.DataFrame,
        ct2: pd.DataFrame,
        business_groups: List[str],
        label: str,
        bg_color: str,
        is_subtraction: bool = True
    ) -> int:
        """เพิ่มแถวคำนวณ (เช่น กำไรขั้นต้น = รายได้ - ต้นทุน)"""
        cells.append(self._create_cell(
            row=current_row,
            col=0,
            value=label,
            style=self._create_header_style(bg_color, bold=True)
        ))

        grand_total = 0
        for idx, bg in enumerate(business_groups):
            val1 = ct1[bg].sum() if bg in ct1.columns else 0
            val2 = ct2[bg].sum() if bg in ct2.columns else 0
            result = val1 - val2 if is_subtraction else val1 + val2
            grand_total += result

            cells.append(self._create_cell(
                row=current_row,
                col=idx + 1,
                value=result,
                style=self._create_number_style(result, bg_color=bg_color, bold=True)
            ))

        cells.append(self._create_cell(
            row=current_row,
            col=len(business_groups) + 1,
            value=grand_total,
            style=self._create_number_style(grand_total, bg_color=bg_color, bold=True)
        ))

        return current_row + 1

    def _build_styles_object(self) -> Dict[str, Any]:
        """สร้าง styles object สำหรับ Univer"""
        styles = {}
        for style_key, style_id in self.styles_registry.items():
            style_def = json.loads(style_key)
            styles[style_id] = style_def
        return styles


# Create global instance
univer_converter_crosstab = UniverConverterCrosstab()

"""
Univer Converter Service
แปลงข้อมูลรายงานเป็น Univer Snapshot Format
"""

from typing import Dict, List, Any, Optional
import json


class UniverConverter:
    """Class สำหรับแปลงข้อมูลเป็น Univer snapshot format"""

    # สีที่ใช้ในรายงาน
    COLORS = {
        "header": "#4472C4",           # สีน้ำเงิน
        "revenue": "#E7E6E6",          # สีเทาอ่อน
        "cost_header": "#F4B084",      # สีส้มอ่อน
        "gross_profit": "#C5E0B4",     # สีเขียวอ่อน
        "selling_header": "#FFD966",   # สีเหลืองอ่อน
        "admin_header": "#B4C7E7",     # สีฟ้าอ่อน
        "ebit": "#FFFF00",             # สีเหลือง
        "ebitda": "#FFD700",           # สีทอง
        "net_profit": "#00B050",       # สีเขียวเข้ม
        "white": "#FFFFFF",            # สีขาว
    }

    # Number formats
    NUMBER_FORMATS = {
        "currency": "#,##0.00",
        "currency_no_decimal": "#,##0",
        "percentage": "0.00%",
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
            value: ค่าที่จะแสดง
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

        # ใส่ค่า
        if value is not None:
            if isinstance(value, (int, float)):
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
        font_color: str = "#000000"
    ) -> Dict[str, Any]:
        """สร้าง style สำหรับ header"""
        return {
            "bg": {"rgb": bg_color},
            "bl": 1 if bold else 0,  # bold
            "fc": {"rgb": font_color},  # font color
            "ht": 2,  # horizontal align: center
            "vt": 2,  # vertical align: center
        }

    def _create_number_style(
        self,
        number_format: str,
        bg_color: Optional[str] = None,
        bold: bool = False
    ) -> Dict[str, Any]:
        """สร้าง style สำหรับตัวเลข"""
        style = {
            "n": {"pattern": number_format},
            "bl": 1 if bold else 0,
        }

        if bg_color:
            style["bg"] = {"rgb": bg_color}

        return style

    def convert_to_snapshot(
        self,
        report_data: Dict[str, Any],
        workbook_name: str = "รายงานผลดำเนินงาน"
    ) -> Dict[str, Any]:
        """
        แปลงข้อมูลรายงานเป็น Univer snapshot

        Args:
            report_data: ข้อมูลรายงานจาก ReportCalculator
            workbook_name: ชื่อ workbook

        Returns:
            Univer snapshot object
        """
        cells = []
        current_row = 0

        # === Header ===
        cells.append(self._create_cell(
            row=current_row,
            col=0,
            value="รายงานผลดำเนินงาน (Profit & Loss Statement)",
            style=self._create_header_style(self.COLORS["header"], font_color="#FFFFFF")
        ))
        current_row += 2

        # === ส่วนรายได้ ===
        cells.append(self._create_cell(
            row=current_row,
            col=0,
            value="รายได้ (Revenue)",
            style=self._create_header_style(self.COLORS["revenue"])
        ))
        current_row += 1

        # รายละเอียดรายได้
        revenue = report_data['data']['revenue']
        revenue_items = [
            ('กลุ่มธุรกิจโครงสร้างพื้นฐาน', 'Infrastructure'),
            ('กลุ่มธุรกิจโทรศัพท์ประจำที่และอินเตอร์เนตบรอดแบนด์', 'Fixed Line & Broadband'),
            ('กลุ่มธุรกิจโทรศัพท์เคลื่อนที่', 'Mobile'),
            ('กลุ่มธุรกิจวงจรระหว่างประเทศ', 'International Circuit'),
            ('กลุ่มธุรกิจดิจิทัล', 'Digital'),
            ('กลุ่มธุรกิจ ICT Solution Business', 'ICT Solution'),
            ('รายได้จากการให้บริการอื่นที่ไม่ใช่โทรคมนาคม', 'Non-Telecom Service'),
            ('รายได้จากการขาย', 'Sale of Goods'),
        ]

        for label, key in revenue_items:
            cells.append(self._create_cell(
                row=current_row,
                col=0,
                value=f"  {label}",
            ))
            cells.append(self._create_cell(
                row=current_row,
                col=1,
                value=revenue.get(key, 0),
                style=self._create_number_style(self.NUMBER_FORMATS["currency"])
            ))
            current_row += 1

        # รายได้รวม
        cells.append(self._create_cell(
            row=current_row,
            col=0,
            value="รายได้รวม",
            style=self._create_header_style(self.COLORS["revenue"], bold=True)
        ))
        cells.append(self._create_cell(
            row=current_row,
            col=1,
            value=revenue.get('Total', 0),
            style=self._create_number_style(
                self.NUMBER_FORMATS["currency"],
                bg_color=self.COLORS["revenue"],
                bold=True
            )
        ))
        current_row += 2

        # === ส่วนต้นทุนบริการ ===
        cells.append(self._create_cell(
            row=current_row,
            col=0,
            value="ต้นทุนบริการและต้นทุนขาย (Cost of Service)",
            style=self._create_header_style(self.COLORS["cost_header"])
        ))
        current_row += 1

        cost_of_service = report_data['data']['cost_of_service']
        cost_items = [
            'ค่าใช้จ่ายตอบแทนแรงงาน',
            'ค่าสวัสดิการ',
            'ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร',
            'ค่าซ่อมแซมและบำรุงรักษาและวัสดุใช้ไป',
            'ค่าสาธารณูปโภค',
            'ค่าใช้จ่ายเกี่ยวกับการกำกับดูแลของ กสทช.',
            'ค่าส่วนแบ่งบริการโทรคมนาคม',
            'ค่าใช้จ่ายบริการโทรคมนาคม',
            'ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์',
            'ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า',
            'ค่าเช่าและค่าใช้สินทรัพย์',
            'ต้นทุนขาย',
            'ค่าใช้จ่ายบริการอื่น',
            'ค่าใช้จ่ายดำเนินงานอื่น',
        ]

        for item in cost_items:
            cells.append(self._create_cell(
                row=current_row,
                col=0,
                value=f"  {item}",
            ))
            cells.append(self._create_cell(
                row=current_row,
                col=1,
                value=cost_of_service.get(item, 0),
                style=self._create_number_style(self.NUMBER_FORMATS["currency"])
            ))
            current_row += 1

        # ต้นทุนรวม
        cells.append(self._create_cell(
            row=current_row,
            col=0,
            value="ต้นทุนบริการและต้นทุนขายรวม",
            style=self._create_header_style(self.COLORS["cost_header"], bold=True)
        ))
        cells.append(self._create_cell(
            row=current_row,
            col=1,
            value=cost_of_service.get('Total', 0),
            style=self._create_number_style(
                self.NUMBER_FORMATS["currency"],
                bg_color=self.COLORS["cost_header"],
                bold=True
            )
        ))
        current_row += 2

        # === กำไรขั้นต้น ===
        gross_profit = report_data['data']['metrics']['gross_profit']
        cells.append(self._create_cell(
            row=current_row,
            col=0,
            value="กำไร(ขาดทุน)ขั้นต้นจากการดำเนินงาน",
            style=self._create_header_style(self.COLORS["gross_profit"], bold=True)
        ))
        cells.append(self._create_cell(
            row=current_row,
            col=1,
            value=gross_profit,
            style=self._create_number_style(
                self.NUMBER_FORMATS["currency"],
                bg_color=self.COLORS["gross_profit"],
                bold=True
            )
        ))
        current_row += 2

        # === EBIT ===
        ebit = report_data['data']['metrics']['ebit']
        cells.append(self._create_cell(
            row=current_row,
            col=0,
            value="กำไร(ขาดทุน)ก่อนต้นทุนจัดหาเงิน รายได้อื่นและค่าใช้จ่ายอื่น (EBIT)",
            style=self._create_header_style(self.COLORS["ebit"], bold=True)
        ))
        cells.append(self._create_cell(
            row=current_row,
            col=1,
            value=ebit,
            style=self._create_number_style(
                self.NUMBER_FORMATS["currency"],
                bg_color=self.COLORS["ebit"],
                bold=True
            )
        ))
        current_row += 2

        # === EBITDA ===
        if 'ebitda' in report_data['data']['metrics']:
            ebitda = report_data['data']['metrics']['ebitda']
            cells.append(self._create_cell(
                row=current_row,
                col=0,
                value="EBITDA",
                style=self._create_header_style(self.COLORS["ebitda"], bold=True)
            ))
            cells.append(self._create_cell(
                row=current_row,
                col=1,
                value=ebitda,
                style=self._create_number_style(
                    self.NUMBER_FORMATS["currency"],
                    bg_color=self.COLORS["ebitda"],
                    bold=True
                )
            ))
            current_row += 2

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
                    "name": "P&L Report",
                    "cellData": self._build_cell_data(cells),
                    "rowCount": current_row + 10,
                    "columnCount": 10,
                    "defaultRowHeight": 25,
                    "defaultColumnWidth": 120,
                }
            }
        }

        return snapshot

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


# Example usage
if __name__ == "__main__":
    # Mock report data
    report_data = {
        'metadata': {},
        'data': {
            'revenue': {
                'Infrastructure': 100000,
                'Fixed Line & Broadband': 500000,
                'Mobile': 800000,
                'International Circuit': 50000,
                'Digital': 150000,
                'ICT Solution': 200000,
                'Non-Telecom Service': 30000,
                'Sale of Goods': 20000,
                'Total': 1850000
            },
            'cost_of_service': {
                'ค่าใช้จ่ายตอบแทนแรงงาน': 300000,
                'ค่าสวัสดิการ': 50000,
                'Total': 800000
            },
            'metrics': {
                'gross_profit': 1050000,
                'ebit': 500000,
                'ebitda': 650000
            }
        }
    }

    # Create converter
    converter = UniverConverter()

    # Convert to snapshot
    snapshot = converter.convert_to_snapshot(report_data)

    # Save to JSON
    with open('sample_snapshot.json', 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    print("Snapshot created successfully!")
    print(f"Total cells: {len(snapshot['sheets']['sheet-01']['cellData'])}")
    print(f"Total styles: {len(snapshot['styles'])}")

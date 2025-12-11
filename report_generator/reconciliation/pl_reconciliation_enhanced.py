"""
Enhanced P&L Reconciliation Script
====================================
ตรวจสอบความถูกต้องและความสอดคล้องของรายงาน P&L ทุก Sheet
รองรับทั้งรายงานรายเดือน (MTH) และสะสม (YTD)

การตรวจสอบ 3 ระดับ:
1. ความครบถ้วน (Completeness): Source CSV vs Excel Report
2. ความสอดคล้อง (Consistency): Cost Type vs GL Group (ต้องเท่ากัน)
3. ความถูกต้อง (Tie-out): Excel vs Financial Statement (Text)
"""

import pandas as pd
import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# ==========================================
# Configuration Classes
# ==========================================

TOLERANCE = 0.001  # ความคลาดเคลื่อนที่ยอมรับได้

class PeriodType(Enum):
    """ประเภทงวดเวลา"""
    MTH = "MTH"  # รายเดือน
    YTD = "YTD"  # สะสม

class DimensionType(Enum):
    """ประเภทมิติการรายงาน"""
    COST_TYPE = "COST"   # มิติประเภทต้นทุน
    GL_GROUP = "GL"      # มิติหมวดบัญชี

class ValidationMode(Enum):
    """ระดับการตรวจสอบ"""
    BASIC = "basic"              # ตรวจแค่ Net Profit (Phase 1)
    ENHANCED = "enhanced"        # ตรวจ Revenue, Expense, Net Profit + Internal Math (Phase 2)
    COMPREHENSIVE = "comprehensive"  # ตรวจทุกอย่างรวมถึง Drill-Down (Phase 3)

@dataclass
class FileConfig:
    """กำหนดค่าไฟล์สำหรับการตรวจสอบ"""
    period_type: PeriodType
    report_excel: str
    source_cost_csv: str
    source_gl_csv: str
    financial_stmt_txt: str

    # ชื่อ Sheet ในไฟล์ Excel
    sheets: Dict[str, str] = None

    def __post_init__(self):
        if self.sheets is None:
            self.sheets = {
                'cost_biz': 'ต้นทุน_กลุ่มธุรกิจ',
                'cost_service_group': 'ต้นทุน_กลุ่มบริการ',
                'cost_service': 'ต้นทุน_บริการ',
                'gl_biz': 'หมวดบัญชี_กลุ่มธุรกิจ',
                'gl_service_group': 'หมวดบัญชี_กลุ่มบริการ',
                'gl_service': 'หมวดบัญชี_บริการ'
            }

# ==========================================
# Helper Functions
# ==========================================

def parse_thai_number(text) -> float:
    """แปลงข้อความตัวเลขภาษาไทยให้เป็น Float"""
    if pd.isna(text):
        return 0.0
    text = str(text).strip()
    if text == '-' or text == '':
        return 0.0
    # จัดการวงเล็บแทนค่าลบ
    if '(' in text and ')' in text:
        text = '-' + text.replace('(', '').replace(')', '')
    text = text.replace(',', '')
    try:
        return float(text)
    except ValueError:
        return 0.0

def get_val_from_df(df: pd.DataFrame, keywords: List[str], col_index: int = 2) -> Optional[float]:
    """
    ค้นหาตัวเลขใน DataFrame โดยใช้ keywords

    Args:
        df: DataFrame ที่ต้องการค้นหา
        keywords: รายการคำที่ต้องมีในคำอธิบาย (column 1)
        col_index: index ของ column ที่เก็บตัวเลข (default=2 คือ column ที่ 3)

    Returns:
        ตัวเลขที่พบ หรือ None ถ้าไม่พบ
    """
    for i, row in df.iterrows():
        desc = str(row[1])
        if all(k in desc for k in keywords):
            return parse_thai_number(row[col_index])
    return None

def get_text_val(lines: List[str], keywords: List[str], column_index: int = 0) -> Optional[float]:
    """
    ค้นหาตัวเลขในไฟล์ Text

    Args:
        lines: บรรทัดทั้งหมดในไฟล์
        keywords: คำที่ต้องการค้นหา
        column_index: index ของ column ที่ต้องการ (0=รายเดือน, 1=สะสม)

    Returns:
        ตัวเลขที่พบ หรือ None ถ้าไม่พบ
    """
    for line in lines:
        if all(k in line for k in keywords):
            tokens = line.split()
            # หาตัวเลขทั้งหมดในบรรทัด
            numbers = []
            for t in tokens:
                if any(c.isdigit() for c in t):
                    try:
                        num = parse_thai_number(t)
                        if num != 0:  # เพิ่มเงื่อนไขเพื่อกรองเลข 0 ออก
                            numbers.append(num)
                    except:
                        pass

            # คืนค่าตาม column_index ที่ต้องการ
            if len(numbers) > column_index:
                return numbers[column_index]
    return None

# ==========================================
# Data Loading Functions
# ==========================================

def load_excel_sheets(file_path: str, sheets: Dict[str, str]) -> Dict[str, pd.DataFrame]:
    """
    โหลด Sheet ทั้งหมดจากไฟล์ Excel

    Args:
        file_path: path ของไฟล์ Excel
        sheets: dictionary ของ sheet names

    Returns:
        dictionary ของ DataFrames
    """
    print(f"กำลังอ่านข้อมูลจากไฟล์ Excel: {file_path}")
    result = {}
    for key, sheet_name in sheets.items():
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            result[key] = df
            print(f"  ✓ โหลด sheet '{sheet_name}' สำเร็จ ({len(df)} rows)")
        except Exception as e:
            print(f"  ✗ ไม่สามารถโหลด sheet '{sheet_name}': {e}")
            result[key] = None
    return result

def load_csv_source(file_path: str) -> pd.DataFrame:
    """โหลดไฟล์ CSV แหล่งข้อมูล"""
    print(f"กำลังอ่านข้อมูลจากไฟล์ CSV: {file_path}")
    try:
        df = pd.read_csv(file_path, encoding='cp874')
        print(f"  ✓ โหลดสำเร็จ ({len(df)} rows)")
        return df
    except Exception as e:
        print(f"  ✗ ไม่สามารถโหลดไฟล์: {e}")
        return None

def load_text_file(file_path: str) -> List[str]:
    """โหลดไฟล์ Text งบการเงิน"""
    print(f"กำลังอ่านข้อมูลจากไฟล์ Text: {file_path}")
    try:
        with open(file_path, 'r', encoding='cp874') as f:
            lines = f.readlines()
        print(f"  ✓ โหลดสำเร็จ ({len(lines)} lines)")
        return lines
    except Exception as e:
        print(f"  ✗ ไม่สามารถโหลดไฟล์: {e}")
        return None

# ==========================================
# Reconciliation Classes
# ==========================================

@dataclass
class ReconciliationResult:
    """ผลการตรวจสอบแต่ละรายการ"""
    check_name: str
    description: str
    value1: float
    value1_label: str
    value2: float
    value2_label: str
    tolerance: float = 1.0  # ความคลาดเคลื่อนที่ยอมรับได้

    @property
    def difference(self) -> float:
        """ส่วนต่างระหว่างค่าทั้งสอง"""
        return self.value1 - self.value2

    @property
    def is_pass(self) -> bool:
        """ตรวจสอบว่าผ่านหรือไม่"""
        return abs(self.difference) < self.tolerance

    @property
    def status(self) -> str:
        """สถานะการตรวจสอบ"""
        return "✅ PASS" if self.is_pass else "❌ FAIL"

class ReconciliationEngine:
    """Engine สำหรับการตรวจสอบความสอดคล้อง"""

    def __init__(self, config: FileConfig, validation_mode: ValidationMode = ValidationMode.ENHANCED):
        self.config = config
        self.validation_mode = validation_mode
        self.results: List[ReconciliationResult] = []

        # Load ข้อมูลทั้งหมด
        self.excel_sheets = load_excel_sheets(config.report_excel, config.sheets)
        self.source_cost_df = load_csv_source(config.source_cost_csv)
        self.source_gl_df = load_csv_source(config.source_gl_csv)
        self.stmt_lines = load_text_file(config.financial_stmt_txt)

    def extract_values(self) -> Dict[str, float]:
        """
        ดึงค่าทั้งหมดที่จำเป็นสำหรับการตรวจสอบ

        Returns:
            Dictionary ของค่าต่างๆ
        """
        values = {}

        # 1. ค่าจาก Source CSV (Cost Type)
        if self.source_cost_df is not None:
            # รายได้รวม = รายได้บริการ + ผลตอบแทนทางการเงินและรายได้อื่น
            revenue_service = self.source_cost_df[
                self.source_cost_df['GROUP'].str.contains('01.รายได้', na=False, regex=False)
            ]['VALUE'].sum()
            revenue_other = self.source_cost_df[
                self.source_cost_df['GROUP'].str.contains('09.ผลตอบแทนทางการเงินและรายได้อื่น', na=False, regex=False)
            ]['VALUE'].sum()
            values['src_cost_revenue'] = revenue_service + revenue_other

            values['src_cost_expense'] = self.source_cost_df[
                self.source_cost_df['GROUP'].str.contains('ค่าใช้จ่าย|ต้นทุน', na=False)
            ]['VALUE'].sum()
            values['src_cost_net_profit'] = self.source_cost_df[
                self.source_cost_df['GROUP'].str.contains('14.กำไร(ขาดทุน) สุทธิ', na=False, regex=False)
            ]['VALUE'].sum()

        # 2. ค่าจาก Source CSV (GL Group)
        if self.source_gl_df is not None:
            # ใช้เลขนำหน้าเพื่อให้แม่นยำ
            values['src_gl_revenue'] = self.source_gl_df[
                self.source_gl_df['GROUP'].str.contains('01.รายได้', na=False, regex=False)
            ]['VALUE'].sum()
            values['src_gl_expense'] = self.source_gl_df[
                self.source_gl_df['GROUP'].str.contains('02.ค่าใช้จ่าย', na=False, regex=False)
            ]['VALUE'].sum()
            values['src_gl_net_profit'] = self.source_gl_df[
                self.source_gl_df['GROUP'].str.contains('05.กำไร(ขาดทุน) สุทธิ', na=False, regex=False)
            ]['VALUE'].sum()

        # 3. ค่าจาก Excel Report - ทุก Sheet
        sheet_keys = [
            ('cost_biz', 'Cost ธุรกิจ'),
            ('cost_service_group', 'Cost กลุ่มบริการ'),
            ('cost_service', 'Cost บริการ'),
            ('gl_biz', 'GL ธุรกิจ'),
            ('gl_service_group', 'GL กลุ่มบริการ'),
            ('gl_service', 'GL บริการ')
        ]

        for sheet_key, label in sheet_keys:
            df = self.excel_sheets.get(sheet_key)
            if df is not None:
                # รายได้ - ทั้ง Cost Type และ GL Group ต้องใช้ "รวมรายได้" หรือ "รายได้รวม"
                # เพื่อให้เทียบกันได้ (รวมทั้งรายได้บริการ + ผลตอบแทนทางการเงินและรายได้อื่น)
                revenue = get_val_from_df(df, ['รายได้รวม'])
                if revenue is None:
                    revenue = get_val_from_df(df, ['รวมรายได้'])
                if revenue is None:
                    revenue = get_val_from_df(df, ['1', 'รายได้'])
                values[f'rep_{sheet_key}_revenue'] = revenue

                # ค่าใช้จ่าย (รวมต้นทุนทางการเงิน)
                # ต้องหา "ค่าใช้จ่ายรวม (รวมต้นทุนทางการเงิน)" ไม่ใช่ "ค่าใช้จ่ายรวม (ไม่รวมต้นทุนทางการเงิน)"
                expense = get_val_from_df(df, ['ค่าใช้จ่ายรวม (รวมต้นทุนทางการเงิน)'])
                if expense is None:
                    expense = get_val_from_df(df, ['ค่าใช้จ่ายรวม'])
                values[f'rep_{sheet_key}_expense'] = expense

                # ภาษีเงินได้นิติบุคคล
                tax = get_val_from_df(df, ['ภาษีเงินได้นิติบุคคล'])
                if tax is None:
                    tax = get_val_from_df(df, ['13.ภาษีเงินได้นิติบุคคล'])
                values[f'rep_{sheet_key}_tax'] = tax

                # กำไรสุทธิ
                net_profit = get_val_from_df(df, ['กำไร', 'สุทธิ'])
                values[f'rep_{sheet_key}_net_profit'] = net_profit

        # 4. ค่าจาก Financial Statement (Text)
        if self.stmt_lines is not None:
            # เลือก column ตามประเภทงวด: MTH=0, YTD=1
            col_idx = 0 if self.config.period_type == PeriodType.MTH else 1
            values['stmt_revenue'] = get_text_val(self.stmt_lines, ['รายได้', 'รวม'], col_idx)
            values['stmt_expense'] = get_text_val(self.stmt_lines, ['ค่าใช้จ่าย', 'รวม'], col_idx)
            values['stmt_net_profit'] = get_text_val(self.stmt_lines, ['กำไร', 'สุทธิ'], col_idx)

        return values

    def run_all_checks(self):
        """รันการตรวจสอบทั้งหมด"""
        print(f"\n{'='*80}")
        print(f"เริ่มการตรวจสอบ: {self.config.period_type.value} [Mode: {self.validation_mode.value.upper()}]")
        print(f"{'='*80}\n")

        values = self.extract_values()

        # เคลียร์ผลลัพธ์เก่า
        self.results = []

        # ======== ระดับที่ 1: ตรวจสอบความครบถ้วน (Source vs Report) ========
        print("📊 ระดับที่ 1: ตรวจสอบความครบถ้วน (Completeness)")
        print("-" * 80)

        # 1.1 Cost Type dimension
        self._check_completeness_cost_type(values)

        # 1.2 GL Group dimension
        self._check_completeness_gl_group(values)

        # ======== ระดับที่ 2: ตรวจสอบความสอดคล้องระหว่าง Sheet ========
        print("\n🔄 ระดับที่ 2: ตรวจสอบความสอดคล้อง (Cross-Sheet Consistency)")
        print("-" * 80)

        self._check_cross_sheet_consistency(values)

        # Phase 2: ตรวจสอบ Internal Math
        if self.validation_mode in [ValidationMode.ENHANCED, ValidationMode.COMPREHENSIVE]:
            print("\n🧮 ระดับที่ 2d: ตรวจสอบการคำนวณภายใน (Internal Math)")
            print("-" * 80)
            self._check_internal_math(values)

        # ======== ระดับที่ 3: ตรวจสอบ Tie-out กับงบการเงิน ========
        print("\n✓ ระดับที่ 3: ตรวจสอบ Tie-out (Financial Statement)")
        print("-" * 80)

        self._check_financial_tieout(values)

    def _check_completeness_cost_type(self, values: Dict[str, float]):
        """ตรวจสอบความครบถ้วนของมิติ Cost Type"""
        # ตรวจสอบกับแต่ละ sheet (เฉพาะ กลุ่มธุรกิจ เพื่อไม่ให้ซ้ำซ้อน)
        sheet_key = 'cost_biz'

        # ตรวจรายได้ (ใช้ "รายได้บริการ" เพื่อให้ตรงกับ Source CSV ที่นับเฉพาะรายได้จากบริการ)
        revenue_key = f'rep_{sheet_key}_revenue'
        if revenue_key in values and values[revenue_key] is not None and values[revenue_key] > 0:
            self.results.append(ReconciliationResult(
                check_name=f"1.1a Revenue: Source Cost vs Report",
                description=f"รายได้จาก CSV (Cost Type) ต้องตรงกับ Report",
                value1=values.get('src_cost_revenue', 0),
                value1_label="Source CSV (Cost)",
                value2=values.get(revenue_key, 0),
                value2_label=f"Report {sheet_key}",
                tolerance=TOLERANCE  # เพิ่ม tolerance เล็กน้อยเนื่องจากอาจมีการปัดเศษ
            ))

        # ตรวจกำไรสุทธิ
        net_profit_key = f'rep_{sheet_key}_net_profit'
        if net_profit_key in values and values[net_profit_key] is not None:
            self.results.append(ReconciliationResult(
                check_name=f"1.1b Net Profit: Source Cost vs Report",
                description=f"กำไรสุทธิจาก CSV (Cost Type) ต้องตรงกับ Report",
                value1=values.get('src_cost_net_profit', 0),
                value1_label="Source CSV (Cost)",
                value2=values.get(net_profit_key, 0),
                value2_label=f"Report {sheet_key}"
            ))

    def _check_completeness_gl_group(self, values: Dict[str, float]):
        """ตรวจสอบความครบถ้วนของมิติ GL Group"""
        # ตรวจสอบเฉพาะ กลุ่มธุรกิจ เพื่อไม่ให้ซ้ำซ้อน
        sheet_key = 'gl_biz'

        # ตรวจรายได้
        revenue_key = f'rep_{sheet_key}_revenue'
        if revenue_key in values and values[revenue_key] is not None:
            self.results.append(ReconciliationResult(
                check_name=f"1.2a Revenue: Source GL vs Report",
                description=f"รายได้จาก CSV (GL Group) ต้องตรงกับ Report",
                value1=values.get('src_gl_revenue', 0),
                value1_label="Source CSV (GL)",
                value2=values.get(revenue_key, 0),
                value2_label=f"Report {sheet_key}",
                tolerance=TOLERANCE
            ))

        # ตรวจกำไรสุทธิ
        net_profit_key = f'rep_{sheet_key}_net_profit'
        if net_profit_key in values and values[net_profit_key] is not None:
            self.results.append(ReconciliationResult(
                check_name=f"1.2b Net Profit: Source GL vs Report",
                description=f"กำไรสุทธิจาก CSV (GL Group) ต้องตรงกับ Report",
                value1=values.get('src_gl_net_profit', 0),
                value1_label="Source CSV (GL)",
                value2=values.get(net_profit_key, 0),
                value2_label=f"Report {sheet_key}"
            ))

    def _check_cross_sheet_consistency(self, values: Dict[str, float]):
        """ตรวจสอบความสอดคล้องระหว่าง Sheet Cost Type และ GL Group"""
        # เปรียบเทียบระหว่างคู่ที่สอดคล้องกัน
        pairs = [
            ('cost_biz', 'gl_biz', 'กลุ่มธุรกิจ'),
            ('cost_service_group', 'gl_service_group', 'กลุ่มบริการ'),
            ('cost_service', 'gl_service', 'บริการ')
        ]

        for cost_key, gl_key, label in pairs:
            # Phase 2: ตรวจ Revenue (Enhanced mode)
            if self.validation_mode in [ValidationMode.ENHANCED, ValidationMode.COMPREHENSIVE]:
                cost_revenue = values.get(f'rep_{cost_key}_revenue')
                gl_revenue = values.get(f'rep_{gl_key}_revenue')

                if cost_revenue is not None and gl_revenue is not None:
                    self.results.append(ReconciliationResult(
                        check_name=f"2a. Cross-Sheet Revenue: {label}",
                        description=f"รายได้ของ Cost Type ({label}) ต้องเท่ากับ GL Group ({label})",
                        value1=cost_revenue,
                        value1_label=f"Cost Type - {label}",
                        value2=gl_revenue,
                        value2_label=f"GL Group - {label}",
                        tolerance=TOLERANCE
                    ))

            # Phase 2: ตรวจ Expense (Enhanced mode)
            if self.validation_mode in [ValidationMode.ENHANCED, ValidationMode.COMPREHENSIVE]:
                cost_expense = values.get(f'rep_{cost_key}_expense')
                gl_expense = values.get(f'rep_{gl_key}_expense')

                if cost_expense is not None and gl_expense is not None:
                    self.results.append(ReconciliationResult(
                        check_name=f"2b. Cross-Sheet Expense: {label}",
                        description=f"ค่าใช้จ่ายของ Cost Type ({label}) ต้องเท่ากับ GL Group ({label})",
                        value1=cost_expense,
                        value1_label=f"Cost Type - {label}",
                        value2=gl_expense,
                        value2_label=f"GL Group - {label}",
                        tolerance=TOLERANCE
                    ))

            # Phase 1: ตรวจ Net Profit (ทุก mode)
            cost_net_profit = values.get(f'rep_{cost_key}_net_profit')
            gl_net_profit = values.get(f'rep_{gl_key}_net_profit')

            if cost_net_profit is not None and gl_net_profit is not None:
                self.results.append(ReconciliationResult(
                    check_name=f"2c. Cross-Sheet Net Profit: {label}",
                    description=f"กำไรสุทธิของ Cost Type ({label}) ต้องเท่ากับ GL Group ({label})",
                    value1=cost_net_profit,
                    value1_label=f"Cost Type - {label}",
                    value2=gl_net_profit,
                    value2_label=f"GL Group - {label}"
                ))

    def _check_internal_math(self, values: Dict[str, float]):
        """ตรวจสอบการคำนวณภายใน: Revenue - Expense - Tax = Net Profit"""
        if self.validation_mode not in [ValidationMode.ENHANCED, ValidationMode.COMPREHENSIVE]:
            return

        # ตรวจทุก Sheet
        sheet_keys = [
            ('cost_biz', 'Cost Type - กลุ่มธุรกิจ'),
            ('cost_service_group', 'Cost Type - กลุ่มบริการ'),
            ('cost_service', 'Cost Type - บริการ'),
            ('gl_biz', 'GL Group - กลุ่มธุรกิจ'),
            ('gl_service_group', 'GL Group - กลุ่มบริการ'),
            ('gl_service', 'GL Group - บริการ')
        ]

        for sheet_key, label in sheet_keys:
            revenue = values.get(f'rep_{sheet_key}_revenue')
            expense = values.get(f'rep_{sheet_key}_expense')
            tax = values.get(f'rep_{sheet_key}_tax')
            net_profit = values.get(f'rep_{sheet_key}_net_profit')

            if revenue is not None and expense is not None and net_profit is not None:
                # สูตร: รายได้รวม - ค่าใช้จ่ายรวม (รวมต้นทุนทางการเงิน) - ภาษี = กำไรสุทธิ
                # หมายเหตุ: "ค่าใช้จ่ายรวม (รวมต้นทุนทางการเงิน)" ไม่รวมภาษี ต้องหักภาษีแยก
                # ภาษีในรายงานเป็นค่าลบอยู่แล้ว ดังนั้นต้อง "ลบ" ค่าลบ (ลบติดลบเป็นบวก)
                # ตัวอย่าง: Revenue - Expense - (-Tax) = Revenue - Expense + Tax
                tax_amount = tax if tax is not None else 0
                calculated_profit = revenue - abs(expense) - tax_amount  # ลบค่าลบ = บวก

                self.results.append(ReconciliationResult(
                    check_name=f"2d. Internal Math: {label}",
                    description=f"Revenue - Expense - Tax = Net Profit ใน {label}",
                    value1=calculated_profit,
                    value1_label="Revenue - Expense - Tax",
                    value2=net_profit,
                    value2_label="Net Profit (in report)",
                    tolerance=TOLERANCE
                ))

    def _check_financial_tieout(self, values: Dict[str, float]):
        """ตรวจสอบความตรงกันกับงบการเงิน"""
        # ใช้ GL Group - กลุ่มธุรกิจ เป็นตัวแทนเปรียบเทียบกับงบการเงิน
        gl_biz_net_profit = values.get('rep_gl_biz_net_profit')
        stmt_net_profit = values.get('stmt_net_profit')

        if gl_biz_net_profit is not None and stmt_net_profit is not None:
            self.results.append(ReconciliationResult(
                check_name="3. Tie-out: Report vs Financial Statement",
                description="กำไรสุทธิใน Report ต้องตรงกับงบการเงิน (Text)",
                value1=gl_biz_net_profit,
                value1_label="Report (GL กลุ่มธุรกิจ)",
                value2=stmt_net_profit,
                value2_label="Financial Statement"
            ))

    def print_results(self):
        """แสดงผลลัพธ์การตรวจสอบ"""
        print(f"\n{'='*100}")
        print(f"{'สรุปผลการตรวจสอบ':^100}")
        print(f"{'='*100}")
        print(f"{'รายการตรวจสอบ':<50} | {'ส่วนต่าง':>15} | {'สถานะ':<10}")
        print(f"{'='*100}")

        passed = 0
        failed = 0

        for result in self.results:
            status_icon = "✅" if result.is_pass else "❌"
            print(f"{result.check_name:<50} | {result.difference:>15,.2f} | {status_icon} {result.status}")

            if not result.is_pass:
                print(f"   └─ {result.description}")
                print(f"   └─ {result.value1_label}: {result.value1:,.2f}")
                print(f"   └─ {result.value2_label}: {result.value2:,.2f}")
                failed += 1
            else:
                passed += 1

        print(f"{'='*100}")
        print(f"ผลรวม: ผ่าน {passed} รายการ | ไม่ผ่าน {failed} รายการ")
        print(f"{'='*100}\n")

# ==========================================
# Main Execution
# ==========================================

def main():
    """ฟังก์ชันหลักสำหรับรันการตรวจสอบ"""

    # Argument Parser
    parser = argparse.ArgumentParser(
        description='โปรแกรมตรวจสอบความถูกต้องและความสอดคล้องของรายงาน P&L',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Validation Modes:
  basic          - ตรวจแค่ Net Profit (Phase 1)
  enhanced       - ตรวจ Revenue, Expense, Net Profit + Internal Math (Phase 2) [DEFAULT]
  comprehensive  - ตรวจทุกอย่างรวมถึง Drill-Down (Phase 3)

Examples:
  # ระบุวันที่ (แนะนำ - ไม่ต้องแก้โค้ด)
  python pl_reconciliation_enhanced.py --date 20251031
  python pl_reconciliation_enhanced.py --date 20251130 --mode basic

  # ใช้ค่า default (ต้องแก้โค้ดทุกครั้ง)
  python pl_reconciliation_enhanced.py --mode enhanced
        """
    )
    parser.add_argument(
        '--date',
        type=str,
        help='วันที่รายงาน ในรูปแบบ YYYYMMDD (เช่น 20251031) - ถ้าไม่ระบุจะใช้ค่าที่กำหนดในโค้ด'
    )
    parser.add_argument(
        '--mode',
        type=str,
        choices=['basic', 'enhanced', 'comprehensive'],
        default='enhanced',
        help='ระดับการตรวจสอบ (default: enhanced)'
    )
    parser.add_argument(
        '--company',
        type=str,
        default='NT',
        help='รหัสบริษัท (default: NT)'
    )

    args = parser.parse_args()
    validation_mode = ValidationMode(args.mode)

    # ใช้ตำแหน่งของไฟล์นี้เป็นฐานในการหา path
    script_dir = Path(__file__).parent

    # ถ้าระบุ --date ให้สร้างชื่อไฟล์อัตโนมัติ
    if args.date:
        # Validate date format
        try:
            date_obj = datetime.strptime(args.date, '%Y%m%d')
            year = date_obj.strftime('%Y')
            month = date_obj.strftime('%Y%m')
            company = args.company

            # กำหนด Configuration สำหรับรายเดือน (MTH)
            config_mth = FileConfig(
                period_type=PeriodType.MTH,
                report_excel=str(script_dir / f'Report_{company}_{month}.xlsx'),
                source_cost_csv=str(script_dir / f'TRN_PL_COSTTYPE_{company}_MTH_TABLE_{args.date}.csv'),
                source_gl_csv=str(script_dir / f'TRN_PL_GLGROUP_{company}_MTH_TABLE_{args.date}.csv'),
                financial_stmt_txt=str(script_dir / f'pld_{company.lower()}_{args.date}.txt')
            )

            # กำหนด Configuration สำหรับสะสม (YTD)
            config_ytd = FileConfig(
                period_type=PeriodType.YTD,
                report_excel=str(script_dir / f'Report_{company}_YTD_{month}.xlsx'),
                source_cost_csv=str(script_dir / f'TRN_PL_COSTTYPE_{company}_YTD_TABLE_{args.date}.csv'),
                source_gl_csv=str(script_dir / f'TRN_PL_GLGROUP_{company}_YTD_TABLE_{args.date}.csv'),
                financial_stmt_txt=str(script_dir / f'pld_{company.lower()}_{args.date}.txt')
            )

            print(f"\n📅 วันที่รายงาน: {date_obj.strftime('%d/%m/%Y')}")
            print(f"🏢 บริษัท: {company}")

        except ValueError:
            print(f"❌ รูปแบบวันที่ไม่ถูกต้อง: {args.date}")
            print("   กรุณาใช้รูปแบบ YYYYMMDD (เช่น 20251031)")
            return
    else:
        # ใช้ค่า default (วิธีเดิม - ต้องแก้โค้ดทุกครั้ง)
        print("\n⚠️  กำลังใช้ค่า default ที่กำหนดในโค้ด")
        print("   แนะนำ: ใช้ --date เพื่อไม่ต้องแก้โค้ดทุกครั้ง")

        # กำหนด Configuration สำหรับรายเดือน (MTH)
        config_mth = FileConfig(
            period_type=PeriodType.MTH,
            report_excel=str(script_dir / 'Report_NT_202510.xlsx'),
            source_cost_csv=str(script_dir / 'TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv'),
            source_gl_csv=str(script_dir / 'TRN_PL_GLGROUP_NT_MTH_TABLE_20251031.csv'),
            financial_stmt_txt=str(script_dir / 'pld_nt_20251031.txt')
        )

        # กำหนด Configuration สำหรับสะสม (YTD)
        config_ytd = FileConfig(
            period_type=PeriodType.YTD,
            report_excel=str(script_dir / 'Report_NT_YTD_202510.xlsx'),
            source_cost_csv=str(script_dir / 'TRN_PL_COSTTYPE_NT_YTD_TABLE_20251031.csv'),
            source_gl_csv=str(script_dir / 'TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv'),
            financial_stmt_txt=str(script_dir / 'pld_nt_20251031.txt')
        )

    # รันการตรวจสอบทั้งสองงวด
    print("\n" + "="*100)
    print("โปรแกรมตรวจสอบความถูกต้องและความสอดคล้องของรายงาน P&L".center(100))
    print(f"Validation Mode: {validation_mode.value.upper()}".center(100))
    print("="*100)

    # ตรวจสอบรายเดือน (MTH)
    engine_mth = ReconciliationEngine(config_mth, validation_mode)
    engine_mth.run_all_checks()
    engine_mth.print_results()

    # ตรวจสอบสะสม (YTD)
    engine_ytd = ReconciliationEngine(config_ytd, validation_mode)
    engine_ytd.run_all_checks()
    engine_ytd.print_results()

if __name__ == "__main__":
    main()

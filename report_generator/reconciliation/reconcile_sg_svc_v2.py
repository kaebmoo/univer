"""
NT P&L Reconciliation - Service Group & Service (Product) Level v2
===================================================================
Fixed version: proper GROUP matching and dynamic product key row detection
"""

import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# ==========================================
# PATH CONFIGURATION - แก้ไขตรงนี้จุดเดียว
# ==========================================
# SCRIPT_DIR = ตำแหน่งของไฟล์ script นี้ (ใช้อ้างอิง relative path ได้)
SCRIPT_DIR = Path(__file__).resolve().parent

# โฟลเดอร์ข้อมูล CSV source (ให้วางไฟล์ CSV ไว้ในโฟลเดอร์นี้)
# ค่า default = โฟลเดอร์ data/ ใต้ตำแหน่ง script นี้
# ตัวอย่างชี้ไปที่อื่น: DATA_DIR = SCRIPT_DIR.parent / 'shared_data'
# ตัวอย่าง absolute  : DATA_DIR = Path(r'C:\Users\username\project\data')  # Windows
#                       DATA_DIR = Path('/Users/username/project/data')      # macOS
DATA_DIR = SCRIPT_DIR / 'data'

# โฟลเดอร์ Excel report ต้นฉบับ (ให้วางไฟล์ Excel ไว้ในโฟลเดอร์นี้)
# ค่า default = โฟลเดอร์ report/ ใต้ตำแหน่ง script นี้
# ตัวอย่างชี้ไปที่อื่น: REPORT_DIR = SCRIPT_DIR.parent / 'reports'
# ตัวอย่าง absolute  : REPORT_DIR = Path(r'C:\Users\username\Documents\NT\Report\PL')  # Windows
#                       REPORT_DIR = Path('/Users/username/Documents/NT/Report/PL')      # macOS
REPORT_DIR = SCRIPT_DIR / 'report'

# ชื่อไฟล์ CSV (อยู่ใน DATA_DIR)
# ตัวอย่าง: เปลี่ยนวันที่ 20251231 เป็นงวดที่ต้องการ เช่น 20260131
CSV_FILENAMES = {
    'COSTTYPE_MTH': 'TRN_PL_COSTTYPE_NT_MTH_TABLE_20251231.csv',
    'COSTTYPE_YTD': 'TRN_PL_COSTTYPE_NT_YTD_TABLE_20251231.csv',
    'GLGROUP_MTH':  'TRN_PL_GLGROUP_NT_MTH_TABLE_20251231.csv',
    'GLGROUP_YTD':  'TRN_PL_GLGROUP_NT_YTD_TABLE_20251231.csv',
}

# ชื่อไฟล์ Excel report (อยู่ใน REPORT_DIR)
# ตัวอย่าง: เปลี่ยนชื่อไฟล์ตามงวดที่ต้องการ เช่น Report_NT_ม.ค.69_...
EXCEL_FILENAMES = {
    'MTH': 'Report_NT_ธ.ค.68_(ก่อนผู้สอบบัญชีรับรอง)_T.xlsx',
    'YTD': 'Report_NT BU_สะสมธ.ค.2568_(ก่อนผู้สอบบัญชีรับรอง) _T.xlsx',
}

# โฟลเดอร์และชื่อไฟล์ผลลัพธ์ (สร้างอัตโนมัติถ้ายังไม่มี)
# ค่า default = โฟลเดอร์ output/ ใต้ตำแหน่ง script นี้
# ตัวอย่างชี้ไปที่อื่น: OUTPUT_DIR = SCRIPT_DIR.parent / 'results'
# ตัวอย่างชื่อไฟล์     : เปลี่ยน 202512 เป็นงวดที่ต้องการ เช่น 202601
OUTPUT_DIR = SCRIPT_DIR / 'output'
OUTPUT_FILENAME = 'reconciliation_sg_svc_v2_202512.xlsx'

# ==========================================

TOLERANCE = 0.001  # ยอมรับผลต่างไม่เกิน 0.01 บาท (floating point)

@dataclass
class CheckResult:
    category: str
    check_name: str
    source_label: str
    source_value: float
    target_label: str
    target_value: float
    tolerance: float = TOLERANCE

    @property
    def diff(self):
        return self.source_value - self.target_value
    @property
    def passed(self):
        return abs(self.diff) <= self.tolerance
    @property
    def status(self):
        return "PASS" if self.passed else "FAIL"


def read_csv_auto_encoding(filepath):
    for enc in ['utf-8', 'cp874', 'tis-620', 'latin-1']:
        try:
            df = pd.read_csv(filepath, encoding=enc)
            if 'TIME_KEY' in df.columns:
                return df
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError("Cannot read {}".format(filepath))


# ==========================================
# Row/Column definitions with GROUP mapping
# ==========================================

# Each entry: (excel_keywords, csv_group_pattern, display_label)
# csv_group_pattern is used to filter CSV GROUP column

COSTTYPE_CHECKS = [
    (['1', 'รวมรายได้'], '01.รายได้', 'รายได้'),
    (['2.', 'ต้นทุนบริการ'], '02.ต้นทุนบริการ', 'ต้นทุนบริการ'),
    (['3.', 'กำไร', 'ขั้นต้น'], '03.กำไร', 'กำไรขั้นต้น'),
    (['5.', 'กำไร', 'หลังหัก'], '05.กำไร', 'กำไรหลังหักค่าใช้จ่ายขาย'),
    (['8.', 'กำไร', 'จัดหาเงิน'], '08.กำไร', 'กำไรก่อนต้นทุนจัดหาเงิน'),
    (['12.', 'กำไร', 'EBT'], '12.กำไร', 'กำไรก่อนภาษี'),
    (['14.', 'กำไร', 'สุทธิ'], '14.กำไร', 'กำไรสุทธิ'),
]

GLGROUP_CHECKS = [
    (['1', 'รวมรายได้'], '01.รายได้', 'รายได้'),
    (['2', 'รวมค่าใช้จ่าย'], '02.ค่าใช้จ่าย', 'ค่าใช้จ่าย'),
    (['3.', 'กำไร', 'EBT'], '03.กำไร', 'กำไรก่อนภาษี'),
    (['5.', 'กำไร', 'สุทธิ'], '05.กำไร', 'กำไรสุทธิ'),
]


def find_data_start_row(ws):
    for row_idx in range(1, 15):
        val = ws.cell(row=row_idx, column=2).value
        if val and str(val).strip().startswith('1') and 'รายได้' in str(val):
            return row_idx
    return 10


def find_row_index(ws, data_start, keywords):
    for row_idx in range(data_start, ws.max_row + 1):
        val = ws.cell(row=row_idx, column=2).value
        if val is None:
            continue
        label = str(val).strip()
        if all(kw in label for kw in keywords):
            return row_idx
    return None


# ==========================================
# Service Group Mapping
# ==========================================

def build_sg_column_map(ws):
    """Build SERVICE_GROUP name → column index from row 7"""
    col_map = {}
    for col_idx in range(1, ws.max_column + 1):
        val = ws.cell(row=7, column=col_idx).value
        if val is None:
            continue
        val_str = str(val).strip()
        if val_str.startswith('รวม'):
            continue
        # Normalize to uppercase
        col_map[val_str.upper()] = col_idx
    return col_map


def match_sg(csv_sg, sg_col_map):
    """Find matching Excel column for a CSV SERVICE_GROUP"""
    csv_norm = csv_sg.strip().upper()

    # 1. Exact match
    if csv_norm in sg_col_map:
        return sg_col_map[csv_norm]

    # 2. Prefix match (first 3 chars like "1.1", "2.3")
    csv_prefix = csv_norm[:3]
    for excel_sg, col_idx in sg_col_map.items():
        if excel_sg[:3] == csv_prefix:
            return col_idx

    # 3. Substring match
    for excel_sg, col_idx in sg_col_map.items():
        if csv_norm in excel_sg or excel_sg in csv_norm:
            return col_idx

    return None


# ==========================================
# Product Key Mapping
# ==========================================

def build_product_column_map(ws):
    """Build PRODUCT_KEY → column index, auto-detecting which row has keys"""
    # Try rows 8 and 9
    for pk_row in [9, 8]:
        col_map = {}
        for col_idx in range(1, ws.max_column + 1):
            val = ws.cell(row=pk_row, column=col_idx).value
            if val is None:
                continue
            val_str = str(val).strip()
            try:
                int(val_str)
                col_map[val_str] = col_idx
            except ValueError:
                continue
        if len(col_map) > 10:  # Found product keys
            return col_map, pk_row

    return {}, 9


# ==========================================
# Reconcile Service Group Level
# ==========================================

def reconcile_service_group(csv_df, ws, csv_type, period_label, sheet_name, results):
    category = "CSV vs Excel by ServiceGroup ({}) - {}".format(period_label, sheet_name)
    checks = COSTTYPE_CHECKS if csv_type == 'COSTTYPE' else GLGROUP_CHECKS

    data_start = find_data_start_row(ws)
    sg_col_map = build_sg_column_map(ws)

    csv_df = csv_df.copy()
    csv_df['VALUE'] = csv_df['VALUE'].astype(float)

    unique_sgs = csv_df['SERVICE_GROUP'].unique()
    total_checks = 0

    for csv_sg in sorted(unique_sgs):
        excel_col = match_sg(csv_sg, sg_col_map)
        if excel_col is None:
            continue

        for excel_kw, csv_group_prefix, desc in checks:
            # Find Excel row
            excel_row = find_row_index(ws, data_start, excel_kw)
            if excel_row is None:
                continue

            # Get Excel value
            excel_val = ws.cell(row=excel_row, column=excel_col).value
            if excel_val is None:
                excel_val = 0.0
            try:
                excel_val = float(excel_val)
            except (ValueError, TypeError):
                continue

            # Skip if Excel is 0 and this is a row that may not have SG breakdown
            # (e.g., กำไรสุทธิ is often only at BU total level)
            if excel_val == 0.0 and 'สุทธิ' in desc:
                # Check if ALL service group columns are 0 for this row
                all_zero = True
                for _, c in sg_col_map.items():
                    v = ws.cell(row=excel_row, column=c).value
                    if v is not None and v != 0:
                        all_zero = False
                        break
                if all_zero:
                    continue  # Skip - this row doesn't have SG breakdown

            # Get CSV value (filter by GROUP prefix)
            csv_filtered = csv_df[
                (csv_df['SERVICE_GROUP'] == csv_sg) &
                (csv_df['GROUP'].str.startswith(csv_group_prefix))
            ]
            csv_val = csv_filtered['VALUE'].sum() if len(csv_filtered) > 0 else 0.0

            sg_label = csv_sg[:45]
            results.append(CheckResult(
                category=category,
                check_name="{} - {}".format(desc, sg_label),
                source_label="CSV",
                source_value=csv_val,
                target_label="Excel col {}".format(get_column_letter(excel_col)),
                target_value=excel_val,
            ))
            total_checks += 1

    return total_checks


# ==========================================
# Reconcile Product Level
# ==========================================

def reconcile_product(csv_df, ws, csv_type, period_label, sheet_name, results):
    category = "CSV vs Excel by Product ({}) - {}".format(period_label, sheet_name)
    checks = COSTTYPE_CHECKS if csv_type == 'COSTTYPE' else GLGROUP_CHECKS

    data_start = find_data_start_row(ws)
    pk_col_map, pk_row = build_product_column_map(ws)

    if len(pk_col_map) == 0:
        print("    Warning: No product keys found in {} {}".format(period_label, sheet_name))
        return 0

    csv_df = csv_df.copy()
    csv_df['VALUE'] = csv_df['VALUE'].astype(float)
    csv_df['PRODUCT_KEY'] = csv_df['PRODUCT_KEY'].astype(str).str.strip()

    # Get product names for labeling
    pk_names = csv_df.drop_duplicates('PRODUCT_KEY').set_index('PRODUCT_KEY')['PRODUCT_NAME'].to_dict()

    unique_pks = csv_df['PRODUCT_KEY'].unique()
    total_checks = 0
    unmatched = []

    for csv_pk in sorted(unique_pks):
        excel_col = pk_col_map.get(csv_pk)
        if excel_col is None:
            unmatched.append(csv_pk)
            continue

        for excel_kw, csv_group_prefix, desc in checks:
            # Find Excel row
            excel_row = find_row_index(ws, data_start, excel_kw)
            if excel_row is None:
                continue

            # Get Excel value
            excel_val = ws.cell(row=excel_row, column=excel_col).value
            if excel_val is None:
                excel_val = 0.0
            try:
                excel_val = float(excel_val)
            except (ValueError, TypeError):
                continue

            # Skip rows where product level isn't populated
            if excel_val == 0.0:
                # Check if this is a row that might not have product breakdown
                sample_vals = [ws.cell(row=excel_row, column=c).value for c in list(pk_col_map.values())[:10]]
                if all(v is None or v == 0 for v in sample_vals):
                    continue

            # Get CSV value
            csv_filtered = csv_df[
                (csv_df['PRODUCT_KEY'] == csv_pk) &
                (csv_df['GROUP'].str.startswith(csv_group_prefix))
            ]
            csv_val = csv_filtered['VALUE'].sum() if len(csv_filtered) > 0 else 0.0

            product_name = pk_names.get(csv_pk, csv_pk)
            if len(product_name) > 25:
                product_name = product_name[:25] + '..'

            results.append(CheckResult(
                category=category,
                check_name="{} - {} ({})".format(desc, product_name, csv_pk),
                source_label="CSV",
                source_value=csv_val,
                target_label="Excel",
                target_value=excel_val,
            ))
            total_checks += 1

    if unmatched:
        print("    Warning: {} unmatched PKs".format(len(unmatched)))

    return total_checks


# ==========================================
# Main
# ==========================================

def main():
    # สร้าง full path จาก config ด้านบน
    csv_files = {key: DATA_DIR / fname for key, fname in CSV_FILENAMES.items()}
    excel_files = {key: REPORT_DIR / fname for key, fname in EXCEL_FILENAMES.items()}
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / OUTPUT_FILENAME

    sheet_sg = {'COSTTYPE': 'ต้นทุน_กลุ่มบริการ', 'GLGROUP': 'หมวดบัญชี_กลุ่มบริการ'}
    sheet_svc = {'COSTTYPE': 'ต้นทุน_บริการ', 'GLGROUP': 'หมวดบัญชี_บริการ'}

    # Load CSVs
    print("Loading CSV files...")
    csv_data = {}
    for key, path in csv_files.items():
        csv_data[key] = read_csv_auto_encoding(str(path))
        csv_data[key]['VALUE'] = csv_data[key]['VALUE'].astype(float)
        print("  {} -> {} rows".format(key, len(csv_data[key])))

    results = []

    for period in ['MTH', 'YTD']:
        print("\n{}".format('=' * 60))
        print("Reconciling {} - Service Group & Product level".format(period))
        print('=' * 60)

        wb = openpyxl.load_workbook(str(excel_files[period]), data_only=True)

        for csv_type in ['COSTTYPE', 'GLGROUP']:
            csv_key = '{}_{}'.format(csv_type, period)
            csv_df = csv_data[csv_key]

            # Service Group
            sn = sheet_sg[csv_type]
            ws = wb[sn]
            print("\n  SG: {} vs {}".format(csv_key, sn))
            n = reconcile_service_group(csv_df, ws, csv_type, period, sn, results)
            print("    -> {} checks".format(n))

            # Product
            sn = sheet_svc[csv_type]
            ws = wb[sn]
            print("\n  Product: {} vs {}".format(csv_key, sn))
            n = reconcile_product(csv_df, ws, csv_type, period, sn, results)
            print("    -> {} checks".format(n))

        wb.close()

    # Print results
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    total = len(results)

    # Print FAIL details
    fail_results = [r for r in results if not r.passed]
    if fail_results:
        print("\n{}".format('=' * 130))
        print("{:^130}".format("FAILED CHECKS DETAIL"))
        print('=' * 130)

        current_cat = None
        for r in fail_results:
            if r.category != current_cat:
                current_cat = r.category
                print("\n--- {} ---".format(current_cat))
                print("{:<60} | {:>18} | {:>18} | {:>15}".format(
                    'Check', 'CSV', 'Excel', 'Diff'))
                print("{}-+-{}-+-{}-+-{}".format('-'*60, '-'*18, '-'*18, '-'*15))

            print("{:<60} | {:>18,.2f} | {:>18,.2f} | {:>15,.2f}".format(
                r.check_name[:60], r.source_value, r.target_value, r.diff))

    print("\n{}".format('=' * 130))
    print("Summary: {} PASSED / {} FAILED / {} Total checks".format(passed, failed, total))

    # Pass rate by category
    print("\n  Pass rate by category:")
    cat_stats = {}
    for r in results:
        if r.category not in cat_stats:
            cat_stats[r.category] = {'passed': 0, 'failed': 0}
        if r.passed:
            cat_stats[r.category]['passed'] += 1
        else:
            cat_stats[r.category]['failed'] += 1

    for cat, stats in cat_stats.items():
        total_cat = stats['passed'] + stats['failed']
        pct = stats['passed'] / total_cat * 100 if total_cat > 0 else 0
        print("    {} -> {}/{} ({:.1f}%)".format(cat[:70], stats['passed'], total_cat, pct))

    print('=' * 130)

    # Export
    records = [{
        'Category': r.category, 'Check': r.check_name,
        'Source Label': r.source_label, 'Source Value': r.source_value,
        'Target Label': r.target_label, 'Target Value': r.target_value,
        'Difference': r.diff, 'Status': r.status,
    } for r in results]

    df_results = pd.DataFrame(records)
    with pd.ExcelWriter(str(output_path), engine='openpyxl') as writer:
        pd.DataFrame([{
            'Total': total, 'Passed': passed, 'Failed': failed,
            'Rate': "{:.1f}%".format(passed/total*100) if total > 0 else 'N/A',
            'Generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }]).to_excel(writer, sheet_name='Summary', index=False)

        df_results.to_excel(writer, sheet_name='All Checks', index=False)
        df_failed = df_results[df_results['Status'] == 'FAIL']
        if len(df_failed) > 0:
            df_failed.to_excel(writer, sheet_name='Failed Checks', index=False)

    print("\nExported to: {}".format(str(output_path)))


if __name__ == '__main__':
    main()

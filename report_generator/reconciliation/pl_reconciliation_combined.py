"""
P&L Reconciliation for Combined Output File
============================================
ตรวจสอบความถูกต้องของไฟล์ pl_combined_output ที่รวม:
- revenue_gl_group (รายได้ตามหมวด GL)
- expense_gl_group (ค่าใช้จ่ายตามหมวด GL)
- summary_other (รายได้อื่น, ค่าใช้จ่ายอื่น, ผลตอบแทนทางการเงิน)

การตรวจสอบ:
1. ยอดรวมใน pl_combined_output = ยอดรวมใน Source CSV
2. รายได้รวม + ค่าใช้จ่ายรวม + summary_other = กำไรสุทธิ
3. ตรวจสอบความสอดคล้องระหว่าง MTH และ YTD
"""

import pandas as pd
import os
from typing import Dict, Optional
from dataclasses import dataclass

# ==========================================
# Helper Functions
# ==========================================

def parse_number(value) -> float:
    """แปลงค่าให้เป็น float"""
    if pd.isna(value):
        return 0.0
    return float(value)

# ==========================================
# Configuration
# ==========================================

@dataclass
class CombinedFileConfig:
    """กำหนดค่าไฟล์สำหรับการตรวจสอบ"""
    combined_file: str
    source_gl_csv_mth: str
    source_gl_csv_ytd: str
    financial_stmt_txt: str

# ==========================================
# Reconciliation Functions
# ==========================================

def load_combined_file(file_path: str) -> Dict[str, pd.DataFrame]:
    """โหลดข้อมูลจากไฟล์ combined output"""
    print(f"กำลังอ่านข้อมูลจากไฟล์ Combined: {file_path}")

    try:
        revenue_gl = pd.read_excel(file_path, sheet_name='revenue_gl_group')
        expense_gl = pd.read_excel(file_path, sheet_name='expense_gl_group')
        summary_other = pd.read_excel(file_path, sheet_name='summary_other')

        print(f"  ✓ โหลด revenue_gl_group สำเร็จ ({len(revenue_gl)} rows)")
        print(f"  ✓ โหลด expense_gl_group สำเร็จ ({len(expense_gl)} rows)")
        print(f"  ✓ โหลด summary_other สำเร็จ ({len(summary_other)} rows)")

        return {
            'revenue_gl': revenue_gl,
            'expense_gl': expense_gl,
            'summary_other': summary_other
        }
    except Exception as e:
        print(f"  ✗ เกิดข้อผิดพลาด: {e}")
        return None

def load_source_csv(file_path: str) -> pd.DataFrame:
    """โหลดไฟล์ CSV แหล่งข้อมูล"""
    try:
        df = pd.read_csv(file_path, encoding='cp874')
        return df
    except Exception as e:
        print(f"  ✗ ไม่สามารถโหลดไฟล์ {file_path}: {e}")
        return None

def calculate_net_profit_from_combined(data: Dict[str, pd.DataFrame], period: str = 'เดือน') -> Dict[str, float]:
    """
    คำนวณกำไรสุทธิจากไฟล์ combined

    Args:
        data: Dictionary ของ DataFrames จาก combined file
        period: 'เดือน' หรือ 'สะสม'

    Returns:
        Dictionary ของค่าต่างๆ
    """
    col_suffix = 'VALUE' if period == 'เดือน' else 'VALUE_YTD'

    # 1. รายได้จาก revenue_gl_group (ไม่รวม R10 ที่เป็นผลตอบแทนฯและรายได้อื่น)
    revenue_df = data['revenue_gl']
    revenue_col = f'REVENUE_{col_suffix}'
    if 'REPORT_CODE' not in revenue_df.columns:
        print(f"WARNING: column 'REPORT_CODE' not found in revenue_gl. Available columns: {list(revenue_df.columns)}")
        total_revenue = 0
    elif revenue_col not in revenue_df.columns:
        print(f"WARNING: column '{revenue_col}' not found in revenue_gl. Available columns: {list(revenue_df.columns)}")
        total_revenue = 0
    else:
        revenue_df_filtered = revenue_df[
            (revenue_df['REPORT_CODE'] != 'R10') &
            (revenue_df['REPORT_CODE'].notna())
        ].copy()
        total_revenue = revenue_df_filtered[revenue_col].sum()

    # 2. ค่าใช้จ่ายจาก expense_gl_group (ไม่รวมค่าใช้จ่ายอื่น C17 ที่อยู่ใน summary_other)
    expense_df = data['expense_gl']
    expense_col = f'EXPENSE_{col_suffix}'
    # กรองเฉพาะรายการที่มี CODE_GROUP (ไม่รวม Grand Total)
    # และตัด C17 (ค่าใช้จ่ายอื่น) ออก เพราะจะเอามาจาก summary_other แทน
    if 'CODE_GROUP' not in expense_df.columns:
        print(f"WARNING: column 'CODE_GROUP' not found in expense_gl. Available columns: {list(expense_df.columns)}")
        total_expense = 0
    elif expense_col not in expense_df.columns:
        print(f"WARNING: column '{expense_col}' not found in expense_gl. Available columns: {list(expense_df.columns)}")
        total_expense = 0
    else:
        expense_df_filtered = expense_df[
            (expense_df['CODE_GROUP'].notna()) &
            (expense_df['CODE_GROUP'] != 'C17')
        ].copy()
        total_expense = expense_df_filtered[expense_col].sum()

    # 3. Summary other - ดึงค่าจาก summary_other
    summary_df = data['summary_other']

    # Bounds checking: verify 'รายการ' column exists before filtering
    if 'รายการ' not in summary_df.columns:
        print(f"WARNING: column 'รายการ' not found in summary_other. Available columns: {list(summary_df.columns)}")
        financial_income = 0
        other_revenue = 0
        other_expense = 0
    else:
        # Bounds checking: verify period column exists
        if period not in summary_df.columns:
            print(f"WARNING: period column '{period}' not found in summary_other. Available columns: {list(summary_df.columns)}")
            financial_income = 0
            other_revenue = 0
            other_expense = 0
        else:
            filtered_fi = summary_df[summary_df['รายการ'] == 'ผลตอบแทนทางการเงิน']
            if len(filtered_fi) > 0:
                financial_income = filtered_fi[period].values[0]
            else:
                print("WARNING: 'ผลตอบแทนทางการเงิน' not found in summary_other - defaulting to 0")
                financial_income = 0

            filtered_or = summary_df[summary_df['รายการ'] == 'รายได้อื่น']
            if len(filtered_or) > 0:
                other_revenue = filtered_or[period].values[0]
            else:
                print("WARNING: 'รายได้อื่น' not found in summary_other - defaulting to 0")
                other_revenue = 0

            filtered_oe = summary_df[summary_df['รายการ'] == 'ค่าใช้จ่ายอื่น']
            if len(filtered_oe) > 0:
                other_expense = filtered_oe[period].values[0]
            else:
                print("WARNING: 'ค่าใช้จ่ายอื่น' not found in summary_other - defaulting to 0")
                other_expense = 0

    # 4. คำนวณกำไรสุทธิ
    # สูตร: รายได้บริการ - ค่าใช้จ่าย + ผลตอบแทนฯ + รายได้อื่น - ค่าใช้จ่ายอื่น
    net_profit = total_revenue - total_expense + financial_income + other_revenue - other_expense

    return {
        'revenue': total_revenue,
        'expense': total_expense,
        'financial_income': financial_income,
        'other_revenue': other_revenue,
        'other_expense': other_expense,
        'net_profit': net_profit,
        'revenue_with_other': total_revenue + financial_income + other_revenue
    }

def get_source_net_profit(csv_file: str) -> float:
    """ดึงกำไรสุทธิจาก Source CSV"""
    df = load_source_csv(csv_file)
    if df is None:
        return 0.0

    net_profit_rows = df[df['GROUP'].str.contains('05.กำไร(ขาดทุน) สุทธิ', na=False, regex=False)]
    return net_profit_rows['VALUE'].sum()

def get_source_revenue(csv_file: str) -> float:
    """ดึงรายได้จาก Source CSV"""
    df = load_source_csv(csv_file)
    if df is None:
        return 0.0

    revenue_rows = df[df['GROUP'].str.contains('01.รายได้', na=False, regex=False)]
    return revenue_rows['VALUE'].sum()

# ==========================================
# Main Reconciliation
# ==========================================

def run_reconciliation(config: CombinedFileConfig):
    """รันการตรวจสอบทั้งหมด"""

    print("\n" + "="*100)
    print("โปรแกรมตรวจสอบความถูกต้องของไฟล์ pl_combined_output".center(100))
    print("="*100 + "\n")

    # 1. โหลดไฟล์ Combined
    combined_data = load_combined_file(config.combined_file)
    if combined_data is None:
        print("\n❌ ไม่สามารถโหลดไฟล์ Combined ได้")
        return

    # 2. คำนวณค่าจาก Combined (MTH)
    print("\n" + "="*100)
    print("ตรวจสอบรายเดือน (MTH)".center(100))
    print("="*100)

    mth_values = calculate_net_profit_from_combined(combined_data, 'เดือน')

    print(f"\n📊 ค่าจากไฟล์ Combined (MTH):")
    print(f"  - รายได้จากบริการ:        {mth_values['revenue']:>20,.2f}")
    print(f"  - ค่าใช้จ่าย:              {mth_values['expense']:>20,.2f}")
    print(f"  - ผลตอบแทนทางการเงิน:     {mth_values['financial_income']:>20,.2f}")
    print(f"  - รายได้อื่น:              {mth_values['other_revenue']:>20,.2f}")
    print(f"  - ค่าใช้จ่ายอื่น:          {mth_values['other_expense']:>20,.2f}")
    print(f"  " + "-" * 60)
    print(f"  - กำไร(ขาดทุน)สุทธิ:       {mth_values['net_profit']:>20,.2f}")
    print(f"  - รายได้รวม (รวมอื่น):     {mth_values['revenue_with_other']:>20,.2f}")

    # 3. เปรียบเทียบกับ Source CSV (MTH)
    print(f"\n🔍 เปรียบเทียบกับ Source CSV (MTH):")
    source_mth_net_profit = get_source_net_profit(config.source_gl_csv_mth)
    source_mth_revenue = get_source_revenue(config.source_gl_csv_mth)

    print(f"  - กำไรสุทธิจาก CSV:        {source_mth_net_profit:>20,.2f}")
    print(f"  - กำไรสุทธิจาก Combined:   {mth_values['net_profit']:>20,.2f}")
    diff_net_mth = source_mth_net_profit - mth_values['net_profit']
    # Tolerance 1.0 for net profit: small rounding differences across aggregation steps
    status_mth = "✅ PASS" if abs(diff_net_mth) < 1.0 else "❌ FAIL"
    print(f"  - ส่วนต่าง:                {diff_net_mth:>20,.2f}  {status_mth}")

    print(f"\n  - รายได้รวมจาก CSV:       {source_mth_revenue:>20,.2f}")
    print(f"  - รายได้รวมจาก Combined:  {mth_values['revenue_with_other']:>20,.2f}")
    diff_rev_mth = source_mth_revenue - mth_values['revenue_with_other']
    # Tolerance 10.0 for revenue: aggregates across multiple sheets (revenue_gl + summary_other)
    # where rounding accumulates more than single-value net profit comparisons
    status_rev_mth = "✅ PASS" if abs(diff_rev_mth) < 10.0 else "❌ FAIL"
    print(f"  - ส่วนต่าง:                {diff_rev_mth:>20,.2f}  {status_rev_mth}")

    # 4. คำนวณค่าจาก Combined (YTD)
    print("\n" + "="*100)
    print("ตรวจสอบสะสม (YTD)".center(100))
    print("="*100)

    ytd_values = calculate_net_profit_from_combined(combined_data, 'สะสม')

    print(f"\n📊 ค่าจากไฟล์ Combined (YTD):")
    print(f"  - รายได้จากบริการ:        {ytd_values['revenue']:>20,.2f}")
    print(f"  - ค่าใช้จ่าย:              {ytd_values['expense']:>20,.2f}")
    print(f"  - ผลตอบแทนทางการเงิน:     {ytd_values['financial_income']:>20,.2f}")
    print(f"  - รายได้อื่น:              {ytd_values['other_revenue']:>20,.2f}")
    print(f"  - ค่าใช้จ่ายอื่น:          {ytd_values['other_expense']:>20,.2f}")
    print(f"  " + "-" * 60)
    print(f"  - กำไร(ขาดทุน)สุทธิ:       {ytd_values['net_profit']:>20,.2f}")
    print(f"  - รายได้รวม (รวมอื่น):     {ytd_values['revenue_with_other']:>20,.2f}")

    # 5. เปรียบเทียบกับ Source CSV (YTD)
    print(f"\n🔍 เปรียบเทียบกับ Source CSV (YTD):")
    source_ytd_net_profit = get_source_net_profit(config.source_gl_csv_ytd)
    source_ytd_revenue = get_source_revenue(config.source_gl_csv_ytd)

    print(f"  - กำไรสุทธิจาก CSV:        {source_ytd_net_profit:>20,.2f}")
    print(f"  - กำไรสุทธิจาก Combined:   {ytd_values['net_profit']:>20,.2f}")
    diff_net_ytd = source_ytd_net_profit - ytd_values['net_profit']
    # Tolerance 1.0 for net profit: small rounding differences across aggregation steps
    status_ytd = "✅ PASS" if abs(diff_net_ytd) < 1.0 else "❌ FAIL"
    print(f"  - ส่วนต่าง:                {diff_net_ytd:>20,.2f}  {status_ytd}")

    print(f"\n  - รายได้รวมจาก CSV:       {source_ytd_revenue:>20,.2f}")
    print(f"  - รายได้รวมจาก Combined:  {ytd_values['revenue_with_other']:>20,.2f}")
    diff_rev_ytd = source_ytd_revenue - ytd_values['revenue_with_other']
    # Tolerance 10.0 for revenue: aggregates across multiple sheets where rounding accumulates
    status_rev_ytd = "✅ PASS" if abs(diff_rev_ytd) < 10.0 else "❌ FAIL"
    print(f"  - ส่วนต่าง:                {diff_rev_ytd:>20,.2f}  {status_rev_ytd}")

    # 6. สรุปผล
    print("\n" + "="*100)
    print("สรุปผลการตรวจสอบ".center(100))
    print("="*100)

    checks = [
        ("MTH: กำไรสุทธิ (Source vs Combined)", diff_net_mth, status_mth),
        ("MTH: รายได้รวม (Source vs Combined)", diff_rev_mth, status_rev_mth),
        ("YTD: กำไรสุทธิ (Source vs Combined)", diff_net_ytd, status_ytd),
        ("YTD: รายได้รวม (Source vs Combined)", diff_rev_ytd, status_rev_ytd),
    ]

    passed = sum(1 for _, _, status in checks if "PASS" in status)
    failed = sum(1 for _, _, status in checks if "FAIL" in status)

    print(f"\n{'รายการตรวจสอบ':<50} | {'ส่วนต่าง':>20} | {'สถานะ':<10}")
    print("="*100)
    for check_name, diff, status in checks:
        print(f"{check_name:<50} | {diff:>20,.2f} | {status}")

    print("="*100)
    print(f"ผลรวม: ผ่าน {passed} รายการ | ไม่ผ่าน {failed} รายการ")
    print("="*100 + "\n")

# ==========================================
# Main Execution
# ==========================================

def main():
    """ฟังก์ชันหลัก"""

    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description='P&L Reconciliation for Combined Output File')
    parser.add_argument('--date', required=True, help='Date in YYYYMMDD format (e.g., 20260331)')
    args = parser.parse_args()

    date = args.date
    date_short = date[:6]  # YYYYMM for Excel file

    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / 'data'

    config = CombinedFileConfig(
        combined_file=str(data_dir / f'pl_combined_output_{date_short}.xlsx'),
        source_gl_csv_mth=str(data_dir / f'TRN_PL_GLGROUP_NT_MTH_TABLE_{date}.csv'),
        source_gl_csv_ytd=str(data_dir / f'TRN_PL_GLGROUP_NT_YTD_TABLE_{date}.csv'),
        financial_stmt_txt=str(data_dir / f'pld_nt_{date}.txt')
    )

    run_reconciliation(config)

if __name__ == "__main__":
    main()

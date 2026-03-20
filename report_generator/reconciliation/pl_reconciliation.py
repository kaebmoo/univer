import pandas as pd
import argparse
from pathlib import Path
from datetime import datetime

# ==========================================
# ส่วนที่ 1: Path Configuration
# ==========================================
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / 'data'                  # CSV + pld_nt_*.txt
REPORT_DIR = SCRIPT_DIR / 'report'              # Excel report (copy มาจาก output/)

# ชื่อ Sheet ในไฟล์ Excel (ต้องสะกดให้ตรงเป๊ะกับในไฟล์)
SHEETS = {
    'cost_biz': 'ต้นทุน_กลุ่มธุรกิจ',
    'gl_biz':   'หมวดบัญชี_กลุ่มธุรกิจ'
}

# ==========================================
# ส่วนที่ 2: ฟังก์ชันช่วย (Helper Functions)
# ==========================================

def parse_thai_number(text):
    """แปลงข้อความตัวเลขที่มีลูกน้ำหรือวงเล็บให้เป็น Float"""
    if pd.isna(text): return 0.0
    text = str(text).strip()
    if text == '-' or text == '': return 0.0
    if '(' in text and ')' in text:
        text = '-' + text.replace('(', '').replace(')', '')
    text = text.replace(',', '')
    try:
        return float(text)
    except ValueError:
        return 0.0

def detect_label_col(df):
    """ค้นหา column ที่มี 'รายละเอียด' ใน DataFrame (คล้าย ExcelSheetReader._detect_label_column)"""
    search_rows = min(15, len(df))
    search_cols = min(10, len(df.columns))
    for row_idx in range(search_rows):
        for col_idx in range(search_cols):
            val = df.iloc[row_idx, col_idx]
            if val is not None and 'รายละเอียด' in str(val):
                return col_idx
    return 1  # default fallback

def get_val_from_df(df, keywords, col_index=2):
    """ค้นหาตัวเลขใน DataFrame (แบบไม่มี Header)"""
    # Dynamically detect label column instead of hardcoding column 1
    label_col = detect_label_col(df)
    for i, row in df.iterrows():
        if label_col >= len(row):
            continue
        desc = str(row[label_col])
        if all(k in desc for k in keywords):
            if col_index >= len(row):
                print(f"WARNING: col_index {col_index} out of bounds (row has {len(row)} columns)")
                return None
            return parse_thai_number(row[col_index])
    return None

def get_text_val(lines, keywords):
    """ค้นหาตัวเลขในไฟล์ Text"""
    for line in lines:
        if all(k in line for k in keywords):
            tokens = line.split()
            for t in tokens:
                if any(c.isdigit() for c in t):
                    try:
                        return parse_thai_number(t)
                    except:
                        pass
    return None

# ==========================================
# ส่วนที่ 3: Main
# ==========================================

def main():
    parser = argparse.ArgumentParser(description='P&L Reconciliation (Basic)')
    parser.add_argument('--date', type=str, required=True,
                        help='วันที่รายงาน YYYYMMDD (เช่น 20251231)')
    parser.add_argument('--company', type=str, default='NT',
                        help='รหัสบริษัท (default: NT)')
    args = parser.parse_args()

    # Validate date
    try:
        date_obj = datetime.strptime(args.date, '%Y%m%d')
        month = date_obj.strftime('%Y%m')
    except ValueError:
        print(f"❌ รูปแบบวันที่ไม่ถูกต้อง: {args.date} (ใช้ YYYYMMDD)")
        return

    company = args.company

    # สร้างชื่อไฟล์จาก --date
    file_report = str(REPORT_DIR / f'Report_{company}_{month}.xlsx')
    file_source_gl = str(DATA_DIR / f'TRN_PL_GLGROUP_{company}_MTH_TABLE_{args.date}.csv')
    file_stmt_txt = str(DATA_DIR / f'pld_{company.lower()}_{args.date}.txt')

    print(f"\n📅 วันที่รายงาน: {date_obj.strftime('%d/%m/%Y')}")
    print(f"🏢 บริษัท: {company}")

    # ==========================================
    # โหลดข้อมูล
    # ==========================================

    print(f"\nกำลังอ่านข้อมูลจากไฟล์ Excel: {file_report} ...")
    try:
        df_rep_cost = pd.read_excel(file_report, sheet_name=SHEETS['cost_biz'], header=None)
        df_rep_gl   = pd.read_excel(file_report, sheet_name=SHEETS['gl_biz'], header=None)
    except FileNotFoundError:
        print(f"❌ ไม่พบไฟล์: {file_report}")
        print(f"   กรุณา copy จาก report_generator/output/ มาไว้ใน report/")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    print(f"กำลังอ่านข้อมูลจากไฟล์ CSV: {file_source_gl} ...")
    try:
        df_src_gl = pd.read_csv(file_source_gl, encoding='cp874')
    except FileNotFoundError:
        print(f"❌ ไม่พบไฟล์: {file_source_gl}")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    print(f"กำลังอ่านข้อมูลจากไฟล์ Text: {file_stmt_txt} ...")
    try:
        with open(file_stmt_txt, 'r', encoding='cp874') as f:
            txt_lines = f.readlines()
    except FileNotFoundError:
        print(f"⚠️  ไม่พบไฟล์งบการเงิน: {file_stmt_txt} (ข้าม check 3)")
        txt_lines = None
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # ==========================================
    # ดึงค่าและเปรียบเทียบ
    # ==========================================

    # --- Source Data ---
    src_net_profit = df_src_gl[df_src_gl['GROUP'].str.contains('สุทธิ', na=False)]['VALUE'].sum()

    # --- Report Data (Excel) ---
    rep_cost_net_profit = get_val_from_df(df_rep_cost, ['กำไร', 'สุทธิ'])

    rep_gl_revenue = get_val_from_df(df_rep_gl, ['รวมรายได้'])
    if rep_gl_revenue is None:
        rep_gl_revenue = get_val_from_df(df_rep_gl, ['1', 'รายได้'])

    rep_gl_net_profit = get_val_from_df(df_rep_gl, ['กำไร', 'สุทธิ'])

    # --- Financial Stmt (Text) ---
    txt_net_profit = get_text_val(txt_lines, ['กำไร', 'สุทธิ']) if txt_lines else None

    # ==========================================
    # แสดงผลลัพธ์
    # ==========================================

    results = [
        {
            'Check': '1. Consistency (Cost Sheet vs GL Sheet)',
            'Val1': rep_cost_net_profit, 'Val2': rep_gl_net_profit,
            'Desc': 'กำไรสุทธิใน Excel 2 Sheet ต้องเท่ากัน'
        },
        {
            'Check': '2. Accuracy (Source CSV vs Report GL)',
            'Val1': src_net_profit, 'Val2': rep_gl_net_profit,
            'Desc': 'กำไรสุทธิจาก CSV ต้องเท่ากับ Excel'
        },
    ]

    if txt_net_profit is not None:
        results.append({
            'Check': '3. Tie-out (Report GL vs Financial Stmt)',
            'Val1': rep_gl_net_profit, 'Val2': txt_net_profit,
            'Desc': 'กำไรสุทธิใน Excel ต้องตรงกับงบการเงิน (Text)'
        })

    print("\n" + "=" * 80)
    print(f"{'รายการตรวจสอบ':<45} | {'Diff':>12} | {'ผลลัพธ์'}")
    print("=" * 80)

    all_pass = True
    for r in results:
        v1 = r['Val1'] if r['Val1'] else 0
        v2 = r['Val2'] if r['Val2'] else 0
        diff = v1 - v2
        status = "✅ PASS" if abs(diff) < 1.0 else "❌ FAIL"
        if status == "❌ FAIL":
            all_pass = False

        print(f"{r['Check']:<45} | {diff:12,.2f} | {status}")
        if status == "❌ FAIL":
            print(f"   └─ {r['Desc']}")
            print(f"   └─ ค่าซ้าย: {v1:,.2f} | ค่าขวา: {v2:,.2f}")

    print("=" * 80)
    if all_pass:
        print("สรุป: ผ่านทุกรายการ ✅")
    else:
        print("สรุป: พบรายการที่ไม่ตรงกัน ❌")


if __name__ == '__main__':
    main()

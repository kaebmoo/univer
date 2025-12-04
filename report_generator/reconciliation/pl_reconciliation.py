import pandas as pd
import os

# ==========================================
# ส่วนที่ 1: กำหนดชื่อไฟล์และ Sheet (Configuration)
# ==========================================

# ชื่อไฟล์ Excel (แก้ชื่อไฟล์ตรงนี้)
FILE_REPORT_MONTHLY = 'report_generator/reconciliation/Report_NT_202510.xlsx'  
FILE_SOURCE_GL = 'report_generator/reconciliation/TRN_PL_GLGROUP_NT_MTH_TABLE_20251031.csv' # ไฟล์ Source ยังคงเป็น CSV
FILE_STMT_TXT = 'report_generator/reconciliation/pld_nt_20251031.txt'

# ชื่อ Sheet ในไฟล์ Excel (ต้องสะกดให้ตรงเป๊ะกับในไฟล์)
SHEETS = {
    'cost_biz': 'ต้นทุน_กลุ่มธุรกิจ',      # ใช้สำหรับเช็คยอดรวมฝั่งต้นทุน
    'gl_biz':   'หมวดบัญชี_กลุ่มธุรกิจ'   # ใช้สำหรับเช็คยอดรวมฝั่งบัญชี (และเทียบกับงบ)
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

def get_val_from_df(df, keywords, col_index=2):
    """ค้นหาตัวเลขใน DataFrame (แบบไม่มี Header)"""
    for i, row in df.iterrows():
        # แปลงเป็น string ก่อนค้นหา เพื่อกัน error กรณีเจอ cell ว่าง
        desc = str(row[1]) 
        if all(k in desc for k in keywords):
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
# ส่วนที่ 3: โหลดข้อมูลจาก Excel และ Source
# ==========================================

print(f"กำลังอ่านข้อมูลจากไฟล์ Excel: {FILE_REPORT_MONTHLY} ...")

try:
    # 1. อ่านไฟล์ Excel (ระบุ Sheet Name)
    # header=None คือให้อ่านมาทั้งแผ่นเป็นกระดาน แล้วเราค่อยไปวนหาบรรทัดเอง (เหมาะกับรายงานที่มีหัวกระดาษรกๆ)
    df_rep_cost = pd.read_excel(FILE_REPORT_MONTHLY, sheet_name=SHEETS['cost_biz'], header=None)
    df_rep_gl   = pd.read_excel(FILE_REPORT_MONTHLY, sheet_name=SHEETS['gl_biz'], header=None)
    
    # 2. อ่านไฟล์ Source & Text
    print(f"กำลังอ่านข้อมูลจากไฟล์ csv: {FILE_SOURCE_GL} ...")
    df_src_gl = pd.read_csv(FILE_SOURCE_GL, encoding='cp874')
    with open(FILE_STMT_TXT, 'r', encoding='cp874') as f:
        txt_lines = f.readlines()

except Exception as e:
    print(f"❌ Error: {e}")
    exit()

# ==========================================
# ส่วนที่ 4: ดึงค่าและเปรียบเทียบ
# ==========================================

# --- Source Data ---
src_net_profit = df_src_gl[df_src_gl['GROUP'].str.contains('สุทธิ', na=False)]['VALUE'].sum()

# --- Report Data (Excel) ---
# อ่านค่าจาก Sheet 'ต้นทุน_กลุ่มธุรกิจ'
rep_cost_net_profit = get_val_from_df(df_rep_cost, ['กำไร', 'สุทธิ'])

# อ่านค่าจาก Sheet 'หมวดบัญชี_กลุ่มธุรกิจ'
rep_gl_revenue    = get_val_from_df(df_rep_gl, ['รวมรายได้']) 
if rep_gl_revenue is None: 
    rep_gl_revenue = get_val_from_df(df_rep_gl, ['1', 'รายได้'])

rep_gl_net_profit = get_val_from_df(df_rep_gl, ['กำไร', 'สุทธิ'])

# --- Financial Stmt (Text) ---
txt_net_profit = get_text_val(txt_lines, ['กำไร', 'สุทธิ'])

# ==========================================
# ส่วนที่ 5: แสดงผลลัพธ์
# ==========================================

results = [
    {
        'Check': '1. Check Consistency (Cost Sheet vs GL Sheet)',
        'Val1': rep_cost_net_profit, 'Val2': rep_gl_net_profit,
        'Desc': 'กำไรสุทธิใน Excel 2 Sheet ต้องเท่ากัน'
    },
    {
        'Check': '2. Check Accuracy (Source vs Report GL)',
        'Val1': src_net_profit, 'Val2': rep_gl_net_profit,
        'Desc': 'กำไรสุทธิจาก CSV ต้องเท่ากับ Excel'
    },
    {
        'Check': '3. Check Tie-out (Report GL vs Financial Stmt)',
        'Val1': rep_gl_net_profit, 'Val2': txt_net_profit,
        'Desc': 'กำไรสุทธิใน Excel ต้องตรงกับงบการเงิน (Text)'
    }
]

print("\n" + "="*80)
print(f"{'รายการตรวจสอบ':<45} | {'Diff':>10} | {'ผลลัพธ์'}")
print("="*80)

for r in results:
    v1 = r['Val1'] if r['Val1'] else 0
    v2 = r['Val2'] if r['Val2'] else 0
    diff = v1 - v2
    status = "✅ PASS" if abs(diff) < 1.0 else "❌ FAIL"
    
    print(f"{r['Check']:<45} | {diff:10,.2f} | {status}")
    if status == "❌ FAIL":
        print(f"   L_ {r['Desc']}")
        print(f"   L_ ค่าซ้าย: {v1:,.2f} | ค่าขวา: {v2:,.2f}")

print("="*80)
'''
วิธีการนำไปใช้

    ติดตั้ง Library: หากเครื่องยังไม่มี pandas ให้ติดตั้งด้วยคำสั่ง pip install pandas openpyxl

    เตรียมไฟล์: วางไฟล์ CSV และ Text ไฟล์ไว้ใน Folder เดียวกับ Script นี้

    แก้ไขชื่อไฟล์: เปลี่ยนชื่อไฟล์ในตัวแปร FILES ด้านบนสุดของ Code ให้ตรงกับชื่อไฟล์จริงของคุณ

    รัน Code: เมื่อรันแล้ว โปรแกรมจะแสดงตารางสรุปว่า Pass หรือ Fail 
'''

import pandas as pd
import re

# ==========================================
# ส่วนที่ 1: กำหนดชื่อไฟล์ (Configuration)
# ==========================================
# คุณสามารถเปลี่ยนชื่อไฟล์ตรงนี้เมื่อต้องการตรวจสอบเดือนถัดไป
FILES = {
    'source_cost': 'TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv',      # ไฟล์ Source: ประเภทต้นทุน
    'source_gl':   'TRN_PL_GLGROUP_NT_MTH_TABLE_20251031.csv',        # ไฟล์ Source: หมวดบัญชี
    'report_cost': 'Report_NT_202510.xlsx - ต้นทุน_กลุ่มธุรกิจ.csv',      # ไฟล์ Report: ประเภทต้นทุน
    'report_gl':   'Report_NT_202510.xlsx - หมวดบัญชี_กลุ่มธุรกิจ.csv',   # ไฟล์ Report: หมวดบัญชี
    'stmt_txt':    'pld_nt_20251031.txt'                             # ไฟล์ Text: งบการเงิน
}

# ==========================================
# ส่วนที่ 2: ฟังก์ชันช่วยกรองข้อมูล (Helper Functions)
# ==========================================

def parse_thai_number(text):
    """แปลงข้อความตัวเลขที่มีลูกน้ำหรือวงเล็บให้เป็น Float"""
    if pd.isna(text): return 0.0
    text = str(text).strip()
    if text == '-' or text == '': return 0.0
    # แปลงวงเล็บ (100) ให้เป็น -100
    if '(' in text and ')' in text:
        text = '-' + text.replace('(', '').replace(')', '')
    text = text.replace(',', '') # เอาลูกน้ำออก
    try:
        return float(text)
    except ValueError:
        return 0.0

def get_report_value(df, keywords, col_index=2):
    """ค้นหาตัวเลขในไฟล์ Report โดยดูจากคำในคอลัมน์แรก"""
    # วนลูปหาบรรทัดที่มี keywords ครบทุกคำ
    for i, row in df.iterrows():
        desc = str(row[1]) 
        if all(k in desc for k in keywords):
            return parse_thai_number(row[col_index])
    return None

def get_text_file_value(lines, keywords):
    """ค้นหาตัวเลขในไฟล์ Text โดยดูจากคำสำคัญ"""
    for line in lines:
        if all(k in line for k in keywords):
            tokens = line.split()
            # กรองเอาเฉพาะส่วนที่เป็นตัวเลข
            for t in tokens:
                if any(c.isdigit() for c in t):
                    try:
                        return parse_thai_number(t)
                    except:
                        pass
    return None

# ==========================================
# ส่วนที่ 3: เริ่มต้นการทำงาน (Main Execution)
# ==========================================

print("กำลังโหลดข้อมูลและตรวจสอบ...")

# 1. โหลดข้อมูล (Load Data)
try:
    df_src_cost = pd.read_csv(FILES['source_cost'])
    df_src_gl = pd.read_csv(FILES['source_gl'])
    df_rep_cost = pd.read_csv(FILES['report_cost'], header=None)
    df_rep_gl = pd.read_csv(FILES['report_gl'], header=None)
    with open(FILES['stmt_txt'], 'r', encoding='utf-8') as f:
        txt_lines = f.readlines()
except FileNotFoundError as e:
    print(f"Error: ไม่พบไฟล์ - {e}")
    exit()

# 2. ดึงค่าตัวเลขที่ต้องการ (Extract Values)

# --- ฝั่ง Source Data ---
# ยอดรายได้รวม (ดึงจาก GL Group จะครบถ้วนกว่า)
src_revenue = df_src_gl[df_src_gl['GROUP'].str.contains('รายได้', na=False)]['VALUE'].sum()
# ยอดกำไรสุทธิ (ดึงจากบรรทัดที่ระบุว่า สุทธิ)
src_net_profit = df_src_gl[df_src_gl['GROUP'].str.contains('สุทธิ', na=False)]['VALUE'].sum()

# --- ฝั่ง Report (Excel) ---
# ยอดรายได้รวม
rep_revenue = get_report_value(df_rep_gl, ['รวมรายได้']) 
if rep_revenue is None: 
    rep_revenue = get_report_value(df_rep_gl, ['1', 'รายได้']) # เผื่อกรณีชื่อไม่ตรงเป๊ะ
# ยอดกำไรสุทธิ (จากรายงาน 2 ฉบับ ต้องเท่ากัน)
rep_cost_net_profit = get_report_value(df_rep_cost, ['กำไร', 'สุทธิ'])
rep_gl_net_profit = get_report_value(df_rep_gl, ['กำไร', 'สุทธิ'])

# --- ฝั่งงบการเงิน (Text File) ---
txt_net_profit = get_text_file_value(txt_lines, ['กำไร', 'สุทธิ'])

# 3. เปรียบเทียบและแสดงผล (Compare & Print)

results = []
# Check 1: ตรวจสอบรายได้ (Source vs Report)
results.append({
    'Title': '1. Revenue Check (Source vs Report)',
    'Val_A': src_revenue,
    'Val_B': rep_revenue
})
# Check 2: ตรวจสอบกำไรสุทธิ (Source vs Report)
results.append({
    'Title': '2. Net Profit Check (Source vs Report)',
    'Val_A': src_net_profit,
    'Val_B': rep_gl_net_profit
})
# Check 3: ตรวจสอบความสอดคล้อง (Cost Report vs GL Report)
results.append({
    'Title': '3. Consistency Check (Cost vs GL Report)',
    'Val_A': rep_cost_net_profit,
    'Val_B': rep_gl_net_profit
})
# Check 4: ตรวจสอบกับงบการเงิน (Report vs Financial Stmt)
results.append({
    'Title': '4. Financial Stmt Tie-out (Report vs GL)',
    'Val_A': rep_gl_net_profit,
    'Val_B': txt_net_profit
})

# แสดงตารางผลลัพธ์
print(f"\n{'CHECKPOINT / รายการตรวจสอบ':<45} | {'SOURCE / ฝั่งซ้าย':>15} | {'TARGET / ฝั่งขวา':>15} | {'DIFF / ผลต่าง':>10} | {'STATUS'}")
print("-" * 105)

all_pass = True
for r in results:
    val_a = r['Val_A'] if r['Val_A'] is not None else 0
    val_b = r['Val_B'] if r['Val_B'] is not None else 0
    diff = val_a - val_b
    status = "PASS" if abs(diff) < 1.0 else "FAIL" # ยอมรับผลต่างทศนิยมเล็กน้อย
    
    if status == "FAIL": all_pass = False
    
    print(f"{r['Title']:<45} | {val_a:15,.2f} | {val_b:15,.2f} | {diff:10,.2f} | {status}")

print("-" * 105)
if all_pass:
    print("\n✅ สรุปผล: ข้อมูลถูกต้องครบถ้วนทุกรายการ (All Passed)")
else:
    print("\n❌ สรุปผล: พบรายการที่ไม่ตรงกัน กรุณาตรวจสอบ (Found Mismatch)")
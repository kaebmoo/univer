import sys
import os

sys.path.insert(0, 'src')

# Test import
# report_generator/src/data_loader
# 1. หาตำแหน่งของไฟล์ debug.py ปัจจุบัน
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. ถอยหลังกลับไป 2 ขั้น เพื่อไปหา root folder (report_generator)
# ขั้นที่ 1: ถอยจาก debug.py -> tests
# ขั้นที่ 2: ถอยจาก tests -> report_generator
project_root = os.path.dirname(current_dir)

# 3. ชี้เป้าไปที่ folder 'src'
src_path = os.path.join(project_root, 'src')

# 4. เพิ่ม path นี้เข้าไปในระบบ เพื่อให้ Python มองเห็น
sys.path.append(src_path)

from data_loader.data_aggregator import DataAggregator
import pandas as pd

# Create dummy data
df = pd.DataFrame({
    'GROUP': ['01.รายได้'],
    'SUB_GROUP': ['01.รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน'],
    'BU': ['1.กลุ่มธุรกิจ HARD INFRASTRUCTURE'],
    'SERVICE_GROUP': ['1.Infrastructure'],
    'PRODUCT_KEY': ['PROD1'],
    'VALUE': [1000.0]
})

agg = DataAggregator(df)

# Test _sum_rows_glgroup
all_row_data = {
    "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน": {"GRAND_TOTAL": 1000.0}
}

result = agg._sum_rows_glgroup(all_row_data, ["- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน"])
print(f"Result: {result}")
print(f"Expected: {{'GRAND_TOTAL': 1000.0}}")

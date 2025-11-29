#!/usr/bin/env python3
"""
Show all SUB_GROUPs for expense (GROUP 02)
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data_loader import CSVLoader, DataProcessor

csv_path = project_root / "data" / "TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv"
loader = CSVLoader()
df = loader.load_csv(csv_path)
processor = DataProcessor()
df = processor.process_data(df)

# Get expense sub-groups
expense_df = df[df['GROUP'] == '02.ค่าใช้จ่าย']
sub_groups = sorted(expense_df['SUB_GROUP'].unique())

print("SUB_GROUPs for 02.ค่าใช้จ่าย:")
print("="*70)
for i, sg in enumerate(sub_groups, 1):
    print(f"{i:2d}. {sg}")

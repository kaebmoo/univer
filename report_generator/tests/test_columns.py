#!/usr/bin/env python3
"""Test column building"""
import pandas as pd
from pathlib import Path
from src.data_loader import CSVLoader, DataProcessor
from src.report_generator import ReportConfig
from src.report_generator.columns.bu_sg_builder import BUSGBuilder

# Load and process data
loader = CSVLoader(encoding='tis-620')
df = loader.load_csv(Path('data/TRN_PL_COSTTYPE_NT_YTD_TABLE_20251031.csv'))
processor = DataProcessor()
df = processor.process_data(df)

# Create config
config = ReportConfig(
    report_type='COSTTYPE',
    period_type='YTD',
    detail_level='BU_SG',
    include_common_size=False
)

# Build columns
builder = BUSGBuilder(config)
columns = builder.build_columns(df)

# Filter to show FIXED LINE & BROADBAND columns only
print("Columns for BU: 4.กลุ่มธุรกิจ FIXED LINE & BROADBAND")
print("=" * 80)
for idx, col in enumerate(columns):
    if col.bu == '4.กลุ่มธุรกิจ FIXED LINE & BROADBAND':
        print(f"{idx:3d}. {col.col_type:20s} | {col.name}")

print("\n" + "=" * 80)
print(f"Total columns: {len(columns)}")

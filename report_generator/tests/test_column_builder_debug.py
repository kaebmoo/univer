#!/usr/bin/env python3
"""Debug column builder for COSTTYPE BU_SG"""
import pandas as pd
from pathlib import Path
from src.data_loader import CSVLoader, DataProcessor
from src.report_generator.core.config import ReportConfig
from src.report_generator.columns.bu_sg_builder import BUSGBuilder

# Load data
loader = CSVLoader(encoding='tis-620')
df = loader.load_csv(Path('data/TRN_PL_COSTTYPE_NT_YTD_TABLE_SAT_20251031.csv'))
processor = DataProcessor()
df = processor.process_data(df)

# Create config
config = ReportConfig(
    report_type="COSTTYPE",
    period_type="YTD",
    detail_level="BU_SG"
)

# Build columns
builder = BUSGBuilder(config)
columns = builder.build_columns(df)

# Check BU 4 columns
bu4 = "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND"
bu4_columns = [col for col in columns if col.bu == bu4]

print(f"BU 4 columns: {len(bu4_columns)}")
print("="*80)

for idx, col in enumerate(bu4_columns):
    print(f"{idx+1}. {col.col_type:20s} | {col.service_group if col.service_group else 'N/A'}")

# Check if any are satellite_summary
has_satellite = any(col.col_type == 'satellite_summary' for col in bu4_columns)
print()
if has_satellite:
    print("✓ SATELLITE summary column found")
else:
    print("❌ NO SATELLITE summary column")

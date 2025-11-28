#!/usr/bin/env python3
"""
Simple runner - avoids settings import
"""
import subprocess
import sys

# Run with Python's -c option to avoid importing settings at module level
code = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

# Now safe to import after path is set
from src.report_generator import ReportGenerator
from config.report_config import ReportConfig
from config.types import ReportType, DetailLevel, PeriodType
from src.data_loader import CSVLoader, DataProcessor

csv_path = "data/TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv"
output = "output/GLGROUP_TEST.xlsx"

config = ReportConfig(
    report_type=ReportType.GLGROUP,
    detail_level=DetailLevel.BU_ONLY,
    period_type=PeriodType.YTD
)

loader = CSVLoader()
df = loader.load(csv_path)

processor = DataProcessor()
processed = processor.process(df)

generator = ReportGenerator(config)
generator.generate(processed, output)

print(f"✅ Generated: {output}")
"""

result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)
sys.exit(result.returncode)

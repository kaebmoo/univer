#!/usr/bin/env python3
"""
Direct Test - Generate GLGROUP report without using CLI
Bypasses settings.py to avoid .env parsing issues
"""
import sys
from pathlib import Path
import pandas as pd
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path (parent of tests directory)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("="*70)
print("GLGROUP Direct Test")
print("="*70)

try:
    # Import core modules (avoid CLI which imports settings)
    # Use ReportConfig from report_generator (has all required attributes)
    from src.report_generator import ReportBuilder, ReportConfig, ReportType, DetailLevel, PeriodType
    from src.data_loader import CSVLoader, DataProcessor, DataAggregator
    
    # Setup paths (project_root is now report_generator directory)
    csv_path = project_root / "data" / "TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv"
    output_dir = project_root / "output"
    output_path = output_dir / "GLGROUP_DIRECT_TEST.xlsx"
    
    # Create output dir
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n📂 CSV: {csv_path}")
    print(f"📊 Output: {output_path}")
    
    # Check CSV exists
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    
    # Create config
    print("\n🔧 Creating config...")
    config = ReportConfig(
        report_type=ReportType.GLGROUP,
        detail_level=DetailLevel.BU_ONLY,
        period_type=PeriodType.YTD
    )
    print(f"   Report Type: {config.report_type.value}")
    print(f"   Detail Level: {config.detail_level.value}")
    print(f"   Period: {config.period_type.value}")
    
    # Load CSV
    print("\n📥 Loading CSV...")
    loader = CSVLoader()
    df = loader.load_csv(csv_path)  # Changed: load() -> load_csv()
    print(f"   Loaded {len(df)} rows")
    
    # Process data
    print("\n⚙️  Processing data...")
    processor = DataProcessor()
    processed_df = processor.process_data(df)  # Changed: process() -> process_data()
    print(f"   Processed {len(processed_df)} rows")
    
    # Create aggregator
    print("\n📊 Creating aggregator...")
    aggregator = DataAggregator(processed_df)
    
    # Generate report
    print("\n📝 Generating report...")
    builder = ReportBuilder(config)
    builder.generate_report(processed_df, output_path, remark_content="")  # Added remark_content parameter
    
    # Check output
    if output_path.exists():
        size_kb = output_path.stat().st_size / 1024
        print(f"\n✅ SUCCESS!")
        print(f"   File: {output_path}")
        print(f"   Size: {size_kb:.1f} KB")
        print("\n🎉 Report generated successfully!")
    else:
        print("\n❌ FAILED: Output file not created")
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)

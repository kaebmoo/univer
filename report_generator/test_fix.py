#!/usr/bin/env python3
"""
Quick Fix Test - Test the fixed column_header_writer
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("Quick Fix Test - Column Headers")
print("="*60)

try:
    from src.report_generator import ReportBuilder, ReportConfig
    from src.data_loader import CSVLoader, DataProcessor
    
    csv_path = Path("data/TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv")
    
    if not csv_path.exists():
        print("❌ Data file not found")
        sys.exit(1)
    
    print("\n1. Loading data...")
    csv_loader = CSVLoader(encoding='tis-620')
    df = csv_loader.load_csv(csv_path)
    
    processor = DataProcessor()
    df = processor.process_data(df)
    print("   ✅ Data loaded")
    
    print("\n2. Generating with FIXED writer...")
    config = ReportConfig(
        report_type="COSTTYPE",
        period_type="MTH",
        detail_level="BU_SG_PRODUCT"
    )
    
    builder = ReportBuilder(config)
    
    output_path = Path("output/fixed_method.xlsx")
    
    # Load remark
    remark_file = csv_path.parent / "remark_MTH.txt"
    remark_content = ""
    if remark_file.exists():
        try:
            for enc in ['utf-8', 'tis-620', 'cp874']:
                try:
                    with open(remark_file, 'r', encoding=enc) as f:
                        remark_content = f.read()
                    break
                except:
                    continue
        except:
            pass
    
    builder.generate_report(df, output_path, remark_content)
    
    print(f"   ✅ Report generated: {output_path}")
    print(f"   ✅ File size: {output_path.stat().st_size / 1024:.1f} KB")
    
    print("\n" + "="*60)
    print("✅ FIXED VERSION GENERATED!")
    print("="*60)
    print(f"\nOutput: {output_path.absolute()}")
    print("\nPlease open in Excel and check:")
    print("  1. No repair warnings")
    print("  2. BU headers have correct colors")
    print("  3. SG headers have correct colors")
    print("  4. Product headers have correct colors")
    print("  5. Merge cells are correct")
    
except Exception as e:
    print("\n❌ ERROR!")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

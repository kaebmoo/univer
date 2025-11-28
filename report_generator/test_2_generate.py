#!/usr/bin/env python3
"""
Test Script 2: Report Generation Test
Test if report can be generated successfully
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("Test 2: Generate Report")
print("="*60)

try:
    print("\n1. Importing modules...")
    from src.report_generator import ReportBuilder, ReportConfig
    from src.data_loader import CSVLoader, DataProcessor
    print("   ✅ Imports successful")
    
    print("\n2. Checking for data file...")
    csv_path = Path("data/TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv")
    
    if not csv_path.exists():
        print(f"   ❌ Data file not found: {csv_path}")
        print("\n   Please ensure data file exists at:")
        print(f"   {csv_path.absolute()}")
        sys.exit(1)
    
    print(f"   ✅ Data file found: {csv_path}")
    
    print("\n3. Loading CSV data...")
    csv_loader = CSVLoader(encoding='tis-620')
    df = csv_loader.load_csv(csv_path)
    print(f"   ✅ Loaded {len(df)} rows")
    
    print("\n4. Processing data...")
    data_processor = DataProcessor()
    df = data_processor.process_data(df)
    print(f"   ✅ Data processed")
    
    print("\n5. Creating report config...")
    config = ReportConfig(
        report_type="COSTTYPE",
        period_type="MTH",
        detail_level="BU_SG_PRODUCT"
    )
    print(f"   ✅ Config: {config.report_type.value} - {config.period_type.value}")
    
    print("\n6. Creating report builder...")
    builder = ReportBuilder(config)
    print("   ✅ Builder created")
    
    print("\n7. Generating report...")
    output_path = Path("output/test_new_module.xlsx")
    output_path.parent.mkdir(exist_ok=True)
    
    # Load remark if exists
    remark_file = csv_path.parent / "remark_MTH.txt"
    remark_content = ""
    if remark_file.exists():
        try:
            for enc in ['utf-8', 'tis-620', 'cp874']:
                try:
                    with open(remark_file, 'r', encoding=enc) as f:
                        remark_content = f.read()
                    print(f"   ✅ Loaded remarks ({enc})")
                    break
                except:
                    continue
        except:
            print("   ⚠️  Could not load remarks")
    
    result_path = builder.generate_report(df, output_path, remark_content)
    print(f"   ✅ Report generated!")
    
    print("\n8. Verifying output file...")
    if result_path.exists():
        file_size = result_path.stat().st_size / 1024  # KB
        print(f"   ✅ File exists: {result_path}")
        print(f"   ✅ File size: {file_size:.1f} KB")
    else:
        print(f"   ❌ File not found: {result_path}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ REPORT GENERATION TEST PASSED!")
    print("="*60)
    print(f"\nGenerated file: {result_path.absolute()}")
    print("\nNext steps:")
    print("1. Open the file in Excel")
    print("2. Compare with output from main_generator.py")
    print("3. Verify all columns and calculations are correct")
    
except Exception as e:
    print("\n" + "="*60)
    print("❌ REPORT GENERATION TEST FAILED!")
    print("="*60)
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

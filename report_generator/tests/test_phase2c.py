#!/usr/bin/env python3
"""
Test Phase 2C - Simplified Builders
Test BU Only and BU+SG builders
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*60)
print("Phase 2C Test - Simplified Builders")
print("="*60)

try:
    from src.report_generator import ReportBuilder, ReportConfig
    from src.data_loader import CSVLoader, DataProcessor
    
    csv_path = Path(__file__).parent.parent / "data" / "TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv"
    
    if not csv_path.exists():
        print("❌ Data file not found")
        sys.exit(1)
    
    print("\n1. Loading data...")
    csv_loader = CSVLoader(encoding='tis-620')
    df = csv_loader.load_csv(csv_path)
    
    processor = DataProcessor()
    df = processor.process_data(df)
    print(f"   ✅ Data loaded ({len(df)} rows)")
    
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
    
    # Test 1: BU Only
    print("\n" + "="*60)
    print("Test 1: BU Only Builder")
    print("="*60)
    
    print("\n2. Creating BU_ONLY config...")
    config1 = ReportConfig(
        report_type="COSTTYPE",
        period_type="MTH",
        detail_level="BU_ONLY"
    )
    print(f"   ✅ Config: {config1.detail_level.value}")
    
    print("\n3. Creating builder...")
    builder1 = ReportBuilder(config1)
    print(f"   ✅ Builder: {type(builder1.column_builder).__name__}")
    
    print("\n4. Generating BU Only report...")
    output1 = Path(__file__).parent.parent / "output" / "bu_only_report.xlsx"
    
    try:
        builder1.generate_report(df, output1, remark_content)
        print(f"   ✅ Report generated: {output1}")
        print(f"   ✅ File size: {output1.stat().st_size / 1024:.1f} KB")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: BU + SG
    print("\n" + "="*60)
    print("Test 2: BU + SG Builder")
    print("="*60)
    
    print("\n5. Creating BU_SG config...")
    config2 = ReportConfig(
        report_type="COSTTYPE",
        period_type="MTH",
        detail_level="BU_SG"
    )
    print(f"   ✅ Config: {config2.detail_level.value}")
    
    print("\n6. Creating builder...")
    builder2 = ReportBuilder(config2)
    print(f"   ✅ Builder: {type(builder2.column_builder).__name__}")
    
    print("\n7. Generating BU+SG report...")
    output2 = Path(__file__).parent.parent / "output" / "bu_sg_report.xlsx"
    
    try:
        builder2.generate_report(df, output2, remark_content)
        print(f"   ✅ Report generated: {output2}")
        print(f"   ✅ File size: {output2.stat().st_size / 1024:.1f} KB")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: BU + SG + Product (existing)
    print("\n" + "="*60)
    print("Test 3: BU + SG + Product Builder (verification)")
    print("="*60)
    
    print("\n8. Creating BU_SG_PRODUCT config...")
    config3 = ReportConfig(
        report_type="COSTTYPE",
        period_type="MTH",
        detail_level="BU_SG_PRODUCT"
    )
    print(f"   ✅ Config: {config3.detail_level.value}")
    
    print("\n9. Creating builder...")
    builder3 = ReportBuilder(config3)
    print(f"   ✅ Builder: {type(builder3.column_builder).__name__}")
    
    print("\n10. Generating BU+SG+Product report...")
    output3 = Path(__file__).parent.parent / "output" / "bu_sg_product_report.xlsx"
    
    try:
        builder3.generate_report(df, output3, remark_content)
        print(f"   ✅ Report generated: {output3}")
        print(f"   ✅ File size: {output3.stat().st_size / 1024:.1f} KB")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("PHASE 2C TEST SUMMARY")
    print("="*60)
    
    results = []
    for path, name in [
        (output1, "BU Only"),
        (output2, "BU + SG"),
        (output3, "BU + SG + Product")
    ]:
        if path.exists():
            size = path.stat().st_size / 1024
            results.append((name, "✅ PASS", f"{size:.1f} KB"))
        else:
            results.append((name, "❌ FAIL", "Not generated"))
    
    for name, status, info in results:
        print(f"{status} - {name:20s} ({info})")
    
    passed = sum(1 for _, status, _ in results if status == "✅ PASS")
    total = len(results)
    
    print(f"\nResult: {passed}/{total} reports generated")
    
    if passed == total:
        print("\n🎉 ALL BUILDERS WORKING!")
        print("\nGenerated files:")
        for path, name in [
            (output1, "BU Only"),
            (output2, "BU + SG"),
            (output3, "BU + SG + Product")
        ]:
            print(f"  - {path.absolute()} ({name})")
    else:
        print("\n⚠️  SOME BUILDERS FAILED")
        print("Check errors above")
    
except Exception as e:
    print("\n" + "="*60)
    print("❌ PHASE 2C TEST FAILED!")
    print("="*60)
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

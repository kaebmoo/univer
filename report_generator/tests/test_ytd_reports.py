#!/usr/bin/env python3
"""
Test YTD Reports - All Detail Levels with Proper Naming
Generate: BU_ONLY, BU_SG, BU_SG_PRODUCT for YTD data
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*70)
print("YTD Report Generation Test - All Detail Levels")
print("="*70)

try:
    from src.report_generator import ReportBuilder, ReportConfig
    from src.data_loader import CSVLoader, DataProcessor
    
    # Data file
    csv_path = Path(__file__).parent.parent / "data" / "TRN_PL_COSTTYPE_NT_YTD_TABLE_20251031.csv"
    
    if not csv_path.exists():
        print(f"❌ Data file not found: {csv_path}")
        sys.exit(1)
    
    print(f"\n📁 Data file: {csv_path.name}")
    
    # Load data
    print("\n1. Loading data...")
    csv_loader = CSVLoader(encoding='tis-620')
    df = csv_loader.load_csv(csv_path)
    
    processor = DataProcessor()
    df = processor.process_data(df)
    print(f"   ✅ Data loaded ({len(df)} rows)")
    
    # Load remark
    remark_file = csv_path.parent / "remark_YTD.txt"
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
    
    # Extract period from filename (202510)
    period = csv_path.stem.split('_')[-1]  # 20251031 -> use as 202510
    if len(period) == 8:  # YYYYMMDD
        period = period[:6]  # YYYYMM
    
    print(f"   📅 Period: {period}")
    
    # Test configurations
    tests = [
        {
            'name': 'BU Only',
            'detail_level': 'BU_ONLY',
            'filename': f'P&L_COSTTYPE_YTD_{period}_BU_ONLY.xlsx'
        },
        {
            'name': 'BU + SG',
            'detail_level': 'BU_SG',
            'filename': f'P&L_COSTTYPE_YTD_{period}_BU_SG.xlsx'
        },
        {
            'name': 'BU + SG + Product',
            'detail_level': 'BU_SG_PRODUCT',
            'filename': f'P&L_COSTTYPE_YTD_{period}_FULL.xlsx'
        }
    ]
    
    results = []
    
    for idx, test in enumerate(tests, 1):
        print(f"\n{'='*70}")
        print(f"Test {idx}: {test['name']}")
        print(f"{'='*70}")
        
        print(f"\n2. Creating config (YTD, {test['detail_level']})...")
        config = ReportConfig(
            report_type="COSTTYPE",
            period_type="YTD",
            detail_level=test['detail_level']
        )
        print(f"   ✅ Config: {config.report_type.value} / {config.period_type.value} / {config.detail_level.value}")
        
        print(f"\n3. Creating builder...")
        builder = ReportBuilder(config)
        print(f"   ✅ Builder: {type(builder.column_builder).__name__}")
        
        print(f"\n4. Generating report...")
        output_path = Path("output") / test['filename']
        
        try:
            builder.generate_report(df, output_path, remark_content)
            
            if output_path.exists():
                size_kb = output_path.stat().st_size / 1024
                print(f"   ✅ Report generated: {test['filename']}")
                print(f"   ✅ File size: {size_kb:.1f} KB")
                results.append((test['name'], '✅ PASS', f'{size_kb:.1f} KB', test['filename']))
            else:
                print(f"   ❌ File not created!")
                results.append((test['name'], '❌ FAIL', 'Not created', test['filename']))
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append((test['name'], '❌ FAIL', str(e)[:50], test['filename']))
    
    # Summary
    print("\n" + "="*70)
    print("YTD REPORT GENERATION SUMMARY")
    print("="*70)
    
    for name, status, info, filename in results:
        print(f"{status} - {name:25s} ({info:15s}) -> {filename}")
    
    passed = sum(1 for _, status, _, _ in results if status == '✅ PASS')
    total = len(results)
    
    print(f"\nResult: {passed}/{total} reports generated")
    
    if passed == total:
        print("\n🎉 ALL YTD REPORTS GENERATED SUCCESSFULLY!")
        print("\n📊 Generated files:")
        for _, status, _, filename in results:
            if status == '✅ PASS':
                full_path = Path("output") / filename
                print(f"  - {full_path.absolute()}")
        
        print("\n📝 File naming convention:")
        print("  P&L_[REPORT_TYPE]_[PERIOD_TYPE]_[YYYYMM]_[DETAIL_LEVEL].xlsx")
        print("  Examples:")
        print(f"    - {results[0][3]} (BU totals only)")
        print(f"    - {results[1][3]} (BU + SG)")
        print(f"    - {results[2][3]} (Full detail)")
    else:
        print("\n⚠️  SOME REPORTS FAILED")
        print("Check errors above")
    
    # Verification checklist
    print("\n" + "="*70)
    print("VERIFICATION CHECKLIST")
    print("="*70)
    print("For each generated file, verify:")
    print("  [ ] Headers correct (BU, SG, Products)")
    print("  [ ] Data populated correctly")
    print("  [ ] YTD period shown in header")
    print("  [ ] 'คำนวณสัดส่วนต้นทุนบริการต่อรายได้' is EMPTY (not 0.00%)")
    print("  [ ] File opens without errors in Excel")
    print("  [ ] Filename follows convention")
    
except Exception as e:
    print("\n" + "="*70)
    print("❌ YTD TEST FAILED!")
    print("="*70)
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

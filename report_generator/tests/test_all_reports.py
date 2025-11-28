#!/usr/bin/env python3
"""
Test All Report Combinations
Generate all combinations: COSTTYPE/GLGROUP x MTH/YTD x BU_ONLY/BU_SG/BU_SG_PRODUCT
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*80)
print("COMPREHENSIVE REPORT GENERATION TEST")
print("Generate all report type combinations with proper naming")
print("="*80)

from src.report_generator import ReportBuilder, ReportConfig
from src.data_loader import CSVLoader, DataProcessor

# Data files mapping
data_files = {
    ('COSTTYPE', 'MTH'): 'TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv',
    ('COSTTYPE', 'YTD'): 'TRN_PL_COSTTYPE_NT_YTD_TABLE_20251031.csv',
    ('GLGROUP', 'MTH'): 'TRN_PL_GLGROUP_NT_MTH_TABLE_20251031.csv',
    ('GLGROUP', 'YTD'): 'TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv',
}

# Remark files
remark_files = {
    'MTH': 'remark_MTH.txt',
    'YTD': 'remark_YTD.txt'
}

detail_levels = {
    'BU_ONLY': 'BU Only',
    'BU_SG': 'BU + SG',
    'BU_SG_PRODUCT': 'Full Detail'
}

def get_filename(report_type, period_type, period, detail_level):
    """Generate output filename following convention"""
    suffix_map = {
        'BU_ONLY': 'BU_ONLY',
        'BU_SG': 'BU_SG',
        'BU_SG_PRODUCT': 'FULL'
    }
    suffix = suffix_map[detail_level]
    return f"P&L_{report_type}_{period_type}_{period}_{suffix}.xlsx"

results = []
total_tests = 0
passed_tests = 0

for (report_type, period_type), csv_filename in data_files.items():
    csv_path = Path("data") / csv_filename
    
    if not csv_path.exists():
        print(f"\n⚠️  Skipping {report_type}/{period_type}: {csv_filename} not found")
        continue
    
    print(f"\n{'='*80}")
    print(f"Data: {report_type} / {period_type}")
    print(f"File: {csv_filename}")
    print(f"{'='*80}")
    
    # Load data once
    print("\n📂 Loading data...")
    csv_loader = CSVLoader(encoding='tis-620')
    df = csv_loader.load_csv(csv_path)
    processor = DataProcessor()
    df = processor.process_data(df)
    print(f"   ✅ Loaded {len(df)} rows")
    
    # Load remark
    remark_file = Path("data") / remark_files[period_type]
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
    
    # Extract period
    period = csv_path.stem.split('_')[-1][:6]  # 20251031 -> 202510
    
    # Test each detail level
    for detail_level, detail_name in detail_levels.items():
        total_tests += 1
        
        print(f"\n  🔧 {detail_name} ({detail_level})...")
        
        try:
            # Create config
            config = ReportConfig(
                report_type=report_type,
                period_type=period_type,
                detail_level=detail_level
            )
            
            # Create builder
            builder = ReportBuilder(config)
            
            # Generate filename
            filename = get_filename(report_type, period_type, period, detail_level)
            output_path = Path("output") / filename
            
            # Generate report
            builder.generate_report(df, output_path, remark_content)
            
            if output_path.exists():
                size_kb = output_path.stat().st_size / 1024
                print(f"     ✅ Generated: {filename} ({size_kb:.1f} KB)")
                results.append((report_type, period_type, detail_name, '✅', filename, f'{size_kb:.1f} KB'))
                passed_tests += 1
            else:
                print(f"     ❌ Failed: File not created")
                results.append((report_type, period_type, detail_name, '❌', filename, 'Not created'))
        
        except Exception as e:
            print(f"     ❌ Error: {str(e)[:60]}")
            results.append((report_type, period_type, detail_name, '❌', 'N/A', str(e)[:30]))

# Summary
print("\n" + "="*80)
print("GENERATION SUMMARY")
print("="*80)

# Group by report type and period
for report_type in ['COSTTYPE', 'GLGROUP']:
    for period_type in ['MTH', 'YTD']:
        group_results = [r for r in results if r[0] == report_type and r[1] == period_type]
        if group_results:
            print(f"\n{report_type} / {period_type}:")
            for _, _, detail, status, filename, info in group_results:
                print(f"  {status} {detail:20s} -> {filename:50s} ({info})")

print(f"\n{'='*80}")
print(f"TOTAL: {passed_tests}/{total_tests} reports generated successfully")
print(f"{'='*80}")

if passed_tests == total_tests:
    print("\n🎉 ALL REPORTS GENERATED SUCCESSFULLY!")
    print("\n📁 Output directory: output/")
    print("\n📝 Naming convention:")
    print("   P&L_[REPORT_TYPE]_[PERIOD_TYPE]_[YYYYMM]_[DETAIL_LEVEL].xlsx")
    print("\n   Where:")
    print("   - REPORT_TYPE: COSTTYPE or GLGROUP")
    print("   - PERIOD_TYPE: MTH or YTD")
    print("   - YYYYMM: 202510")
    print("   - DETAIL_LEVEL: BU_ONLY, BU_SG, or FULL")
else:
    print(f"\n⚠️  {total_tests - passed_tests} report(s) failed")
    print("Check errors above")
    sys.exit(1)

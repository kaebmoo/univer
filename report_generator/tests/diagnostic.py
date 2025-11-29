#!/usr/bin/env python3
"""
Diagnostic Script - Check GLGROUP Implementation Status
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("="*70)
print("GLGROUP IMPLEMENTATION DIAGNOSTIC")
print("="*70)

# Check file existence
print("\n📁 File Check:")
files_to_check = [
    "config/types.py",
    "config/report_config.py",
    "config/row_order_glgroup.py",
    "config/data_mapping_glgroup.py",
    "src/data_loader/data_aggregator.py",
    "src/report_generator/writers/data_writer.py",
]

for file_path in files_to_check:
    full_path = project_root / file_path
    status = "✅" if full_path.exists() else "❌"
    print(f"  {status} {file_path}")

# Check GLGROUP methods in aggregator
print("\n🔍 Checking DataAggregator GLGROUP methods:")
try:
    from src.data_loader.data_aggregator import DataAggregator
    
    methods = [
        'get_row_data_glgroup',
        'calculate_summary_row_glgroup',
        '_sum_rows_glgroup'
    ]
    
    for method in methods:
        has_method = hasattr(DataAggregator, method)
        status = "✅" if has_method else "❌"
        print(f"  {status} {method}")
        
except Exception as e:
    print(f"  ❌ Error importing DataAggregator: {e}")

# Check data_writer updates
print("\n🔍 Checking data_writer.py GLGROUP support:")
try:
    with open(project_root / "src/report_generator/writers/data_writer.py", 'r') as f:
        content = f.read()
        
    checks = [
        ('is_glgroup detection', 'is_glgroup ='),
        ('GLGROUP method call', 'get_row_data_glgroup'),
        ('Tax row GLGROUP', 'is_tax_row_glgroup'),
        ('Net Profit GLGROUP', 'is_net_profit_row_glgroup'),
    ]
    
    for name, pattern in checks:
        found = pattern in content
        status = "✅" if found else "❌"
        print(f"  {status} {name}")
        
except Exception as e:
    print(f"  ❌ Error reading data_writer.py: {e}")

# Test data loading
print("\n📊 Testing GLGROUP data loading:")
try:
    from src.data_loader import CSVLoader, DataProcessor, DataAggregator
    
    csv_path = project_root / "data" / "TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv"
    
    if csv_path.exists():
        print(f"  ✅ CSV file exists: {csv_path.name}")
        
        loader = CSVLoader()
        df = loader.load_csv(csv_path)  # Pass Path object directly
        print(f"  ✅ Loaded {len(df)} rows")
        
        processor = DataProcessor()
        processed = processor.process_data(df)
        print(f"  ✅ Processed {len(processed)} rows")
        
        aggregator = DataAggregator(processed)
        print(f"  ✅ Created aggregator")
        
        # Test GLGROUP method
        if hasattr(aggregator, 'get_row_data_glgroup'):
            test_label = "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน"
            bu_list = processor.get_unique_business_units(processed)
            sg_dict = {bu: processor.get_unique_service_groups(processed, bu) for bu in bu_list}
            
            result = aggregator.get_row_data_glgroup(test_label, bu_list, sg_dict)
            print(f"  ✅ get_row_data_glgroup() returned {len(result)} keys")
            
            # Check key format
            if result:
                sample_keys = list(result.keys())[:3]
                print(f"  📋 Sample keys: {sample_keys}")
                
                # Check for lowercase vs uppercase
                has_lowercase = any('grand_total' in str(k) for k in result.keys())
                has_uppercase = any('GRAND_TOTAL' in str(k) or 'grand_total' in str(k) for k in result.keys())
                
                if has_lowercase:
                    print(f"  ⚠️  Found lowercase 'grand_total' key")
                if 'grand_total' in result:
                    print(f"  ✅ grand_total value: {result['grand_total']:,.2f}")
            else:
                print(f"  ❌ No data returned!")
        else:
            print(f"  ❌ Method get_row_data_glgroup not found")
    else:
        print(f"  ❌ CSV file not found: {csv_path}")
        
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("DIAGNOSIS COMPLETE")
print("="*70)

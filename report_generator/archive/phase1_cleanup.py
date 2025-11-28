#!/usr/bin/env python3
"""
Phase 1 Cleanup Script - Move old excel_generator to archive
"""
import shutil
from pathlib import Path

def main():
    # Paths
    src_path = Path("/Users/seal/Documents/GitHub/univer/report_generator/src/excel_generator")
    dest_path = Path("/Users/seal/Documents/GitHub/univer/report_generator/archive/old_implementations/excel_generator_v1")
    
    # Check if source exists
    if not src_path.exists():
        print(f"❌ Source not found: {src_path}")
        return
    
    # Check if destination already has README (we just created it)
    if (dest_path / "README.md").exists():
        print(f"✓ Archive directory ready: {dest_path}")
    
    # Copy files one by one
    files_to_copy = [
        "__init__.py",
        "excel_generator.py", 
        "excel_formatter.py",
        "excel_calculator.py"
    ]
    
    for file in files_to_copy:
        src_file = src_path / file
        dest_file = dest_path / file
        
        if src_file.exists():
            shutil.copy2(src_file, dest_file)
            print(f"✓ Copied: {file}")
        else:
            print(f"⚠️  Not found: {file}")
    
    print("\n" + "="*60)
    print("✅ Phase 1 Cleanup - Step 2 Complete!")
    print("="*60)
    print(f"Archived: {dest_path}")
    print("\nNext: Remove src/excel_generator (manual)")

if __name__ == "__main__":
    main()

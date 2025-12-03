#!/usr/bin/env python3
"""
Phase 1 Cleanup Script - Move old excel_generator to archive
"""
import shutil
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')

def main():
    # Paths
    src_path = Path("/Users/seal/Documents/GitHub/univer/report_generator/src/excel_generator")
    dest_path = Path("/Users/seal/Documents/GitHub/univer/report_generator/archive/old_implementations/excel_generator_v1")
    
    # Check if source exists
    if not src_path.exists():
        logging.error(f"❌ Source not found: {src_path}")
        return
    
    # Check if destination already has README (we just created it)
    if (dest_path / "README.md").exists():
        logging.info(f"✓ Archive directory ready: {dest_path}")
    
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
            logging.info(f"✓ Copied: {file}")
        else:
            logging.warning(f"⚠️  Not found: {file}")
    
    logging.info("\n" + "="*60)
    logging.info("✅ Phase 1 Cleanup - Step 2 Complete!")
    logging.info("="*60)
    logging.info(f"Archived: {dest_path}")
    logging.info("\nNext: Remove src/excel_generator (manual)")

if __name__ == "__main__":
    main()

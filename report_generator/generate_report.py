#!/usr/bin/env python3
"""
Univer Report Generator - Simple CLI

สร้างรายงาน P&L Excel จากไฟล์ CSV

Usage:
    # Generate COSTTYPE MTH report with full details
    python generate_report.py

    # Generate GLGROUP YTD report
    python generate_report.py --report-type GLGROUP --period YTD

    # Generate with BU and SG level only
    python generate_report.py --detail-level BU_SG

    # Specify data file
    python generate_report.py --csv-file data/TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv

Examples:
    # Quick test with default settings
    python generate_report.py

    # Full control
    python generate_report.py \\
        --csv-file data/TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv \\
        --output output/my_report.xlsx \\
        --report-type COSTTYPE \\
        --period MTH \\
        --detail-level BU_SG_PRODUCT
"""
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)

from src.data_loader import CSVLoader, DataProcessor
from src.report_generator import ReportBuilder, ReportConfig
from config.settings import settings


def find_csv_file(data_dir: Path, report_type: str, period_type: str) -> Path:
    """Find the most recent CSV file matching criteria"""
    pattern = f"*{report_type}*{period_type}*.csv"
    files = sorted(data_dir.glob(pattern), reverse=True)

    if not files:
        raise FileNotFoundError(
            f"No CSV file found matching pattern: {pattern}\n"
            f"Search directory: {data_dir}"
        )

    return files[0]


def load_remark_file(csv_path: Path, period_type: str = None) -> str:
    """
    Load remark file if exists
    
    Strategy:
    1. Try to find remark file matching CSV date suffix (e.g., remark_20251031.txt)
    2. If not found, try remark_*.txt pattern and use the most recent one
    3. Return empty string if no remark file exists
    
    Args:
        csv_path: Path to CSV file (used to extract date suffix and directory)
        period_type: Period type (MTH/YTD) - not currently used but kept for compatibility
    
    Returns:
        Remark content as string, or empty string if not found
    """
    data_dir = csv_path.parent
    
    # Strategy 1: Extract date suffix from CSV filename
    # CSV filename format: TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv
    csv_stem = csv_path.stem  # TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031
    parts = csv_stem.split('_')
    date_suffix = parts[-1] if parts else None
    
    if date_suffix and date_suffix.isdigit():
        remark_file = data_dir / f"remark_{date_suffix}.txt"
        if remark_file.exists():
            return _read_remark_file(remark_file)
    
    # Strategy 2: Find any remark_*.txt file (use most recent)
    remark_files = sorted(data_dir.glob("remark_*.txt"), reverse=True)
    if remark_files:
        return _read_remark_file(remark_files[0])
    
    return ""


def _read_remark_file(remark_file: Path) -> str:
    """
    Read remark file with multiple encoding fallbacks
    
    Args:
        remark_file: Path to remark file
    
    Returns:
        File content as string
    """
    for encoding in ['utf-8', 'tis-620', 'cp874', 'windows-874']:
        try:
            with open(remark_file, 'r', encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    return ""


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Univer Report Generator - Generate P&L Excel Reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Input/Output
    parser.add_argument(
        '--csv-file',
        type=Path,
        help='CSV data file path (auto-detect if not specified)'
    )
    parser.add_argument(
        '--data-dir',
        type=Path,
        default=Path('data'),
        help='Data directory (default: data/)'
    )
    parser.add_argument(
        '--output',
        '-o',
        type=Path,
        help='Output Excel file path (auto-generated if not specified)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('output'),
        help='Output directory (default: output/)'
    )

    # Report Configuration
    parser.add_argument(
        '--report-type',
        '-t',
        choices=['COSTTYPE', 'GLGROUP'],
        default='COSTTYPE',
        help='Report type (default: COSTTYPE)'
    )
    parser.add_argument(
        '--period',
        '-p',
        choices=['MTH', 'YTD'],
        default='MTH',
        help='Period type (default: MTH)'
    )
    parser.add_argument(
        '--detail-level',
        '-d',
        choices=['BU_ONLY', 'BU_SG', 'BU_SG_PRODUCT'],
        default='BU_SG_PRODUCT',
        help='Detail level (default: BU_SG_PRODUCT - full details)'
    )

    # Options
    parser.add_argument(
        '--common-size',
        action='store_true',
        default=None,
        help='Include Common Size columns (default: auto - True for BU_ONLY, False otherwise)'
    )
    parser.add_argument(
        '--no-common-size',
        action='store_true',
        help='Disable Common Size columns'
    )
    parser.add_argument(
        '--encoding',
        default='tis-620',
        help='CSV encoding (default: tis-620)'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Print header
    print("=" * 70)
    print("📊 Univer Report Generator")
    print("=" * 70)

    try:
        # 1. Find or validate CSV file
        if args.csv_file:
            csv_path = args.csv_file
            if not csv_path.exists():
                print(f"❌ Error: CSV file not found: {csv_path}")
                sys.exit(1)
        else:
            print(f"\n🔍 Searching for CSV file...")
            print(f"   Directory: {args.data_dir}")
            print(f"   Pattern: *{args.report_type}*{args.period}*.csv")
            csv_path = find_csv_file(args.data_dir, args.report_type, args.period)

        print(f"\n📄 CSV File: {csv_path.name}")

        # 2. Load CSV data
        print(f"\n📥 Loading data...")
        csv_loader = CSVLoader(encoding=args.encoding)
        df = csv_loader.load_csv(csv_path)
        print(f"   ✅ Loaded {len(df):,} rows")

        # 3. Process data
        print(f"\n⚙️  Processing data...")
        data_processor = DataProcessor()
        df = data_processor.process_data(df)
        print(f"   ✅ Data processed")

        # 4. Create report configuration
        print(f"\n📋 Report Configuration:")
        print(f"   Type: {args.report_type}")
        print(f"   Period: {args.period}")
        print(f"   Detail Level: {args.detail_level}")
        
        # Determine common_size setting
        include_common_size = None
        if args.no_common_size:
            include_common_size = False
        elif args.common_size:
            include_common_size = True
        # else: None = auto-detect in ReportConfig

        config = ReportConfig(
            report_type=args.report_type,
            period_type=args.period,
            detail_level=args.detail_level,
            include_common_size=include_common_size
        )
        
        if config.include_common_size:
            print(f"   Common Size: Enabled")

        # 5. Determine output path
        if args.output:
            output_path = args.output
        else:
            args.output_dir.mkdir(parents=True, exist_ok=True)
            # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # ใหม่: ดึงค่า TIME_KEY จากข้อมูล
            if 'TIME_KEY' in df.columns and not df.empty:
                # ดึงค่าจากแถวแรก (iloc[0]) มาแปลงเป็น string และตัดช่องว่าง
                time_key = str(df['TIME_KEY'].iloc[0]).strip()
            else:
                # Fallback: ถ้าไม่มี column TIME_KEY หรือไม่มีข้อมูล ให้ใช้เวลาปัจจุบันเหมือนเดิม
                time_key = datetime.now().strftime("%Y%m%d_%H%M%S")

            filename = f"PL_{args.report_type}_{args.period}_{args.detail_level}_{time_key}.xlsx"
            output_path = args.output_dir / filename

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 6. Load remark file
        remark_content = load_remark_file(csv_path)
        if remark_content:
            # Extract date suffix from CSV filename for display
            csv_stem = csv_path.stem
            date_suffix = csv_stem.split('_')[-1] if csv_stem else ''
            print(f"\n📝 Loaded remarks from: remark_{date_suffix}.txt")

        # 7. Generate report
        print(f"\n🔨 Generating Excel report...")
        builder = ReportBuilder(config)
        result_path = builder.generate_report(df, output_path, remark_content)

        # 8. Success!
        file_size = result_path.stat().st_size / 1024  # KB

        print(f"\n✅ Report generated successfully!")
        print(f"\n📊 Output File:")
        print(f"   Path: {result_path}")
        print(f"   Size: {file_size:.1f} KB")

        print("\n" + "=" * 70)
        print("🎉 Done!")
        print("=" * 70)

        if args.verbose:
            print(f"\nFull path: {result_path.absolute()}")

        return 0

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Tip: Use --csv-file to specify the CSV file directly")
        return 1

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            print("\n" + "=" * 70)
            print("Stack Trace:")
            print("=" * 70)
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

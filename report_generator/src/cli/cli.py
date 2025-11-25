"""
Command-Line Interface for Report Generation
"""
import argparse
import sys
from pathlib import Path
import logging
from typing import Optional

# Setup path to import from parent directories
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import settings
from src.data_loader import CSVLoader, DataProcessor
from src.excel_generator import ExcelGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReportCLI:
    """Command-line interface for report generation"""

    def __init__(self):
        """Initialize CLI"""
        self.csv_loader = CSVLoader(encoding=settings.csv_encoding)
        self.data_processor = DataProcessor()

    def generate_report(
        self,
        data_dir: Path,
        output_dir: Path,
        date_str: Optional[str] = None,
        report_type: Optional[str] = None
    ) -> Path:
        """
        Generate report from command line

        Args:
            data_dir: Directory containing CSV files
            output_dir: Directory to save output files
            date_str: Date string (YYYYMMDD) to match files
            report_type: Report type (auto-detect if None)

        Returns:
            Path to generated file
        """
        logger.info("=" * 60)
        logger.info("Univer Report Generator - CLI Mode")
        logger.info("=" * 60)

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load data files
        logger.info(f"Loading data from: {data_dir}")
        data_files = self.csv_loader.load_data_files(
            data_dir,
            date_str=date_str
        )

        if not data_files:
            logger.error("No data files found!")
            sys.exit(1)

        logger.info(f"Loaded {len(data_files)} file(s)")

        # Determine which file to use
        # Priority: COSTTYPE_YTD > COSTTYPE_MTH > GLGROUP_YTD > GLGROUP_MTH
        if report_type:
            report_type = report_type.upper()
            matching = [k for k in data_files.keys() if report_type in k.upper()]
            if not matching:
                logger.error(f"No files found for report type: {report_type}")
                sys.exit(1)
            file_key = matching[0]
        else:
            # Auto-select
            priority = ['costtype_ytd', 'costtype_mth', 'glgroup_ytd', 'glgroup_mth']
            file_key = None
            for key in priority:
                if key in data_files:
                    file_key = key
                    break

            if not file_key:
                file_key = list(data_files.keys())[0]

        df = data_files[file_key]
        logger.info(f"Using file: {file_key}")
        logger.info(f"Data shape: {df.shape}")

        # Process data
        logger.info("Processing data...")
        df_processed = self.data_processor.process_data(df, report_type=file_key)

        # Load remark file
        remark_content = self.csv_loader.load_remark_file(data_dir, date_str)

        # Determine report type and period
        is_costtype = 'COSTTYPE' in file_key.upper()
        is_ytd = 'YTD' in file_key.upper()

        report_type_str = "COSTTYPE" if is_costtype else "GLGROUP"
        period_type_str = "YTD" if is_ytd else "MTH"

        # Generate output filename
        timestamp = df_processed['TIME_KEY'].iloc[0] if 'TIME_KEY' in df_processed.columns and not df_processed.empty else "unknown"
        output_filename = f"P&L_{report_type_str}_{period_type_str}_{timestamp}.xlsx"
        output_path = output_dir / output_filename

        # Generate Excel report
        logger.info("Generating Excel report...")
        generator = ExcelGenerator(
            settings=settings.__dict__,
            bu_colors=settings.bu_colors,
            row_colors=settings.row_colors
        )

        result_path = generator.generate_report(
            data=df_processed,
            output_path=output_path,
            report_type=report_type_str,
            period_type=period_type_str,
            remark_content=remark_content
        )

        logger.info("=" * 60)
        logger.info(f"✓ Report generated successfully!")
        logger.info(f"Output: {result_path}")
        logger.info("=" * 60)

        return result_path

    @staticmethod
    def main():
        """Main entry point for CLI"""
        parser = argparse.ArgumentParser(
            description='Generate P&L Excel reports from CSV files',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Generate from data directory with auto-detection
  python -m src.cli.cli --data-dir ../data --output-dir ./output

  # Generate specific report type
  python -m src.cli.cli --data-dir ../data --output-dir ./output --type COSTTYPE

  # Generate for specific date
  python -m src.cli.cli --data-dir ../data --output-dir ./output --date 20251031

  # Specify all parameters
  python -m src.cli.cli --data-dir ../data --output-dir ./output --type COSTTYPE --date 20251031
            """
        )

        parser.add_argument(
            '--data-dir',
            type=Path,
            required=True,
            help='Directory containing CSV data files'
        )

        parser.add_argument(
            '--output-dir',
            type=Path,
            default=Path('./output'),
            help='Directory to save generated reports (default: ./output)'
        )

        parser.add_argument(
            '--date',
            type=str,
            help='Date string to match files (YYYYMMDD, e.g., 20251031)'
        )

        parser.add_argument(
            '--type',
            type=str,
            choices=['COSTTYPE', 'GLGROUP', 'costtype', 'glgroup'],
            help='Report type (COSTTYPE or GLGROUP)'
        )

        parser.add_argument(
            '--encoding',
            type=str,
            default='tis-620',
            help='CSV file encoding (default: tis-620)'
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )

        args = parser.parse_args()

        # Set logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Update encoding setting
        if args.encoding:
            settings.csv_encoding = args.encoding

        # Create CLI instance and run
        cli = ReportCLI()

        try:
            cli.generate_report(
                data_dir=args.data_dir,
                output_dir=args.output_dir,
                date_str=args.date,
                report_type=args.type
            )
        except Exception as e:
            logger.error(f"Error generating report: {e}", exc_info=True)
            sys.exit(1)


if __name__ == '__main__':
    ReportCLI.main()

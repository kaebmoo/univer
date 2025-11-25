#!/usr/bin/env python3
"""
Test script to generate all 4 report types
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from src.data_loader import CSVLoader, DataProcessor
from src.excel_generator import ExcelGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    data_dir = Path("../data")
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)

    csv_loader = CSVLoader(encoding=settings.csv_encoding)
    data_processor = DataProcessor()

    # Load all data files
    logger.info("Loading all data files...")
    data_files = csv_loader.load_data_files(data_dir, date_str="20251031")

    # Load remark
    remark_content = csv_loader.load_remark_file(data_dir, "20251031")

    # Generate report for each file type
    generator = ExcelGenerator(
        settings=settings.__dict__,
        bu_colors=settings.bu_colors,
        row_colors=settings.row_colors
    )

    report_configs = [
        ("costtype_mth", "COSTTYPE", "MTH"),
        ("costtype_ytd", "COSTTYPE", "YTD"),
        ("glgroup_mth", "GLGROUP", "MTH"),
        ("glgroup_ytd", "GLGROUP", "YTD"),
    ]

    for file_key, report_type, period_type in report_configs:
        if file_key not in data_files:
            logger.warning(f"Skipping {file_key} - not found")
            continue

        logger.info(f"\n{'='*60}")
        logger.info(f"Generating {report_type} {period_type} report...")
        logger.info(f"{'='*60}")

        df = data_files[file_key]
        df_processed = data_processor.process_data(df, report_type=file_key)

        timestamp = df_processed['TIME_KEY'].iloc[0] if 'TIME_KEY' in df_processed.columns and not df_processed.empty else "unknown"
        output_filename = f"P&L_{report_type}_{period_type}_{timestamp}.xlsx"
        output_path = output_dir / output_filename

        generator.generate_report(
            data=df_processed,
            output_path=output_path,
            report_type=report_type,
            period_type=period_type,
            remark_content=remark_content
        )

        logger.info(f"✓ Generated: {output_path}")

    logger.info(f"\n{'='*60}")
    logger.info("All reports generated successfully!")
    logger.info(f"{'='*60}")

if __name__ == "__main__":
    main()

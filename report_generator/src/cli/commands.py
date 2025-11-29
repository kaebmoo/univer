"""
CLI Commands Module
Provides simple function-based interface for report generation
"""
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data_loader import CSVLoader, DataProcessor
from src.report_generator import ReportBuilder, ReportConfig
from config.types import ReportType, DetailLevel, PeriodType


def generate_report(
    csv_path: str,
    output_name: str,
    report_type: ReportType,
    detail_level: DetailLevel,
    period_type: PeriodType,
    encoding: str = 'tis-620',
    output_dir: str = 'output'
) -> Path:
    """
    Generate a P&L report from CSV data
    
    Args:
        csv_path: Path to CSV file
        output_name: Output filename (e.g., 'report.xlsx')
        report_type: ReportType.COSTTYPE or ReportType.GLGROUP
        detail_level: DetailLevel.BU_ONLY, BU_SG, or BU_SG_PRODUCT
        period_type: PeriodType.MTH or PeriodType.YTD
        encoding: CSV encoding (default: tis-620)
        output_dir: Output directory (default: 'output')
    
    Returns:
        Path to generated Excel file
    """
    # Resolve paths
    csv_path = Path(csv_path)
    output_path = Path(output_dir) / output_name
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load CSV
    csv_loader = CSVLoader(encoding=encoding)
    df = csv_loader.load_csv(csv_path)
    print(f"Loaded {len(df):,} rows from {csv_path.name}")
    
    # Process data
    data_processor = DataProcessor()
    df = data_processor.process_data(df)
    
    # Create config
    config = ReportConfig(
        report_type=report_type.value,
        period_type=period_type.value,
        detail_level=detail_level.value
    )
    
    # Generate report
    builder = ReportBuilder(config)
    result_path = builder.generate_report(df, output_path)
    
    return result_path


def load_remark_file(csv_path: Path, period_type: str) -> str:
    """Load remark file if exists"""
    remark_file = csv_path.parent / f"remark_{period_type}.txt"
    
    if not remark_file.exists():
        return ""
    
    for encoding in ['utf-8', 'tis-620', 'cp874']:
        try:
            with open(remark_file, 'r', encoding=encoding) as f:
                return f.read()
        except:
            continue
    
    return ""

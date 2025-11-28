"""
CSV Loader - Load CSV files with Thai encoding support
"""
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict
import glob
import logging

logger = logging.getLogger(__name__)


class CSVLoader:
    """Load CSV files with proper Thai encoding"""

    def __init__(self, encoding: str = "tis-620"):
        """
        Initialize CSV Loader

        Args:
            encoding: Encoding to use for CSV files (tis-620, cp874, utf-8-sig)
        """
        self.encoding = encoding
        self.fallback_encodings = ["tis-620", "cp874", "utf-8-sig", "utf-8"]

    def load_csv(self, file_path: Path) -> pd.DataFrame:
        """
        Load CSV file with automatic encoding detection

        Args:
            file_path: Path to CSV file

        Returns:
            DataFrame with loaded data

        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If file can't be decoded with any encoding
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Try primary encoding first
        try:
            logger.info(f"Loading {file_path} with encoding {self.encoding}")
            df = pd.read_csv(file_path, encoding=self.encoding)
            logger.info(f"Successfully loaded {len(df)} rows from {file_path.name}")
            return df
        except UnicodeDecodeError:
            logger.warning(f"Failed to load with {self.encoding}, trying fallback encodings")

        # Try fallback encodings
        for enc in self.fallback_encodings:
            if enc == self.encoding:
                continue
            try:
                logger.info(f"Trying encoding: {enc}")
                df = pd.read_csv(file_path, encoding=enc)
                logger.info(f"Successfully loaded with {enc}")
                return df
            except UnicodeDecodeError:
                continue

        raise UnicodeDecodeError(
            f"Could not decode file {file_path} with any of the tried encodings: "
            f"{[self.encoding] + self.fallback_encodings}"
        )

    def load_data_files(
        self,
        data_dir: Path,
        file_pattern: Optional[str] = None,
        date_str: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Load all data files matching the pattern

        Args:
            data_dir: Directory containing data files
            file_pattern: Glob pattern for files (e.g., "TRN_PL_*_20251031.csv")
            date_str: Date string to match (e.g., "20251031")

        Returns:
            Dictionary with file types as keys and DataFrames as values
        """
        if not data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {data_dir}")

        results = {}

        # Define file patterns
        patterns = {
            "costtype_mth": f"TRN_PL_COSTTYPE_NT_MTH_TABLE_{date_str or '*'}.csv",
            "costtype_ytd": f"TRN_PL_COSTTYPE_NT_YTD_TABLE_{date_str or '*'}.csv",
            "glgroup_mth": f"TRN_PL_GLGROUP_NT_MTH_TABLE_{date_str or '*'}.csv",
            "glgroup_ytd": f"TRN_PL_GLGROUP_NT_YTD_TABLE_{date_str or '*'}.csv",
        }

        for file_type, pattern in patterns.items():
            # Find matching files
            matching_files = list(data_dir.glob(pattern))

            if not matching_files:
                logger.warning(f"No files found matching pattern: {pattern}")
                continue

            # Use the most recent file if multiple matches
            file_path = sorted(matching_files)[-1]
            logger.info(f"Loading {file_type}: {file_path.name}")

            try:
                df = self.load_csv(file_path)
                results[file_type] = df
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                raise

        return results

    def load_remark_file(self, data_dir: Path, date_str: Optional[str] = None) -> str:
        """
        Load remark text file

        Args:
            data_dir: Directory containing remark file
            date_str: Date string to match (e.g., "20251031")

        Returns:
            Remark text content
        """
        pattern = f"remark_{date_str or '*'}.txt"
        matching_files = list(data_dir.glob(pattern))

        if not matching_files:
            logger.warning(f"No remark file found matching pattern: {pattern}")
            return ""

        file_path = sorted(matching_files)[-1]
        logger.info(f"Loading remark file: {file_path.name}")

        # Try different encodings for text file
        for enc in self.fallback_encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    content = f.read()
                return content
            except UnicodeDecodeError:
                continue

        logger.error(f"Could not decode remark file: {file_path}")
        return ""

    @staticmethod
    def extract_date_from_filename(filename: str) -> Optional[str]:
        """
        Extract date string from filename

        Args:
            filename: Filename to extract date from

        Returns:
            Date string (e.g., "20251031") or None
        """
        import re
        match = re.search(r'(\d{8})\.csv$', filename)
        return match.group(1) if match else None

    @staticmethod
    def parse_time_key(time_key: int) -> tuple:
        """
        Parse TIME_KEY to extract year and month

        Args:
            time_key: TIME_KEY value (e.g., 202510)

        Returns:
            Tuple of (year, month)
        """
        time_str = str(time_key)
        if len(time_str) == 6:
            year = int(time_str[:4])
            month = int(time_str[4:6])
            return year, month
        else:
            raise ValueError(f"Invalid TIME_KEY format: {time_key}")

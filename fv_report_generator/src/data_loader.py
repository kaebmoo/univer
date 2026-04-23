"""
CSV loader — reuse report_generator.CSVLoader if available, else fall back to a
direct pandas read_csv with Thai encoding fallbacks.
"""
import sys
from pathlib import Path

import pandas as pd


_REPO_ROOT = Path(__file__).resolve().parents[2]
_RG_ROOT = _REPO_ROOT / "report_generator"
if _RG_ROOT.exists() and str(_RG_ROOT) not in sys.path:
    sys.path.insert(0, str(_RG_ROOT))

try:
    from src.data_loader.csv_loader import CSVLoader as _RGLoader  # type: ignore
except Exception:
    _RGLoader = None


_FALLBACK_ENCODINGS = ("tis-620", "cp874", "utf-8-sig", "utf-8")


def load_fv_csv(csv_path: Path, encoding: str = "tis-620") -> pd.DataFrame:
    """Load an FV data-warehouse CSV with Thai encoding fallbacks."""
    csv_path = Path(csv_path)
    if _RGLoader is not None:
        return _RGLoader(encoding=encoding).load_csv(csv_path)

    last_err = None
    for enc in (encoding, *_FALLBACK_ENCODINGS):
        try:
            df = pd.read_csv(csv_path, encoding=enc)
            return df.dropna(how="all")
        except UnicodeDecodeError as e:
            last_err = e
    raise last_err or UnicodeDecodeError("unknown", b"", 0, 1, "failed")

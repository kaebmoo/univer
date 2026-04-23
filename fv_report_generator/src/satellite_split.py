"""
SATELLITE sub-group mapping — reuses report_generator/config/satellite_config.py.

The FV Report_P14 splits "4.5 กลุ่มบริการ SATELLITE" into Satellite-NT and
Satellite-ไทยคม at row 7 of the header. CSV doesn't carry this split, so we
derive it from PRODUCT_KEY.
"""
import sys
from pathlib import Path

from .normalizer import canonical, canonical_product_key


_REPO_ROOT = Path(__file__).resolve().parents[2]
_RG_ROOT = _REPO_ROOT / "report_generator"
if _RG_ROOT.exists() and str(_RG_ROOT) not in sys.path:
    sys.path.insert(0, str(_RG_ROOT))

try:
    from config.satellite_config import (
        SATELLITE_GROUPS,
        SATELLITE_SOURCE_NAME,
        ENABLE_SATELLITE_SPLIT,
    )
except Exception:
    SATELLITE_GROUPS = {}
    SATELLITE_SOURCE_NAME = "4.5 กลุ่มบริการ SATELLITE"
    ENABLE_SATELLITE_SPLIT = False


_SG_SOURCE_CANON = canonical(SATELLITE_SOURCE_NAME)

# pkey_canonical -> canonical(subsg_name)
_PRODUCT_TO_SUBSG = {}
# canonical(subsg_name) -> raw label
_SUBSG_LABELS = {}
for group in SATELLITE_GROUPS.values():
    raw_subsg = group["name"]
    cn = canonical(raw_subsg)
    _SUBSG_LABELS[cn] = raw_subsg
    for pkey in group["product_keys"]:
        _PRODUCT_TO_SUBSG[canonical_product_key(pkey)] = cn


def subsg_for(sg_canonical: str, pkey_canonical: str) -> str:
    """Return canonical sub-SG label for a (SG, PRODUCT_KEY) pair.

    Defaults to sg_canonical itself for non-split service groups.
    """
    if not ENABLE_SATELLITE_SPLIT:
        return sg_canonical
    if sg_canonical != _SG_SOURCE_CANON:
        return sg_canonical
    return _PRODUCT_TO_SUBSG.get(pkey_canonical, sg_canonical)


def is_split_sg(sg_canonical: str) -> bool:
    return ENABLE_SATELLITE_SPLIT and sg_canonical == _SG_SOURCE_CANON

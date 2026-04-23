"""Tests for the canonical label normalizer."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.normalizer import canonical, canonical_product_key  # noqa: E402


def test_strips_numeric_prefix():
    assert canonical("1. รายได้") == canonical("01.รายได้") == "รายได้"


def test_strips_multi_level_prefix():
    # 4.5.1 and 1.2.3 should both collapse to the trailing text
    assert canonical("4.5.1 กลุ่มบริการ SATELLITE-NT") == canonical("กลุ่มบริการ Satellite-NT")


def test_cost_suffix_stripped():
    # "ต้นทุนบริการ - Variable Cost" and "ต้นทุนบริการ - Fixed Cost" normalize the same WAY;
    # distinguishing VC/FC is done at the section/GROUP level, not here.
    a = canonical("ต้นทุนบริการและต้นทุนขาย - Variable Cost")
    b = canonical("ต้นทุนบริการและต้นทุนขาย - Fixed Cost")
    assert a == b == "ต้นทุนบริการและต้นทุนขาย"


def test_punctuation_variants_match():
    # Template's "(1)-(2)" vs CSV's "(1) (2)" — both should collapse.
    a = canonical("3. กำไรส่วนเกิน [CONTRIBUTION MARGIN] (1)-(2)")
    b = canonical("03.กำไรส่วนเกิน [CONTRIBUTION MARGIN] (1) (2)")
    assert a == b


def test_trailing_colon_stripped():
    assert canonical("ต้นทุนบริการและต้นทุนขาย :") == canonical("ต้นทุนบริการและต้นทุนขาย")


def test_canonical_product_key_strips_zero_padding_and_newline():
    assert canonical_product_key("000000000181030004") == "181030004"
    assert canonical_product_key("181030004\n") == "181030004"
    assert canonical_product_key("  181030004  ") == "181030004"


def test_empty_inputs():
    assert canonical(None) == ""
    assert canonical("") == ""
    assert canonical_product_key(None) == ""

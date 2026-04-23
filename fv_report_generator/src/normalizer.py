"""
Label normalizer — convert CSV and template labels to a common canonical form.

CSV uses prefixes like "01.", "02." and suffixes like "... :" on SUB_GROUP1.
Template uses human formatting like "    - label" for items, "label - Variable Cost" for groups.
We normalize both to a shared canonical key so we can match row/column identities.
"""
import re


_NUMERIC_PREFIX = re.compile(r"^\s*\d+(?:\.\d+)*\.?\s*")
_COST_SUFFIX = re.compile(r"\s*-?\s*(Variable|Fixed)\s*Cost\s*$", re.IGNORECASE)
# Replace any run of non-word, non-Thai characters with a single space so that
# punctuation variants between CSV and the template ("(1)-(2)" vs "(1) (2)",
# commas, dashes, colons, slashes) all canonicalize to the same form.
_NON_WORD = re.compile(r"[^\w\u0E00-\u0E7F]+", re.UNICODE)
_WHITESPACE = re.compile(r"\s+")


def canonical(text):
    """Normalize a Thai/English label so CSV and template variants compare equal."""
    if text is None:
        return ""
    s = str(text).replace("\xa0", " ")
    s = _NUMERIC_PREFIX.sub("", s)
    s = _COST_SUFFIX.sub("", s)
    s = _NON_WORD.sub(" ", s)
    s = _WHITESPACE.sub(" ", s).strip()
    return s.casefold()


def canonical_product_key(key):
    """Strip leading zeros, whitespace, and newlines from a product key."""
    if key is None:
        return ""
    s = str(key).strip().replace("\n", "").replace("\xa0", "")
    s = s.lstrip("0")
    return s

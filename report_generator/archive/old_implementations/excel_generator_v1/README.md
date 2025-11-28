# Old ExcelGenerator - Archived

**Archive Date:** 2025-11-26  
**Reason:** Being replaced with new modular architecture based on main_generator.py

## Contents

This directory contains the old ExcelGenerator implementation that was used by:
- `src/cli/cli.py`
- `src/web/routes/report.py`
- `test_all_reports.py`

## Files

- `__init__.py` - Module exports
- `excel_generator.py` - Main generator class
- `excel_formatter.py` - Formatting module
- `excel_calculator.py` - Calculation module

## Known Limitations

❌ **Missing Features:**
- No Service Group Total columns ("รวม SG")
- No Product-level columns (PRODUCT_KEY, PRODUCT_NAME)
- Cannot generate BU-only reports
- Cannot generate BU+SG reports

✅ **Working Features:**
- Basic BU Total columns
- Service Group aggregation (no SG total column)
- COSTTYPE and GLGROUP support
- MTH and YTD support

## Why Archived?

The main_generator.py has more complete features:
1. ✅ BU Total + SG Total + Products
2. ✅ Context-aware ratio calculations
3. ✅ Proper multi-level headers
4. ✅ All formatting correct

## Restoration

If needed, this can be restored:
```bash
cp -r archive/old_implementations/excel_generator_v1 src/excel_generator
```

**DO NOT DELETE THIS ARCHIVE**

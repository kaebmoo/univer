# Report Generator Module - Developer Guide

**Version:** 2.0.0  
**Created:** 2025-11-26  
**Architecture:** Modular

---

## 📁 Module Structure

```
src/report_generator/
├── __init__.py                      # Main exports
│
├── core/                            # Core logic
│   ├── __init__.py
│   ├── config.py                    # ✅ ReportConfig (DONE)
│   └── report_builder.py           # ⏳ Main orchestrator (TODO)
│
├── columns/                         # Column builders
│   ├── __init__.py                  
│   ├── base_column_builder.py      # ✅ Base class (DONE)
│   ├── bu_only_builder.py          # ⏳ BU only (TODO)
│   ├── bu_sg_builder.py            # ⏳ BU + SG (TODO)
│   └── bu_sg_product_builder.py    # ⏳ BU + SG + Products (TODO)
│
├── rows/                            # Row builders
│   ├── __init__.py
│   ├── row_builder.py              # ⏳ Build rows from ROW_ORDER (TODO)
│   └── row_calculator.py           # ⏳ Calculate row values (TODO)
│
├── writers/                         # Excel writers
│   ├── __init__.py
│   ├── header_writer.py            # ⏳ Write headers (TODO)
│   ├── column_header_writer.py     # ⏳ Write column headers (TODO)
│   ├── data_writer.py              # ⏳ Write data rows (TODO)
│   └── remark_writer.py            # ⏳ Write remarks (TODO)
│
├── formatters/                      # Formatting
│   ├── __init__.py
│   ├── cell_formatter.py           # ⏳ Cell formatting (TODO)
│   ├── color_manager.py            # ⏳ Color management (TODO)
│   └── style_applier.py            # ⏳ Apply styles (TODO)
│
└── calculators/                     # Calculations
    ├── __init__.py
    ├── aggregator.py                # ⏳ Data aggregation (TODO)
    ├── ratio_calculator.py          # ⏳ Ratio calculations (TODO)
    └── product_calculator.py        # ⏳ Product calculations (TODO)
```

---

## 🎯 Design Patterns

### 1. Strategy Pattern - Column Builders

Different column builders for different detail levels:

```python
# BU Only
BaseColumnBuilder → BUOnlyBuilder
Result: รายละเอียด | รวมทั้งสิ้น | รวม BU1 | รวม BU2 | ...

# BU + SG
BaseColumnBuilder → BUSGBuilder  
Result: ... | รวม BU | SG1 | SG2 | ...

# BU + SG + Products (Current)
BaseColumnBuilder → BUSGProductBuilder
Result: ... | รวม BU | รวม SG | Product1 | Product2 | ...
```

### 2. Builder Pattern - Report Builder

Orchestrates all modules to generate report:

```python
class ReportBuilder:
    def generate_report(data, output_path):
        # 1. Build structure
        columns = column_builder.build_columns(data)
        rows = row_builder.build_rows()
        
        # 2. Create workbook
        wb = Workbook()
        
        # 3. Write content
        header_writer.write(ws)
        data_writer.write(ws, data, columns, rows)
        
        # 4. Format
        formatter.apply_all(ws)
        
        # 5. Save
        wb.save(output_path)
```

### 3. Single Responsibility Principle

Each module has ONE clear job:
- **Columns:** Build column structure
- **Rows:** Build row structure  
- **Writers:** Write to Excel
- **Formatters:** Apply formatting
- **Calculators:** Calculate values

---

## 🔧 Implementation Guide

### Phase 2A: ✅ Foundation (DONE)
- [x] Directory structure
- [x] `__init__.py` files
- [x] `core/config.py`
- [x] `columns/base_column_builder.py`
- [x] Documentation skeleton

### Phase 2B: Extract Logic from main_generator.py

**Priority Order:**

1. **bu_sg_product_builder.py** (Current logic)
   - Extract column building code (lines 140-260 of main_generator.py)
   - Keep EXACT same logic
   - Test: Generate same columns

2. **row_builder.py**
   - Extract row building code (uses ROW_ORDER)
   - Simple: just iterate and create RowDef objects

3. **data_writer.py**
   - Extract data writing logic (lines 260-450)
   - Most complex part
   - Keep all calculation logic

4. **cell_formatter.py**
   - Extract formatting code
   - Font, colors, borders, alignment

5. **aggregator.py**
   - Use existing DataAggregator from data_loader
   - Or extract if needed

6. **report_builder.py**
   - Wire everything together
   - Main orchestrator

### Phase 2C: New Builders

1. **bu_only_builder.py**
   - Simplified version
   - Only BU totals, no SG or products

2. **bu_sg_builder.py**
   - Medium complexity
   - BU totals + SG columns, no products

---

## 📝 Code Templates

### Template: Column Builder

```python
from .base_column_builder import BaseColumnBuilder, ColumnDef
from typing import List
import pandas as pd

class MyColumnBuilder(BaseColumnBuilder):
    """Build columns for [DESCRIPTION]"""
    
    def build_columns(self, data: pd.DataFrame) -> List[ColumnDef]:
        columns = []
        
        # 1. Label column
        columns.append(self._create_label_column())
        
        # 2. Grand total
        columns.append(self._create_grand_total_column())
        
        # 3. Your logic here
        # ...
        
        return columns
```

### Template: Writer

```python
from openpyxl import Workbook
from typing import List

class MyWriter:
    """Write [WHAT] to Excel"""
    
    def __init__(self, config):
        self.config = config
    
    def write(self, ws, data, ...):
        """Write content to worksheet"""
        # Your logic here
        pass
```

---

## 🧪 Testing Strategy

### Unit Tests
Test each module independently:
```python
def test_bu_only_builder():
    config = ReportConfig(detail_level="BU_ONLY")
    builder = BUOnlyBuilder(config)
    columns = builder.build_columns(test_data)
    
    assert len(columns) == expected_count
    assert columns[0].col_type == "label"
    # ...
```

### Integration Tests
Test complete report generation:
```python
def test_generate_report():
    config = ReportConfig(...)
    builder = ReportBuilder(config)
    path = builder.generate_report(data, output_path)
    
    # Verify file created
    assert path.exists()
    
    # Compare with reference
    # ...
```

---

## 🚀 Usage Examples

### Example 1: Generate Current Style Report

```python
from src.report_generator import ReportBuilder, ReportConfig

config = ReportConfig(
    report_type="COSTTYPE",
    period_type="MTH",
    detail_level="BU_SG_PRODUCT"  # Current default
)

builder = ReportBuilder(config)
builder.generate_report(data, "output/report.xlsx", remark)
```

### Example 2: Generate BU Only Report

```python
config = ReportConfig(
    report_type="COSTTYPE",
    period_type="MTH",
    detail_level="BU_ONLY"  # Simplified
)

builder = ReportBuilder(config)
builder.generate_report(data, "output/bu_only.xlsx", remark)
```

### Example 3: Generate BU + SG Report

```python
config = ReportConfig(
    report_type="GLGROUP",  # Different dimension
    period_type="YTD",
    detail_level="BU_SG"    # Medium detail
)

builder = ReportBuilder(config)
builder.generate_report(data, "output/bu_sg.xlsx", remark)
```

---

## ⚠️ Important Notes

### Preserving Features

**MUST KEEP:**
- Service Group Total columns ("รวม SG")
- Product-level columns (PRODUCT_KEY, PRODUCT_NAME)
- Context-aware ratio calculations (3 types)
- Multi-level headers
- All current formatting

### Migration Path

1. Phase 2B: Extract current logic → modules
2. Test: Verify same output as main_generator.py
3. Phase 2C: Add new builders (BU only, BU+SG)
4. Test: Verify new report types work
5. Phase 3: Integrate with CLI, Web API

---

## 📞 Questions?

Check:
- `REFACTOR_PLAN.md` - Overall plan
- `main_generator.py` - Reference implementation
- `backup_20251126/` - Original backup

---

**Last Updated:** 2025-11-26  
**Status:** Phase 2A Complete, Ready for 2B

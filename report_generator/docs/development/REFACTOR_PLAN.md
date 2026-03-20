# 🔄 Refactoring Plan - REVISED
# Excel Report Generator Modularization

**Date:** 2025-11-26  
**Status:** Ready to Execute  
**Priority:** High  

---

## 🎯 PRIMARY OBJECTIVES

### 1. Preserve ALL Features from generate_report.py
- ✅ BU Total + SG Total + Product-level columns
- ✅ Context-aware ratio calculations (3 types)
- ✅ Multi-dimensional reporting support

### 2. Enable Flexible Report Configurations
**Current:** มิติต้นทุน (COSTTYPE) → BU + SG + Products only

**Target:** Support multiple report dimensions:
1. **BU Only** - รายงานระดับกลุ่มธุรกิจ
2. **BU + SG** - รายงานระดับกลุ่มธุรกิจ + กลุ่มบริการ  
3. **BU + SG + Products** - รายงานระดับกลุ่มธุรกิจ + กลุ่มบริการ + บริการ (current)

For BOTH:
- **มิติต้นทุน (COSTTYPE)**
- **มิติหมวดบัญชี (GLGROUP)**

### 3. Create Modular Architecture
Transform monolithic 600-line file into maintainable modules while keeping exact same output.

---

## 📋 EXECUTION PHASES

### Phase 0: ✅ BACKUP (COMPLETED)
- [x] Backup generate_report.py → backup_20251126/
- [x] Create backup README

### Phase 1: 🗂️ CLEANUP & RENAME (15 minutes)

**Actions:**
```bash
# 1. Rename for clarity
mv generate_report.py main_generator.py

# 2. Archive old ExcelGenerator  
mkdir -p archive/old_implementations/excel_generator_v1
mv src/excel_generator archive/old_implementations/excel_generator_v1/

# 3. Create archive README
```

**Expected Result:**
- main_generator.py = Standalone working script
- Old ExcelGenerator archived (not deleted)
- Clean slate for new module

---

### Phase 2: 🏗️ CREATE MODULAR STRUCTURE (3-4 hours)

#### 2.1 Create New Module Structure

```
src/
└── report_generator/                    # NEW MODULE
    ├── __init__.py                      # Export main classes
    │
    ├── core/                            # Core generation logic
    │   ├── __init__.py
    │   ├── report_builder.py           # Main orchestrator
    │   └── config.py                    # Report configuration
    │
    ├── columns/                         # Column structure builders
    │   ├── __init__.py
    │   ├── base_column_builder.py      # Base class
    │   ├── bu_only_builder.py          # BU only columns
    │   ├── bu_sg_builder.py            # BU + SG columns
    │   └── bu_sg_product_builder.py    # BU + SG + Products (current)
    │
    ├── rows/                            # Row structure builders
    │   ├── __init__.py
    │   ├── row_builder.py              # Build from ROW_ORDER
    │   └── row_calculator.py           # Calculate row values
    │
    ├── writers/                         # Excel writers
    │   ├── __init__.py
    │   ├── header_writer.py            # Write header & info box
    │   ├── column_header_writer.py     # Write column headers
    │   ├── data_writer.py              # Write data rows
    │   └── remark_writer.py            # Write remarks
    │
    ├── formatters/                      # Excel formatting
    │   ├── __init__.py
    │   ├── cell_formatter.py           # Format individual cells
    │   ├── color_manager.py            # Manage BU colors
    │   └── style_applier.py            # Apply styles
    │
    └── calculators/                     # Data calculations
        ├── __init__.py
        ├── aggregator.py                # Aggregate data
        ├── ratio_calculator.py          # 3 types of ratios
        └── product_calculator.py        # Product-level calculations
```

#### 2.2 Key Classes & Design

**ReportConfig** - Define report structure
```python
@dataclass
class ReportConfig:
    report_type: str  # "COSTTYPE" or "GLGROUP"
    period_type: str  # "MTH" or "YTD"
    detail_level: str  # "BU_ONLY", "BU_SG", "BU_SG_PRODUCT"
    
    # Column settings
    include_bu_total: bool = True
    include_sg_total: bool = True
    include_products: bool = True
    
    # Display settings
    show_info_box: bool = True
    show_remarks: bool = True
```

**ColumnBuilder Strategy Pattern**
```python
class BaseColumnBuilder(ABC):
    @abstractmethod
    def build_columns(self, data: pd.DataFrame) -> List[ColumnDef]:
        pass

class BUOnlyBuilder(BaseColumnBuilder):
    """Build: รายละเอียด | รวมทั้งสิ้น | รวม BU1 | รวม BU2 | ..."""
    
class BUSGBuilder(BaseColumnBuilder):
    """Build: ... | รวม BU | SG1 | SG2 | ..."""
    
class BUSGProductBuilder(BaseColumnBuilder):
    """Build: ... | รวม BU | รวม SG | Product1 | Product2 | ..."""
```

**ReportBuilder** - Main orchestrator
```python
class ReportBuilder:
    def __init__(self, config: ReportConfig):
        self.config = config
        self.column_builder = self._get_column_builder()
        self.row_builder = RowBuilder()
        # ... other components
    
    def generate_report(
        self, 
        data: pd.DataFrame,
        output_path: Path,
        remark_content: str = ""
    ) -> Path:
        # 1. Build structure
        columns = self.column_builder.build_columns(data)
        rows = self.row_builder.build_rows()
        
        # 2. Create workbook
        wb = Workbook()
        ws = wb.active
        
        # 3. Write content
        self.header_writer.write(ws, data, self.config)
        self.column_header_writer.write(ws, columns)
        self.data_writer.write(ws, data, columns, rows)
        self.remark_writer.write(ws, remark_content)
        
        # 4. Apply formatting
        self.formatter.apply_all(ws, columns, rows)
        
        # 5. Save
        wb.save(output_path)
        return output_path
```

#### 2.3 Implementation Steps

**Step 1:** Create directory structure
```bash
mkdir -p src/report_generator/{core,columns,rows,writers,formatters,calculators}
touch src/report_generator/{__init__.py,core/__init__.py,columns/__init__.py,...}
```

**Step 2:** Extract & refactor logic from main_generator.py
- Column building → `columns/bu_sg_product_builder.py` (current logic)
- Row building → `rows/row_builder.py`
- Data writing → `writers/data_writer.py`
- Formatting → `formatters/cell_formatter.py`
- Calculations → `calculators/aggregator.py`

**Step 3:** Create other column builders
- `columns/bu_only_builder.py` - NEW (for BU only reports)
- `columns/bu_sg_builder.py` - NEW (for BU + SG reports)

**Step 4:** Wire everything together in `core/report_builder.py`

**Step 5:** Create simple API in `__init__.py`
```python
from .core.report_builder import ReportBuilder
from .core.config import ReportConfig

__all__ = ['ReportBuilder', 'ReportConfig']
```

---

### Phase 3: 🔗 INTEGRATION (2 hours)

#### 3.1 Update Entry Points

**1. Create new main_generator_v2.py** (uses new module)
```python
from src.report_generator import ReportBuilder, ReportConfig

config = ReportConfig(
    report_type="COSTTYPE",
    period_type="MTH", 
    detail_level="BU_SG_PRODUCT"  # Current default
)

builder = ReportBuilder(config)
builder.generate_report(data, output_path, remark_content)
```

**2. Update src/cli/cli.py**
```python
from src.report_generator import ReportBuilder, ReportConfig

# Add CLI option for detail level
parser.add_argument(
    '--detail-level',
    choices=['bu', 'bu_sg', 'bu_sg_product'],
    default='bu_sg_product',
    help='Report detail level'
)

# Use in generation
config = ReportConfig(
    report_type=args.type,
    period_type=period_type,
    detail_level=args.detail_level.upper()
)
```

**3. Update src/web/routes/report.py**
```python
from src.report_generator import ReportBuilder, ReportConfig

# Add to API model
class ReportGenerateRequest(BaseModel):
    data_dir: str
    date_str: Optional[str] = None
    report_type: Optional[str] = None
    detail_level: str = "bu_sg_product"  # NEW

# Use in endpoint
config = ReportConfig(...)
builder = ReportBuilder(config)
```

**4. Update test_all_reports.py**
```python
from src.report_generator import ReportBuilder, ReportConfig

# Test all combinations
for detail_level in ['BU_ONLY', 'BU_SG', 'BU_SG_PRODUCT']:
    for report_type in ['COSTTYPE', 'GLGROUP']:
        for period_type in ['MTH', 'YTD']:
            config = ReportConfig(
                report_type=report_type,
                period_type=period_type,
                detail_level=detail_level
            )
            # Generate and compare
```

#### 3.2 Testing Strategy

**Level 1: Unit Tests**
- Test each column builder individually
- Test row builder
- Test calculators
- Test formatters

**Level 2: Integration Tests**
- Generate report with new module
- Compare with main_generator.py output
- Verify Excel files are identical (or visually same)

**Level 3: Regression Tests**
- Run test_all_reports.py
- Verify all 4 report types work
- Check CLI mode
- Check Web API mode

---

### Phase 4: 📚 DOCUMENTATION (1 hour)

#### 4.1 Update Main Documentation

**README.md**
- Add section on flexible report configurations
- Document new detail_level options
- Update architecture diagram

**USAGE.md**
- Add examples for different detail levels
- CLI examples with --detail-level
- API examples with detail_level parameter

#### 4.2 Create Module Documentation

**src/report_generator/README.md**
- Architecture overview
- How to add new column builders
- How to add new formatters
- Examples

#### 4.3 API Documentation

**Each module should have:**
- Docstrings for all classes
- Docstrings for all public methods
- Usage examples in docstrings

---

## ✅ SUCCESS CRITERIA

### Functional Requirements
- [ ] Generate same output as main_generator.py (current BU+SG+Product)
- [ ] Support BU Only reports (NEW)
- [ ] Support BU + SG reports (NEW)
- [ ] Support BU + SG + Product reports (CURRENT)
- [ ] Work for both COSTTYPE and GLGROUP
- [ ] Work for both MTH and YTD
- [ ] All calculations correct (especially ratios)
- [ ] All formatting preserved

### Technical Requirements
- [ ] Modular architecture
- [ ] Each module has single responsibility
- [ ] Easy to add new column builders
- [ ] Easy to add new formatters
- [ ] Well documented
- [ ] Unit tests for key components

### Integration Requirements
- [ ] CLI mode works with new options
- [ ] Web API works with new parameters
- [ ] test_all_reports.py passes
- [ ] No breaking changes to existing usage

---

## 🚀 EXECUTION ORDER

### Today (Phase 1)
1. ✅ Backup complete
2. [ ] Rename generate_report.py → main_generator.py
3. [ ] Archive old ExcelGenerator
4. [ ] Test main_generator.py still works

### Tomorrow (Phase 2 - Part 1)
1. [ ] Create module structure
2. [ ] Extract column building logic
3. [ ] Create BUSGProductBuilder (current logic)
4. [ ] Test column generation

### Day 3 (Phase 2 - Part 2)
1. [ ] Extract row building logic
2. [ ] Extract data writing logic
3. [ ] Extract formatting logic
4. [ ] Test complete report generation

### Day 4 (Phase 2 - Part 3 + Phase 3)
1. [ ] Create BUOnlyBuilder
2. [ ] Create BUSGBuilder
3. [ ] Wire everything in ReportBuilder
4. [ ] Update entry points
5. [ ] Integration testing

### Day 5 (Phase 4)
1. [ ] Documentation
2. [ ] Final testing
3. [ ] Deploy

---

## 📝 IMPORTANT NOTES

### Feature Preservation
**CRITICAL:** The following must work EXACTLY as before:
- Product-level columns with PRODUCT_KEY and PRODUCT_NAME
- Service Group Total columns ("รวม SG")
- Context-aware ratio calculations
- Info box (5 separate lines)
- All current formatting

### New Capabilities
**MUST ADD:** Support for simplified reports:
1. **BU Only:** Fast summary view
2. **BU + SG:** Middle-ground detail
3. **BU + SG + Product:** Full detail (current)

### Testing
**MUST VERIFY:** 
- Output files identical to current version
- All 12 report combinations work (3 levels × 2 types × 2 periods)
- Performance is acceptable
- No regressions in existing features

---

## 🆘 ROLLBACK PLAN

If anything goes wrong:

```bash
# Restore from backup
cp backup_20251126/generate_report_ORIGINAL.py generate_report.py

# Restore old ExcelGenerator if needed
cp -r archive/old_implementations/excel_generator_v1 src/excel_generator

# Run tests to verify
python generate_report.py
python test_all_reports.py
```

---

**Created by:** Claude  
**Last Updated:** 2025-11-26  
**Status:** READY TO EXECUTE

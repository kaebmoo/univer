# Report Generator - Documentation

เอกสารประกอบระบบ Report Generator จัดเป็นหมวดหมู่ดังนี้

---

## guides/ - คู่มือการใช้งาน

| ไฟล์ | รายละเอียด |
| ---- | ---------- |
| [USAGE.md](guides/USAGE.md) | คู่มือการใช้งาน generate_report.py |
| [README_run_reports.md](guides/README_run_reports.md) | คู่มือ run_reports.sh (batch) |
| [README_report_concat.md](guides/README_report_concat.md) | คู่มือ report_concat.py (รวมไฟล์) |
| [TESTING_GUIDE.md](guides/TESTING_GUIDE.md) | คู่มือการทดสอบระบบ |
| [REPORT_GENERATOR_WORKFLOW.md](guides/REPORT_GENERATOR_WORKFLOW.md) | Workflow การสร้างรายงาน |
| [execution_flow.md](guides/execution_flow.md) | ลำดับการทำงานของโค้ด |
| [module_usage_analysis.md](guides/module_usage_analysis.md) | วิเคราะห์การใช้งาน modules |

---

## features/ - เอกสาร Features

| ไฟล์ | รายละเอียด |
| ---- | ---------- |
| [SATELLITE_SPLIT_README.md](features/SATELLITE_SPLIT_README.md) | การแยกกลุ่ม SATELLITE (4.5.1 NT / 4.5.2 ไทยคม) |
| [COMMON_SIZE_FEATURE.md](features/COMMON_SIZE_FEATURE.md) | Common Size (% ต่อรายได้รวม) |
| [GLGROUP_IMPLEMENTATION_GUIDE.md](features/GLGROUP_IMPLEMENTATION_GUIDE.md) | การ implement มิติหมวดบัญชี (GLGROUP) |
| [ROWS_CALCULATE.md](features/ROWS_CALCULATE.md) | สูตรคำนวณแถวสรุป (EBITDA, EBT, etc.) |
| [fixed_number_format.md](features/fixed_number_format.md) | รูปแบบตัวเลขใน Excel |

---

## reconciliation/ - เอกสาร Reconciliation

คู่มือหลัก: [reconciliation/README.md](../../reconciliation/README.md) (อยู่ใน folder reconciliation/ โดยตรง)

เอกสารแนวคิดและ methodology:

| ไฟล์ | รายละเอียด |
| ---- | ---------- |
| [Reconciliation.md](reconciliation/Reconciliation.md) | กรอบแนวคิดและหลักการตรวจกระทบยอด |
| [README_Enhanced.md](reconciliation/README_Enhanced.md) | คู่มือ Enhanced reconciliation |
| [reconciliation_plan.md](reconciliation/reconciliation_plan.md) | แผนการทำ reconciliation |
| [manual.md](reconciliation/manual.md) | คู่มือ reconciliation แบบ manual |
| [km.md](reconciliation/km.md) | Knowledge management |

---

## development/ - ประวัติการพัฒนา

เอกสารเหล่านี้เป็นบันทึกระหว่างการพัฒนา สำหรับอ้างอิงย้อนหลัง

### Changelogs

- [CHANGELOG.md](development/CHANGELOG.md)
- [CHANGELOG_month_support.md](development/CHANGELOG_month_support.md)

### สถานะโครงการ

- [PROJECT_STATUS.md](development/PROJECT_STATUS.md)
- [IMPLEMENTATION_STATUS.md](development/IMPLEMENTATION_STATUS.md)
- [CHECKLIST.md](development/CHECKLIST.md)
- [COMPLETION_REPORT.md](development/COMPLETION_REPORT.md)

### Phases

- [PHASE1_PROGRESS.md](development/PHASE1_PROGRESS.md)
- [PHASE2A_COMPLETE.md](development/PHASE2A_COMPLETE.md)
- [PHASE2B_COMPLETE.md](development/PHASE2B_COMPLETE.md)
- [PHASE2C_TODO.md](development/PHASE2C_TODO.md)

### GLGROUP Development

- [GLGROUP_IMPLEMENTATION_COMPLETE.md](development/GLGROUP_IMPLEMENTATION_COMPLETE.md)
- [GLGROUP_TODO.md](development/GLGROUP_TODO.md)
- [GLGROUP_FIX_APPLIED.md](development/GLGROUP_FIX_APPLIED.md)

### Bug Fixes

- [BUG_FIX_REPORT.md](development/BUG_FIX_REPORT.md)
- [BUG_ANALYSIS_AND_FIX_PLAN.md](development/BUG_ANALYSIS_AND_FIX_PLAN.md)
- [FIX_PRODUCT_LINE_ITEMS.md](development/FIX_PRODUCT_LINE_ITEMS.md)
- [FIX_ROW13_14.md](development/FIX_ROW13_14.md)
- [FIX_TAX_NETPROFIT_COLORS.md](development/FIX_TAX_NETPROFIT_COLORS.md)
- [DATA_WRITER_FIXES.md](development/DATA_WRITER_FIXES.md)

### Refactoring

- [REFACTOR_PLAN.md](development/REFACTOR_PLAN.md)

### Session Notes

- [SUMMARY.md](development/SUMMARY.md)
- [SESSION_SUMMARY.md](development/SESSION_SUMMARY.md)

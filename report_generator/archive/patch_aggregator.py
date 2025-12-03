#!/usr/bin/env python3
"""
Auto-patch DataAggregator with GLGROUP methods
Run this to add GLGROUP support to data_aggregator.py
"""
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')

logging.info("="*70)
logging.info("Adding GLGROUP Methods to DataAggregator")
logging.info("="*70)

aggregator_file = Path("src/data_loader/data_aggregator.py")

if not aggregator_file.exists():
    logging.error(f"❌ File not found: {aggregator_file}")
    sys.exit(1)

# Read current content
with open(aggregator_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if already patched
if 'get_row_data_glgroup' in content:
    logging.info("✅ Already patched! GLGROUP methods exist.")
    sys.exit(0)

logging.info("\n📝 Reading GLGROUP methods...")

# Read the methods to add
methods_to_add = '''
    # ==================== GLGROUP METHODS ====================
    
    def get_row_data_glgroup(
        self,
        label: str,
        bu_list: List[str],
        service_group_dict: Dict[str, List[str]]
    ) -> Dict[str, float]:
        """
        Get row data for GLGROUP dimension
        Uses GROUP/SUB_GROUP from data directly
        """
        from config.data_mapping_glgroup import get_group_sub_group_glgroup
        
        group, sub_group = get_group_sub_group_glgroup(label)
        
        if not group:
            return {}
        
        filtered = self.df[
            (self.df['GROUP'] == group) & 
            (self.df['SUB_GROUP'] == sub_group)
        ]
        
        if len(filtered) == 0:
            logger.info(f"No data for GLGROUP: {group} / {sub_group}")
            return {}
        
        result = {}
        result['grand_total'] = filtered['VALUE'].sum()
        
        for bu in bu_list:
            bu_data = filtered[filtered['BU'] == bu]
            bu_total = bu_data['VALUE'].sum()
            result[f'bu_total_{bu}'] = bu_total
            
            if bu in service_group_dict:
                for sg in service_group_dict[bu]:
                    sg_data = bu_data[bu_data['SERVICE_GROUP'] == sg]
                    sg_total = sg_data['VALUE'].sum()
                    result[f'sg_total_{bu}_{sg}'] = sg_total
                    
                    products = sg_data.groupby('PRODUCT_KEY')['VALUE'].sum()
                    for product_key, value in products.items():
                        result[f'product_{bu}_{sg}_{product_key}'] = value
        
        return result

    def calculate_summary_row_glgroup(
        self,
        label: str,
        bu_list: List[str],
        service_group_dict: Dict[str, List[str]],
        all_row_data: Dict[str, Dict]
    ) -> Dict[str, float]:
        """Calculate summary rows for GLGROUP"""
        from config.row_order_glgroup import ROW_ORDER_GLGROUP
        
        formula = None
        for level, row_label, is_calc, calc_formula, is_bold in ROW_ORDER_GLGROUP:
            if row_label == label and is_calc:
                formula = calc_formula
                break
        
        if not formula:
            return {}
        
        if formula == "sum_group_1":
            revenue_labels = [
                "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน",
                "- รายได้กลุ่มธุรกิจโทรศัพท์ประจำที่และบรอดแบนด์",
                "- รายได้กลุ่มธุรกิจโทรศัพท์เคลื่อนที่",
                "- รายได้กลุ่มธุรกิจวงจรระหว่างประเทศ",
                "- รายได้กลุ่มธุรกิจดิจิทัล",
                "- รายได้กลุ่มธุรกิจ ICT Solution Business",
                "- รายได้จากการให้บริการอื่นที่ไม่ใช่โทรคมนาคม",
                "- รายได้จากการขาย",
                "     - ผลตอบแทนทางการเงิน",
                "     - รายได้อื่น"
            ]
            return self._sum_rows_glgroup(all_row_data, revenue_labels)
        
        elif formula == "sum_group_2":
            expense_labels = [
                "- ค่าใช้จ่ายตอบแทนแรงงาน", "- ค่าสวัสดิการ",
                "- ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร",
                "- ค่าซ่อมแซมและบำรุงรักษาและวัสดุใช้ไป",
                "- ค่าสาธารณูปโภค",
                "- ค่าใช้จ่ายการตลาดและส่งเสริมการขาย",
                "- ค่าใช้จ่ายเผยแพร่ประชาสัมพันธ์",
                "- ค่าใช้จ่ายเกี่ยวกับการกำกับดูแลของ กสทช.",
                "- ค่าส่วนแบ่งบริการโทรคมนาคม",
                "- ค่าใช้จ่ายบริการโทรคมนาคม",
                "- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์",
                "- ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า",
                "- ค่าเช่าและค่าใช้สินทรัพย์", "- ต้นทุนขาย",
                "- ค่าใช้จ่ายบริการอื่น",
                "- ค่าใช้จ่ายดำเนินงานอื่น", "- ค่าใช้จ่ายอื่น",
                "- ต้นทุนทางการเงิน-ด้านการดำเนินงาน",
                "- ต้นทุนทางการเงิน-ด้านการจัดหาเงิน"
            ]
            return self._sum_rows_glgroup(all_row_data, expense_labels)
        
        elif formula == "sum_service_revenue":
            service_labels = [
                "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน",
                "- รายได้กลุ่มธุรกิจโทรศัพท์ประจำที่และบรอดแบนด์",
                "- รายได้กลุ่มธุรกิจโทรศัพท์เคลื่อนที่",
                "- รายได้กลุ่มธุรกิจวงจรระหว่างประเทศ",
                "- รายได้กลุ่มธุรกิจดิจิทัล",
                "- รายได้กลุ่มธุรกิจ ICT Solution Business",
                "- รายได้จากการให้บริการอื่นที่ไม่ใช่โทรคมนาคม",
                "- รายได้จากการขาย"
            ]
            return self._sum_rows_glgroup(all_row_data, service_labels)
        
        elif formula == "total_revenue":
            return all_row_data.get("1 รวมรายได้", {}).copy()
        
        elif formula == "total_expense_no_finance":
            total = all_row_data.get("2 รวมค่าใช้จ่าย", {}).copy()
            op = all_row_data.get("- ต้นทุนทางการเงิน-ด้านการดำเนินงาน", {})
            fund = all_row_data.get("- ต้นทุนทางการเงิน-ด้านการจัดหาเงิน", {})
            result = {}
            for key in total:
                result[key] = total.get(key, 0) - op.get(key, 0) - fund.get(key, 0)
            return result
        
        elif formula == "total_expense_with_finance":
            return all_row_data.get("2 รวมค่าใช้จ่าย", {}).copy()
        
        elif formula == "ebitda":
            ebt = all_row_data.get("3.กำไร(ขาดทุน)ก่อนหักภาษีเงินได้ (EBT) (1)-(2)", {})
            dep = all_row_data.get("- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์", {})
            amort = all_row_data.get("- ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า", {})
            result = {}
            all_keys = set(ebt.keys()) | set(dep.keys()) | set(amort.keys())
            for key in all_keys:
                result[key] = ebt.get(key, 0) + dep.get(key, 0) + amort.get(key, 0)
            return result
        
        return {}

    def _sum_rows_glgroup(self, all_row_data: Dict[str, Dict], labels: List[str]) -> Dict[str, float]:
        """Sum multiple rows for GLGROUP"""
        result = {}
        for label in labels:
            if label in all_row_data:
                for key, value in all_row_data[label].items():
                    result[key] = result.get(key, 0) + value
        return result
'''

# Find where to insert (before the last line of the class)
# Look for the end of the class
lines = content.split('\n')
insert_idx = -1

for i in range(len(lines) - 1, 0, -1):
    line = lines[i].strip()
    if line and not line.startswith('#') and not line.startswith('"""'):
        # Found last substantial line
        insert_idx = i + 1
        break

if insert_idx == -1:
    logging.error("❌ Could not find insertion point")
    sys.exit(1)

# Insert methods
lines.insert(insert_idx, methods_to_add)
new_content = '\n'.join(lines)

# Backup original
backup_file = aggregator_file.with_suffix('.py.backup')
with open(backup_file, 'w', encoding='utf-8') as f:
    f.write(content)

logging.info(f"💾 Backup saved: {backup_file}")

# Write patched version
with open(aggregator_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

logging.info(f"✅ Patched: {aggregator_file}")
logging.info("\n📊 Added methods:")
logging.info("  - get_row_data_glgroup()")
logging.info("  - calculate_summary_row_glgroup()")
logging.info("  - _sum_rows_glgroup()")

logging.info("\n" + "="*70)
logging.info("✅ GLGROUP METHODS ADDED SUCCESSFULLY!")
logging.info("="*70)

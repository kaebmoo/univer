import os
import logging
import pandas as pd
import openpyxl
from copy import copy

# Configure basic logging for this script
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# 1. หาตำแหน่งที่ตั้งจริงของไฟล์ script (report_concat.py) ในเครื่อง
# ผลลัพธ์จะเป็น .../univer/report_generator
script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. กำหนด input/output โดยอ้างอิงจากตำแหน่ง script
# โครงสร้างโฟลเดอร์ที่ code นี้คาดหวังคือ:
# univer/
#   └── report_generator/
#       ├── report_concat.py  (ไฟล์นี้)
#       ├── data/             
#       └── output/           (ต้องมีไฟล์ excel อยู่ในนี้) (ไฟล์ผลลัพธ์จะมาโผล่ที่นี่)

input_dir = os.path.join(script_dir, 'output')
output_dir = os.path.join(script_dir, 'output')

# Debug: ปริ้นท์ออกมาดูว่า path ถูกต้องไหม
logging.info(f"Script Location: {script_dir}")
logging.info(f"Reading from:    {input_dir}")
logging.info(f"Writing to:      {output_dir}")
logging.info("-" * 30)

# ตรวจสอบว่ามี folder output หรือไม่ ถ้าไม่มีให้สร้าง
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 1. Get a list of all files in the input_dir (ดึงรายชื่อไฟล์ครั้งเดียว ใช้ได้ทั้ง 2 งาน)
all_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]

logging.info("Starting Process...\n")

# ==========================================
# PART 1: สร้างรายงานเดือน (MTH)
# ==========================================
logging.info("--- Processing MTH Report ---")

# 2. Filter for MTH .xlsx files and sort them
mth_files = sorted([f for f in all_files if 'MTH' in f and f.endswith('.xlsx')])

if not mth_files:
    logging.warning("No 'MTH' Excel files found in the input directory.")
else:
    logging.info(f"Found {len(mth_files)} 'MTH' Excel files:")
    for f in mth_files:
        logging.info(f"- {f}")

    # 3. Extract the YYYYMM part
    date_part_mth = mth_files[0].split('_')[-1].replace('.xlsx', '')
    output_filename_mth = f"Report_NT_{date_part_mth}.xlsx"
    output_filepath_mth = os.path.join(output_dir, output_filename_mth)
    logging.info(f"\nOutput MTH report will be saved as: {output_filepath_mth}")

    # 4. Define filename patterns
    file_patterns_mth_order = [
        "PL_COSTTYPE_MTH_BU_ONLY",
        "PL_COSTTYPE_MTH_BU_SG",
        "PL_COSTTYPE_MTH_BU_SG_PRODUCT",
        "PL_GLGROUP_MTH_BU_ONLY",
        "PL_GLGROUP_MTH_BU_SG",
        "PL_GLGROUP_MTH_BU_SG_PRODUCT"
    ]

    thai_sheet_names_map_mth = {
        "PL_COSTTYPE_MTH_BU_ONLY": "ต้นทุน_กลุ่มธุรกิจ",
        "PL_COSTTYPE_MTH_BU_SG": "ต้นทุน_กลุ่มบริการ",
        "PL_COSTTYPE_MTH_BU_SG_PRODUCT": "ต้นทุน_บริการ",
        "PL_GLGROUP_MTH_BU_ONLY": "หมวดบัญชี_กลุ่มธุรกิจ",
        "PL_GLGROUP_MTH_BU_SG": "หมวดบัญชี_กลุ่มบริการ",
        "PL_GLGROUP_MTH_BU_SG_PRODUCT": "หมวดบัญชี_บริการ"
    }

    # 5. Create new workbook
    output_wb_mth = openpyxl.Workbook()
    default_sheet = output_wb_mth['Sheet']
    output_wb_mth.remove(default_sheet)
    logging.info("\nCreated new empty workbook for MTH report.")

    # 6. Iterate through patterns
    for pattern in file_patterns_mth_order:
        found_file = None
        for f in mth_files:
            if f.startswith(pattern) and f.endswith(f'_{date_part_mth}.xlsx'):
                found_file = f
                break

        if found_file:
            full_file_path = os.path.join(input_dir, found_file)
            source_wb = openpyxl.load_workbook(full_file_path)
            source_sheet = source_wb.active

            sheet_name = thai_sheet_names_map_mth.get(pattern, pattern)
            new_sheet = output_wb_mth.create_sheet(title=sheet_name)

            # Copy cell values and styles
            for row in source_sheet.iter_rows():
                for cell in row:
                    new_cell = new_sheet[cell.coordinate]
                    new_cell.value = cell.value
                    if cell.has_style:
                        new_cell.font = copy(cell.font)
                        new_cell.border = copy(cell.border)
                        new_cell.fill = copy(cell.fill)
                        new_cell.number_format = copy(cell.number_format)
                        new_cell.protection = copy(cell.protection)
                        new_cell.alignment = copy(cell.alignment)

            # Copy dimensions
            for row_idx, rd in source_sheet.row_dimensions.items():
                new_sheet.row_dimensions[row_idx] = copy(rd)
            for col_idx, cd in source_sheet.column_dimensions.items():
                new_sheet.column_dimensions[col_idx] = copy(cd)

            # Copy merged cells
            for merged_cell_range in source_sheet.merged_cells.ranges:
                new_sheet.merge_cells(str(merged_cell_range))

            logging.info(f"  - Copied '{found_file}' to sheet '{sheet_name}' with formatting.")
        else:
            logging.warning(f"  - Warning: No file found for pattern '{pattern}'. Skipping.")

    # 7. Save
    output_wb_mth.save(output_filepath_mth)
    logging.info(f"\nSuccessfully created MTH report: {output_filepath_mth}")


logging.info("\n" + "="*40 + "\n")


# ==========================================
# PART 2: สร้างรายงานปี (YTD)
# ==========================================
logging.info("--- Processing YTD Report ---")

# 2. Filter for YTD .xlsx files and sort them (ใช้ all_files ตัวเดิม)
ytd_files = sorted([f for f in all_files if 'YTD' in f and f.endswith('.xlsx')])

if not ytd_files:
    logging.warning("No 'YTD' Excel files found in the input directory.")
else:
    logging.info(f"Found {len(ytd_files)} 'YTD' Excel files:")
    for f in ytd_files:
        logging.info(f"- {f}")

    # 3. Extract YYYY only
    date_part_ytd_full = ytd_files[0].split('_')[-1].replace('.xlsx', '')
    year_part_ytd = date_part_ytd_full[:4] # เอาแค่ปี 4 หลัก
    output_filename_ytd = f"Report_NT_{year_part_ytd}.xlsx"
    output_filepath_ytd = os.path.join(output_dir, output_filename_ytd)
    logging.info(f"\nOutput YTD report will be saved as: {output_filepath_ytd}")

    # 4. Define filename patterns
    file_patterns_ytd_order = [
        "PL_COSTTYPE_YTD_BU_ONLY",
        "PL_COSTTYPE_YTD_BU_SG",
        "PL_COSTTYPE_YTD_BU_SG_PRODUCT",
        "PL_GLGROUP_YTD_BU_ONLY",
        "PL_GLGROUP_YTD_BU_SG",
        "PL_GLGROUP_YTD_BU_SG_PRODUCT"
    ]

    thai_sheet_names_map_ytd = {
        "PL_COSTTYPE_YTD_BU_ONLY": "ต้นทุน_กลุ่มธุรกิจ",
        "PL_COSTTYPE_YTD_BU_SG": "ต้นทุน_กลุ่มบริการ",
        "PL_COSTTYPE_YTD_BU_SG_PRODUCT": "ต้นทุน_บริการ",
        "PL_GLGROUP_YTD_BU_ONLY": "หมวดบัญชี_กลุ่มธุรกิจ",
        "PL_GLGROUP_YTD_BU_SG": "หมวดบัญชี_กลุ่มบริการ",
        "PL_GLGROUP_YTD_BU_SG_PRODUCT": "หมวดบัญชี_บริการ"
    }

    # 5. Create new workbook
    output_wb_ytd = openpyxl.Workbook()
    default_sheet_ytd = output_wb_ytd['Sheet']
    output_wb_ytd.remove(default_sheet_ytd)
    logging.info("\nCreated new empty workbook for YTD report.")

    # 6. Iterate through patterns
    for pattern in file_patterns_ytd_order:
        found_file = None
        for f in ytd_files:
            if f.startswith(pattern) and f.endswith(f'_{date_part_ytd_full}.xlsx'):
                found_file = f
                break

        if found_file:
            full_file_path = os.path.join(input_dir, found_file)
            source_wb = openpyxl.load_workbook(full_file_path)
            source_sheet = source_wb.active

            sheet_name = thai_sheet_names_map_ytd.get(pattern, pattern)
            new_sheet = output_wb_ytd.create_sheet(title=sheet_name)

            # Copy cell values and styles
            for row in source_sheet.iter_rows():
                for cell in row:
                    new_cell = new_sheet[cell.coordinate]
                    new_cell.value = cell.value
                    if cell.has_style:
                        new_cell.font = copy(cell.font)
                        new_cell.border = copy(cell.border)
                        new_cell.fill = copy(cell.fill)
                        new_cell.number_format = copy(cell.number_format)
                        new_cell.protection = copy(cell.protection)
                        new_cell.alignment = copy(cell.alignment)

            # Copy dimensions
            for row_idx, rd in source_sheet.row_dimensions.items():
                new_sheet.row_dimensions[row_idx] = copy(rd)
            for col_idx, cd in source_sheet.column_dimensions.items():
                new_sheet.column_dimensions[col_idx] = copy(cd)

            # Copy merged cells
            for merged_cell_range in source_sheet.merged_cells.ranges:
                new_sheet.merge_cells(str(merged_cell_range))

            logging.info(f"  - Copied '{found_file}' to sheet '{sheet_name}' with formatting.")
        else:
            logging.warning(f"  - Warning: No file found for pattern '{pattern}'. Skipping.")

    # 7. Save
    output_wb_ytd.save(output_filepath_ytd)
    logging.info(f"\nSuccessfully created YTD report: {output_filepath_ytd}")
    
logging.info("\nAll processes completed.")
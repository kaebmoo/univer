#!/bin/bash

echo "--- Starting Report Generation ---"

# --- YTD Period ---
echo "Processing YTD Reports..."
python3 generate_report.py --report-type COSTTYPE  --period YTD
python3 generate_report.py --report-type COSTTYPE  --period YTD --detail-level BU_SG
python3 generate_report.py --report-type COSTTYPE  --period YTD --detail-level BU_ONLY

python3 generate_report.py --report-type GLGROUP  --period YTD
python3 generate_report.py --report-type GLGROUP  --period YTD --detail-level BU_SG
python3 generate_report.py --report-type GLGROUP  --period YTD --detail-level BU_ONLY

# --- MTH Period ---
echo "Processing MTH Reports..."
python3 generate_report.py --report-type COSTTYPE  --period MTH
python3 generate_report.py --report-type COSTTYPE  --period MTH --detail-level BU_SG
python3 generate_report.py --report-type COSTTYPE  --period MTH --detail-level BU_ONLY

python3 generate_report.py --report-type GLGROUP  --period MTH
python3 generate_report.py --report-type GLGROUP  --period MTH --detail-level BU_SG
python3 generate_report.py --report-type GLGROUP  --period MTH --detail-level BU_ONLY

echo "--- All Reports Generated Successfully ---"
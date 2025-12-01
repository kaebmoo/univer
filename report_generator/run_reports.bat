@echo off
echo --- Starting Report Generation ---

REM --- YTD Period ---
echo Processing YTD Reports...
python generate_report.py --report-type COSTTYPE  --period YTD
python generate_report.py --report-type COSTTYPE  --period YTD --detail-level BU_SG
python generate_report.py --report-type COSTTYPE  --period YTD --detail-level BU_ONLY

python generate_report.py --report-type GLGROUP  --period YTD
python generate_report.py --report-type GLGROUP  --period YTD --detail-level BU_SG
python generate_report.py --report-type GLGROUP  --period YTD --detail-level BU_ONLY

REM --- MTH Period ---
echo Processing MTH Reports...
python generate_report.py --report-type COSTTYPE  --period MTH
python generate_report.py --report-type COSTTYPE  --period MTH --detail-level BU_SG
python generate_report.py --report-type COSTTYPE  --period MTH --detail-level BU_ONLY

python generate_report.py --report-type GLGROUP  --period MTH
python generate_report.py --report-type GLGROUP  --period MTH --detail-level BU_SG
python generate_report.py --report-type GLGROUP  --period MTH --detail-level BU_ONLY

echo --- All Reports Generated Successfully ---
pause
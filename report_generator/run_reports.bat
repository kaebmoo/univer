@echo off
REM Usage: run_reports.bat [YYYYMM] [PERIOD]
REM Examples:
REM   run_reports.bat              - All months, both MTH and YTD
REM   run_reports.bat 202509       - Month 202509, both MTH and YTD
REM   run_reports.bat "" YTD       - All months, YTD only
REM   run_reports.bat 202509 MTH   - Month 202509, MTH only

setlocal enabledelayedexpansion

REM Parse arguments
set "MONTH_FILTER=%~1"
set "PERIOD_FILTER=%~2"

REM Convert period to uppercase and validate
if not "%PERIOD_FILTER%"=="" (
    for %%A in (A B C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
        set "PERIOD_FILTER=!PERIOD_FILTER:%%A=%%A!"
    )
    call :StrToUpper PERIOD_FILTER

    if not "!PERIOD_FILTER!"=="MTH" if not "!PERIOD_FILTER!"=="YTD" (
        echo Error: Invalid period '!PERIOD_FILTER!'. Must be MTH or YTD
        pause
        exit /b 1
    )
)

goto :main

:StrToUpper
set "%~1=!%~1:a=A!"
set "%~1=!%~1:b=B!"
set "%~1=!%~1:c=C!"
set "%~1=!%~1:d=D!"
set "%~1=!%~1:e=E!"
set "%~1=!%~1:f=F!"
set "%~1=!%~1:g=G!"
set "%~1=!%~1:h=H!"
set "%~1=!%~1:i=I!"
set "%~1=!%~1:j=J!"
set "%~1=!%~1:k=K!"
set "%~1=!%~1:l=L!"
set "%~1=!%~1:m=M!"
set "%~1=!%~1:n=N!"
set "%~1=!%~1:o=O!"
set "%~1=!%~1:p=P!"
set "%~1=!%~1:q=Q!"
set "%~1=!%~1:r=R!"
set "%~1=!%~1:s=S!"
set "%~1=!%~1:t=T!"
set "%~1=!%~1:u=U!"
set "%~1=!%~1:v=V!"
set "%~1=!%~1:w=W!"
set "%~1=!%~1:x=X!"
set "%~1=!%~1:y=Y!"
set "%~1=!%~1:z=Z!"
goto :eof

:main

REM Function to extract unique months from CSV files
if "%MONTH_FILTER%"=="" (
    echo --- Starting Report Generation for ALL months ---
    if not "%PERIOD_FILTER%"=="" echo Period Filter: %PERIOD_FILTER%

    REM Get unique months from CSV files
    set "months="
    for %%f in (data\*.csv) do (
        set "filename=%%~nf"
        REM Extract YYYYMMDD (8 digits) from filename
        for /f "tokens=* delims=" %%a in ("!filename!") do (
            echo %%a | findstr /r "[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]" >nul
            if !errorlevel! equ 0 (
                for /f "tokens=* delims=" %%b in ("%%a") do (
                    set "temp=%%b"
                    REM Extract last 8 digits and get first 6 (YYYYMM)
                    for /f "tokens=* delims=" %%c in ('echo !temp! ^| findstr /r "[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$"') do (
                        set "datepart=%%c"
                        set "month=!datepart:~-8,6!"
                        REM Check if month already in list
                        echo !months! | find "!month!" >nul
                        if errorlevel 1 (
                            set "months=!months! !month!"
                        )
                    )
                )
            )
        )
    )

    if "!months!"=="" (
        echo Error: No CSV files found in data\ directory
        pause
        exit /b 1
    )

    echo Found months:!months!
    echo.

    REM Process each month
    for %%m in (!months!) do (
        call :process_month %%m
    )
) else (
    REM Specific month provided
    echo --- Starting Report Generation for Month: %MONTH_FILTER% ---
    if not "%PERIOD_FILTER%"=="" echo Period Filter: %PERIOD_FILTER%
    call :process_month %MONTH_FILTER%
)

echo.
echo --- Individual Report Files Generated Successfully ---

REM --- Concatenate Reports ---
echo.
echo --- Starting Report Concatenation ---
if "%MONTH_FILTER%"=="" (
    python report_concat.py
) else (
    python report_concat.py --month %MONTH_FILTER%
)

echo.
echo ===================================================
echo --- All Reports Completed Successfully ---
echo ===================================================
pause
goto :eof

:process_month
set "month=%~1"
echo.
echo ==========================================
echo Processing Month: %month%
if not "%PERIOD_FILTER%"=="" (
    echo Period: %PERIOD_FILTER% only
) else (
    echo Period: Both MTH and YTD
)
echo ==========================================

REM --- YTD Period ---
if "%PERIOD_FILTER%"=="" goto :do_ytd
if "%PERIOD_FILTER%"=="YTD" goto :do_ytd
goto :skip_ytd

:do_ytd
echo Processing YTD Reports...
python generate_report.py --report-type COSTTYPE  --period YTD --month %month%
python generate_report.py --report-type COSTTYPE  --period YTD --detail-level BU_SG --month %month%
python generate_report.py --report-type COSTTYPE  --period YTD --detail-level BU_ONLY --month %month%

python generate_report.py --report-type GLGROUP  --period YTD --month %month%
python generate_report.py --report-type GLGROUP  --period YTD --detail-level BU_SG --month %month%
python generate_report.py --report-type GLGROUP  --period YTD --detail-level BU_ONLY --month %month%

:skip_ytd

REM --- MTH Period ---
if "%PERIOD_FILTER%"=="" goto :do_mth
if "%PERIOD_FILTER%"=="MTH" goto :do_mth
goto :skip_mth

:do_mth
echo Processing MTH Reports...
python generate_report.py --report-type COSTTYPE  --period MTH --month %month%
python generate_report.py --report-type COSTTYPE  --period MTH --detail-level BU_SG --month %month%
python generate_report.py --report-type COSTTYPE  --period MTH --detail-level BU_ONLY --month %month%

python generate_report.py --report-type GLGROUP  --period MTH --month %month%
python generate_report.py --report-type GLGROUP  --period MTH --detail-level BU_SG --month %month%
python generate_report.py --report-type GLGROUP  --period MTH --detail-level BU_ONLY --month %month%

:skip_mth

echo Done: Completed reports for month %month%
goto :eof
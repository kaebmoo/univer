@echo off
REM Usage: run_reports.bat [YYYYMM] [PERIOD]
REM Examples:
REM   run_reports.bat              - All months, both MTH and YTD
REM   run_reports.bat 202509       - Month 202509, both MTH and YTD
REM   run_reports.bat "" YTD       - All months, YTD only
REM   run_reports.bat 202509 MTH   - Month 202509, MTH only

REM This batch file is a wrapper that calls the PowerShell script
REM PowerShell is more reliable for complex string manipulation on Windows

setlocal

set "MONTH_FILTER=%~1"
set "PERIOD_FILTER=%~2"

REM Build PowerShell command
set "PS_CMD=powershell.exe -ExecutionPolicy Bypass -File "%~dp0run_reports.ps1""

if not "%MONTH_FILTER%"=="" (
    set "PS_CMD=%PS_CMD% -Month "%MONTH_FILTER%""
)

if not "%PERIOD_FILTER%"=="" (
    set "PS_CMD=%PS_CMD% -Period "%PERIOD_FILTER%""
)

REM Execute PowerShell script
%PS_CMD%

REM Capture exit code from PowerShell
set EXIT_CODE=%ERRORLEVEL%

REM Pause to show results
pause

exit /b %EXIT_CODE%
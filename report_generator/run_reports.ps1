# Usage: .\run_reports.ps1 [YYYYMM] [PERIOD]
# Examples:
#   .\run_reports.ps1              - All months, both MTH and YTD
#   .\run_reports.ps1 202509       - Month 202509, both MTH and YTD
#   .\run_reports.ps1 -Period YTD  - All months, YTD only
#   .\run_reports.ps1 202509 MTH   - Month 202509, MTH only

param(
    [string]$Month = "",
    [string]$Period = ""
)

# Convert period to uppercase and validate
if ($Period -ne "") {
    $Period = $Period.ToUpper()
    if ($Period -ne "MTH" -and $Period -ne "YTD") {
        Write-Host "Error: Invalid period '$Period'. Must be MTH or YTD" -ForegroundColor Red
        exit 1
    }
}

# Ensure this script works from its own directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $scriptDir

# Prefer the project's virtual environment python if available
$venvPython = Join-Path $scriptDir "..\.venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $python = $venvPython
} else {
    $python = "python"
}

# Function to extract unique months from CSV files
function Get-AvailableMonths {
    $csvFiles = Get-ChildItem -Path "data\*.csv" -ErrorAction SilentlyContinue
    if ($csvFiles.Count -eq 0) {
        return @()
    }

    $months = @()
    foreach ($file in $csvFiles) {
        $filename = $file.BaseName
        # Extract 8 digits (YYYYMMDD) from filename
        if ($filename -match '\d{8}') {
            $dateStr = $matches[0]
            $monthStr = $dateStr.Substring(0, 6)
            if ($months -notcontains $monthStr) {
                $months += $monthStr
            }
        }
    }
    return $months | Sort-Object
}

function Run-Python {
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$Args
    )

    Write-Host "Running: $python $($Args -join ' ')"
    & $python @Args
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Python command failed with exit code $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

# Function to generate reports for a specific month
function Generate-ReportsForMonth {
    param(
        [string]$MonthParam,
        [string]$PeriodFilter
    )

    Write-Host ""
    Write-Host "=========================================="
    Write-Host "Processing Month: $MonthParam"
    if ($PeriodFilter -ne "") {
        Write-Host "Period: $PeriodFilter only"
    } else {
        Write-Host "Period: Both MTH and YTD"
    }
    Write-Host "=========================================="

    # --- YTD Period ---
    if ($PeriodFilter -eq "" -or $PeriodFilter -eq "YTD") {
        Write-Host "Processing YTD Reports..."
        Run-Python -Args @("generate_report.py", "--report-type", "COSTTYPE", "--period", "YTD", "--month", $MonthParam)
        Run-Python -Args @("generate_report.py", "--report-type", "COSTTYPE", "--period", "YTD", "--detail-level", "BU_SG", "--month", $MonthParam)
        Run-Python -Args @("generate_report.py", "--report-type", "COSTTYPE", "--period", "YTD", "--detail-level", "BU_ONLY", "--month", $MonthParam)

        Run-Python -Args @("generate_report.py", "--report-type", "GLGROUP", "--period", "YTD", "--month", $MonthParam)
        Run-Python -Args @("generate_report.py", "--report-type", "GLGROUP", "--period", "YTD", "--detail-level", "BU_SG", "--month", $MonthParam)
        Run-Python -Args @("generate_report.py", "--report-type", "GLGROUP", "--period", "YTD", "--detail-level", "BU_ONLY", "--month", $MonthParam)
    }

    # --- MTH Period ---
    if ($PeriodFilter -eq "" -or $PeriodFilter -eq "MTH") {
        Write-Host "Processing MTH Reports..."
        Run-Python -Args @("generate_report.py", "--report-type", "COSTTYPE", "--period", "MTH", "--month", $MonthParam)
        Run-Python -Args @("generate_report.py", "--report-type", "COSTTYPE", "--period", "MTH", "--detail-level", "BU_SG", "--month", $MonthParam)
        Run-Python -Args @("generate_report.py", "--report-type", "COSTTYPE", "--period", "MTH", "--detail-level", "BU_ONLY", "--month", $MonthParam)

        Run-Python -Args @("generate_report.py", "--report-type", "GLGROUP", "--period", "MTH", "--month", $MonthParam)
        Run-Python -Args @("generate_report.py", "--report-type", "GLGROUP", "--period", "MTH", "--detail-level", "BU_SG", "--month", $MonthParam)
        Run-Python -Args @("generate_report.py", "--report-type", "GLGROUP", "--period", "MTH", "--detail-level", "BU_ONLY", "--month", $MonthParam)
    }

    Write-Host "Done: Completed reports for month $MonthParam"
}

# Main execution
if ($Month -ne "") {
    # Specific month provided
    Write-Host "--- Starting Report Generation for Month: $Month ---"
    if ($Period -ne "") {
        Write-Host "Period Filter: $Period"
    }
    Generate-ReportsForMonth -MonthParam $Month -PeriodFilter $Period
} else {
    # No month specified - process all months
    Write-Host "--- Starting Report Generation for ALL months ---"
    if ($Period -ne "") {
        Write-Host "Period Filter: $Period"
    }

    $months = Get-AvailableMonths

    if ($months.Count -eq 0) {
        Write-Host "Error: No CSV files found in data\ directory" -ForegroundColor Red
        exit 1
    }

    Write-Host "Found months: $($months -join ', ')"
    Write-Host ""

    foreach ($m in $months) {
        Generate-ReportsForMonth -MonthParam $m -PeriodFilter $Period
    }
}

Write-Host ""
Write-Host "--- Individual Report Files Generated Successfully ---"

# --- Concatenate Reports ---
Write-Host ""
Write-Host "--- Starting Report Concatenation ---"
if ($Month -ne "") {
    Run-Python -Args @("report_concat.py", "--month", $Month)
} else {
    Run-Python -Args @("report_concat.py")
}

Write-Host ""
Write-Host "==================================================="
Write-Host "--- All Reports Completed Successfully ---"
Write-Host "==================================================="

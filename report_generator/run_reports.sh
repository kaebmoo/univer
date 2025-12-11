#!/bin/bash

# Usage: ./run_reports.sh [YYYYMM] [PERIOD]
# Examples:
#   ./run_reports.sh              - All months, both MTH and YTD
#   ./run_reports.sh 202509       - Month 202509, both MTH and YTD
#   ./run_reports.sh "" YTD       - All months, YTD only
#   ./run_reports.sh 202509 MTH   - Month 202509, MTH only

# Parse arguments
MONTH_FILTER="$1"
PERIOD_FILTER=$(echo "$2" | tr '[:lower:]' '[:upper:]')  # Convert to uppercase

# Validate period filter
if [ -n "$PERIOD_FILTER" ] && [ "$PERIOD_FILTER" != "MTH" ] && [ "$PERIOD_FILTER" != "YTD" ]; then
    echo "❌ Error: Invalid period '$PERIOD_FILTER'. Must be MTH or YTD"
    exit 1
fi

# Function to extract unique months from CSV files
get_available_months() {
    local months=$(ls data/*.csv 2>/dev/null | grep -oE '[0-9]{8}' | cut -c1-6 | sort -u)
    echo "$months"
}

# Function to generate reports for a specific month
generate_reports_for_month() {
    local month=$1
    local period_filter=$2

    echo ""
    echo "=========================================="
    echo "Processing Month: $month"
    if [ -n "$period_filter" ]; then
        echo "Period: $period_filter only"
    else
        echo "Period: Both MTH and YTD"
    fi
    echo "=========================================="

    # --- YTD Period ---
    if [ -z "$period_filter" ] || [ "$period_filter" = "YTD" ]; then
        echo "Processing YTD Reports..."
        python3 generate_report.py --report-type COSTTYPE  --period YTD --month $month
        python3 generate_report.py --report-type COSTTYPE  --period YTD --detail-level BU_SG --month $month
        python3 generate_report.py --report-type COSTTYPE  --period YTD --detail-level BU_ONLY --month $month

        python3 generate_report.py --report-type GLGROUP  --period YTD --month $month
        python3 generate_report.py --report-type GLGROUP  --period YTD --detail-level BU_SG --month $month
        python3 generate_report.py --report-type GLGROUP  --period YTD --detail-level BU_ONLY --month $month
    fi

    # --- MTH Period ---
    if [ -z "$period_filter" ] || [ "$period_filter" = "MTH" ]; then
        echo "Processing MTH Reports..."
        python3 generate_report.py --report-type COSTTYPE  --period MTH --month $month
        python3 generate_report.py --report-type COSTTYPE  --period MTH --detail-level BU_SG --month $month
        python3 generate_report.py --report-type COSTTYPE  --period MTH --detail-level BU_ONLY --month $month

        python3 generate_report.py --report-type GLGROUP  --period MTH --month $month
        python3 generate_report.py --report-type GLGROUP  --period MTH --detail-level BU_SG --month $month
        python3 generate_report.py --report-type GLGROUP  --period MTH --detail-level BU_ONLY --month $month
    fi

    echo "✓ Completed reports for month $month"
}

# Main execution
if [ -n "$MONTH_FILTER" ]; then
    # Specific month provided
    echo "--- Starting Report Generation for Month: $MONTH_FILTER ---"
    if [ -n "$PERIOD_FILTER" ]; then
        echo "Period Filter: $PERIOD_FILTER"
    fi
    generate_reports_for_month "$MONTH_FILTER" "$PERIOD_FILTER"
else
    # No month specified - process all months
    echo "--- Starting Report Generation for ALL months ---"
    if [ -n "$PERIOD_FILTER" ]; then
        echo "Period Filter: $PERIOD_FILTER"
    fi

    months=$(get_available_months)

    if [ -z "$months" ]; then
        echo "❌ Error: No CSV files found in data/ directory"
        exit 1
    fi

    echo "Found months: $months"
    echo ""

    for month in $months; do
        generate_reports_for_month "$month" "$PERIOD_FILTER"
    done
fi

echo ""
echo "--- Individual Report Files Generated Successfully ---"

# --- Concatenate Reports ---
echo ""
echo "--- Starting Report Concatenation ---"
if [ -n "$MONTH_FILTER" ]; then
    python3 report_concat.py --month $MONTH_FILTER
else
    python3 report_concat.py
fi

echo ""
echo "==================================================="
echo "--- All Reports Completed Successfully ---"
echo "==================================================="
"""
Report Router
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.models.auth import UserInfo
from app.models.report import (
    ReportFilter,
    FilterOptions,
    UniverWorkbook
)
from app.routers.auth import get_current_user
from app.services.data_loader import data_loader
from app.services.report_calculator import report_calculator
from app.services.univer_converter import univer_converter

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/report", tags=["Report"])


@router.get("/filters", response_model=FilterOptions)
async def get_filter_options(
    current_user: UserInfo = Depends(get_current_user)
):
    """
    Get available filter options

    Returns available years, business groups, and services
    that can be used to filter reports.

    Args:
        current_user: Current authenticated user

    Returns:
        FilterOptions with available years, business groups, and services
    """
    logger.info(f"Filter options requested by {current_user.email}")

    try:
        filter_options = data_loader.get_available_filters()
        return filter_options

    except FileNotFoundError as e:
        logger.error(f"Data file not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data files not found. Please ensure CSV files are uploaded."
        )
    except Exception as e:
        logger.error(f"Error getting filter options: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load filter options"
        )


@router.post("/generate")
async def generate_report(
    filter: ReportFilter,
    current_user: UserInfo = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate P&L report with specified filters

    Generate a complete Profit & Loss report based on the provided filters.
    Returns report data with revenue, costs, and calculated metrics.

    Args:
        filter: Report filter parameters (year, months, business_groups)
        current_user: Current authenticated user

    Returns:
        Complete report data with metrics and calculations

    Raises:
        HTTPException 400: If invalid filter parameters
        HTTPException 404: If no data found for the specified filters
        HTTPException 500: If report generation fails
    """
    logger.info(
        f"Report generation requested by {current_user.email}: "
        f"year={filter.year}, months={filter.months}, "
        f"groups={filter.business_groups or 'all'}"
    )

    try:
        # Generate report
        report = report_calculator.generate_full_report(
            year=filter.year,
            months=filter.months,
            business_groups=filter.business_groups,
            view_type='monthly',
            display_type='both',
            show_common_size=True
        )

        logger.info(
            f"Report generated successfully: "
            f"Revenue={report['data']['revenue'].get('Total', 0):,.2f}"
        )

        return report

    except ValueError as e:
        logger.error(f"Invalid filter parameters: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except FileNotFoundError as e:
        logger.error(f"Data file not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data files not found"
        )
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.post("/univer")
async def generate_univer_snapshot(
    filter: ReportFilter,
    current_user: UserInfo = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate Univer snapshot for spreadsheet display

    Generate a Univer-compatible snapshot that can be loaded directly
    into the Univer spreadsheet component on the frontend.

    Args:
        filter: Report filter parameters (year, months, business_groups)
        current_user: Current authenticated user

    Returns:
        Univer snapshot object with sheets, cells, and styles

    Raises:
        HTTPException 400: If invalid filter parameters
        HTTPException 404: If no data found for the specified filters
        HTTPException 500: If snapshot generation fails
    """
    logger.info(
        f"Univer snapshot requested by {current_user.email}: "
        f"year={filter.year}, months={filter.months}"
    )

    try:
        # Generate report data
        report = report_calculator.generate_full_report(
            year=filter.year,
            months=filter.months,
            business_groups=filter.business_groups,
            view_type='monthly',
            display_type='both',
            show_common_size=True
        )

        # Convert to Univer snapshot
        snapshot = univer_converter.convert_to_snapshot(
            report_data=report,
            workbook_name=f"รายงานผลดำเนินงาน {filter.year}"
        )

        logger.info(
            f"Univer snapshot generated successfully: "
            f"{len(snapshot.get('sheets', {}))} sheets"
        )

        return snapshot

    except ValueError as e:
        logger.error(f"Invalid filter parameters: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except FileNotFoundError as e:
        logger.error(f"Data file not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data files not found"
        )
    except Exception as e:
        logger.error(f"Error generating Univer snapshot: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Univer snapshot: {str(e)}"
        )


@router.post("/reload-data")
async def reload_data(
    current_user: UserInfo = Depends(get_current_user)
):
    """
    Reload data from CSV files

    Force reload of data from CSV files, clearing any cached data.
    Useful when CSV files have been updated.

    Args:
        current_user: Current authenticated user

    Returns:
        Success message with data statistics
    """
    logger.info(f"Data reload requested by {current_user.email}")

    try:
        data_loader.reload_data()

        # Get data statistics
        df = data_loader.load_profit_loss_data()

        return {
            "message": "Data reloaded successfully",
            "statistics": {
                "total_rows": len(df),
                "years": sorted(df['YEAR'].unique().tolist()),
                "business_groups": len(df['BUSINESS_GROUP'].unique()),
                "last_load_time": data_loader.last_load_time.isoformat() if data_loader.last_load_time else None
            }
        }

    except Exception as e:
        logger.error(f"Error reloading data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload data: {str(e)}"
        )


@router.post("/export")
async def export_to_excel(
    filter: ReportFilter,
    current_user: UserInfo = Depends(get_current_user)
):
    """
    Export report to Excel file in crosstab format

    Generate P&L report and export as Excel (.xlsx) file with
    crosstab layout showing cost centers across columns.

    Args:
        filter: Report filter parameters (year, months, business_groups)
        current_user: Current authenticated user

    Returns:
        Excel file download response

    Raises:
        HTTPException 400: If invalid filter parameters
        HTTPException 404: If no data found
        HTTPException 500: If export fails
    """
    from fastapi.responses import StreamingResponse
    from io import BytesIO
    import pandas as pd
    from datetime import datetime as dt
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    logger.info(
        f"Excel export requested by {current_user.email}: "
        f"year={filter.year}, months={filter.months}"
    )

    try:
        # Load raw data and create crosstab
        df = data_loader.filter_data(filter.year, filter.months, filter.business_groups)

        # Create Excel file in memory
        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Create P&L Report crosstab

            # Revenue crosstab (use TYPE='รายได้' and AMOUNT column)
            df_revenue = df[df['TYPE'] == 'รายได้'].copy()
            if not df_revenue.empty:
                revenue_pivot = pd.pivot_table(
                    df_revenue,
                    index=['TYPE', 'หมวดบัญชี'],
                    columns='SERVICE_GROUP',
                    values='AMOUNT',
                    aggfunc='sum',
                    fill_value=0,
                    margins=True,
                    margins_name='รวมทั้งหมด'
                )
                revenue_pivot.to_excel(writer, sheet_name='รายได้', merge_cells=False)

            # Cost of Service crosstab (use AMOUNT column)
            df_cost = df[df['TYPE'] == 'ต้นทุนบริการ'].copy()
            if not df_cost.empty:
                cost_pivot = pd.pivot_table(
                    df_cost,
                    index=['TYPE', 'หมวดบัญชี'],
                    columns='SERVICE_GROUP',
                    values='AMOUNT',
                    aggfunc='sum',
                    fill_value=0,
                    margins=True,
                    margins_name='รวมทั้งหมด'
                )
                cost_pivot.to_excel(writer, sheet_name='ต้นทุนบริการ', merge_cells=False)

            # Selling Expense crosstab (use AMOUNT column)
            df_selling = df[df['TYPE'] == 'ค่าใช้จ่ายขายและการตลาด'].copy()
            if not df_selling.empty:
                selling_pivot = pd.pivot_table(
                    df_selling,
                    index=['TYPE', 'หมวดบัญชี'],
                    columns='SERVICE_GROUP',
                    values='AMOUNT',
                    aggfunc='sum',
                    fill_value=0,
                    margins=True,
                    margins_name='รวมทั้งหมด'
                )
                selling_pivot.to_excel(writer, sheet_name='ค่าใช้จ่ายขาย', merge_cells=False)

            # Admin Expense crosstab (use AMOUNT column)
            df_admin = df[df['TYPE'] == 'ค่าใช้จ่ายสนับสนุน'].copy()
            if not df_admin.empty:
                admin_pivot = pd.pivot_table(
                    df_admin,
                    index=['TYPE', 'หมวดบัญชี'],
                    columns='SERVICE_GROUP',
                    values='AMOUNT',
                    aggfunc='sum',
                    fill_value=0,
                    margins=True,
                    margins_name='รวมทั้งหมด'
                )
                admin_pivot.to_excel(writer, sheet_name='ค่าใช้จ่ายสนับสนุน', merge_cells=False)

            # Complete P&L crosstab (all types combined, use AMOUNT column)
            pl_pivot = pd.pivot_table(
                df,
                index=['TYPE', 'หมวดบัญชี'],
                columns='SERVICE_GROUP',
                values='AMOUNT',
                aggfunc='sum',
                fill_value=0,
                margins=True,
                margins_name='รวมทั้งหมด'
            )
            pl_pivot.to_excel(writer, sheet_name='P&L Report', merge_cells=False)

            # Apply formatting to all sheets
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]

                # Header formatting
                header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
                header_font = Font(bold=True, color='FFFFFF', size=11)

                # Format header rows
                for row in worksheet.iter_rows(min_row=1, max_row=2, min_col=1, max_col=worksheet.max_column):
                    for cell in row:
                        cell.fill = header_fill
                        cell.font = header_font
                        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

                # Format total column/row
                total_fill = PatternFill(start_color='FFD966', end_color='FFD966', fill_type='solid')
                total_font = Font(bold=True)

                # Find and format "รวมทั้งหมด" rows and columns
                for row in worksheet.iter_rows(min_row=3, max_row=worksheet.max_row):
                    if row[0].value == 'รวมทั้งหมด' or (row[1].value and 'รวม' in str(row[1].value)):
                        for cell in row:
                            cell.fill = total_fill
                            cell.font = total_font

                # Format number columns
                for row in worksheet.iter_rows(min_row=3, max_row=worksheet.max_row, min_col=3):
                    for cell in row:
                        if isinstance(cell.value, (int, float)):
                            cell.number_format = '#,##0.00'
                            cell.alignment = Alignment(horizontal='right')

                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if cell.value:
                                max_length = max(max_length, len(str(cell.value)))
                        except:
                            pass
                    adjusted_width = min(max_length + 3, 60)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

                # Add borders
                thin_border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
                for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row, min_col=1, max_col=worksheet.max_column):
                    for cell in row:
                        cell.border = thin_border

        # Prepare file for download
        output.seek(0)

        # Generate filename
        months_str = '-'.join(map(str, filter.months))
        filename = f"P&L_Report_{filter.year}_{months_str}_{dt.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        logger.info(f"Excel file generated successfully: {filename}")

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except ValueError as e:
        logger.error(f"Invalid filter parameters: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error exporting to Excel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export to Excel: {str(e)}"
        )


@router.get("/health")
async def report_health_check():
    """
    Health check for report service

    Returns:
        Service status and data loading status
    """
    return {
        "status": "healthy",
        "service": "Report",
        "data_loaded": data_loader.is_data_loaded,
        "last_load_time": data_loader.last_load_time.isoformat() if data_loader.last_load_time else None
    }

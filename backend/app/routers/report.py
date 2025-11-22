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

"""
Report Router - Simplified version for viewing pre-generated Excel reports
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from pathlib import Path

from app.models.auth import UserInfo
from app.routers.auth import get_current_user
from app.services.excel_to_univer import excel_to_univer_converter

logger = logging.getLogger(__name__)

# Configuration for pre-generated reports
REPORTS_DIR = Path("/Users/seal/Documents/GitHub/univer/report_generator/output")

# Simple in-memory cache to store parsed workbook data
workbook_cache = {}

# Create router
router = APIRouter(prefix="/report", tags=["Report"])


@router.get("/reports/list", response_model=List[str])
async def list_pregenerated_reports(
    current_user: UserInfo = Depends(get_current_user)
):
    """
    List all available pre-generated Excel reports.

    Scans the designated report directory and returns a list of
    all `.xlsx` files found.

    Args:
        current_user: Current authenticated user.

    Returns:
        A list of Excel report filenames.
    """
    logger.info(f"Report list requested by {current_user.email}")
    try:
        if not REPORTS_DIR.exists() or not REPORTS_DIR.is_dir():
            logger.warning(f"Reports directory not found: {REPORTS_DIR}")
            return []

        # Scan directory, filter for .xlsx files, and sort alphabetically
        files = sorted([
            f.name for f in REPORTS_DIR.iterdir()
            if f.is_file() and f.suffix.lower() == '.xlsx' and not f.name.startswith('~')
        ])
        return files
    except Exception as e:
        logger.error(f"Error listing reports in {REPORTS_DIR}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list available reports."
        )


@router.get("/reports/view/{filename}", response_model=Dict[str, Any])
async def view_pregenerated_report(
    filename: str,
    current_user: UserInfo = Depends(get_current_user)
):
    """
    Load a pre-generated Excel file and convert it to Univer JSON format.

    This endpoint reads an existing Excel file, converts it into a Univer-compatible
    JSON object, and returns it. It uses a cache to speed up subsequent requests
    for the same file.

    Args:
        filename: The name of the Excel file to load.
        current_user: Current authenticated user.

    Returns:
        A Univer-compatible workbook object in JSON format.
    """
    logger.info(f"Report '{filename}' requested by {current_user.email}")

    if ".." in filename or filename.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid filename.")

    file_path = REPORTS_DIR / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"Report '{filename}' not found.")

    # Caching Logic
    file_mod_time = file_path.stat().st_mtime
    cache_key = f"{filename}::{file_mod_time}"

    if cache_key in workbook_cache:
        logger.info(f"Returning cached version of '{filename}'.")
        return workbook_cache[cache_key]

    try:
        logger.info(f"No cache found for '{filename}', starting conversion.")
        
        # Convert the Excel file to a Univer snapshot
        snapshot = excel_to_univer_converter.convert_file_to_snapshot(file_path)

        # Store the converted snapshot in the cache
        workbook_cache[cache_key] = snapshot
        
        # Limit cache size (keep only last 10 files)
        if len(workbook_cache) > 10:
            # Remove oldest cache entry
            oldest_key = next(iter(workbook_cache))
            workbook_cache.pop(oldest_key)
            logger.info(f"Cache limit reached, removed oldest entry: {oldest_key}")

        logger.info(f"Conversion successful for '{filename}', result stored in cache.")
        return snapshot

    except Exception as e:
        logger.error(f"Failed to convert report '{filename}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the report: {e}"
        )


@router.post("/reports/clear-cache")
async def clear_reports_cache(
    current_user: UserInfo = Depends(get_current_user)
):
    """
    Clear the in-memory cache of converted report snapshots.

    Useful after updating the Excel to Univer converter or when
    you want to force re-conversion of all reports.

    Args:
        current_user: Current authenticated user.

    Returns:
        Status message with number of cached items cleared.
    """
    logger.info(f"Cache clear requested by {current_user.email}")

    cache_size = len(workbook_cache)
    workbook_cache.clear()

    logger.info(f"Cleared {cache_size} cached snapshots.")

    return {
        "message": "Cache cleared successfully",
        "cleared_count": cache_size
    }


@router.get("/health")
async def report_health_check():
    """
    Health check for report service

    Returns:
        Service status
    """
    return {
        "status": "healthy",
        "service": "Report Viewer",
        "reports_directory": str(REPORTS_DIR),
        "directory_exists": REPORTS_DIR.exists(),
        "cache_size": len(workbook_cache)
    }

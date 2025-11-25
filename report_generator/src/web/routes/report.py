"""
Report Generation Routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List
import logging
from datetime import datetime

from config.settings import settings
from src.web.models.auth import UserInfo
from src.web.models.report import (
    AvailableFile,
    ReportGenerateRequest,
    ReportGenerateResponse,
    EmailSendRequest,
    EmailSendResponse
)
from src.web.routes.auth import get_current_user
from src.data_loader import CSVLoader, DataProcessor
from src.excel_generator import ExcelGenerator
from src.web.utils.email import create_email_sender

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
csv_loader = CSVLoader(encoding=settings.csv_encoding)
data_processor = DataProcessor()
email_sender = create_email_sender(settings)


@router.get("/files", response_model=List[AvailableFile])
async def list_available_files(
    current_user: UserInfo = Depends(get_current_user)
):
    """
    List available CSV data files

    Args:
        current_user: Current authenticated user

    Returns:
        List of available files
    """
    data_dir = Path(settings.data_dir)

    if not data_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data directory not found: {data_dir}"
        )

    # Find all CSV files matching patterns
    patterns = [
        "TRN_PL_COSTTYPE_NT_MTH_TABLE_*.csv",
        "TRN_PL_COSTTYPE_NT_YTD_TABLE_*.csv",
        "TRN_PL_GLGROUP_NT_MTH_TABLE_*.csv",
        "TRN_PL_GLGROUP_NT_YTD_TABLE_*.csv"
    ]

    files = []
    for pattern in patterns:
        for file_path in data_dir.glob(pattern):
            # Extract file type and date
            filename = file_path.name
            date_str = csv_loader.extract_date_from_filename(filename) or "unknown"

            if "COSTTYPE" in filename and "MTH" in filename:
                file_type = "COSTTYPE_MTH"
            elif "COSTTYPE" in filename and "YTD" in filename:
                file_type = "COSTTYPE_YTD"
            elif "GLGROUP" in filename and "MTH" in filename:
                file_type = "GLGROUP_MTH"
            elif "GLGROUP" in filename and "YTD" in filename:
                file_type = "GLGROUP_YTD"
            else:
                file_type = "UNKNOWN"

            files.append(AvailableFile(
                filename=filename,
                file_type=file_type,
                date_str=date_str,
                size=file_path.stat().st_size,
                modified=datetime.fromtimestamp(file_path.stat().st_mtime)
            ))

    # Sort by date (newest first)
    files.sort(key=lambda x: x.date_str, reverse=True)

    logger.info(f"Found {len(files)} available files for {current_user.email}")

    return files


@router.post("/generate", response_model=ReportGenerateResponse)
async def generate_report(
    request: ReportGenerateRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """
    Generate Excel report from CSV file

    Args:
        request: Report generation request
        current_user: Current authenticated user

    Returns:
        Report generation response
    """
    logger.info(f"Report generation requested by {current_user.email}: {request.filename}")

    data_dir = Path(settings.data_dir)
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find file
    file_path = data_dir / request.filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {request.filename}"
        )

    try:
        # Load CSV
        logger.info(f"Loading CSV file: {file_path}")
        df = csv_loader.load_csv(file_path)

        # Process data
        logger.info("Processing data...")
        report_type = request.report_type or (
            "COSTTYPE" if "COSTTYPE" in request.filename else "GLGROUP"
        )
        df_processed = data_processor.process_data(df, report_type=report_type)

        # Load remark file
        date_str = csv_loader.extract_date_from_filename(request.filename)
        remark_content = csv_loader.load_remark_file(data_dir, date_str)

        # Determine period type
        period_type = request.period_type or (
            "YTD" if "YTD" in request.filename else "MTH"
        )

        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"P&L_{report_type}_{period_type}_{date_str}_{timestamp}.xlsx"
        output_path = output_dir / output_filename

        # Generate Excel
        logger.info("Generating Excel report...")
        generator = ExcelGenerator(
            settings=settings.__dict__,
            bu_colors=settings.bu_colors,
            row_colors=settings.row_colors
        )

        result_path = generator.generate_report(
            data=df_processed,
            output_path=output_path,
            report_type=report_type,
            period_type=period_type,
            remark_content=remark_content
        )

        # Get file info
        file_size = result_path.stat().st_size
        download_url = f"/api/report/download/{output_filename}"

        logger.info(f"Report generated successfully: {result_path}")

        return ReportGenerateResponse(
            success=True,
            filename=output_filename,
            file_path=str(result_path),
            file_size=file_size,
            download_url=download_url,
            message="Report generated successfully"
        )

    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_report(
    filename: str,
    current_user: UserInfo = Depends(get_current_user)
):
    """
    Download generated report

    Args:
        filename: Report filename
        current_user: Current authenticated user

    Returns:
        File response
    """
    output_dir = Path(settings.output_dir)
    file_path = output_dir / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {filename}"
        )

    logger.info(f"File download: {filename} by {current_user.email}")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.post("/send-email", response_model=EmailSendResponse)
async def send_report_email(
    request: EmailSendRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """
    Send report via email

    Args:
        request: Email send request
        current_user: Current authenticated user

    Returns:
        Email send response
    """
    if not email_sender:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email service not configured"
        )

    output_dir = Path(settings.output_dir)
    file_path = output_dir / request.report_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report file not found: {request.report_filename}"
        )

    # Generate subject and body if not provided
    subject = request.subject or f"รายงาน P&L - {request.report_filename}"

    body = request.body or f"""
เรียน ท่านผู้รับรายงาน

ขอส่งรายงาน P&L ตามไฟล์แนบ

ชื่อไฟล์: {request.report_filename}
ส่งโดย: {current_user.email}
วันที่ส่ง: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

ขอบคุณครับ/ค่ะ
Univer Report Generator System
    """

    try:
        # Send email
        logger.info(f"Sending report to {request.to_emails}")
        success = email_sender.send_report_email(
            to_emails=request.to_emails,
            subject=subject,
            body=body,
            report_path=file_path
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email"
            )

        logger.info(f"Email sent successfully to {request.to_emails}")

        return EmailSendResponse(
            success=True,
            message="Email sent successfully",
            recipients=request.to_emails
        )

    except Exception as e:
        logger.error(f"Error sending email: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )


@router.get("/health")
async def report_health():
    """Health check for report service"""
    data_dir = Path(settings.data_dir)
    output_dir = Path(settings.output_dir)

    return {
        "status": "healthy",
        "data_dir_exists": data_dir.exists(),
        "output_dir_exists": output_dir.exists(),
        "email_configured": email_sender is not None
    }

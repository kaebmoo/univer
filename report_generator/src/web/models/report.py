"""
Report Models
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AvailableFile(BaseModel):
    """Available data file"""
    filename: str
    file_type: str  # COSTTYPE_MTH, COSTTYPE_YTD, etc.
    date_str: str  # YYYYMMDD
    size: int  # bytes
    modified: datetime


class ReportGenerateRequest(BaseModel):
    """Request to generate report"""
    filename: str
    report_type: Optional[str] = None  # Auto-detect if None
    period_type: Optional[str] = None  # Auto-detect if None


class ReportGenerateResponse(BaseModel):
    """Response after generating report"""
    success: bool
    filename: str
    file_path: str
    file_size: int
    download_url: str
    message: str


class EmailSendRequest(BaseModel):
    """Request to send report via email"""
    report_filename: str
    to_emails: List[str]
    subject: Optional[str] = None  # Auto-generate if None
    body: Optional[str] = None  # Auto-generate if None


class EmailSendResponse(BaseModel):
    """Response after sending email"""
    success: bool
    message: str
    recipients: List[str]

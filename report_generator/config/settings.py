"""
Configuration settings for Univer Report Generator
"""
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Application
    app_name: str = "Univer Report Generator"
    app_env: str = "development"
    debug: bool = True

    # Data files configuration
    data_dir: Path = Path("../data")
    output_dir: Path = Path("./output")

    # File patterns
    costtype_mth_pattern: str = "TRN_PL_COSTTYPE_NT_MTH_TABLE_*.csv"
    costtype_ytd_pattern: str = "TRN_PL_COSTTYPE_NT_YTD_TABLE_*.csv"
    glgroup_mth_pattern: str = "TRN_PL_GLGROUP_NT_MTH_TABLE_*.csv"
    glgroup_ytd_pattern: str = "TRN_PL_GLGROUP_NT_YTD_TABLE_*.csv"
    remark_file: str = "remark_*.txt"

    # Data encoding (Thai encoding)
    csv_encoding: str = "tis-620"  # หรือ "windows-874" หรือ "cp874"

    # Excel formatting
    excel_font_name: str = "TH Sarabun New"
    excel_font_size: int = 18
    excel_header_font_size: int = 18
    excel_remark_font_size: int = 16
    excel_info_box_font_size: int = 14

    # Report start position
    report_start_row: int = 6  # Row 6 (0-indexed: 5)
    report_start_col: int = 2  # Column B (0-indexed: 1)

    # Header position
    header_start_row: int = 2  # Row 2 (0-indexed: 1)

    # Info box position (top right)
    info_box_start_col: int = 7  # Column G
    info_box_start_row: int = 2

    # Colors configuration (Business Units / Service Groups)
    bu_colors: dict = {
        "HARD INFRASTRUCTURE": "#E2EFDA",
        "INTERNATIONAL": "#DDEBF7",
        "MOBILE": "#DBD3E5",
        "FIXED LINE & BROADBAND": "#FCE4D6",
        "DIGITAL": "#D9E1F2",
        "ICT SOLUTION": "#C6E0B4",
        "กลุ่มบริการอื่นไม่ใช่โทรคมนาคม": "#BDD7EE",
        "รายได้อื่น/ค่าใช้จ่ายอื่น": "#EAC1C0",
    }

    # Row colors
    row_colors: dict = {
        "รายละเอียด": "#F4DEDC",
        "section_header": "#F8CBAD",  # สำหรับ 1.รายได้, 2.ต้นทุน, etc.
    }

    # Info box color
    info_box_color: str = "#F8CBAD"

    # Email configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@company.com"
    smtp_from_name: str = "Univer Report System"
    smtp_use_ssl: bool = True

    # OTP configuration
    otp_length: int = 6
    otp_expiration: int = 300  # seconds (5 minutes)
    otp_max_attempts: int = 3

    # Allowed email domains
    allowed_email_domains: List[str] = ["company.com", "company.co.th"]

    # Web server
    web_host: str = "0.0.0.0"
    web_port: int = 8000

    # JWT configuration
    jwt_secret: str = "change-this-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 1440  # minutes (24 hours)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def is_email_allowed(self, email: str) -> bool:
        """Check if email domain is allowed"""
        domain = email.split("@")[-1].lower()
        return domain in [d.lower() for d in self.allowed_email_domains]


# Global settings instance
settings = Settings()

"""
Email Utilities - Send emails via SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class EmailSender:
    """Send emails via SMTP"""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
        from_name: str = "",
        use_ssl: bool = True
    ):
        """
        Initialize Email Sender

        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port (587 for TLS, 465 for SSL)
            username: SMTP username
            password: SMTP password
            from_email: From email address
            from_name: From name
            use_ssl: Use SSL/TLS
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.from_name = from_name
        self.use_ssl = use_ssl

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        attachments: Optional[List[Path]] = None,
        html: bool = False
    ) -> bool:
        """
        Send email

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body: Email body
            attachments: List of file paths to attach
            html: Whether body is HTML

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>" if self.from_name else self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject

            # Add body
            mime_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, mime_type, 'utf-8'))

            # Add attachments
            if attachments:
                for file_path in attachments:
                    if not file_path.exists():
                        logger.warning(f"Attachment not found: {file_path}")
                        continue

                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {file_path.name}'
                        )
                        msg.attach(part)

            # Connect and send
            if self.use_ssl and self.smtp_port == 465:
                # SSL
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.username, self.password)
                    server.send_message(msg)
            else:
                # TLS
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    server.send_message(msg)

            logger.info(f"Email sent successfully to {to_emails}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_otp_email(self, to_email: str, otp: str) -> bool:
        """
        Send OTP email

        Args:
            to_email: Recipient email
            otp: OTP code

        Returns:
            True if sent successfully
        """
        subject = "รหัส OTP สำหรับเข้าสู่ระบบ Univer Report Generator"
        body = f"""
สวัสดีครับ/ค่ะ

รหัส OTP ของคุณคือ: {otp}

รหัสนี้มีอายุ 5 นาที กรุณาใช้รหัสนี้เพื่อเข้าสู่ระบบ

หากคุณไม่ได้ร้องขอรหัสนี้ กรุณาเพิกเฉยต่ออีเมลนี้

ขอบคุณครับ/ค่ะ
Univer Report Generator System
        """

        return self.send_email([to_email], subject, body)

    def send_report_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        report_path: Path
    ) -> bool:
        """
        Send report email with attachment

        Args:
            to_emails: List of recipient emails
            subject: Email subject
            body: Email body
            report_path: Path to report file

        Returns:
            True if sent successfully
        """
        return self.send_email(
            to_emails=to_emails,
            subject=subject,
            body=body,
            attachments=[report_path]
        )


# Create global email sender (will be None if credentials not configured)
def create_email_sender(settings) -> Optional[EmailSender]:
    """Create email sender from settings"""
    if not settings.smtp_username or not settings.smtp_password:
        logger.warning("SMTP credentials not configured, email sending disabled")
        return None

    return EmailSender(
        smtp_server=settings.smtp_server,
        smtp_port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        from_email=settings.smtp_from_email,
        from_name=settings.smtp_from_name,
        use_ssl=settings.smtp_use_ssl
    )

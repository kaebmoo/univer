"""
Email Sending Utilities
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


def send_otp_email(to_email: str, otp_code: str) -> bool:
    """
    Send OTP code via email

    Args:
        to_email: Recipient email address
        otp_code: OTP code to send

    Returns:
        True if email sent successfully, False otherwise
    """
    # Development mode: Just log OTP instead of sending email
    if settings.app_env == "development" and (
        settings.smtp_username == "your-email@gmail.com"
        or not settings.smtp_username
    ):
        logger.info("=" * 60)
        logger.info("📧 DEVELOPMENT MODE - OTP EMAIL")
        logger.info(f"To: {to_email}")
        logger.info(f"OTP Code: {otp_code}")
        logger.info(f"Expires in: {settings.otp_expiration // 60} minutes")
        logger.info("=" * 60)
        print(f"\n{'='*60}")
        print(f"📧 OTP for {to_email}: {otp_code}")
        print(f"{'='*60}\n")
        return True

    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"รหัส OTP สำหรับเข้าสู่ระบบ {settings.app_name}"
        msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
        msg["To"] = to_email

        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .content {{
                    background: white;
                    border-radius: 8px;
                    padding: 30px;
                    text-align: center;
                }}
                .otp-code {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #667eea;
                    letter-spacing: 8px;
                    padding: 20px;
                    background: #f7f7f7;
                    border-radius: 8px;
                    margin: 20px 0;
                    font-family: 'Courier New', monospace;
                }}
                .warning {{
                    color: #e74c3c;
                    font-size: 14px;
                    margin-top: 20px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    color: white;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <h2>🔐 รหัส OTP สำหรับเข้าสู่ระบบ</h2>
                    <p>กรุณาใช้รหัส OTP ด้านล่างเพื่อเข้าสู่ระบบ {settings.app_name}</p>

                    <div class="otp-code">{otp_code}</div>

                    <p>รหัส OTP นี้จะหมดอายุภายใน <strong>{settings.otp_expiration // 60} นาที</strong></p>

                    <div class="warning">
                        ⚠️ กรุณาอย่าแชร์รหัส OTP นี้กับผู้อื่น<br>
                        หากคุณไม่ได้ทำการขอรหัส OTP กรุณาเพิกเฉยต่ออีเมลนี้
                    </div>
                </div>

                <div class="footer">
                    <p>อีเมลนี้ถูกส่งโดยอัตโนมัติ กรุณาอย่าตอบกลับ</p>
                    <p>&copy; 2025 {settings.app_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Create plain text version
        text_content = f"""
        รหัส OTP สำหรับเข้าสู่ระบบ {settings.app_name}

        รหัส OTP ของคุณคือ: {otp_code}

        รหัส OTP นี้จะหมดอายุภายใน {settings.otp_expiration // 60} นาที

        กรุณาอย่าแชร์รหัส OTP นี้กับผู้อื่น
        หากคุณไม่ได้ทำการขอรหัส OTP กรุณาเพิกเฉยต่ออีเมลนี้

        ---
        อีเมลนี้ถูกส่งโดยอัตโนมัติ กรุณาอย่าตอบกลับ
        © 2025 {settings.app_name}. All rights reserved.
        """

        # Attach parts
        part1 = MIMEText(text_content, "plain", "utf-8")
        part2 = MIMEText(html_content, "html", "utf-8")
        msg.attach(part1)
        msg.attach(part2)

        # Send email
        logger.info(f"Sending OTP email to {to_email}")

        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)

        logger.info(f"OTP email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send OTP email to {to_email}: {str(e)}")
        return False


def send_notification_email(
    to_email: str,
    subject: str,
    message: str,
    html_message: Optional[str] = None
) -> bool:
    """
    Send a general notification email

    Args:
        to_email: Recipient email address
        subject: Email subject
        message: Plain text message
        html_message: Optional HTML version of message

    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
        msg["To"] = to_email

        # Attach plain text
        part1 = MIMEText(message, "plain", "utf-8")
        msg.attach(part1)

        # Attach HTML if provided
        if html_message:
            part2 = MIMEText(html_message, "html", "utf-8")
            msg.attach(part2)

        # Send email
        logger.info(f"Sending notification email to {to_email}")

        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)

        logger.info(f"Notification email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send notification email to {to_email}: {str(e)}")
        return False

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "your-email@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "your-app-password")
FROM_NAME = os.getenv("FROM_NAME", "CourseStore")

async def send_purchase_confirmation(
    user_email: str,
    user_name: str,
    course_title: str,
    download_link: str
):
    subject = f"Your Course Access: {course_title}"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #0f0f1a; color: #e2e8f0; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #1e1b4b 0%, #1e293b 100%);
                         border-radius: 16px; padding: 40px; border: 1px solid rgba(79,70,229,0.3); }}
            .logo {{ font-size: 28px; font-weight: 700; color: #4F46E5; text-align: center; }}
            .badge {{ background: #22C55E; color: white; padding: 6px 16px; border-radius: 20px;
                      font-size: 12px; font-weight: 600; display: inline-block; margin: 10px 0; }}
            h1 {{ color: #e2e8f0; font-size: 24px; }}
            p {{ color: #94a3b8; line-height: 1.6; }}
            .course-card {{ background: rgba(79,70,229,0.1); border: 1px solid rgba(79,70,229,0.3);
                            border-radius: 12px; padding: 20px; margin: 20px 0; }}
            .download-btn {{ display: inline-block; background: linear-gradient(135deg, #4F46E5, #7C3AED);
                             color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none;
                             font-weight: 600; font-size: 16px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #475569; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">CourseStore</div>
            <div style="text-align:center;"><div class="badge">Payment Verified</div></div>
            <h1>Welcome, {user_name}!</h1>
            <p>Your payment has been verified. Your course access is now activated.</p>
            <div class="course-card">
                <strong style="color:#a5b4fc;">{course_title}</strong>
            </div>
            <div style="text-align:center;">
                <a href="{download_link}" class="download-btn">Access Course Now</a>
            </div>
            <div class="footer">
                <p>Thank you for choosing CourseStore</p>
                <p>2024 CourseStore. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{FROM_NAME} <{SMTP_USER}>"
    message["To"] = user_email
    message.attach(MIMEText(html_body, "html"))
    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASS,
            start_tls=True,
        )
        logger.info(f"Email sent to {user_email}")
        return True
    except Exception as e:
        logger.error(f"Email failed: {e}")
        return False

async def send_rejection_email(
    user_email: str,
    user_name: str,
    course_title: str,
    admin_note: str
):
    subject = f"Payment Update: {course_title}"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family:Arial,sans-serif;background:#0f0f1a;color:#e2e8f0;padding:20px;">
        <div style="max-width:600px;margin:0 auto;background:#1e293b;border-radius:16px;padding:40px;">
            <h2>Hi {user_name},</h2>
            <p>We could not verify your payment for <strong>{course_title}</strong>.</p>
            <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:8px;padding:16px;color:#fca5a5;">
                <strong>Note:</strong> {admin_note or "Payment could not be verified. Please try again."}
            </div>
            <p>Please try again or contact support.</p>
            <p style="color:#475569;font-size:12px;">2024 CourseStore</p>
        </div>
    </body>
    </html>
    """
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{FROM_NAME} <{SMTP_USER}>"
    message["To"] = user_email
    message.attach(MIMEText(html_body, "html"))
    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASS,
            start_tls=True,
        )
        return True
    except Exception as e:
        logger.error(f"Rejection email failed: {e}")
        return False

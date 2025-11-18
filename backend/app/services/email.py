import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from app.core.config import settings


async def send_email(to_email: str, subject: str, html_content: str):
    """Send an email"""
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>"
    message["To"] = to_email

    # Add HTML part
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
    except Exception as e:
        print(f"Error sending email: {e}")
        # In production, log this properly


async def send_verification_email(email: str, token: str):
    """Send email verification link"""
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    html_template = Template("""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .button { background-color: #6366f1; color: white; padding: 12px 24px;
                     text-decoration: none; border-radius: 6px; display: inline-block; }
            .footer { margin-top: 30px; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Welcome to Azolute AI!</h2>
            <p>Thank you for signing up. Please verify your email address by clicking the button below:</p>
            <p><a href="{{ verification_url }}" class="button">Verify Email</a></p>
            <p>Or copy and paste this link into your browser:</p>
            <p>{{ verification_url }}</p>
            <div class="footer">
                <p>This link will expire in 7 days.</p>
                <p>If you didn't create an account, please ignore this email.</p>
            </div>
        </div>
    </body>
    </html>
    """)

    html_content = html_template.render(verification_url=verification_url)
    await send_email(email, "Verify your email - Azolute AI", html_content)


async def send_password_reset_email(email: str, token: str):
    """Send password reset link"""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    html_template = Template("""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .button { background-color: #6366f1; color: white; padding: 12px 24px;
                     text-decoration: none; border-radius: 6px; display: inline-block; }
            .footer { margin-top: 30px; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Reset Your Password</h2>
            <p>We received a request to reset your password. Click the button below to set a new password:</p>
            <p><a href="{{ reset_url }}" class="button">Reset Password</a></p>
            <p>Or copy and paste this link into your browser:</p>
            <p>{{ reset_url }}</p>
            <div class="footer">
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request a password reset, please ignore this email.</p>
            </div>
        </div>
    </body>
    </html>
    """)

    html_content = html_template.render(reset_url=reset_url)
    await send_email(email, "Reset your password - Azolute AI", html_content)

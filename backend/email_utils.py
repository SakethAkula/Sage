"""
Sage - Email Utilities
Handles OTP generation and email sending
"""

import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Email configuration from environment
SMTP_EMAIL = os.environ.get('SMTP_EMAIL', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')  # App password for Gmail
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))

# Store OTPs temporarily (in production, use Redis or database)
otp_store = {}


def generate_otp(length=6):
    """Generate a random numeric OTP."""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(to_email, otp, purpose="verification"):
    """Send OTP email for verification or password reset."""
    
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("SMTP credentials not configured")
        return False
    
    subject = "Sage - Email Verification OTP" if purpose == "verification" else "Sage - Password Reset OTP"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f9f7; margin: 0; padding: 20px; }}
            .container {{ max-width: 500px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #3dbda7 0%, #2d8a7a 100%); padding: 30px; text-align: center; }}
            .header h1 {{ color: white; margin: 0; font-size: 28px; }}
            .header p {{ color: rgba(255,255,255,0.9); margin: 10px 0 0 0; }}
            .content {{ padding: 30px; text-align: center; }}
            .otp-box {{ background: #f0f9f7; border: 2px dashed #3dbda7; border-radius: 10px; padding: 20px; margin: 20px 0; }}
            .otp-code {{ font-size: 36px; font-weight: bold; color: #2d8a7a; letter-spacing: 8px; }}
            .message {{ color: #666; line-height: 1.6; }}
            .footer {{ background: #f8f8f8; padding: 20px; text-align: center; color: #999; font-size: 12px; }}
            .warning {{ color: #e74c3c; font-size: 13px; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌿 Sage</h1>
                <p>AI Healthcare Chatbot</p>
            </div>
            <div class="content">
                <p class="message">
                    {"Please verify your email address to complete your registration." if purpose == "verification" else "You requested to reset your password."}
                </p>
                <div class="otp-box">
                    <p style="margin: 0 0 10px 0; color: #666;">Your OTP Code:</p>
                    <div class="otp-code">{otp}</div>
                </div>
                <p class="message">This code will expire in <strong>10 minutes</strong>.</p>
                <p class="warning">If you didn't request this, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>© 2026 Sage Healthcare. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"Sage Healthcare <{SMTP_EMAIL}>"
        msg['To'] = to_email
        
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        
        print(f"OTP email sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def store_otp(email, otp, purpose="verification"):
    """Store OTP for verification."""
    import time
    otp_store[f"{purpose}:{email}"] = {
        'otp': otp,
        'created_at': time.time(),
        'expires_at': time.time() + 600  # 10 minutes
    }


def verify_otp(email, otp, purpose="verification"):
    """Verify the OTP."""
    import time
    key = f"{purpose}:{email}"
    
    if key not in otp_store:
        return False, "OTP not found. Please request a new one."
    
    stored = otp_store[key]
    
    if time.time() > stored['expires_at']:
        del otp_store[key]
        return False, "OTP has expired. Please request a new one."
    
    if stored['otp'] != otp:
        return False, "Invalid OTP. Please try again."
    
    # OTP is valid, remove it
    del otp_store[key]
    return True, "OTP verified successfully."


def send_verification_otp(email):
    """Generate and send verification OTP."""
    otp = generate_otp()
    store_otp(email, otp, "verification")
    return send_otp_email(email, otp, "verification"), otp


def send_password_reset_otp(email):
    """Generate and send password reset OTP."""
    otp = generate_otp()
    store_otp(email, otp, "reset")
    return send_otp_email(email, otp, "reset"), otp
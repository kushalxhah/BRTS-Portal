import requests
import random
from time import time
from config.settings import BREVO_API_KEY, BREVO_SENDER_EMAIL, BREVO_SENDER_NAME
from .database import save_otp


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email_brevo(email, name, otp):
    try:
        url = "https://api.brevo.com/v3/smtp/email"
        
        headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json"
        }
        
        # Professional HTML email template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 30px auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .otp-box {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 10px;
                    text-align: center;
                    margin: 25px 0;
                }}
                .otp-code {{
                    font-size: 36px;
                    font-weight: bold;
                    letter-spacing: 8px;
                    margin: 10px 0;
                }}
                .info-text {{
                    color: #555;
                    line-height: 1.6;
                    margin: 15px 0;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚌 Ahmedabad BRTS Portal</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px;">Email Verification</p>
                </div>
                <div class="content">
                    <h2 style="color: #333;">Hello {name},</h2>
                    <p class="info-text">
                        Thank you for registering with Ahmedabad BRTS Portal! To complete your registration, 
                        please verify your email address using the OTP below.
                    </p>
                    
                    <div class="otp-box">
                        <p style="margin: 0; font-size: 16px;">Your Verification Code</p>
                        <div class="otp-code">{otp}</div>
                        <p style="margin: 10px 0 0 0; font-size: 14px;">Valid for 3 minutes</p>
                    </div>
                    
                    <p class="info-text">
                        Enter this code on the registration page to verify your email and activate your account.
                    </p>
                    
                    <div class="warning">
                        <strong>⚠️ Security Note:</strong> Never share this OTP with anyone. Our team will never 
                        ask you for this code via phone or email.
                    </div>
                    
                    <p class="info-text">
                        If you didn't request this verification code, please ignore this email.
                    </p>
                </div>
                <div class="footer">
                    <p style="margin: 5px 0;">Ahmedabad BRTS Portal - Smart Travel Solution</p>
                    <p style="margin: 5px 0;">© 2026 All Rights Reserved</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        payload = {
            "sender": {
                "name": BREVO_SENDER_NAME,
                "email": BREVO_SENDER_EMAIL
            },
            "to": [
                {
                    "email": email,
                    "name": name
                }
            ],
            "subject": f"🔐 Your Verification Code: {otp} - Ahmedabad BRTS Portal",
            "htmlContent": html_content
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 201:
            # Store OTP in database
            if save_otp(email, otp):
                return True, "OTP sent successfully"
            else:
                return False, "Failed to save OTP"
        else:
            print(f"Brevo API Error: {response.status_code} - {response.text}")
            # Fallback: if IP not whitelisted or any API error, use demo mode
            if save_otp(email, otp):
                return True, f"DEMO_OTP:{otp}"
            else:
                return False, "Failed to save OTP"

    except Exception as e:
        print(f"Error sending OTP via Brevo: {e}")
        # Fallback to demo mode
        if save_otp(email, otp):
            return True, f"DEMO_OTP:{otp}"
        else:
            return False, "Failed to save OTP"


def verify_otp(email, entered_otp):
    """Verify the entered OTP - now handled by database.py"""
    from .database import verify_otp as db_verify_otp
    return db_verify_otp(email, entered_otp)


def get_remaining_time(email):
    """Get remaining time for OTP in seconds - now handled by database.py"""
    from .database import get_remaining_time as db_get_remaining_time
    return db_get_remaining_time(email)
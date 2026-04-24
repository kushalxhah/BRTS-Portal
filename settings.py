"""
Configuration settings for BRTS Portal
""" 

# Database Configuration (MySQL via XAMPP)
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',  # Default XAMPP MySQL password is empty
    'database': 'brts_portal',
    'charset': 'utf8mb4',
    'autocommit': True
}

# Email Service Configuration (Brevo API)
BREVO_API_KEY = "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"
BREVO_SENDER_EMAIL = "kushalkshah1606@gmail.com"
BREVO_SENDER_NAME = "Ahmedabad BRTS Portal"

# App Configuration
APP_TITLE = "Ahmedabad BRTS Portal"
APP_ICON = "🚌"
PAGE_LAYOUT = "wide"

# OTP Configuration
OTP_VALIDITY_SECONDS = 180  # 3 minutes
MAX_OTP_ATTEMPTS = 3

# Payment Configuration
FARE_PER_KM = 5.0
MAX_TICKETS_PER_BOOKING = 10
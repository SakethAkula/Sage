"""
Sage - Database Configuration
Reads from environment variables for Cloud Run deployment
"""
import os

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'sage_db'),
    'charset': 'utf8mb4'
}

# For Cloud SQL connection via Unix socket
DB_SOCKET = os.environ.get('DB_SOCKET', None)

# Google OAuth (optional)
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', '')

# Anthropic API Key
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# Flask secret key
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

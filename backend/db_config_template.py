"""
Sage - Database Configuration Template
Copy this file to db_config.py and fill in your credentials
"""

DB_CONFIG = {
    'host': 'localhost',  # For PythonAnywhere: YOUR_USERNAME.mysql.pythonanywhere-services.com
    'user': 'root',       # For PythonAnywhere: YOUR_USERNAME
    'password': 'YOUR_PASSWORD_HERE',
    'database': 'sage_db', # For PythonAnywhere: YOUR_USERNAME$sage_db
    'charset': 'utf8mb4'
}

# Google OAuth (optional)
GOOGLE_CLIENT_ID = 'YOUR_GOOGLE_CLIENT_ID'
GOOGLE_CLIENT_SECRET = 'YOUR_GOOGLE_CLIENT_SECRET'
GOOGLE_REDIRECT_URI = 'http://localhost:5000/auth/google/callback'

# Anthropic API Key
ANTHROPIC_API_KEY = 'YOUR_ANTHROPIC_API_KEY'
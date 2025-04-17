# ------------------- Constants and Configuration -------------------

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "new_password",  # Replace with your MySQL password
    "database": "library_system"
}

DB_NAME = "library_system"

# Session file paths
USER_SESSION_FILE = 'user_session.json'
ADMIN_SESSION_FILE = 'admin_session.json'

# Application Constants
FINE_RATE_PER_DAY = 0.50  # $0.50 per day for overdue books
LOAN_PERIOD_DAYS = 14  # Default loan period in days
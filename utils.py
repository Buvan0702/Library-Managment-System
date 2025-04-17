import mysql.connector
from tkinter import messagebox
import os
import json
import hashlib
from datetime import datetime, timedelta
from config import DB_CONFIG, DB_NAME, USER_SESSION_FILE, ADMIN_SESSION_FILE

# ------------------- Database Utility Functions -------------------
def connect_db():
    """Connect to the database"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Connection Error", f"Failed to connect to database: {err}")
        return None

def verify_database():
    """Verify that the database and tables exist"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        # Check if tables exist
        tables = ["Books", "Users", "Loans", "Fines"]
        for table in tables:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            if not cursor.fetchone():
                return False
        
        return True
    except mysql.connector.Error:
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def create_database():
    """Create the library_system database and tables"""
    try:
        # Connect without database selected
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        cursor = connection.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        
        # Create Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role ENUM('member', 'admin') DEFAULT 'member',
                registration_date DATE DEFAULT (CURRENT_DATE),
                CONSTRAINT email_unique UNIQUE (email)
            )
        """)
        
        # Create Books table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Books (
                book_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(100) NOT NULL,
                isbn VARCHAR(20) UNIQUE,
                publication_year INT,
                genre VARCHAR(50),
                description TEXT,
                total_copies INT DEFAULT 1,
                available_copies INT DEFAULT 1
            )
        """)
        
        # Create Loans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Loans (
                loan_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                book_id INT,
                loan_date DATE DEFAULT (CURRENT_DATE),
                due_date DATE,
                return_date DATE NULL,
                FOREIGN KEY (user_id) REFERENCES Users(user_id),
                FOREIGN KEY (book_id) REFERENCES Books(book_id)
            )
        """)
        
        # Create Fines table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Fines (
                fine_id INT AUTO_INCREMENT PRIMARY KEY,
                loan_id INT,
                amount DECIMAL(10, 2) NOT NULL,
                description VARCHAR(255),
                paid BOOLEAN DEFAULT FALSE,
                payment_date DATE NULL,
                FOREIGN KEY (loan_id) REFERENCES Loans(loan_id)
            )
        """)
        
        # Check if there's at least one admin user
        cursor.execute("SELECT COUNT(*) FROM Users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        # Create default admin if none exists
        if admin_count == 0:
            default_password = hashlib.sha256("admin123".encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO Users (first_name, last_name, email, password, role)
                VALUES ('Admin', 'User', 'admin@library.com', %s, 'admin')
            """, (default_password,))
        
        # Insert sample book data if the Books table is empty
        cursor.execute("SELECT COUNT(*) FROM Books")
        book_count = cursor.fetchone()[0]
        
        if book_count == 0:
            sample_books = [
                ("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565", 1925, "Fiction", "A novel about the American Dream", 5, 5),
                ("To Kill a Mockingbird", "Harper Lee", "9780061120084", 1960, "Fiction", "Classic novel of racial injustice", 3, 3),
                ("1984", "George Orwell", "9780451524935", 1949, "Dystopian", "Dystopian social science fiction", 4, 4),
                ("Pride and Prejudice", "Jane Austen", "9780141439518", 1813, "Romance", "A romantic novel of manners", 2, 2),
                ("The Hobbit", "J.R.R. Tolkien", "9780547928227", 1937, "Fantasy", "Fantasy novel and prelude to Lord of the Rings", 3, 3),
                ("The Catcher in the Rye", "J.D. Salinger", "9780316769488", 1951, "Fiction", "Story of teenage angst and alienation", 2, 2),
                ("The Lord of the Rings", "J.R.R. Tolkien", "9780618640157", 1954, "Fantasy", "Epic high-fantasy novel", 3, 3),
                ("Animal Farm", "George Orwell", "9780451526342", 1945, "Satire", "Allegorical novella", 4, 4),
                ("The Da Vinci Code", "Dan Brown", "9780307474278", 2003, "Mystery", "Mystery thriller novel", 5, 5),
                ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling", "9780590353427", 1997, "Fantasy", "Fantasy novel", 6, 6)
            ]
            
            cursor.executemany("""
                INSERT INTO Books (title, author, isbn, publication_year, genre, description, total_copies, available_copies)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, sample_books)
        
        connection.commit()
        return True
    except mysql.connector.Error as err:
        messagebox.showerror("Database Setup Error", f"Failed to set up database: {err}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

# ------------------- Session Utility Functions -------------------
def load_user_session():
    """Load user data from session file"""
    try:
        if os.path.exists(USER_SESSION_FILE):
            with open(USER_SESSION_FILE, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        messagebox.showerror("Session Error", f"Failed to load session: {e}")
        return None

def save_user_session(user_data):
    """Save user data to session file"""
    with open(USER_SESSION_FILE, 'w') as f:
        json.dump(user_data, f)

def clear_user_session():
    """Delete the user session file"""
    if os.path.exists(USER_SESSION_FILE):
        os.remove(USER_SESSION_FILE)

def load_admin_session():
    """Load admin session data"""
    try:
        if os.path.exists(ADMIN_SESSION_FILE):
            with open(ADMIN_SESSION_FILE, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        messagebox.showerror("Session Error", f"Failed to load session: {e}")
        return None

def save_admin_session(admin_data):
    """Save admin session data"""
    with open(ADMIN_SESSION_FILE, 'w') as f:
        json.dump(admin_data, f)

def clear_admin_session():
    """Delete the admin session file"""
    if os.path.exists(ADMIN_SESSION_FILE):
        os.remove(ADMIN_SESSION_FILE)

# ------------------- Date Utility Functions -------------------
def format_date(date_str):
    """Format date string to more readable format"""
    try:
        if isinstance(date_str, datetime):
            return date_str.strftime('%b %d, %Y')
        
        date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
        return date_obj.strftime('%b %d, %Y')
    except:
        return str(date_str)

def calculate_fine(due_date_str):
    """Calculate fine if book is overdue"""
    try:
        if isinstance(due_date_str, datetime):
            due_date = due_date_str
        else:
            due_date = datetime.strptime(str(due_date_str), '%Y-%m-%d')
        
        today = datetime.now()
        
        if today > due_date:
            days_overdue = (today - due_date).days
            fine = days_overdue * 0.50  # $0.50 per day
            return f"${fine:.2f}"
        return "$0.00"
    except Exception as e:
        print(f"Error calculating fine: {e}")
        return "$0.00"

def is_overdue(due_date_str):
    """Check if a book is overdue"""
    try:
        if isinstance(due_date_str, datetime):
            due_date = due_date_str
        else:
            due_date = datetime.strptime(str(due_date_str), '%Y-%m-%d')
        
        return datetime.now() > due_date
    except Exception as e:
        print(f"Error checking overdue: {e}")
        return False

def format_currency(amount):
    """Format amount as currency"""
    try:
        return f"${float(amount):.2f}"
    except:
        return f"${0:.2f}"

# ------------------- Password Utility Functions -------------------
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()
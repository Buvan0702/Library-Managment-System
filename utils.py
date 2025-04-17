from config import Config
import mysql.connector
from PIL import Image, ImageTk
import os
import tkinter as tk

# Connect to the database
def connect_to_database():
    """Establish and return a connection to the MySQL database"""
    conn = mysql.connector.connect(
        host=Config.db_host,
        user=Config.user,
        password=Config.password,
        database=Config.database
    )
    return conn

def center_window(window, width=900, height=600):
    """Centers a given window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def load_and_resize_image(image_path, width, height):
    """Load and resize an image to the specified dimensions"""
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return None
    
    try:
        img = Image.open(image_path)
        img = img.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

def create_tables():
    """
    Creates the necessary tables for the Library Management System.
    Tables include users, books, borrowed_books, and fines.
    """
    queries = {
        "users": """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT NOT NULL AUTO_INCREMENT,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                user_type ENUM('student', 'admin', 'lecturer') NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'active',
                date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id)
            );
        """,
        "books": """
            CREATE TABLE IF NOT EXISTS books (
                book_id INT NOT NULL AUTO_INCREMENT,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(100) NOT NULL,
                isbn VARCHAR(20) UNIQUE,
                genre VARCHAR(50),
                publication_year INT,
                publisher VARCHAR(100),
                total_copies INT NOT NULL DEFAULT 1,
                available_copies INT NOT NULL DEFAULT 1,
                date_added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (book_id)
            );
        """,
        "borrowed_books": """
            CREATE TABLE IF NOT EXISTS borrowed_books (
                borrow_id INT NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                borrow_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                due_date TIMESTAMP NOT NULL,
                return_date TIMESTAMP NULL,
                fine_amount DECIMAL(10, 2) DEFAULT 0.00,
                fine_paid BOOLEAN DEFAULT FALSE,
                status ENUM('borrowed', 'returned', 'overdue') NOT NULL DEFAULT 'borrowed',
                PRIMARY KEY (borrow_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
            );
        """,
        "fines": """
            CREATE TABLE IF NOT EXISTS fines (
                fine_id INT NOT NULL AUTO_INCREMENT,
                borrow_id INT NOT NULL,
                user_id INT NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                paid BOOLEAN DEFAULT FALSE,
                payment_date TIMESTAMP NULL,
                PRIMARY KEY (fine_id),
                FOREIGN KEY (borrow_id) REFERENCES borrowed_books(borrow_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
        """
    }

    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        for table_name, query in queries.items():
            cursor.execute(query)
        conn.commit()
        print("Tables created successfully!")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating tables: {e}")
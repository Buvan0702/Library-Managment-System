import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
import os
import sys
import subprocess
from PIL import Image, ImageTk

from config import DB_CONFIG, DB_NAME
from utils import verify_database, create_database

# ------------------- Main Application Class -------------------
class LibraryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("800x600")
        
        # Set appearance mode and default color theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        
        # Create the main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        
        # Title and welcome message
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(50, 20))
        
        # Title
        title_label = ctk.CTkLabel(
            title_frame,
            text="Library Management System",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#116636"
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Your Gateway to Knowledge and Discovery",
            font=ctk.CTkFont(size=14),
            text_color="#555555"
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Try to load and display a library image
        try:
            self.setup_image()
        except Exception as e:
            print(f"Could not load image: {e}")
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        buttons_frame.pack(pady=40)
        
        # Login button
        login_button = ctk.CTkButton(
            buttons_frame,
            text="User Login",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#116636",
            hover_color="#0d4f29",
            width=200,
            height=50,
            corner_radius=8,
            command=self.open_login
        )
        login_button.pack(pady=10)
        
        # Signup button
        signup_button = ctk.CTkButton(
            buttons_frame,
            text="New User? Sign Up",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2196f3",
            hover_color="#1976d2",
            width=200,
            height=50,
            corner_radius=8,
            command=self.open_signup
        )
        signup_button.pack(pady=10)
        
        # Admin button
        admin_button = ctk.CTkButton(
            buttons_frame,
            text="Admin Login",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#757575",
            hover_color="#616161",
            width=200,
            height=50,
            corner_radius=8,
            command=self.open_admin
        )
        admin_button.pack(pady=10)
        
        # Footer with information
        footer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        # Add default admin credentials if we just created the database
        if not verify_database():
            create_database()
            admin_info = ctk.CTkLabel(
                footer_frame,
                text="Default Admin Login: admin@library.com / Password: admin123",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#116636"
            )
            admin_info.pack()
    
    def setup_image(self):
        """Try to load and display a library image"""
        # Check for predefined image first
        image_path = "images/library.png"
        
        if not os.path.exists(image_path):
            # No image found - create a placeholder
            image_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            image_frame.pack(pady=20)
            
            placeholder = ctk.CTkLabel(
                image_frame,
                text="📚",
                font=ctk.CTkFont(size=120),
                text_color="#116636"
            )
            placeholder.pack()
        else:
            # Image found - display it
            image_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            image_frame.pack(pady=20)
            
            # Load and resize the image
            pil_image = Image.open(image_path)
            pil_image = pil_image.resize((300, 200))
            img = ImageTk.PhotoImage(pil_image)
            
            # Create image label
            image_label = tk.Label(image_frame, image=img, bg="#F0F0F0")
            image_label.image = img  # Keep a reference to avoid garbage collection
            image_label.pack()
    
    def open_login(self):
        """Open the login page"""
        self.root.destroy()
        from auth import login_window
        login_window()
    
    def open_signup(self):
        """Open the signup page"""
        self.root.destroy()
        from auth import signup_window
        signup_window()
    
    def open_admin(self):
        """Open the admin page"""
        self.root.destroy()
        from auth import admin_window
        admin_window()

# ------------------- Main Execution -------------------
if __name__ == "__main__":
    # Check and create database if needed
    if not verify_database():
        print("Setting up database...")
        if not create_database():
            sys.exit(1)
    
    # Check if required files exist
    required_files = ["auth.py", "config.py", "utils.py"]
    required_folders = ["admin", "student", "librarian", "images"]
    
    missing_files = [file for file in required_files if not os.path.exists(file)]
    missing_folders = [folder for folder in required_folders if not os.path.exists(folder)]
    
    if missing_files or missing_folders:
        messagebox.showwarning(
            "Missing Files or Folders", 
            f"The following required files are missing:\n{', '.join(missing_files)}\n\n"
            f"The following required folders are missing:\n{', '.join(missing_folders)}\n\n"
            "Some features may not work correctly."
        )
    
    # Start the application
    root = ctk.CTk()
    app = LibraryManagementSystem(root)
    root.mainloop()
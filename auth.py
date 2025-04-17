import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import re
import mysql.connector

from config import DB_CONFIG
from utils import connect_db, hash_password, save_user_session

# ------------------- Login Window -------------------
def login_window():
    """Create and run the login window"""
    # Initialize the window
    root = ctk.CTk()
    root.title("Library Management System")
    root.geometry("1000x600")
    root.resizable(False, False)

    # Create main frame with rounded corners
    main_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=15)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Create two columns (left for image, right for login)
    left_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=0)
    left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    right_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=0)
    right_frame.pack(side="right", fill="both", expand=True, padx=40, pady=40)

    # Add login heading to the right frame
    heading_label = ctk.CTkLabel(
        right_frame, 
        text="Library Login", 
        font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
        text_color="#15883e"
    )
    heading_label.pack(pady=(20, 10))

    # Add descriptive text
    desc_text = "Access thousands of books, track borrowed items, and manage\nyour library account effortlessly."
    desc_label = ctk.CTkLabel(
        right_frame,
        text=desc_text,
        font=ctk.CTkFont(family="Arial", size=12),
        text_color="gray"
    )
    desc_label.pack(pady=(0, 30))

    # Email Entry
    email_label = ctk.CTkLabel(
        right_frame,
        text="Email Address",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        text_color="#333333",
        anchor="w"
    )
    email_label.pack(anchor="w", pady=(0, 5))

    email_entry = ctk.CTkEntry(
        right_frame,
        width=350,
        height=40,
        font=ctk.CTkFont(family="Arial", size=13),
        border_width=1,
        corner_radius=5
    )
    email_entry.pack(pady=(0, 20))

    # Password Entry
    password_label = ctk.CTkLabel(
        right_frame,
        text="Password",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        text_color="#333333",
        anchor="w"
    )
    password_label.pack(anchor="w", pady=(0, 5))

    password_entry = ctk.CTkEntry(
        right_frame,
        width=350,
        height=40,
        font=ctk.CTkFont(family="Arial", size=13),
        border_width=1,
        corner_radius=5,
        show="•"
    )
    password_entry.pack(pady=(0, 30))

    # Login Button
    def login_action():
        email = email_entry.get()
        password = password_entry.get()

        if not email or not password:
            messagebox.showwarning("Input Error", "Please enter both email and password.")
            return

        hashed_password = hash_password(password)

        try:
            connection = connect_db()
            if not connection:
                return
                
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT user_id, first_name, last_name, email, role FROM Users WHERE email = %s AND password = %s",
                (email, hashed_password)
            )
            user = cursor.fetchone()

            if user:
                # Save user session
                save_user_session(user)
                
                # Show success message
                messagebox.showinfo("Success", f"Welcome {user['first_name']} {user['last_name']}!")
                
                # Close the login window and open home page
                root.destroy()
                if user['role'] == 'admin':
                    from admin.admin_dashboard import run_admin
                    run_admin()
                else:
                    from student.dashboard import run_dashboard
                    run_dashboard()
            else:
                messagebox.showerror("Login Failed", "Invalid Email or Password.")
        
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    login_button = ctk.CTkButton(
        right_frame,
        text="Login",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        corner_radius=5,
        height=45,
        width=350,
        fg_color="#15883e",
        hover_color="#0d6f2f",
        text_color="white",
        command=login_action
    )
    login_button.pack(pady=(0, 20))

    # Links Frame
    links_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
    links_frame.pack(fill="x", pady=(0, 20))

    # Forgot Password Link
    def forgot_password_action():
        email = email_entry.get()
        if not email:
            messagebox.showwarning("Input Required", "Please enter your email address first.")
            return
            
        messagebox.showinfo("Password Reset", 
                        f"A password reset link would be sent to {email}.\n"
                        "This feature would be implemented in a real system.")

    forgot_link = ctk.CTkButton(
        links_frame,
        text="🔑 Forgot Password?",
        font=ctk.CTkFont(family="Arial", size=12),
        fg_color="transparent",
        hover_color="#f0f0f0",
        text_color="#15883e",
        width=30,
        command=forgot_password_action
    )
    forgot_link.pack(side="left")

    # Spacer
    spacer_label = ctk.CTkLabel(links_frame, text="|", text_color="#15883e")
    spacer_label.pack(side="left", padx=20)

    # Sign Up Link
    def signup_action():
        root.destroy()
        signup_window()

    signup_link = ctk.CTkButton(
        links_frame,
        text="👤 New User? Sign Up Here",
        font=ctk.CTkFont(family="Arial", size=12),
        fg_color="transparent",
        hover_color="#f0f0f0",
        text_color="#15883e",
        width=30,
        command=signup_action
    )
    signup_link.pack(side="left")

    # Try to load the illustration image for the left side
    try:
        # Load and resize the image
        image_path = "images/library.png"  # Path to your image
        pil_image = Image.open(image_path)
        pil_image = pil_image.resize((400, 400))
        img = ImageTk.PhotoImage(pil_image)
        
        # Create image label
        image_label = tk.Label(left_frame, image=img, bg="white")
        image_label.image = img  # Keep a reference to avoid garbage collection
        image_label.pack(pady=50)
    except Exception as e:
        # If image loading fails, display a placeholder text
        print(f"Error loading image: {e}")
        placeholder = ctk.CTkLabel(
            left_frame,
            text="Library\nManagement\nSystem",
            font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
            text_color="#15883e"
        )
        placeholder.pack(expand=True)

    # Bind Enter key to login action
    password_entry.bind("<Return>", lambda event: login_action())

    # Start the application
    root.mainloop()

# ------------------- Sign Up Window -------------------
def signup_window():
    """Create and run the signup window"""
    # Initialize the window
    root = ctk.CTk()
    root.title("Library Management System - Sign Up")
    root.geometry("1200x800")
    root.resizable(False, False)

    # Create main frame with rounded corners
    main_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=15, border_width=2, border_color="#15aa3e")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Create two columns (left for image, right for signup form)
    left_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=0)
    left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    right_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=0)
    right_frame.pack(side="right", fill="both", expand=True, padx=40, pady=40)

    # Add signup heading to the right frame
    heading_label = ctk.CTkLabel(
        right_frame, 
        text="Create an Account", 
        font=ctk.CTkFont(family="Arial", size=30, weight="bold"),
        text_color="#15aa3e"
    )
    heading_label.pack(pady=(20, 10))

    # Add descriptive text
    desc_text = "Sign up to explore books, borrow items, and manage your library account."
    desc_label = ctk.CTkLabel(
        right_frame,
        text=desc_text,
        font=ctk.CTkFont(family="Arial", size=12),
        text_color="gray"
    )
    desc_label.pack(pady=(0, 30))

    # Full Name Entry
    full_name_label = ctk.CTkLabel(
        right_frame,
        text="Full Name",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        text_color="#333333",
        anchor="w"
    )
    full_name_label.pack(anchor="w", pady=(0, 5))

    full_name_entry = ctk.CTkEntry(
        right_frame,
        width=350,
        height=40,
        font=ctk.CTkFont(family="Arial", size=13),
        border_width=1,
        corner_radius=5,
        placeholder_text=" "
    )
    full_name_entry.pack(pady=(0, 15))

    # Email Entry
    email_label = ctk.CTkLabel(
        right_frame,
        text="Email Address",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        text_color="#333333",
        anchor="w"
    )
    email_label.pack(anchor="w", pady=(0, 5))

    email_entry = ctk.CTkEntry(
        right_frame,
        width=350,
        height=40,
        font=ctk.CTkFont(family="Arial", size=13),
        border_width=1,
        corner_radius=5,
        placeholder_text=" "
    )
    email_entry.pack(pady=(0, 15))

    password_label = ctk.CTkLabel(
        right_frame,
        text="Password",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        text_color="#333333",
        anchor="w"
    )
    password_label.pack(anchor="w", pady=(0, 5))

    password_entry = ctk.CTkEntry(
        right_frame,
        width=350,
        height=40,
        font=ctk.CTkFont(family="Arial", size=13),
        border_width=1,
        corner_radius=5,
        placeholder_text=" ",
        show="•"
    )
    password_entry.pack(pady=(0, 15))

    # Confirm Password Entry
    confirm_password_label = ctk.CTkLabel(
        right_frame,
        text="Confirm Password",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        text_color="#333333",
        anchor="w"
    )
    confirm_password_label.pack(anchor="w", pady=(0, 5))

    confirm_password_entry = ctk.CTkEntry(
        right_frame,
        width=350,
        height=40,
        font=ctk.CTkFont(family="Arial", size=13),
        border_width=1,
        corner_radius=5,
        placeholder_text=" ",
        show="•"
    )
    confirm_password_entry.pack(pady=(0, 25))

    # Sign Up Button
    def signup_action():
        full_name = full_name_entry.get().strip()
        email = email_entry.get().strip()
        password = password_entry.get()
        confirm_password = confirm_password_entry.get()

        # Check if any fields are empty
        if not full_name or not email or not password or not confirm_password:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        # Validate email format
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, email):
            messagebox.showwarning("Email Error", "Please enter a valid email address.")
            return

        # Check if passwords match
        if password != confirm_password:
            messagebox.showwarning("Password Error", "Passwords do not match.")
            return

        # Hash the password
        hashed_password = hash_password(password)

        try:
            connection = connect_db()
            if not connection:
                return
                
            cursor = connection.cursor()

            # Check if email already exists
            cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
            existing_user = cursor.fetchone()
            if existing_user:
                messagebox.showwarning("Email Error", "Email already exists. Please use a different email.")
                return

            # Split full name into first and last name (best effort)
            name_parts = full_name.split()
            first_name = name_parts[0] if name_parts else ""
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            # Insert the user data into the database
            cursor.execute(
                "INSERT INTO Users (first_name, last_name, email, password, role) VALUES (%s, %s, %s, %s, %s)",
                (first_name, last_name, email, hashed_password, "member")
            )

            connection.commit()
            messagebox.showinfo("Success", "User registered successfully!")
            
            # After successful registration, redirect to login page
            root.destroy()
            login_window()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    signup_button = ctk.CTkButton(
        right_frame,
        text="Sign Up",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        corner_radius=5,
        height=45,
        width=350,
        fg_color="#15aa3e",
        hover_color="#0d7f2f",
        text_color="white",
        command=signup_action
    )
    signup_button.pack(pady=(5, 15))

    # Already have an account link
    def login_action():
        root.destroy()
        login_window()
        
    login_link = ctk.CTkButton(
        right_frame,
        text="Already have an account? Login here",
        font=ctk.CTkFont(family="Arial", size=12),
        fg_color="transparent",
        hover_color="#f0f0f0",
        text_color="#15aa3e",
        width=30,
        command=login_action
    )
    login_link.pack(pady=(5, 0))

    # Try to load the illustration image for the left side
    try:
        # Load and resize the image
        image_path = "images/library.png"  # Path to your image
        pil_image = Image.open(image_path)
        pil_image = pil_image.resize((600, 600))
        img = ImageTk.PhotoImage(pil_image)
        
        # Create image label
        image_label = tk.Label(left_frame, image=img, bg="white")
        image_label.image = img  # Keep a reference to avoid garbage collection
        image_label.pack(pady=50)
    except Exception as e:
        # If image loading fails, display a placeholder text
        print(f"Error loading image: {e}")
        placeholder = ctk.CTkLabel(
            left_frame,
            text="Library\nManagement\nSystem",
            font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
            text_color="#15aa3e"
        )
        placeholder.pack(expand=True)

    # Start the application
    root.mainloop()

# ------------------- For direct execution -------------------
if __name__ == "__main__":
    login_window()
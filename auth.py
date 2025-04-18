import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import re
import mysql.connector

from config import DB_CONFIG
from utils import connect_db, hash_password, save_user_session, generate_secret, update_password
def admin_window():
    """Create and run the admin login window"""
    # Initialize the window
    root = ctk.CTk()
    root.title("Admin Login")
    root.geometry("800x600")
    root.resizable(False, False)

    # Create main frame with rounded corners
    main_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=15)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Add login heading
    heading_label = ctk.CTkLabel(
        main_frame, 
        text="Admin Login", 
        font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
        text_color="#15883e"
    )
    heading_label.pack(pady=(100, 10))

    # Add descriptive text
    desc_label = ctk.CTkLabel(
        main_frame,
        text="Enter your administrator credentials to access the system",
        font=ctk.CTkFont(family="Arial", size=12),
        text_color="gray"
    )
    desc_label.pack(pady=(0, 30))

    # Email Entry
    email_label = ctk.CTkLabel(
        main_frame,
        text="Email Address",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        text_color="#333333",
        anchor="w"
    )
    email_label.pack(anchor="w", padx=200, pady=(0, 5))

    email_entry = ctk.CTkEntry(
        main_frame,
        width=400,
        height=40,
        font=ctk.CTkFont(family="Arial", size=13),
        border_width=1,
        corner_radius=5,
        placeholder_text="Enter admin email"
    )
    email_entry.pack(pady=(0, 20))

    # Password Entry Label
    password_label = ctk.CTkLabel(
        main_frame,
        text="Password",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        text_color="#333333",
        anchor="w"
    )
    password_label.pack(anchor="w", padx=200, pady=(0, 5))

    # Container frame to hold password entry and visibility button
    password_container = ctk.CTkFrame(main_frame, fg_color="transparent", width=400, height=40)
    password_container.pack(pady=(0, 10))
    password_container.pack_propagate(False)

    # Password entry field
    password_entry = ctk.CTkEntry(
        password_container,
        font=ctk.CTkFont(family="Arial", size=13),
        border_width=1,
        corner_radius=5,
        show="•",
        placeholder_text="Enter admin password",
        width=350,
        height=40
    )
    password_entry.place(x=0, y=0)

    # Password visibility toggle
    def toggle_password_visibility():
        if password_entry.cget("show") == "•":
            password_entry.configure(show="")
            visibility_button.configure(text="👁️")
        else:
            password_entry.configure(show="•")
            visibility_button.configure(text="👁️‍🗨️")

    visibility_button = ctk.CTkButton(
        password_container,
        text="👁️‍🗨️",
        font=ctk.CTkFont(size=14),
        width=35,
        height=40,
        fg_color="#f0f0f0",
        text_color="#333333",
        hover_color="#e0e0e0",
        corner_radius=5,
        command=toggle_password_visibility
    )
    visibility_button.place(x=360, y=0)

    # Error message label
    error_label = ctk.CTkLabel(
        main_frame,
        text="",
        font=ctk.CTkFont(size=12),
        text_color="#d32f2f"
    )
    error_label.pack(pady=(10, 10))

    # Admin Login Action
    def admin_login_action():
        email = email_entry.get().strip()
        password = password_entry.get()

        if not email or not password:
            error_label.configure(text="Please enter both email and password.")
            return

        # Hash the password
        hashed_password = hash_password(password)

        try:
            connection = connect_db()
            if not connection:
                error_label.configure(text="Database connection failed.")
                return
                
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT user_id, first_name, last_name, email, role FROM Users WHERE email = %s AND password = %s AND role = 'admin'",
                (email, hashed_password)
            )
            user = cursor.fetchone()

            if user:
                # Save user session
                save_user_session(user)
                
                # Show success message
                messagebox.showinfo("Success", f"Welcome Admin {user['first_name']} {user['last_name']}!")
                
                # Close the login window and open admin dashboard
                root.destroy()
                from admin.admin_dashboard import run_admin
                run_admin()
            else:
                error_label.configure(text="Invalid Admin Credentials.")
        
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    # Login Button
    login_button = ctk.CTkButton(
        main_frame,
        text="Login",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        corner_radius=5,
        height=45,
        width=400,
        fg_color="#15883e",
        hover_color="#0d6f2f",
        text_color="white",
        command=admin_login_action
    )
    login_button.pack(pady=(20, 20))

    # Back to Main Window Button
    def back_to_main():
        root.destroy()
        from main import LibraryManagementSystem
        root = ctk.CTk()
        LibraryManagementSystem(root)
        root.mainloop()

    back_button = ctk.CTkButton(
        main_frame,
        text="Back to Main Menu",
        font=ctk.CTkFont(family="Arial", size=12),
        fg_color="transparent",
        hover_color="#f0f0f0",
        text_color="#15883e",
        corner_radius=5,
        height=30,
        width=400,
        command=back_to_main
    )
    back_button.pack(pady=(0, 20))

    # Bind Enter key to login action
    password_entry.bind("<Return>", lambda event: admin_login_action())

    # Start the application
    root.mainloop()
# ------------------- Password Validation -------------------
def check_password_strength(password):
    """Check password strength and return feedback"""
    # Initialize score and feedback
    score = 0
    feedback = []
    
    # Length check
    if len(password) < 8:
        feedback.append("Password should be at least 8 characters")
    else:
        score += 1
    
    # Uppercase check
    if not re.search(r'[A-Z]', password):
        feedback.append("Include at least one uppercase letter")
    else:
        score += 1
    
    # Lowercase check
    if not re.search(r'[a-z]', password):
        feedback.append("Include at least one lowercase letter")
    else:
        score += 1
    
    # Digit check
    if not re.search(r'\d', password):
        feedback.append("Include at least one number")
    else:
        score += 1
    
    # Special character check
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        feedback.append("Include at least one special character")
    else:
        score += 1
    
    # Determine strength
    if score == 0:
        strength = "Very Weak"
        color = "#FF0000"  # Red
    elif score == 1:
        strength = "Weak"
        color = "#FF4500"  # OrangeRed
    elif score == 2:
        strength = "Moderate"
        color = "#FFA500"  # Orange
    elif score == 3:
        strength = "Good"
        color = "#FFFF00"  # Yellow
    elif score == 4:
        strength = "Strong"
        color = "#9ACD32"  # YellowGreen
    else:
        strength = "Very Strong"
        color = "#008000"  # Green
    
    return {
        "score": score,
        "strength": strength,
        "feedback": feedback,
        "color": color
    }

# ------------------- Password Reset Window -------------------
def password_reset_window(parent=None):
    """Create and run the password reset window"""
    # If parent exists, destroy it
    if parent:
        parent.destroy()
        
    # Initialize the window
    reset_window = ctk.CTk()
    reset_window.title("Reset Password")
    reset_window.geometry("800x800")
    reset_window.resizable(False, False)
    
    # Create main frame
    main_frame = ctk.CTkFrame(reset_window, fg_color="white", corner_radius=15)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Add heading
    heading_label = ctk.CTkLabel(
        main_frame, 
        text="Reset Your Password", 
        font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
        text_color="#15883e"
    )
    heading_label.pack(pady=(20, 10))
    
    # Add description
    desc_label = ctk.CTkLabel(
        main_frame,
        text="Enter your email and secret key to reset your password",
        font=ctk.CTkFont(family="Arial", size=12),
        text_color="gray"
    )
    desc_label.pack(pady=(0, 20))
    
    # Email Entry
    email_label = ctk.CTkLabel(
        main_frame,
        text="Email Address",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        text_color="#333333",
        anchor="w"
    )
    email_label.pack(anchor="w", padx=40, pady=(0, 5))
    
    email_entry = ctk.CTkEntry(
        main_frame,
        width=400,
        height=40,
        font=ctk.CTkFont(family="Arial", size=13),
        border_width=1,
        corner_radius=5,
        placeholder_text="Enter your email"
    )
    email_entry.pack(padx=40, pady=(0, 15))
    
    # Secret Key Entry
    secret_label = ctk.CTkLabel(
        main_frame,
        text="Secret Key",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        text_color="#333333",
        anchor="w"
    )
    secret_label.pack(anchor="w", padx=40, pady=(0, 5))
    
    secret_entry = ctk.CTkEntry(
        main_frame,
        width=400,
        height=40,
        font=ctk.CTkFont(family="Arial", size=13),
        border_width=1,
        corner_radius=5,
        placeholder_text="Enter your secret key"
    )
    secret_entry.pack(padx=40, pady=(0, 15))
    
    # New Password Entry
    new_password_label = ctk.CTkLabel(
        main_frame,
        text="New Password",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        text_color="#333333",
        anchor="w"
    )
    new_password_label.pack(anchor="w", padx=40, pady=(0, 5))
    
    # Container for password
    password_container = ctk.CTkFrame(main_frame, fg_color="transparent", width=400, height=40)
    password_container.pack(padx=40, pady=(0, 5))
    password_container.pack_propagate(False)
    
    new_password_entry = ctk.CTkEntry(
        password_container,
        width=355,
        height=40,
        font=ctk.CTkFont(family="Arial", size=13),
        border_width=1,
        corner_radius=5,
        show="•",
        placeholder_text="Enter your new password"
    )
    new_password_entry.place(x=0, y=0)
    
    # Password visibility toggle
    def toggle_password_visibility():
        if new_password_entry.cget("show") == "•":
            new_password_entry.configure(show="")
            visibility_button.configure(text="👁️")
        else:
            new_password_entry.configure(show="•")
            visibility_button.configure(text="👁️‍🗨️")
    
    visibility_button = ctk.CTkButton(
        password_container,
        text="👁️‍🗨️",
        font=ctk.CTkFont(size=14),
        width=35,
        height=40,
        fg_color="#f0f0f0",
        text_color="#333333",
        hover_color="#e0e0e0",
        corner_radius=5,
        command=toggle_password_visibility
    )
    visibility_button.place(x=360, y=0)
    
    # Password strength indicator
    strength_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    strength_frame.pack(padx=40, pady=(0, 5), fill="x")
    
    strength_label = ctk.CTkLabel(
        strength_frame,
        text="Password Strength: ",
        font=ctk.CTkFont(size=12),
        text_color="#666666"
    )
    strength_label.pack(side="left")
    
    strength_value = ctk.CTkLabel(
        strength_frame,
        text="Not Set",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color="#666666"
    )
    strength_value.pack(side="left")
    
    # Password feedback
    feedback_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    feedback_frame.pack(padx=40, pady=(0, 15), fill="x")
    
    feedback_label = ctk.CTkLabel(
        feedback_frame,
        text="",
        font=ctk.CTkFont(size=11),
        text_color="#666666",
        justify="left"
    )
    feedback_label.pack(anchor="w")
    
    # Update password strength indicator as user types
    def update_password_strength(event=None):
        password = new_password_entry.get()
        
        if not password:
            strength_value.configure(text="Not Set", text_color="#666666")
            feedback_label.configure(text="")
            return
        
        strength_info = check_password_strength(password)
        
        # Update strength label
        strength_value.configure(
            text=strength_info["strength"], 
            text_color=strength_info["color"]
        )
        
        # Update feedback
        feedback_text = "\n".join(f"• {item}" for item in strength_info["feedback"])
        feedback_label.configure(text=feedback_text)
    
    # Bind the password entry to the strength checker
    new_password_entry.bind("<KeyRelease>", update_password_strength)
    
    # Error message label
    error_label = ctk.CTkLabel(
        main_frame,
        text="",
        font=ctk.CTkFont(size=12),
        text_color="#d32f2f"
    )
    error_label.pack(padx=40, pady=(0, 10))
    
    # Reset Button
    def reset_action():
        email = email_entry.get().strip()
        secret = secret_entry.get().strip()
        new_password = new_password_entry.get()
        
        # Validate inputs
        if not email or not secret or not new_password:
            error_label.configure(text="All fields are required")
            return
        
        # Check password strength
        strength_info = check_password_strength(new_password)
        if strength_info["score"] < 3:  # Require at least "Good" strength
            error_label.configure(text="Please choose a stronger password")
            return
        
        # Update the password
        success, message = update_password(email, secret, new_password)
        
        if success:
            messagebox.showinfo("Success", message)
            reset_window.destroy()
            login_window()
        else:
            error_label.configure(text=message)
    
    reset_button = ctk.CTkButton(
        main_frame,
        text="Reset Password",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        corner_radius=5,
        height=45,
        width=400,
        fg_color="#15883e",
        hover_color="#0d6f2f",
        text_color="white",
        command=reset_action
    )
    reset_button.pack(padx=40, pady=(10, 15))
    
    # Back to Login Button
    def back_to_login():
        reset_window.destroy()
        login_window()
    
    back_button = ctk.CTkButton(
        main_frame,
        text="Back to Login",
        font=ctk.CTkFont(family="Arial", size=12),
        fg_color="transparent",
        hover_color="#f0f0f0",
        text_color="#15883e",
        corner_radius=5,
        height=30,
        width=400,
        command=back_to_login
    )
    back_button.pack(padx=40, pady=(0, 20))
    
    # Start the application
    reset_window.mainloop()

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
        corner_radius=5,
        placeholder_text="Enter your email"
    )
    email_entry.pack(pady=(0, 20))

    # Password Entry Label
    password_label = ctk.CTkLabel(
        right_frame,
        text="Password",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        text_color="#333333",
        anchor="w"
    )
    password_label.pack(anchor="w", pady=(0, 5))

    # Container frame to hold password entry and visibility button side by side
    password_container = ctk.CTkFrame(right_frame, fg_color="transparent", width=350, height=40)
    password_container.pack(pady=(0, 10))
    # Make sure the frame doesn't resize to fit its children
    password_container.pack_propagate(False)

    # Password entry field
    password_entry = ctk.CTkEntry(
        password_container,
        font=ctk.CTkFont(family="Arial", size=13),
        border_width=1,
        corner_radius=5,
        show="•",
        placeholder_text="Enter your password",
        width=300,
        height=40
    )
    password_entry.place(x=0, y=0)

    # Password visibility toggle
    def toggle_password_visibility():
        if password_entry.cget("show") == "•":
            password_entry.configure(show="")
            visibility_button.configure(text="👁️")
        else:
            password_entry.configure(show="•")
            visibility_button.configure(text="👁️‍🗨️")

    visibility_button = ctk.CTkButton(
        password_container,
        text="👁️‍🗨️",
        font=ctk.CTkFont(size=14),
        width=35,
        height=40,
        fg_color="#f0f0f0",
        text_color="#333333",
        hover_color="#e0e0e0",
        corner_radius=5,
        command=toggle_password_visibility
    )
    visibility_button.place(x=310, y=0)

    # Error message label
    error_label = ctk.CTkLabel(
        right_frame,
        text="",
        font=ctk.CTkFont(size=12),
        text_color="#d32f2f"
    )
    error_label.pack(pady=(0, 5))

    # Login Button
    def login_action():
        email = email_entry.get()
        password = password_entry.get()

        if not email or not password:
            error_label.configure(text="Please enter both email and password.")
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
                error_label.configure(text="Invalid Email or Password.")
        
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
    login_button.pack(pady=(10, 20))

    # Links Frame
    links_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
    links_frame.pack(fill="x", pady=(0, 20))

    # Forgot Password Link
    def forgot_password_action():
        root.destroy()
        password_reset_window()

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
        print("Sign up button clicked")
        try:
            root.destroy()
            print("Login window destroyed")
            signup_window()
            print("Signup window opened")
        except Exception as e:
            print(f"Error opening signup window: {e}")

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
    # If a parent is needed, pass in the root window that called this function
    # Initialize the window
    root = ctk.CTk()
    root.title("Library Management System - Sign Up")
    root.geometry("1200x1000")
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
        placeholder_text="Enter your full name"
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
        placeholder_text="Enter your email address"
    )
    email_entry.pack(pady=(0, 15))

    # Password Label
    password_label = ctk.CTkLabel(
        right_frame,
        text="Password",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        text_color="#333333",
        anchor="w"
    )
    password_label.pack(anchor="w", pady=(0, 5))

    # Container frame for password entry and visibility button
    password_container = ctk.CTkFrame(right_frame, fg_color="transparent", width=350, height=40)
    password_container.pack(pady=(0, 5))
    password_container.pack_propagate(False)  # Fix the size
    
    # Password entry
    password_entry = ctk.CTkEntry(
        password_container,
        font=ctk.CTkFont(family="Arial", size=13),
        border_width=1,
        corner_radius=5,
        placeholder_text="Enter your password",
        show="•",
        width=305,
        height=40
    )
    password_entry.place(x=0, y=0)

    # Password visibility toggle
    def toggle_password_visibility():
        if password_entry.cget("show") == "•":
            password_entry.configure(show="")
            visibility_button.configure(text="👁️")
        else:
            password_entry.configure(show="•")
            visibility_button.configure(text="👁️‍🗨️")

    visibility_button = ctk.CTkButton(
        password_container,
        text="👁️‍🗨️",
        font=ctk.CTkFont(size=14),
        width=35,
        height=40,
        fg_color="#f0f0f0",
        text_color="#333333",
        hover_color="#e0e0e0",
        corner_radius=5,
        command=toggle_password_visibility
    )
    visibility_button.place(x=310, y=0)

    # Password strength indicator
    strength_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
    strength_frame.pack(pady=(0, 5), fill="x")

    strength_label = ctk.CTkLabel(
        strength_frame,
        text="Password Strength: ",
        font=ctk.CTkFont(size=12),
        text_color="#666666"
    )
    strength_label.pack(side="left")

    strength_value = ctk.CTkLabel(
        strength_frame,
        text="Not Set",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color="#666666"
    )
    strength_value.pack(side="left")

    # Password strength feedback
    feedback_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
    feedback_frame.pack(pady=(0, 15), fill="x")

    feedback_label = ctk.CTkLabel(
        feedback_frame,
        text="",
        font=ctk.CTkFont(size=11),
        text_color="#666666",
        justify="left"
    )
    feedback_label.pack(anchor="w")

    # Update password strength indicator as user types
    def update_password_strength(event=None):
        password = password_entry.get()
        
        if not password:
            strength_value.configure(text="Not Set", text_color="#666666")
            feedback_label.configure(text="")
            return
        
        strength_info = check_password_strength(password)
        
        # Update strength label
        strength_value.configure(
            text=strength_info["strength"], 
            text_color=strength_info["color"]
        )
        
        # Update feedback
        feedback_text = "\n".join(f"• {item}" for item in strength_info["feedback"])
        feedback_label.configure(text=feedback_text)

    # Bind the password entry to the strength checker
    password_entry.bind("<KeyRelease>", update_password_strength)

    # Confirm Password Label
    confirm_password_label = ctk.CTkLabel(
        right_frame,
        text="Confirm Password",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        text_color="#333333",
        anchor="w"
    )
    confirm_password_label.pack(anchor="w", pady=(0, 5))

    # Container for confirm password
    confirm_container = ctk.CTkFrame(right_frame, fg_color="transparent", width=350, height=40)
    confirm_container.pack(pady=(0, 15))
    confirm_container.pack_propagate(False)  # Fix the size

    # Confirm password entry
    confirm_password_entry = ctk.CTkEntry(
        confirm_container,
        font=ctk.CTkFont(family="Arial", size=13),
        border_width=1,
        corner_radius=5,
        placeholder_text="Confirm your password",
        show="•",
        width=305,
        height=40
    )
    confirm_password_entry.place(x=0, y=0)

    # Confirm Password visibility toggle
    def toggle_confirm_visibility():
        if confirm_password_entry.cget("show") == "•":
            confirm_password_entry.configure(show="")
            confirm_visibility_button.configure(text="👁️")
        else:
            confirm_password_entry.configure(show="•")
            confirm_visibility_button.configure(text="👁️‍🗨️")

    confirm_visibility_button = ctk.CTkButton(
        confirm_container,
        text="👁️‍🗨️",
        font=ctk.CTkFont(size=14),
        width=35,
        height=40,
        fg_color="#f0f0f0",
        text_color="#333333",
        hover_color="#e0e0e0",
        corner_radius=5,
        command=toggle_confirm_visibility
    )
    confirm_visibility_button.place(x=310, y=0)

    # Secret Key Label
    secret_key_label = ctk.CTkLabel(
        right_frame,
        text="Secret Key",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        text_color="#333333",
        anchor="w"
    )
    secret_key_label.pack(anchor="w", pady=(0, 5))

    # Secret Key Entry
    secret_key_entry = ctk.CTkEntry(
        right_frame,
        width=350,
        height=40,
        font=ctk.CTkFont(family="Arial", size=13),
        border_width=1,
        corner_radius=5,
        placeholder_text="Enter your secret key"
    )
    secret_key_entry.pack(pady=(0, 15))

    # Error message label
    error_label = ctk.CTkLabel(
        right_frame,
        text="",
        font=ctk.CTkFont(size=12),
        text_color="#d32f2f"
    )
    error_label.pack(pady=(0, 10))

    # Sign Up Button
    def signup_action():
        full_name = full_name_entry.get().strip()
        email = email_entry.get().strip()
        password = password_entry.get()
        confirm_password = confirm_password_entry.get()
        secret_key = secret_key_entry.get().strip()

        # Check if any fields are empty
        if not full_name or not email or not password or not confirm_password or not secret_key:
            error_label.configure(text="All fields are required.")
            return

        # Validate email format
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]'
        if not re.match(pattern, email):
            error_label.configure(text="Please enter a valid email address.")
            return

        # Check if passwords match
        if password != confirm_password:
            error_label.configure(text="Passwords do not match.")
            return

        # Check password strength
        strength_info = check_password_strength(password)
        if strength_info["score"] < 3:  # Require at least "Good" strength
            error_label.configure(text="Please choose a stronger password.")
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
                error_label.configure(text="Email already exists. Please use a different email.")
                return

            # Split full name into first and last name (best effort)
            name_parts = full_name.split()
            first_name = name_parts[0] if name_parts else ""
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            # Insert the user data into the database including the secret key
            cursor.execute(
                "INSERT INTO Users (first_name, last_name, email, password, secret, role) VALUES (%s, %s, %s, %s, %s, %s)",
                (first_name, last_name, email, hashed_password, secret_key, "member")
            )

            connection.commit()
            
            # Show account creation success message
            secret_message = (f"Your account has been created successfully!\n\n"
                             f"IMPORTANT: Your secret key has been saved.\n\n"
                             f"Keep this key safe. You will need it if you ever forget your password.")
            messagebox.showinfo("Account Created", secret_message)
            
            # After successful registration, redirect to login page
            root.destroy()
            login_window()

        except mysql.connector.Error as err:
            error_label.configure(text=f"Database Error: {str(err)}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    # Sign Up Button
    signup_button = ctk.CTkButton(
        right_frame,
        text="Sign Up",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        corner_radius=5,
        height=45,
        width=350,
        fg_color="#15883e",
        hover_color="#0d6f2f",
        text_color="white",
        command=signup_action
    )
    signup_button.pack(pady=(10, 20))

    # Back to Login Link
    def back_to_login():
        root.destroy()
        login_window()

    back_link = ctk.CTkButton(
        right_frame,
        text="Already have an account? Back to Login",
        font=ctk.CTkFont(family="Arial", size=12),
        fg_color="transparent",
        hover_color="#f0f0f0",
        text_color="#15883e",
        width=350,
        command=back_to_login
    )
    back_link.pack(pady=(0, 20))

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

    # Start the application
    root.mainloop()
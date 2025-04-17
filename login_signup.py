import customtkinter as ctk
import mysql.connector
import bcrypt
import re
import os
from PIL import Image, ImageTk
from utils import connect_to_database, center_window
from CTkMessagebox import CTkMessagebox

# Function to validate user credentials
def validate_user(email, password):
    try:
        conn = connect_to_database()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return user
        return None
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return None

# Function to add a new user
def add_user(first_name, last_name, email, password, user_type):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False, "Email already exists."

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        query = """
        INSERT INTO users (first_name, last_name, email, password, user_type, status)
        VALUES (%s, %s, %s, %s, %s, 'active')
        """
        cursor.execute(query, (first_name, last_name, email, hashed_password, user_type))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "User created successfully."
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return False, f"Database error: {err}"

# Function to reset a user's password
def reset_password_logic(email, new_password):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        # Check if email exists
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        if not user:
            return False, "Email not found."

        # Update password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        update_query = "UPDATE users SET password = %s WHERE email = %s"
        cursor.execute(update_query, (hashed_password, email))
        conn.commit()

        cursor.close()
        conn.close()
        return True, "Password reset successfully."
    except mysql.connector.Error as err:
        return False, f"Database error: {err}"

# Function to check password strength
def is_password_strong(password):
    if len(password) >= 8 and re.search(r"[A-Z]", password) and re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return True
    return False

class LoginWindow(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.is_signup_mode = False

        # Background color
        self.configure(fg_color="#f0f0f0")

        # Form Frame
        self.form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15, width=430, height=580)
        self.form_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.form_frame.grid_propagate(False)
        self.form_frame.pack_propagate(False)

        # Initialize Login View
        self.create_login_view()

    def clear_form_frame(self):
        """Clear all widgets in the form frame."""
        for widget in self.form_frame.winfo_children():
            widget.destroy()

    def create_login_view(self):
        """Create Login View."""
        self.clear_form_frame()
        self.is_signup_mode = False

        # Create an inner frame to hold the form content
        self.inner_frame = ctk.CTkFrame(self.form_frame, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title
        self.title_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Library Login", 
            font=("Arial", 24, "bold"), 
            text_color="#25a249"  # Green color for library theme
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 20))

        # User Type Selection
        self.user_type_label = ctk.CTkLabel(
            self.inner_frame, 
            text="User Type:", 
            font=("Arial", 14), 
            text_color="#555"
        )
        self.user_type_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.user_type_var = ctk.StringVar(value="student")
        self.user_type_menu = ctk.CTkOptionMenu(
            self.inner_frame, 
            values=["student", "lecturer", "admin"], 
            variable=self.user_type_var, 
            width=200,
            fg_color="#25a249",
            button_color="#1e8138"
        )
        self.user_type_menu.grid(row=1, column=1, padx=10, pady=5, sticky="e")

        # Email
        self.email_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Email:", 
            font=("Arial", 14), 
            text_color="#555"
        )
        self.email_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.email_entry = ctk.CTkEntry(
            self.inner_frame, 
            placeholder_text="Enter Email", 
            width=220, 
            height=40
        )
        self.email_entry.grid(row=2, column=1, padx=10, pady=5, sticky="e")
        
        self.email_error_label = ctk.CTkLabel(
            self.inner_frame, 
            text="", 
            font=("Arial", 12), 
            text_color="red", 
            width=200
        )
        self.email_error_label.grid(row=3, column=1, padx=10, pady=0, sticky="w")

        # Password
        self.password_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Password:", 
            font=("Arial", 14), 
            text_color="#555"
        )
        self.password_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        
        self.password_entry = ctk.CTkEntry(
            self.inner_frame, 
            placeholder_text="Enter Password", 
            show="*", 
            width=220, 
            height=40
        )
        self.password_entry.grid(row=4, column=1, padx=10, pady=5, sticky="e")
        
        self.password_error_label = ctk.CTkLabel(
            self.inner_frame, 
            text="", 
            font=("Arial", 12), 
            text_color="red", 
            width=200
        )
        self.password_error_label.grid(row=5, column=1, sticky="w")

        # Show Password Checkbox
        self.show_password_var = ctk.BooleanVar(value=False)
        self.show_password_checkbox = ctk.CTkCheckBox(
            self.inner_frame, 
            text="Show Password", 
            variable=self.show_password_var, 
            command=self.toggle_password,
            fg_color="#25a249"
        )
        self.show_password_checkbox.grid(row=6, column=0, padx=(10, 5), pady=10, sticky="w")

        # Forgot Password Link
        self.forgot_password_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Forgot Password?", 
            font=("Arial", 12, "underline"), 
            text_color="#25a249",  # Green color for link
            cursor="hand2"
        )
        self.forgot_password_label.grid(row=6, column=1, padx=(5, 10), pady=10, sticky="e")
        self.forgot_password_label.bind("<Button-1>", lambda e: self.create_forgot_password_view())

        # Login Button
        self.login_button = ctk.CTkButton(
            self.inner_frame, 
            text="Login", 
            command=self.login, 
            width=150, 
            height=40,
            fg_color="#25a249",
            hover_color="#1e8138"
        )
        self.login_button.grid(row=7, column=0, columnspan=2, pady=10)

        # Switch to Sign-Up Button
        self.switch_to_signup_button = ctk.CTkButton(
            self.inner_frame, 
            text="Create an Account", 
            command=self.create_signup_view, 
            width=150, 
            height=40,
            fg_color="#555",
            hover_color="#333"
        )
        self.switch_to_signup_button.grid(row=8, column=0, columnspan=2, pady=(10, 20))

    def create_signup_view(self):
        """Create Sign-Up View."""
        self.clear_form_frame()
        self.is_signup_mode = True

        # Create an inner frame to hold the form content
        self.inner_frame = ctk.CTkFrame(self.form_frame, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=40, pady=10)

        # Title
        self.title_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Create a New Account", 
            font=("Arial", 24, "bold"), 
            text_color="#25a249"
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 20))

        # First Name
        self.first_name_label = ctk.CTkLabel(
            self.inner_frame, 
            text="First Name:", 
            font=("Arial", 14), 
            text_color="#555"
        )
        self.first_name_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.first_name_entry = ctk.CTkEntry(
            self.inner_frame, 
            placeholder_text="Enter First Name", 
            width=220, 
            height=40
        )
        self.first_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="e")
        
        self.first_name_error_label = ctk.CTkLabel(
            self.inner_frame, 
            text="", 
            font=("Arial", 12), 
            text_color="red"
        )
        self.first_name_error_label.grid(row=2, column=1, padx=10, sticky="w")

        # Last Name
        self.last_name_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Last Name:", 
            font=("Arial", 14), 
            text_color="#555"
        )
        self.last_name_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        self.last_name_entry = ctk.CTkEntry(
            self.inner_frame, 
            placeholder_text="Enter Last Name", 
            width=220, 
            height=40
        )
        self.last_name_entry.grid(row=3, column=1, padx=10, pady=5, sticky="e")
        
        self.last_name_error_label = ctk.CTkLabel(
            self.inner_frame, 
            text="", 
            font=("Arial", 12), 
            text_color="red"
        )
        self.last_name_error_label.grid(row=4, column=1, padx=10, sticky="w")

        # Email
        self.email_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Email:", 
            font=("Arial", 14), 
            text_color="#555"
        )
        self.email_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        
        self.email_entry = ctk.CTkEntry(
            self.inner_frame, 
            placeholder_text="Enter Email", 
            width=220, 
            height=40
        )
        self.email_entry.grid(row=5, column=1, padx=10, pady=5, sticky="e")
        
        self.email_error_label = ctk.CTkLabel(
            self.inner_frame, 
            text="", 
            font=("Arial", 12), 
            text_color="red"
        )
        self.email_error_label.grid(row=6, column=1, padx=10, sticky="w")

        # Password
        self.password_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Password:", 
            font=("Arial", 14), 
            text_color="#555"
        )
        self.password_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")
        
        self.password_entry = ctk.CTkEntry(
            self.inner_frame, 
            placeholder_text="Enter Password", 
            show="*", 
            width=220, 
            height=40
        )
        self.password_entry.grid(row=7, column=1, padx=10, pady=5, sticky="e")
        
        self.password_error_label = ctk.CTkLabel(
            self.inner_frame, 
            text="", 
            font=("Arial", 12), 
            text_color="red"
        )
        self.password_error_label.grid(row=8, column=1, padx=10, sticky="w")

        # User Type (Limited to student for sign-up)
        self.user_type_label = ctk.CTkLabel(
            self.inner_frame, 
            text="User Type:", 
            font=("Arial", 14), 
            text_color="#555"
        )
        self.user_type_label.grid(row=9, column=0, padx=10, pady=5, sticky="w")
        
        self.user_type_var = ctk.StringVar(value="student")
        self.user_type_entry = ctk.CTkOptionMenu(
            self.inner_frame, 
            values=["student"], 
            variable=self.user_type_var, 
            width=200,
            fg_color="#25a249",
            button_color="#1e8138"
        )
        self.user_type_entry.grid(row=9, column=1, padx=10, pady=5, sticky="e")

        # Sign-Up Button
        self.signup_button = ctk.CTkButton(
            self.inner_frame, 
            text="Sign Up", 
            command=self.signup, 
            width=150, 
            height=40,
            fg_color="#25a249",
            hover_color="#1e8138"
        )
        self.signup_button.grid(row=10, column=0, columnspan=2, pady=10)

        # Back to Login Button
        self.switch_to_login_button = ctk.CTkButton(
            self.inner_frame, 
            text="Back to Login", 
            command=self.create_login_view, 
            width=150, 
            height=40,
            fg_color="#555",
            hover_color="#333"
        )
        self.switch_to_login_button.grid(row=11, column=0, columnspan=2, pady=(10, 20))

    def create_forgot_password_view(self):
        """Create Forgot Password View."""
        self.clear_form_frame()

        # Create an inner frame to organize the content
        self.inner_frame = ctk.CTkFrame(self.form_frame, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=30, pady=10)

        # Title
        self.title_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Reset Your Password", 
            font=("Arial", 24, "bold"), 
            text_color="#25a249"
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 20))

        # Email
        self.email_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Email:", 
            font=("Arial", 14), 
            text_color="#555"
        )
        self.email_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.email_entry = ctk.CTkEntry(
            self.inner_frame, 
            placeholder_text="Enter your registered email", 
            width=220, 
            height=40
        )
        self.email_entry.grid(row=1, column=1, padx=10, pady=5, sticky="e")
        
        self.email_error_label = ctk.CTkLabel(
            self.inner_frame, 
            text="", 
            font=("Arial", 12), 
            text_color="red"
        )
        self.email_error_label.grid(row=2, column=1, sticky="w", padx=10)

        # New Password
        self.new_password_label = ctk.CTkLabel(
            self.inner_frame, 
            text="New Password:", 
            font=("Arial", 14), 
            text_color="#555"
        )
        self.new_password_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        self.new_password_entry = ctk.CTkEntry(
            self.inner_frame, 
            placeholder_text="Enter new password", 
            show="*", 
            width=220, 
            height=40
        )
        self.new_password_entry.grid(row=3, column=1, padx=10, pady=5, sticky="e")
        
        self.new_password_error_label = ctk.CTkLabel(
            self.inner_frame, 
            text="", 
            font=("Arial", 12), 
            text_color="red"
        )
        self.new_password_error_label.grid(row=4, column=1, sticky="w", padx=10)

        # Confirm Password
        self.confirm_password_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Confirm Password:", 
            font=("Arial", 14), 
            text_color="#555"
        )
        self.confirm_password_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        
        self.confirm_password_entry = ctk.CTkEntry(
            self.inner_frame, 
            placeholder_text="Re-enter new password", 
            show="*", 
            width=220, 
            height=40
        )
        self.confirm_password_entry.grid(row=5, column=1, padx=10, pady=5, sticky="e")
        
        self.confirm_password_error_label = ctk.CTkLabel(
            self.inner_frame, 
            text="", 
            font=("Arial", 12), 
            text_color="red"
        )
        self.confirm_password_error_label.grid(row=6, column=1, sticky="w", padx=10)

        # Reset Password Button
        self.reset_password_button = ctk.CTkButton(
            self.inner_frame, 
            text="Reset Password", 
            command=self.reset_password, 
            width=150, 
            height=40,
            fg_color="#25a249",
            hover_color="#1e8138"
        )
        self.reset_password_button.grid(row=7, column=0, columnspan=2, pady=10)

        # Back to Login Button
        self.back_to_login_button = ctk.CTkButton(
            self.inner_frame, 
            text="Back to Login", 
            command=self.create_login_view, 
            width=150, 
            height=40,
            fg_color="#555",
            hover_color="#333"
        )
        self.back_to_login_button.grid(row=8, column=0, columnspan=2, pady=(10, 20))

    def reset_password(self):
        """Handle Password Reset."""
        email = self.email_entry.get().strip()
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        # Reset error labels
        self.email_error_label.configure(text="")
        self.new_password_error_label.configure(text="")
        self.confirm_password_error_label.configure(text="")

        valid = True  # Validation flag

        # Validate email
        if not email or "@" not in email or "." not in email:
            self.email_error_label.configure(text="Enter a valid email address.")
            valid = False

        # Validate new password
        if not new_password or not is_password_strong(new_password):
            self.new_password_error_label.configure(
                text="Password must be at least 8 characters with uppercase and special character."
            )
            valid = False

        # Validate password match
        if new_password != confirm_password:
            self.confirm_password_error_label.configure(text="Passwords do not match.")
            valid = False

        if valid:
            success, message = reset_password_logic(email, new_password)
            if success:
                CTkMessagebox(title="Password Reset", message="Your password has been reset successfully.", icon="info")
                self.create_login_view()  # Redirect to login view on success
            else:
                self.email_error_label.configure(text=message)

    def toggle_password(self):
        """Toggle password visibility."""
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")

    def signup(self):
        """Handle Sign-Up Process."""
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        user_type = self.user_type_var.get()

        # Reset error messages
        self.first_name_error_label.configure(text="")
        self.last_name_error_label.configure(text="")
        self.email_error_label.configure(text="")
        self.password_error_label.configure(text="")

        valid = True  # Validation flag

        # Validate fields
        if not first_name:
            self.first_name_error_label.configure(text="First Name is required.")
            valid = False
        if not last_name:
            self.last_name_error_label.configure(text="Last Name is required.")
            valid = False
        if not email or "@" not in email or "." not in email:
            self.email_error_label.configure(text="Invalid email address.")
            valid = False
        if not is_password_strong(password):
            self.password_error_label.configure(
                text="Password must be at least 8 characters with uppercase and special character."
            )
            valid = False

        if valid:
            # If all fields are valid, attempt to create the user
            success, message = add_user(first_name, last_name, email, password, user_type)
            if success:
                CTkMessagebox(title="Account Created", message="Your account has been created successfully. You can now log in.", icon="info")
                self.create_login_view()  # Redirect to login view on success
            else:
                if "Email already exists" in message:
                    self.email_error_label.configure(text="Email already exists.")
                else:
                    CTkMessagebox(title="Error", message=f"An error occurred: {message}", icon="error")

    def login(self):
        """Handle Login."""
        email = self.email_entry.get()
        password = self.password_entry.get()
        user_type = self.user_type_var.get()

        # Reset error labels
        self.email_error_label.configure(text="")
        self.password_error_label.configure(text="")

        if not email:
            self.email_error_label.configure(text="Email is required.")
            return
        elif "@" not in email or "." not in email:
            self.email_error_label.configure(text="Invalid email address.")
            return 

        if not password:
            self.password_error_label.configure(text="Password is required.")
            return

        user = validate_user(email, password)
        if user and user["user_type"] == user_type:
            self.navigate_to_dashboard(user["user_type"], user["user_id"])
        else:
            self.password_error_label.configure(text="Invalid credentials or user type.")

    def navigate_to_dashboard(self, role, user_id):
        """Navigate to Dashboard based on the user's role."""
        self.master.destroy()  # Close the current login window
        
        # Navigate to the appropriate dashboard
        if role == "student":
            from student.student_view import StudentDashboard
            dashboard = StudentDashboard(user_id=user_id)
        elif role == "lecturer":
            from lecturer.lecturer_view import LecturerDashboard
            dashboard = LecturerDashboard(user_id=user_id)
        elif role == "admin":
            from admin.admin_view import AdminDashboard
            dashboard = AdminDashboard(user_id=user_id)
        else:
            raise ValueError(f"Unknown role: {role}")

        # Start the dashboard's main loop
        dashboard.mainloop()


# Main Application
if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("900x600")
    center_window(app, 900, 600)
    login_window = LoginWindow(app)
    login_window.pack(expand=True, fill="both")
    app.mainloop()
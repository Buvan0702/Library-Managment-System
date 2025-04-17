import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import hashlib

from utils import connect_db, load_user_session, save_user_session, clear_user_session

# ------------------- Profile Functions -------------------
def get_user_profile(user_id):
    """Get user profile information"""
    connection = connect_db()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                user_id, 
                first_name, 
                last_name, 
                email, 
                role,
                DATE_FORMAT(registration_date, '%Y-%m-%d') AS registration_date
            FROM 
                Users 
            WHERE 
                user_id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        print(f"User profile loaded for user {user_id}")
        return result
    except Exception as err:
        print(f"Error getting user profile: {err}")
        messagebox.showerror("Database Error", str(err))
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_user_profile(user_id, first_name, last_name, email, current_password=None, new_password=None):
    """Update user profile information"""
    connection = connect_db()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # If changing password, verify current password
        if current_password and new_password:
            # Hash the provided current password
            hashed_current = hashlib.sha256(current_password.encode()).hexdigest()
            
            # Check if the current password matches
            cursor.execute("SELECT password FROM Users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                print(f"No user found with ID {user_id}")
                return False
            
            stored_hash = result[0]
            
            if stored_hash != hashed_current:
                messagebox.showerror("Password Error", "Current password is incorrect.")
                return False
            
            # Hash the new password
            hashed_new = hashlib.sha256(new_password.encode()).hexdigest()
            
            # Update user with new password
            cursor.execute(
                "UPDATE Users SET first_name = %s, last_name = %s, email = %s, password = %s WHERE user_id = %s", 
                (first_name, last_name, email, hashed_new, user_id)
            )
        else:
            # Update user without changing password
            cursor.execute(
                "UPDATE Users SET first_name = %s, last_name = %s, email = %s WHERE user_id = %s", 
                (first_name, last_name, email, user_id)
            )
        
        connection.commit()
        return True
    except Exception as err:
        print(f"Error updating profile: {err}")
        messagebox.showerror("Database Error", str(err))
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# ------------------- UI Class -------------------
class ProfileApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System - User Profile")
        self.root.geometry("1100x700")
        
        # Set appearance mode and default color theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        
        # Load user session
        self.user = load_user_session()
        if not self.user:
            messagebox.showerror("Session Error", "No active user session found.")
            self.logout()
            return
        
        # Initialize UI
        self.setup_ui()
        
        # Load profile data
        self.load_profile()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Create main grid layout
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#f0f5f0", corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
    
    def create_sidebar(self):
        """Create the sidebar with navigation buttons"""
        sidebar = ctk.CTkFrame(self.root, width=210, fg_color="#116636", corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)  # Prevent the frame from shrinking

        # Sidebar Title
        title_label = ctk.CTkLabel(sidebar, text="📑 Library System", font=ctk.CTkFont(size=16, weight="bold"), 
                                  text_color="white", anchor="w", padx=10, pady=10)
        title_label.pack(fill="x", pady=(20, 10))
        
        # User welcome message
        user_welcome = ctk.CTkLabel(sidebar, 
                                 text=f"Welcome,\n{self.user['first_name']} {self.user['last_name']}", 
                                 font=ctk.CTkFont(size=12, weight="bold"), 
                                 text_color="white", anchor="w", padx=10, pady=10)
        user_welcome.pack(fill="x", pady=(0, 20))
        
        # Separator
        separator = ctk.CTkFrame(sidebar, height=1, fg_color="white")
        separator.pack(fill="x", padx=10, pady=10)

        # Sidebar Buttons with commands
        menu_items = [
            ("🏠 Dashboard", self.open_dashboard),
            ("🔍 Search Books", self.open_search),
            ("📖 My Borrowed Books", self.open_borrowed),
            ("💰 Fines & Fees", self.open_fines),
            ("👤 My Profile", None),  # Current page
            ("🚪 Logout", self.logout)
        ]

        for text, command in menu_items:
            if command:  # Regular button
                button = ctk.CTkButton(sidebar, text=text, font=ctk.CTkFont(size=12), 
                                     fg_color="transparent", text_color="white", anchor="w",
                                     hover_color="#0d4f29", corner_radius=0, height=40,
                                     command=command)
            else:  # Current page (highlight)
                button = ctk.CTkButton(sidebar, text=text, font=ctk.CTkFont(size=12), 
                                     fg_color="#0d4f29", text_color="white", anchor="w",
                                     hover_color="#0d4f29", corner_radius=0, height=40)
            button.pack(fill="x", pady=2)
    
    def load_profile(self):
        """Load and display user profile data"""
        # Get user profile data
        profile = get_user_profile(self.user['user_id'])
        if not profile:
            messagebox.showerror("Error", "Failed to load profile data.")
            return
        
        # Profile Title
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        title = ctk.CTkLabel(title_frame, text="My Profile", 
                           font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=10)

        # Separator line
        separator_frame = ctk.CTkFrame(self.main_frame, height=1, fg_color="#d1d1d1")
        separator_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        # Profile Frame
        profile_frame = ctk.CTkFrame(self.main_frame, fg_color="white", corner_radius=10)
        profile_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)
        profile_frame.grid_columnconfigure(0, weight=1)
        
        # Header with user role and join date
        header_frame = ctk.CTkFrame(profile_frame, fg_color="#f0f5f0", corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 30), ipady=10)
        
        role_text = f"Account Type: {profile['role'].capitalize()}"
        role_label = ctk.CTkLabel(header_frame, text=role_text, font=ctk.CTkFont(size=14, weight="bold"))
        role_label.pack(side="left", padx=20)
        
        from utils import format_date
        joined_text = f"Member Since: {format_date(profile['registration_date'])}"
        joined_label = ctk.CTkLabel(header_frame, text=joined_text, font=ctk.CTkFont(size=14))
        joined_label.pack(side="right", padx=20)
        
        # Profile form
        form_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        form_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=10)
        form_frame.grid_columnconfigure(1, weight=1)
        
        # First Name
        ctk.CTkLabel(form_frame, text="First Name:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", pady=(10, 5))
        first_name_entry = ctk.CTkEntry(form_frame, width=300, height=35, font=ctk.CTkFont(size=12))
        first_name_entry.grid(row=0, column=1, sticky="w", pady=(10, 5))
        first_name_entry.insert(0, profile['first_name'])
        
        # Last Name
        ctk.CTkLabel(form_frame, text="Last Name:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=1, column=0, sticky="w", pady=5)
        last_name_entry = ctk.CTkEntry(form_frame, width=300, height=35, font=ctk.CTkFont(size=12))
        last_name_entry.grid(row=1, column=1, sticky="w", pady=5)
        last_name_entry.insert(0, profile['last_name'])
        
        # Email
        ctk.CTkLabel(form_frame, text="Email:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=0, sticky="w", pady=5)
        email_entry = ctk.CTkEntry(form_frame, width=300, height=35, font=ctk.CTkFont(size=12))
        email_entry.grid(row=2, column=1, sticky="w", pady=5)
        email_entry.insert(0, profile['email'])
        
        # Separator
        separator = ctk.CTkFrame(profile_frame, height=1, fg_color="#d1d1d1")
        separator.grid(row=2, column=0, sticky="ew", padx=40, pady=20)
        
        # Password change section
        password_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        password_frame.grid(row=3, column=0, sticky="nsew", padx=40, pady=10)
        password_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(password_frame, text="Change Password", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Current Password
        ctk.CTkLabel(password_frame, text="Current Password:", font=ctk.CTkFont(size=14)).grid(row=1, column=0, sticky="w", pady=5)
        current_password_entry = ctk.CTkEntry(password_frame, width=300, height=35, font=ctk.CTkFont(size=12), show="•")
        current_password_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        # New Password
        ctk.CTkLabel(password_frame, text="New Password:", font=ctk.CTkFont(size=14)).grid(row=2, column=0, sticky="w", pady=5)
        new_password_entry = ctk.CTkEntry(password_frame, width=300, height=35, font=ctk.CTkFont(size=12), show="•")
        new_password_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Confirm New Password
        ctk.CTkLabel(password_frame, text="Confirm New Password:", font=ctk.CTkFont(size=14)).grid(row=3, column=0, sticky="w", pady=5)
        confirm_password_entry = ctk.CTkEntry(password_frame, width=300, height=35, font=ctk.CTkFont(size=12), show="•")
        confirm_password_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        # Action buttons
        button_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, sticky="ew", padx=40, pady=(20, 30))
        
        def save_profile():
            # Validate inputs
            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            email = email_entry.get().strip()
            
            if not first_name or not last_name or not email:
                messagebox.showwarning("Input Error", "Name and email fields cannot be empty.")
                return
            
            # Check for password change
            current_password = current_password_entry.get()
            new_password = new_password_entry.get()
            confirm_password = confirm_password_entry.get()
            
            if new_password or confirm_password or current_password:
                # Password change requested
                if not current_password:
                    messagebox.showwarning("Password Error", "Please enter your current password.")
                    return
                
                if not new_password:
                    messagebox.showwarning("Password Error", "Please enter a new password.")
                    return
                
                if new_password != confirm_password:
                    messagebox.showwarning("Password Error", "New passwords do not match.")
                    return
                
                # Update profile with password change
                if update_user_profile(profile['user_id'], first_name, last_name, email, current_password, new_password):
                    messagebox.showinfo("Success", "Profile updated successfully with new password.")
                    # Update session info
                    self.user['first_name'] = first_name
                    self.user['last_name'] = last_name
                    self.user['email'] = email
                    save_user_session(self.user)
                    self.refresh_page()  # Refresh page
            else:
                # Update profile without changing password
                if update_user_profile(profile['user_id'], first_name, last_name, email):
                    messagebox.showinfo("Success", "Profile updated successfully.")
                    # Update session info
                    self.user['first_name'] = first_name
                    self.user['last_name'] = last_name
                    self.user['email'] = email
                    save_user_session(self.user)
                    self.refresh_page()  # Refresh page
        
        # Save button
        save_button = ctk.CTkButton(button_frame, text="Save Changes", font=ctk.CTkFont(size=14), 
                                  fg_color="#116636", hover_color="#0d4f29", width=150, height=40,
                                  command=save_profile)
        save_button.pack(side="right")
    
    def refresh_page(self):
        """Refresh the profile page"""
        # Clear current content
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Reload profile data
        self.load_profile()
    
    def open_dashboard(self):
        """Open the dashboard page"""
        self.root.destroy()
        from student.dashboard import run_dashboard
        run_dashboard()
    
    def open_search(self):
        """Open the search books page"""
        self.root.destroy()
        from student.browse import run_browse
        run_browse()
    
    def open_borrowed(self):
        """Open the borrowed books page"""
        self.root.destroy()
        from student.borrowed import run_borrowed
        run_borrowed()
    
    def open_fines(self):
        """Open the fines page"""
        self.root.destroy()
        from student.fines import run_fines
        run_fines()
    
    def logout(self):
        """Logout and return to login page"""
        try:
            # Clear the session
            clear_user_session()
            
            # Close current window
            self.root.destroy()
            
            # Open login page
            import os
            os.system("python auth.py")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to logout: {e}")
            self.root.destroy()

# ------------------- Run Function -------------------
def run_profile():
    """Run the profile application"""
    root = ctk.CTk()
    app = ProfileApp(root)
    root.mainloop()

# ------------------- Main Execution -------------------
if __name__ == "__main__":
    run_profile()
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import re
from datetime import datetime

from utils import connect_db, hash_password

def get_users(search_term=""):
    """Get all users with optional search"""
    connection = connect_db()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        if search_term:
            query = """
                SELECT 
                    user_id, first_name, last_name, email, role, 
                    registration_date
                FROM 
                    Users
                WHERE 
                    first_name LIKE %s OR last_name LIKE %s OR email LIKE %s
                ORDER BY 
                    registration_date DESC
            """
            search_param = f"%{search_term}%"
            cursor.execute(query, (search_param, search_param, search_param))
        else:
            query = """
                SELECT 
                    user_id, first_name, last_name, email, role, 
                    registration_date
                FROM 
                    Users
                ORDER BY 
                    registration_date DESC
            """
            cursor.execute(query)
        
        return cursor.fetchall()
    except Exception as err:
        messagebox.showerror("Database Error", str(err))
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_user(first_name, last_name, email, password, role="member"):
    """Create a new user"""
    connection = connect_db()
    if not connection:
        return False, "Database connection failed"
    
    try:
        cursor = connection.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT user_id FROM Users WHERE email = %s", (email,))
        if cursor.fetchone():
            return False, "A user with this email already exists"
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Insert the new user
        cursor.execute(
            """
            INSERT INTO Users (
                first_name, last_name, email, password, role, registration_date
            ) VALUES (%s, %s, %s, %s, %s, CURDATE())
            """,
            (first_name, last_name, email, hashed_password, role)
        )
        
        connection.commit()
        return True, "User created successfully"
    except Exception as err:
        return False, f"Database Error: {err}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_user(user_id, first_name, last_name, email, role, new_password=None):
    """Update an existing user"""
    connection = connect_db()
    if not connection:
        return False, "Database connection failed"
    
    try:
        cursor = connection.cursor()
        
        # Check if user exists
        cursor.execute("SELECT user_id FROM Users WHERE user_id = %s", (user_id,))
        if not cursor.fetchone():
            return False, "User not found"
        
        # Update user with or without password change
        if new_password:
            hashed_password = hash_password(new_password)
            cursor.execute(
                """
                UPDATE Users SET 
                    first_name = %s, last_name = %s, email = %s, role = %s, password = %s
                WHERE user_id = %s
                """,
                (first_name, last_name, email, role, hashed_password, user_id)
            )
        else:
            cursor.execute(
                """
                UPDATE Users SET 
                    first_name = %s, last_name = %s, email = %s, role = %s
                WHERE user_id = %s
                """,
                (first_name, last_name, email, role, user_id)
            )
        
        connection.commit()
        return True, "User updated successfully"
    except Exception as err:
        return False, f"Database Error: {err}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def delete_user(user_id):
    """Delete a user"""
    connection = connect_db()
    if not connection:
        return False, "Database connection failed"
    
    try:
        cursor = connection.cursor()
        
        # Check if user has active loans
        cursor.execute(
            "SELECT COUNT(*) FROM Loans WHERE user_id = %s AND return_date IS NULL", 
            (user_id,)
        )
        
        if cursor.fetchone()[0] > 0:
            return False, "Cannot delete user: they have active loans"
        
        # Delete any fines
        cursor.execute(
            """
            DELETE FROM Fines
            WHERE loan_id IN (SELECT loan_id FROM Loans WHERE user_id = %s)
            """, 
            (user_id,)
        )
        
        # Delete loan history
        cursor.execute("DELETE FROM Loans WHERE user_id = %s", (user_id,))
        
        # Delete the user
        cursor.execute("DELETE FROM Users WHERE user_id = %s", (user_id,))
        
        connection.commit()
        return True, "User deleted successfully"
    except Exception as err:
        return False, f"Database Error: {err}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# ------------------- UI Functions -------------------
def show_users_management(content_frame):
    """Show the user management page in the provided content frame"""
    # Clear content area
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    # Create user management title
    title = ctk.CTkLabel(
        content_frame, 
        text="User Management",
        font=ctk.CTkFont(size=24, weight="bold"),
        anchor="w"
    )
    title.pack(anchor="w", padx=30, pady=(20, 10))
    
    # Search and Add User Bar
    action_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    action_frame.pack(fill="x", padx=30, pady=(10, 20))
    
    # Search box
    search_var = tk.StringVar()
    search_entry = ctk.CTkEntry(
        action_frame,
        width=400,
        height=40,
        placeholder_text="Search by name or email",
        textvariable=search_var
    )
    search_entry.pack(side="left")
    
    def perform_search():
        search_term = search_var.get()
        populate_users_table(users_tree, search_term)
    
    search_button = ctk.CTkButton(
        action_frame,
        text="🔍 Search",
        width=120,
        height=40,
        fg_color="#116636",
        hover_color="#0d4f29",
        command=perform_search
    )
    search_button.pack(side="left", padx=(10, 0))
    
    # Add New User Button
    add_button = ctk.CTkButton(
        action_frame,
        text="+ Add New User",
        width=150,
        height=40,
        fg_color="#2196f3",
        hover_color="#1976d2",
        command=lambda: show_user_form(content_frame, users_tree)
    )
    add_button.pack(side="right")
    
    # Bind Enter key to search
    search_entry.bind("<Return>", lambda event: perform_search())
    
    # Users Table
    table_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
    
    # Style for treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="white", fieldbackground="white", foreground="black")
    style.configure("Treeview.Heading", background="#f0f0f0", foreground="black", font=("Arial", 10, "bold"))
    style.map("Treeview", background=[("selected", "#116636")], foreground=[("selected", "white")])
    
    # Table columns
    users_columns = ("ID", "First Name", "Last Name", "Email", "Role", "Registration Date", "Actions")
    
    # Create treeview
    users_tree = ttk.Treeview(
        table_frame, 
        columns=users_columns, 
        show="headings", 
        height=20,
        selectmode="browse"
    )
    users_tree.pack(side="left", fill="both", expand=True)
    
    # Add a scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=users_tree.yview)
    scrollbar.pack(side="right", fill="y")
    users_tree.configure(yscrollcommand=scrollbar.set)
    
    # Configure column widths and headings
    column_widths = {
        "ID": 50,
        "First Name": 120,
        "Last Name": 120,
        "Email": 200,
        "Role": 100,
        "Registration Date": 120,
        "Actions": 120
    }
    
    for col in users_columns:
        users_tree.heading(col, text=col)
        users_tree.column(col, width=column_widths.get(col, 100), anchor="w" if col != "Actions" else "center")
    
    # Initial load of users
    populate_users_table(users_tree)

def populate_users_table(users_tree, search_term=""):
    """Populate the users table with data"""
    # Clear existing data
    for item in users_tree.get_children():
        users_tree.delete(item)
    
    # Get users data
    users = get_users(search_term)
    
    # Insert users into table
    for user in users:
        reg_date = user['registration_date']
        if isinstance(reg_date, datetime):
            reg_date = reg_date.strftime('%Y-%m-%d')
        
        item_id = users_tree.insert("", "end", values=(
            user['user_id'],
            user['first_name'],
            user['last_name'],
            user['email'],
            user['role'],
            reg_date,
            ""  # Actions column will be filled with buttons
        ))
        
    # Add buttons to the Actions column
    add_user_action_buttons(users_tree)

def add_user_action_buttons(users_tree):
    """Add edit and delete buttons to the users table"""
    for item in users_tree.get_children():
        # Get the user ID
        user_id = users_tree.item(item, 'values')[0]
        
        # Get bounding box for action column
        col_idx = 6  # "Actions" column index
        bbox = users_tree.bbox(item, column=col_idx)
        
        if bbox:  # If visible
            # Create a frame for the buttons
            button_frame = ctk.CTkFrame(users_tree, fg_color="transparent")
            button_frame.place(x=bbox[0], y=bbox[1], width=120, height=bbox[3])
            
            # Edit button
            edit_button = ctk.CTkButton(
                button_frame, 
                text="Edit",
                width=50,
                height=20,
                fg_color="#FFA500",
                hover_color="#FF8C00",
                corner_radius=4,
                font=ctk.CTkFont(size=10),
                command=lambda u_id=user_id: show_user_form(users_tree.master.master, users_tree, u_id)
            )
            edit_button.pack(side="left", padx=(0, 5))
            
            # Delete button
            delete_button = ctk.CTkButton(
                button_frame, 
                text="Delete",
                width=50,
                height=20,
                fg_color="#FF5252",
                hover_color="#D32F2F",
                corner_radius=4,
                font=ctk.CTkFont(size=10),
                command=lambda u_id=user_id: confirm_delete_user(users_tree, u_id)
            )
            delete_button.pack(side="left")

def show_user_form(content_frame, users_tree, user_id=None):
    """Show form to add or edit a user"""
    # Create a dialog window
    dialog = ctk.CTkToplevel(content_frame)
    dialog.title("Add New User" if user_id is None else "Edit User")
    dialog.geometry("500x470")
    dialog.resizable(False, False)
    dialog.grab_set()  # Make it modal
    
    # Center the dialog on screen
    dialog_x = content_frame.winfo_rootx() + (content_frame.winfo_width() // 2) - 250
    dialog_y = content_frame.winfo_rooty() + (content_frame.winfo_height() // 2) - 235
    dialog.geometry(f"+{dialog_x}+{dialog_y}")
    
    # User data (empty for new, populated for edit)
    user_data = {}
    if user_id:
        # Fetch user data for editing
        users = get_users()
        for user in users:
            if str(user['user_id']) == str(user_id):
                user_data = user
                break
    
    # Form frame
    form_frame = ctk.CTkFrame(dialog)
    form_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    form_title = ctk.CTkLabel(
        form_frame,
        text="Add New User" if user_id is None else "Edit User",
        font=ctk.CTkFont(size=20, weight="bold")
    )
    form_title.pack(pady=(0, 20))
    
    # Input fields frame
    input_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    input_frame.pack(fill="x", pady=10)
    
    # Configure grid
    input_frame.grid_columnconfigure(1, weight=1)
    
    # First Name field
    ctk.CTkLabel(input_frame, text="First Name:", anchor="e", width=100).grid(row=0, column=0, padx=(20, 10), pady=10, sticky="e")
    first_name_entry = ctk.CTkEntry(input_frame, width=300, height=30)
    first_name_entry.grid(row=0, column=1, padx=(0, 20), pady=10, sticky="ew")
    if 'first_name' in user_data:
        first_name_entry.insert(0, user_data['first_name'])
    
    # Last Name field
    ctk.CTkLabel(input_frame, text="Last Name:", anchor="e", width=100).grid(row=1, column=0, padx=(20, 10), pady=10, sticky="e")
    last_name_entry = ctk.CTkEntry(input_frame, width=300, height=30)
    last_name_entry.grid(row=1, column=1, padx=(0, 20), pady=10, sticky="ew")
    if 'last_name' in user_data:
        last_name_entry.insert(0, user_data['last_name'])
    
    # Email field
    ctk.CTkLabel(input_frame, text="Email:", anchor="e", width=100).grid(row=2, column=0, padx=(20, 10), pady=10, sticky="e")
    email_entry = ctk.CTkEntry(input_frame, width=300, height=30)
    email_entry.grid(row=2, column=1, padx=(0, 20), pady=10, sticky="ew")
    if 'email' in user_data:
        email_entry.insert(0, user_data['email'])
    
    # Role field
    ctk.CTkLabel(input_frame, text="Role:", anchor="e", width=100).grid(row=3, column=0, padx=(20, 10), pady=10, sticky="e")
    
    role_var = tk.StringVar(value=user_data.get('role', 'member'))
    role_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
    role_frame.grid(row=3, column=1, padx=(0, 20), pady=10, sticky="ew")
    
    member_radio = ctk.CTkRadioButton(
        role_frame, 
        text="Member", 
        variable=role_var, 
        value="member",
        fg_color="#116636"
    )
    member_radio.pack(side="left", padx=(0, 20))
    
    admin_radio = ctk.CTkRadioButton(
        role_frame, 
        text="Admin", 
        variable=role_var, 
        value="admin",
        fg_color="#116636"
    )
    admin_radio.pack(side="left")
    
    # Password field (required for new users)
    ctk.CTkLabel(input_frame, text="Password:", anchor="e", width=100).grid(row=4, column=0, padx=(20, 10), pady=10, sticky="e")
    password_entry = ctk.CTkEntry(input_frame, width=300, height=30, show="•")
    password_entry.grid(row=4, column=1, padx=(0, 20), pady=10, sticky="ew")
    
    # Password note
    pass_note = "Password required for new users" if user_id is None else "Leave blank to keep current password"
    pass_note_label = ctk.CTkLabel(
        input_frame, 
        text=pass_note, 
        font=ctk.CTkFont(size=10), 
        text_color="gray"
    )
    pass_note_label.grid(row=5, column=1, padx=(0, 20), pady=(0, 10), sticky="w")
    
    # Error message label
    error_label = ctk.CTkLabel(
        form_frame,
        text="",
        font=ctk.CTkFont(size=12),
        text_color="#d32f2f"
    )
    error_label.pack(pady=(10, 0))
    
    # Button frame
    button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    button_frame.pack(fill="x", pady=(20, 0))
    
    # Cancel button
    cancel_button = ctk.CTkButton(
        button_frame,
        text="Cancel",
        font=ctk.CTkFont(size=14),
        fg_color="#f0f0f0",
        text_color="#333333",
        hover_color="#e0e0e0",
        width=100,
        height=35,
        command=dialog.destroy
    )
    cancel_button.pack(side="left", padx=5)
    
    # Save/Update button
    def save_user():
        # Validate input
        first_name = first_name_entry.get().strip()
        last_name = last_name_entry.get().strip()
        email = email_entry.get().strip()
        role = role_var.get()
        password = password_entry.get()
        
        # Basic validation
        if not first_name or not last_name or not email:
            error_label.configure(text="First name, last name and email are required")
            return
        
        # Email validation
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            error_label.configure(text="Please enter a valid email address")
            return
        
        # Password required for new users
        if not user_id and not password:
            error_label.configure(text="Password is required for new users")
            return
        
        # Save/update the user
        if user_id:  # Update existing user
            success, message = update_user(user_id, first_name, last_name, email, role, password if password else None)
        else:  # Add new user
            success, message = create_user(first_name, last_name, email, password, role)
        
        if success:
            dialog.destroy()
            populate_users_table(users_tree)  # Refresh the table
            messagebox.showinfo("Success", message)
        else:
            error_label.configure(text=message)
    
    save_button = ctk.CTkButton(
        button_frame,
        text="Save" if user_id is None else "Update",
        font=ctk.CTkFont(size=14),
        fg_color="#116636",
        hover_color="#0d4f29",
        width=100,
        height=35,
        command=save_user
    )
    save_button.pack(side="right", padx=5)

def confirm_delete_user(users_tree, user_id):
    """Show confirmation dialog before deleting a user"""
    # Find user name
    user_name = ""
    for item in users_tree.get_children():
        values = users_tree.item(item, 'values')
        if str(values[0]) == str(user_id):
            user_name = f"{values[1]} {values[2]}"
            break
    
    result = messagebox.askyesno(
        "Confirm Delete", 
        f"Are you sure you want to delete the user:\n\n{user_name}?\n\nThis action cannot be undone."
    )
    
    if result:
        success, message = delete_user(user_id)
        if success:
            messagebox.showinfo("Success", message)
            populate_users_table(users_tree)  # Refresh the table
        else:
            messagebox.showerror("Error", message)
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import os
from datetime import datetime

from config import DB_CONFIG
from utils import connect_db, load_admin_session, save_admin_session, clear_admin_session
from admin.admin_books import show_books_management
from admin.admin_users import show_users_management
from admin.admin_fines import show_fines_management

# ------------------- Admin Dashboard Class -------------------
class LibraryAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System - Admin Dashboard")
        self.root.geometry("1200x700")
        
        # Set appearance mode and default color theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        
        # Check admin session
        self.admin = load_admin_session()
        if not self.admin:
            self.show_login()
            return
        
        # Set up UI once admin is authenticated
        self.setup_ui()
        
        # Load dashboard by default
        self.show_dashboard()
        
    def setup_ui(self):
        """Set up the main UI once admin is authenticated"""
        # Create main frame layout
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#f0f4f0")
        self.main_frame.pack(fill="both", expand=True)
        
        # Create sidebar
        self.sidebar = ctk.CTkFrame(self.main_frame, width=210, fg_color="#116636")
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        
        # Content frame (right side)
        self.content = ctk.CTkFrame(self.main_frame, fg_color="#e6f4e6")
        self.content.pack(side="right", fill="both", expand=True, padx=0, pady=0)
        
        # Set up sidebar
        self.setup_sidebar()
        
        # Initialize content frames dictionary
        self.content_frames = {}
    
    def setup_sidebar(self):
        """Set up the sidebar with navigation"""
        # Admin Dashboard Label
        library_label = ctk.CTkLabel(
            self.sidebar, 
            text="📚 Library Admin", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        library_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        # Admin name
        admin_welcome = ctk.CTkLabel(
            self.sidebar,
            text=f"Welcome,\n{self.admin['first_name']} {self.admin['last_name']}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        )
        admin_welcome.pack(anchor="w", padx=20, pady=(0, 20))
        
        # Separator
        separator = ctk.CTkFrame(self.sidebar, height=1, fg_color="white")
        separator.pack(fill="x", padx=10, pady=10)
        
        # Menu buttons 
        menu_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("📚 Manage Books", self.show_books),
            ("👥 Manage Users", self.show_users),
            ("💰 Manage Fines", self.show_fines),
        ]
        
        # Create buttons
        self.menu_buttons = {}
        for text, command in menu_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color="white",
                hover_color="#0d4f29",
                command=command
            )
            btn.pack(fill="x", pady=5, padx=10)
            self.menu_buttons[text] = btn
        
        # Add some space before logout
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=200)
        spacer.pack(fill="x")
        
        # Logout button at bottom
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Logout",
            anchor="w",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color="white",
            hover_color="#0d4f29",
            command=self.logout
        )
        logout_btn.pack(fill="x", pady=5, padx=10, side="bottom")
    
    def highlight_active_menu(self, active_menu):
        """Highlight the active menu button"""
        for text, button in self.menu_buttons.items():
            if text == active_menu:
                button.configure(fg_color="#0d4f29")
            else:
                button.configure(fg_color="transparent")
    
    def show_login(self):
        """Show admin login screen"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create login frame
        login_frame = ctk.CTkFrame(self.root)
        login_frame.pack(fill="both", expand=True)
        
        # Add title
        title_label = ctk.CTkLabel(
            login_frame,
            text="Library Admin Login",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(100, 30))
        
        # Create input fields frame
        input_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
        input_frame.pack(pady=20)
        
        # Email field
        email_label = ctk.CTkLabel(
            input_frame,
            text="Email:",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=100,
            anchor="e"
        )
        email_label.grid(row=0, column=0, padx=(20, 10), pady=10)
        
        email_entry = ctk.CTkEntry(
            input_frame,
            width=300,
            height=40,
            placeholder_text="Enter admin email"
        )
        email_entry.grid(row=0, column=1, padx=(0, 20), pady=10)
        
        # Password field
        password_label = ctk.CTkLabel(
            input_frame,
            text="Password:",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=100,
            anchor="e"
        )
        password_label.grid(row=1, column=0, padx=(20, 10), pady=10)
        
        password_entry = ctk.CTkEntry(
            input_frame,
            width=300,
            height=40,
            placeholder_text="Enter password",
            show="•"
        )
        password_entry.grid(row=1, column=1, padx=(0, 20), pady=10)
        
        # Error message label
        error_label = ctk.CTkLabel(
            login_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#d32f2f"
        )
        error_label.pack()
        
        # Login button
        def handle_login():
            email = email_entry.get()
            password = password_entry.get()
            
            if not email or not password:
                error_label.configure(text="Please enter both email and password")
                return
            
            # Hash the password
            from utils import hash_password
            hashed_password = hash_password(password)
            
            connection = connect_db()
            if connection:
                try:
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute(
                        "SELECT user_id, first_name, last_name, email, role FROM Users WHERE email = %s AND password = %s AND role = 'admin'",
                        (email, hashed_password)
                    )
                    admin = cursor.fetchone()
                    
                    if admin:
                        # Save admin session
                        save_admin_session(admin)
                        
                        # Reload the application
                        self.admin = admin
                        self.setup_ui()
                        self.show_dashboard()
                    else:
                        error_label.configure(text="Invalid admin credentials or insufficient privileges")
                finally:
                    if connection.is_connected():
                        cursor.close()
                        connection.close()
        
        login_button = ctk.CTkButton(
            login_frame,
            text="Login",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#116636",
            hover_color="#0d4f29",
            width=200,
            height=40,
            command=handle_login
        )
        login_button.pack(pady=20)
        
        # Bind Enter key to login
        password_entry.bind("<Return>", lambda event: handle_login())
        
        # Back button
        def go_back():
            self.root.destroy()
            import main
            root = ctk.CTk()
            main.LibraryManagementSystem(root)
            root.mainloop()
            
        back_button = ctk.CTkButton(
            login_frame,
            text="Back to Main Menu",
            font=ctk.CTkFont(size=12),
            fg_color="#888888",
            hover_color="#666666",
            width=150,
            height=30,
            command=go_back
        )
        back_button.pack(pady=10)
    
    def show_dashboard(self):
        """Show the dashboard page"""
        self.highlight_active_menu("📊 Dashboard")
        
        # Clear content area
        for widget in self.content.winfo_children():
            widget.destroy()
        
        # Get dashboard statistics
        stats = self.get_dashboard_stats()
        
        # Create dashboard title
        title = ctk.CTkLabel(
            self.content, 
            text="Admin Dashboard",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w"
        )
        title.pack(anchor="w", padx=30, pady=(20, 20))
        
        # Summary Cards
        cards_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        # Configure grid columns
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)
        
        # Card data and icons
        card_data = [
            ("Total Books", f"{stats.get('total_books', 0):,}", "📚"),
            ("Books Borrowed", f"{stats.get('borrowed_books', 0):,}", "📖"),
            ("Registered Users", f"{stats.get('total_users', 0):,}", "👥"),
            ("Pending Fines", f"${stats.get('pending_fines', 0):,.2f}", "💰")
        ]
        
        # Create summary cards
        for i, (title, value, icon) in enumerate(card_data):
            card = ctk.CTkFrame(cards_frame, fg_color="white", corner_radius=10)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew", ipadx=15, ipady=15)
            
            # Icon and title in same frame
            header_frame = ctk.CTkFrame(card, fg_color="transparent")
            header_frame.pack(anchor="w", padx=15, pady=(15, 5))
            
            icon_label = ctk.CTkLabel(
                header_frame,
                text=icon,
                font=ctk.CTkFont(size=20),
                text_color="#116636"
            )
            icon_label.pack(side="left", padx=(0, 5))
            
            title_label = ctk.CTkLabel(
                header_frame,
                text=title,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#116636"
            )
            title_label.pack(side="left")
            
            # Value
            value_label = ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#333333"
            )
            value_label.pack(anchor="w", padx=15, pady=(5, 15))
        
        # Create two columns for bottom section
        bottom_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        bottom_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
        
        # Recent Loans Section
        recent_loans_frame = ctk.CTkFrame(bottom_frame, fg_color="white", corner_radius=10)
        recent_loans_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        
        recent_title = ctk.CTkLabel(
            recent_loans_frame,
            text="Recent Loans",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        recent_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Recent loans table
        loans_columns = ("Book", "User", "Loan Date", "Due Date")
        loans_frame = ctk.CTkFrame(recent_loans_frame, fg_color="transparent")
        loans_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Style for treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", fieldbackground="white", foreground="black")
        style.configure("Treeview.Heading", background="#f0f0f0", foreground="black", font=("Arial", 10, "bold"))
        style.map("Treeview", background=[("selected", "#116636")], foreground=[("selected", "white")])
        
        # Create treeview
        loans_tree = ttk.Treeview(loans_frame, columns=loans_columns, show="headings", height=8)
        loans_tree.pack(side="left", fill="both", expand=True)
        
        # Configure columns
        for col in loans_columns:
            loans_tree.heading(col, text=col)
            loans_tree.column(col, width=100)
        
        # Populate with recent loans
        for loan in stats.get('recent_loans', []):
            loans_tree.insert("", "end", values=(
                loan[0],  # Book title
                f"{loan[1]} {loan[2]}",  # User name
                loan[3].strftime('%b %d, %Y') if isinstance(loan[3], datetime) else loan[3],  # Loan date
                loan[4].strftime('%b %d, %Y') if isinstance(loan[4], datetime) else loan[4]   # Due date
            ))
        
        # Genres Section
        genres_frame = ctk.CTkFrame(bottom_frame, fg_color="white", corner_radius=10)
        genres_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        
        genres_title = ctk.CTkLabel(
            genres_frame,
            text="Books by Genre",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        genres_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Create canvas for the bar chart
        chart_frame = ctk.CTkFrame(genres_frame, fg_color="transparent")
        chart_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Simple bar chart implementation
        bar_canvas = ctk.CTkCanvas(chart_frame, bg="white", highlightthickness=0)
        bar_canvas.pack(fill="both", expand=True)
        
        # Get genre data
        genres = stats.get('genres', [])
        if genres:
            # Find the maximum count for scaling
            max_count = max(g[1] for g in genres)
            bar_width = 80
            spacing = 40
            start_x = 50
            max_height = 200
            
            # Draw bars
            for i, (genre, count) in enumerate(genres):
                # Calculate positions
                x = start_x + i * (bar_width + spacing)
                y_bottom = 250
                bar_height = (count / max_count) * max_height
                y_top = y_bottom - bar_height
                
                # Draw bar
                bar_canvas.create_rectangle(
                    x, y_bottom, x + bar_width, y_top,
                    fill="#116636", outline=""
                )
                
                # Draw genre label
                bar_canvas.create_text(
                    x + bar_width/2, y_bottom + 20,
                    text=genre, font=("Arial", 9), fill="#333333"
                )
                
                # Draw count label
                bar_canvas.create_text(
                    x + bar_width/2, y_top - 15,
                    text=str(count), font=("Arial", 10, "bold"), fill="#333333"
                )
    
    def get_dashboard_stats(self):
        """Get statistics for the dashboard"""
        connection = connect_db()
        if not connection:
            return {}
        
        try:
            cursor = connection.cursor()
            
            # Total Books Count
            cursor.execute("SELECT SUM(total_copies) FROM Books")
            total_books = cursor.fetchone()[0] or 0
            
            # Borrowed Books Count
            cursor.execute("SELECT COUNT(*) FROM Loans WHERE return_date IS NULL")
            borrowed_books = cursor.fetchone()[0] or 0
            
            # Total Users Count
            cursor.execute("SELECT COUNT(*) FROM Users")
            total_users = cursor.fetchone()[0] or 0
            
            # Pending Fines Amount
            cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM Fines WHERE paid = 0")
            pending_fines = cursor.fetchone()[0] or 0
            
            # Books by Genre
            cursor.execute("""
                SELECT genre, COUNT(*) as count 
                FROM Books 
                GROUP BY genre 
                ORDER BY count DESC 
                LIMIT 5
            """)
            genres = cursor.fetchall()
            
            # Recent Loans
            cursor.execute("""
                SELECT 
                    b.title, u.first_name, u.last_name, l.loan_date, l.due_date
                FROM 
                    Loans l
                JOIN 
                    Books b ON l.book_id = b.book_id
                JOIN 
                    Users u ON l.user_id = u.user_id
                WHERE 
                    l.return_date IS NULL
                ORDER BY 
                    l.loan_date DESC
                LIMIT 5
            """)
            recent_loans = cursor.fetchall()
            
            return {
                "total_books": total_books,
                "borrowed_books": borrowed_books,
                "total_users": total_users,
                "pending_fines": pending_fines,
                "genres": genres,
                "recent_loans": recent_loans
            }
        except Exception as err:
            messagebox.showerror("Database Error", str(err))
            return {}
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def show_books(self):
        """Show the book management page"""
        self.highlight_active_menu("📚 Manage Books")
        show_books_management(self.content)
        
    def show_users(self):
        """Show the user management page"""
        self.highlight_active_menu("👥 Manage Users")
        show_users_management(self.content)
    
    def show_fines(self):
        """Show the fines management page"""
        self.highlight_active_menu("💰 Manage Fines")
        show_fines_management(self.content)
    
    def logout(self):
        """Logout and return to login screen"""
        # Clear the admin session
        clear_admin_session()
        
        # Show login screen
        self.show_login()

# ------------------- Run Admin App -------------------
def run_admin():
    root = ctk.CTk()
    app = LibraryAdminApp(root)
    root.mainloop()

# ------------------- Main Execution -------------------
if __name__ == "__main__":
    run_admin()
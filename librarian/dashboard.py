import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import os

from utils import connect_db, load_user_session, clear_user_session

# We'll create a stub file for now, since the librarian functionality
# will be similar to a combination of admin and student functions

# ------------------- Main LibrarianApp Class -------------------
class LibrarianApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System - Librarian Dashboard")
        self.root.geometry("1200x700")
        
        # Set appearance mode and default color theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        
        # Load user session
        self.user = load_user_session()
        if not self.user or self.user['role'] != 'librarian':
            messagebox.showerror("Session Error", "No active librarian session found.")
            self.logout()
            return
        
        # Set up UI
        self.setup_ui()
        
        # Show dashboard as default
        self.show_dashboard()
    
    def setup_ui(self):
        """Set up the main UI"""
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
    
    def setup_sidebar(self):
        """Set up the sidebar with navigation"""
        # Librarian Dashboard Label
        library_label = ctk.CTkLabel(
            self.sidebar, 
            text="📚 Library Staff", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        library_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        # Librarian name
        welcome_text = f"Welcome,\n{self.user['first_name']} {self.user['last_name']}"
        librarian_welcome = ctk.CTkLabel(
            self.sidebar,
            text=welcome_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        )
        librarian_welcome.pack(anchor="w", padx=20, pady=(0, 20))
        
        # Separator
        separator = ctk.CTkFrame(self.sidebar, height=1, fg_color="white")
        separator.pack(fill="x", padx=10, pady=10)
        
        # Menu buttons 
        menu_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("📚 Manage Books", self.show_books),
            ("👥 Manage Loans", self.show_loans),
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
    
    def show_dashboard(self):
        """Show the dashboard page"""
        self.highlight_active_menu("📊 Dashboard")
        
        # Clear content area
        for widget in self.content.winfo_children():
            widget.destroy()
        
        # Create dashboard title
        title = ctk.CTkLabel(
            self.content, 
            text="Librarian Dashboard",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w"
        )
        title.pack(anchor="w", padx=30, pady=(20, 20))
        
        # Placeholder content - this would be filled with actual dashboard widgets
        placeholder = ctk.CTkLabel(
            self.content,
            text="Librarian functionality would be implemented here.\n\n"
                "This would include book management, user loans, and fine processing.",
            font=ctk.CTkFont(size=16)
        )
        placeholder.pack(pady=100)
        
        # Note about implementation
        note = ctk.CTkLabel(
            self.content,
            text="Note: For this project, the librarian role is a placeholder.\n"
                "The actual functionality would be similar to a combination of admin and user features.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        note.pack(pady=10)
    
    def show_books(self):
        """Show the book management page"""
        self.highlight_active_menu("📚 Manage Books")
        
        # Clear content area
        for widget in self.content.winfo_children():
            widget.destroy()
        
        # Create books title
        title = ctk.CTkLabel(
            self.content, 
            text="Book Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w"
        )
        title.pack(anchor="w", padx=30, pady=(20, 20))
        
        # Placeholder content
        placeholder = ctk.CTkLabel(
            self.content,
            text="Book management functionality would be implemented here.",
            font=ctk.CTkFont(size=16)
        )
        placeholder.pack(pady=100)
    
    def show_loans(self):
        """Show the loan management page"""
        self.highlight_active_menu("👥 Manage Loans")
        
        # Clear content area
        for widget in self.content.winfo_children():
            widget.destroy()
        
        # Create loans title
        title = ctk.CTkLabel(
            self.content, 
            text="Loan Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w"
        )
        title.pack(anchor="w", padx=30, pady=(20, 20))
        
        # Placeholder content
        placeholder = ctk.CTkLabel(
            self.content,
            text="Loan management functionality would be implemented here.",
            font=ctk.CTkFont(size=16)
        )
        placeholder.pack(pady=100)
    
    def show_fines(self):
        """Show the fines management page"""
        self.highlight_active_menu("💰 Manage Fines")
        
        # Clear content area
        for widget in self.content.winfo_children():
            widget.destroy()
        
        # Create fines title
        title = ctk.CTkLabel(
            self.content, 
            text="Fines Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w"
        )
        title.pack(anchor="w", padx=30, pady=(20, 20))
        
        # Placeholder content
        placeholder = ctk.CTkLabel(
            self.content,
            text="Fines management functionality would be implemented here.",
            font=ctk.CTkFont(size=16)
        )
        placeholder.pack(pady=100)
    
    def logout(self):
        """Logout and return to login page"""
        try:
            # Clear the session
            clear_user_session()
            
            # Close current window
            self.root.destroy()
            
            # Open login page
            os.system("python auth.py")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to logout: {e}")
            self.root.destroy()

# ------------------- Run Function -------------------
def run_librarian():
    """Run the librarian application"""
    root = ctk.CTk()
    app = LibrarianApp(root)
    root.mainloop()

# ------------------- Main Execution -------------------
if __name__ == "__main__":
    run_librarian()
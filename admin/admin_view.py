import tkinter as tk
import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import messagebox
import mysql.connector
from CTkMessagebox import CTkMessagebox
import os
import re
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import bcrypt
import tkinter.ttk as ttk

from admin.admin_nav import AdminNavigationFrame
from utils import connect_to_database, center_window

class AdminDashboard(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.title("Library Management System - Admin Dashboard")
        self.geometry("900x600")
        center_window(self)

        # Configure layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initialize navigation and frames, pass sign-out command to navigation frame
        self.navigation_frame = AdminNavigationFrame(master=self, signout_command=self.sign_out)
        self.navigation_frame.grid(row=0, column=0, sticky="ns")

        self.home_frame = HomeFrame(master=self)
        self.user_management_frame = UserManagementFrame(master=self)
        self.book_management_frame = BookManagementFrame(master=self)
        self.reports_frame = ReportsFrame(master=self)

        # Display the default frame (Home)
        self.show_frame("home")

    def show_frame(self, frame_name):
        """Display the selected frame using grid."""
        # Hide all frames
        self.home_frame.grid_forget()
        self.user_management_frame.grid_forget()
        self.book_management_frame.grid_forget()
        self.reports_frame.grid_forget()

        # Show the selected frame
        if frame_name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "user_management":
            self.user_management_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "book_management":
            self.book_management_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "reports":
            self.reports_frame.grid(row=0, column=1, sticky="nsew")

    def sign_out(self):
        """Handle the sign-out process and return to the login window."""
        confirm = messagebox.askyesno("Sign Out", "Are you sure you want to sign out?")
        if confirm:
            self.destroy()  # Close the dashboard window
            self.show_login_window()  # Show the login window

    def show_login_window(self):
        """Reopen the login window after signing out."""
        from login_signup import LoginWindow
        root = ctk.CTk()  # Create a new Tkinter root
        root.geometry("900x600") 
        center_window(root, width=900, height=600) 
        login_window = LoginWindow(root)
        login_window.pack(fill="both", expand=True)
        root.mainloop()


class HomeFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="#f0f0f0")

        # Inner frame for central alignment
        self.inner_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=30, pady=20)

        # Get statistics from database
        self.total_books, self.books_borrowed, self.total_users, self.pending_fines = self.get_statistics()

        # Title Label
        self.title_label = ctk.CTkLabel(
            self.inner_frame,
            text="Welcome to the Admin Dashboard",
            font=("Arial", 24, "bold"),
            text_color="#25a249"
        )
        self.title_label.pack(pady=(20, 30))

        # Statistics Cards
        self.stats_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=30, pady=10)
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Total Books Card
        self.create_stat_card(self.stats_frame, 0, "Total Books", self.total_books, "#4caf50")
        
        # Books Borrowed Card
        self.create_stat_card(self.stats_frame, 1, "Books Borrowed", self.books_borrowed, "#2196f3")
        
        # Registered Users Card
        self.create_stat_card(self.stats_frame, 2, "Registered Users", self.total_users, "#ff9800")
        
        # Pending Fines Card
        self.create_stat_card(self.stats_frame, 3, "Pending Fines", f"${self.pending_fines}", "#f44336")

        # Decorative Separator
        self.separator = ctk.CTkFrame(self.inner_frame, fg_color="#ddd", height=2)
        self.separator.pack(fill="x", padx=30, pady=20)

        # Footer Note
        self.footer_label = ctk.CTkLabel(
            self.inner_frame,
            text="Navigate through the features using the left menu.\n"
                 "Manage users, books, and view reports efficiently.",
            font=("Arial", 12, "italic"),
            text_color="#777",
            justify="center"
        )
        self.footer_label.pack(pady=20)

    def create_stat_card(self, parent, column, title, value, color):
        """Create a statistics card with title and value."""
        card_frame = ctk.CTkFrame(parent, corner_radius=10)
        card_frame.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        
        title_label = ctk.CTkLabel(
            card_frame,
            text=title,
            font=("Arial", 14),
            text_color="#555"
        )
        title_label.pack(pady=(15, 5))
        
        value_label = ctk.CTkLabel(
            card_frame,
            text=str(value),
            font=("Arial", 22, "bold"),
            text_color=color
        )
        value_label.pack(pady=(5, 15))

    def get_statistics(self):
        """Get statistics from the database."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Get total books
            cursor.execute("SELECT COUNT(*) FROM books")
            total_books = cursor.fetchone()[0]
            
            # Get books borrowed (currently checked out)
            cursor.execute("SELECT COUNT(*) FROM borrowed_books WHERE return_date IS NULL")
            books_borrowed = cursor.fetchone()[0]
            
            # Get registered users
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            # Get pending fines
            cursor.execute("SELECT SUM(amount) FROM fines WHERE paid = FALSE")
            result = cursor.fetchone()[0]
            pending_fines = result if result else 0.00
            
            cursor.close()
            conn.close()
            
            return total_books, books_borrowed, total_users, pending_fines
        
        except mysql.connector.Error as err:
            print(f"Database Error: {err}")
            return 0, 0, 0, 0.00


class UserManagementFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="#f0f0f0")

        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="User Management",
            font=("Arial", 24, "bold"),
            text_color="#25a249"
        )
        self.title_label.pack(pady=(20, 10))

        # Buttons for Adding and Deleting Users
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=(10, 10))

        self.add_user_button = ctk.CTkButton(
            self.button_frame,
            text="Add New User",
            command=self.open_add_user_window,
            width=150,
            fg_color="#25a249",
            hover_color="#1e8138"
        )
        self.add_user_button.pack(side="left", padx=10)

        self.delete_user_button = ctk.CTkButton(
            self.button_frame,
            text="Delete Selected User",
            command=self.delete_selected_user,
            width=150,
            fg_color="#f44336",
            hover_color="#d32f2f"
        )
        self.delete_user_button.pack(side="left", padx=10)

        # Treeview for displaying users
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("ID", "First Name", "Last Name", "Email", "Role"),
            show="headings",
            height=15
        )
        self.tree.pack(side="left", fill="both", expand=True)

        # Define column headers
        self.tree.heading("ID", text="ID")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Last Name", text="Last Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Role", text="Role")

        # Adjust column widths
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("First Name", width=120, anchor="center")
        self.tree.column("Last Name", width=120, anchor="center")
        self.tree.column("Email", width=200, anchor="center")
        self.tree.column("Role", width=100, anchor="center")

        # Add a scrollbar
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        # Load users into the table
        self.load_users()

        # Right-click context menu for deleting users
        self.tree.bind("<Button-3>", self.open_context_menu)

    def load_users(self):
        """Fetch user data from the database and display it in the Treeview."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT user_id, first_name, last_name, email, user_type FROM users")
            users = cursor.fetchall()
            cursor.close()
            conn.close()

            # Clear existing rows in the Treeview
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Add users to the Treeview
            for user in users:
                self.tree.insert(
                    "",
                    "end",
                    values=(user["user_id"], user["first_name"], user["last_name"], user["email"], user["user_type"])
                )

        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"Error fetching users: {err}", icon="error")

    def open_add_user_window(self):
        """Open a new CTk window to add a user."""
        add_window = ctk.CTkToplevel(self)
        add_window.title("Add New User")
        add_window.geometry("400x500")
        center_window(add_window, width=400, height=500) 

        ctk.CTkLabel(add_window, text="First Name:", font=("Arial", 14)).pack(pady=5)
        first_name_entry = ctk.CTkEntry(add_window, width=250)
        first_name_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Last Name:", font=("Arial", 14)).pack(pady=5)
        last_name_entry = ctk.CTkEntry(add_window, width=250)
        last_name_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Email:", font=("Arial", 14)).pack(pady=5)
        email_entry = ctk.CTkEntry(add_window, width=250)
        email_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Password:", font=("Arial", 14)).pack(pady=5)
        password_entry = ctk.CTkEntry(add_window, show="*", width=250)
        password_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Role:", font=("Arial", 14)).pack(pady=5)
        role_dropdown = ctk.CTkOptionMenu(
            add_window, 
            values=["student", "lecturer", "admin"],
            width=250,
            fg_color="#25a249",
            button_color="#1e8138"
        )
        role_dropdown.pack(pady=5)

        def validate_email(email):
            """Validate email format."""
            email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            return re.match(email_regex, email) is not None

        def validate_password(password):
            """Validate password strength."""
            return len(password) >= 8 and any(char.isdigit() for char in password) and any(char.isalpha() for char in password)

        def save_user():
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            email = email_entry.get()
            password = password_entry.get()
            role = role_dropdown.get()

            if not (first_name and last_name and email and password and role):
                CTkMessagebox(title="Input Error", message="All fields are required!", icon="warning")
                return

            if not validate_email(email):
                CTkMessagebox(title="Input Error", message="Invalid email format!", icon="warning")
                return

            if not validate_password(password):
                CTkMessagebox(
                    title="Input Error",
                    message="Password must be at least 8 characters long and contain both letters and numbers.",
                    icon="warning"
                )
                return

            try:
                # Hash the password using bcrypt
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                conn = connect_to_database()
                cursor = conn.cursor()
                query = """
                    INSERT INTO users (first_name, last_name, email, password, user_type)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (first_name, last_name, email, hashed_password, role))
                conn.commit()
                cursor.close()
                conn.close()

                self.load_users()
                CTkMessagebox(title="Success", message="User added successfully!", icon="check")
                add_window.destroy()

            except mysql.connector.Error as err:
                CTkMessagebox(title="Database Error", message=f"Error adding user: {err}", icon="error")

        save_button = ctk.CTkButton(
            add_window, 
            text="Save", 
            command=save_user, 
            fg_color="#25a249",
            hover_color="#1e8138",
            width=250
        )
        save_button.pack(pady=20)

    def open_context_menu(self, event):
        """Open a context menu to delete a selected user."""
        row_id = self.tree.identify_row(event.y)
        if row_id:
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label="Delete", command=lambda: self.delete_user(row_id))
            menu.post(event.x_root, event.y_root)

    def delete_selected_user(self):
        """Delete the currently selected user."""
        selected_item = self.tree.selection()
        if not selected_item:
            CTkMessagebox(title="Selection Error", message="No user selected!", icon="warning")
            return

        row_id = selected_item[0]
        self.delete_user(row_id)

    def delete_user(self, row_id):
        """Delete a user from the database."""
        values = self.tree.item(row_id, "values")
        user_id = values[0]

        confirm = CTkMessagebox(
            title="Delete Confirmation",
            message="Are you sure you want to delete this user?",
            icon="question",
            option_1="Yes",
            option_2="No",
        )
        if confirm.get() != "Yes":
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            conn.commit()
            cursor.close()
            conn.close()

            self.load_users()
            CTkMessagebox(title="Deleted", message="User deleted successfully.", icon="info")

        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"Error deleting user: {err}", icon="error")


class ReportsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="#f0f0f0")
        
        # Title for the Reports Section
        self.title_label = ctk.CTkLabel(
            self, 
            text="Library Reports", 
            font=("Arial", 24, "bold"), 
            text_color="#25a249"
        )
        self.title_label.pack(padx=20, pady=20)

        # Dropdown to select the type of report
        self.report_type_var = ctk.StringVar(value="Select Report Type")
        self.report_dropdown = ctk.CTkOptionMenu(
            self,
            variable=self.report_type_var,
            values=["Books by Genre", "Books Borrowed Over Time", "Popular Books", "Overdue Books"],
            fg_color="#25a249",
            button_color="#1e8138"
        )
        self.report_dropdown.pack(padx=10, pady=10)

        # Generate Reports Button
        self.generate_button = ctk.CTkButton(
            self,
            text="Generate Report",
            command=self.generate_reports,
            fg_color="#25a249",
            hover_color="#1e8138",
            width=200,
        )
        self.generate_button.pack(padx=10, pady=20)

        # Frame for Plots
        self.plot_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10, width=800, height=400)
        self.plot_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
    def generate_reports(self):
        """Fetches data for reports and displays the selected plot."""
        report_type = self.report_type_var.get()
        if report_type == "Select Report Type":
            CTkMessagebox(
                title="Select Report",
                message="Please select a report type from the dropdown.",
                icon="warning"
            )
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            # Date 3 months ago
            three_months_ago = datetime.now() - timedelta(days=90)

            if report_type == "Books by Genre":
                cursor.execute(
                    "SELECT genre, COUNT(*) as count FROM books GROUP BY genre ORDER BY count DESC"
                )
                genre_data = cursor.fetchall()
                if genre_data:
                    self.plot_genres(genre_data)
                else:
                    self.display_empty_message("No genre data available.")

            elif report_type == "Books Borrowed Over Time":
                cursor.execute(
                    "SELECT DATE_FORMAT(borrow_date, '%Y-%m') AS month, COUNT(borrow_id) AS borrows_count "
                    "FROM borrowed_books WHERE borrow_date >= %s GROUP BY month ORDER BY month ASC",
                    (three_months_ago,)
                )
                borrow_data = cursor.fetchall()
                if borrow_data:
                    self.plot_borrows(borrow_data)
                else:
                    self.display_empty_message("No borrowing data available for the last 3 months.")

            elif report_type == "Popular Books":
                cursor.execute(
                    "SELECT b.title, COUNT(bb.borrow_id) as borrow_count "
                    "FROM books b JOIN borrowed_books bb ON b.book_id = bb.book_id "
                    "GROUP BY b.book_id ORDER BY borrow_count DESC LIMIT 10"
                )
                popular_books = cursor.fetchall()
                if popular_books:
                    self.plot_popular_books(popular_books)
                else:
                    self.display_empty_message("No borrowing data available.")

            elif report_type == "Overdue Books":
                today = datetime.now().strftime('%Y-%m-%d')
                cursor.execute(
                    "SELECT u.first_name, u.last_name, b.title, bb.due_date "
                    "FROM borrowed_books bb "
                    "JOIN users u ON bb.user_id = u.user_id "
                    "JOIN books b ON bb.book_id = b.book_id "
                    "WHERE bb.return_date IS NULL AND bb.due_date < %s "
                    "ORDER BY bb.due_date",
                    (today,)
                )
                overdue_books = cursor.fetchall()
                if overdue_books:
                    self.display_overdue_books(overdue_books)
                else:
                    self.display_empty_message("No overdue books at this time.")

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            CTkMessagebox(
                title="Database Error",
                message=f"An error occurred: {err}",
                icon="error"
            )

    def plot_genres(self, genre_data):
        """Display book counts by genre as a bar plot."""
        self.clear_plot_frame()
        
        genres = [data[0] if data[0] else "Uncategorized" for data in genre_data]
        counts = [data[1] for data in genre_data]

        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        bars = ax.bar(genres, counts, color="#25a249")
        ax.set_title("Books by Genre", fontsize=14)
        ax.set_xlabel("Genre", fontsize=12)
        ax.set_ylabel("Number of Books", fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        
        # Add count labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    str(int(height)), ha='center', va='bottom')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def plot_borrows(self, borrow_data):
        """Display the number of books borrowed over time as a line plot."""
        self.clear_plot_frame()
        
        months = [data[0] for data in borrow_data]
        counts = [data[1] for data in borrow_data]

        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(months, counts, marker='o', linestyle='-', color="#25a249", linewidth=2)
        ax.set_title("Books Borrowed Over Time", fontsize=14)
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Number of Books Borrowed", fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add data point labels
        for i, count in enumerate(counts):
            ax.text(i, count + 0.3, str(count), ha='center', fontsize=9)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def plot_popular_books(self, popular_books):
        """Display the most popular books as a horizontal bar plot."""
        self.clear_plot_frame()
        
        titles = [data[0] for data in popular_books]
        counts = [data[1] for data in popular_books]
        
        # Reverse lists to display in ascending order (most popular at the top)
        titles.reverse()
        counts.reverse()

        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        bars = ax.barh(titles, counts, color="#25a249")
        ax.set_title("Most Popular Books", fontsize=14)
        ax.set_xlabel("Number of Times Borrowed", fontsize=12)
        ax.set_ylabel("Book Title", fontsize=12)
        
        # Add count labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2., str(int(width)), 
                   ha='left', va='center')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def display_overdue_books(self, overdue_books):
        """Display a table of overdue books."""
        self.clear_plot_frame()
        
        # Create a frame for the table
        table_frame = ctk.CTkFrame(self.plot_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Table headers
        headers = ["User", "Book Title", "Due Date", "Days Overdue"]
        for col, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                table_frame,
                text=header,
                font=("Arial", 14, "bold"),
                text_color="#25a249"
            )
            header_label.grid(row=0, column=col, padx=10, pady=5, sticky="w")
        
        # Add a separator
        separator = ctk.CTkFrame(table_frame, height=1, fg_color="#ddd")
        separator.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
        
        # Add data rows
        today = datetime.now()
        for i, (first_name, last_name, title, due_date) in enumerate(overdue_books, start=2):
            # Calculate days overdue
            due_date_obj = datetime.strptime(str(due_date), '%Y-%m-%d')
            days_overdue = (today - due_date_obj).days
            
            # User name
            user_label = ctk.CTkLabel(
                table_frame,
                text=f"{first_name} {last_name}",
                font=("Arial", 12),
                text_color="#333"
            )
            user_label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            
            # Book title
            title_label = ctk.CTkLabel(
                table_frame,
                text=title,
                font=("Arial", 12),
                text_color="#333"
            )
            title_label.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            
            # Due date
            due_date_label = ctk.CTkLabel(
                table_frame,
                text=due_date.strftime('%Y-%m-%d'),
                font=("Arial", 12),
                text_color="#333"
            )
            due_date_label.grid(row=i, column=2, padx=10, pady=5, sticky="w")
            
            # Days overdue
            days_label = ctk.CTkLabel(
                table_frame,
                text=str(days_overdue),
                font=("Arial", 12),
                text_color="#f44336"
            )
            days_label.grid(row=i, column=3, padx=10, pady=5, sticky="w")

    def display_empty_message(self, message):
        """Display a message when no data is available for the selected report."""
        self.clear_plot_frame()
        empty_label = ctk.CTkLabel(
            self.plot_frame,
            text=message,
            font=("Arial", 14, "bold"),
            text_color="#777"
        )
        empty_label.pack(expand=True)

    def clear_plot_frame(self):
        """Clear all widgets in the plot frame."""
        for widget in self.plot_frame.winfo_children():
            widget.destroy()


class BookManagementFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="#f0f0f0")

        # Title
        self.title_label = ctk.CTkLabel(
            self, 
            text="Book Management", 
            font=("Arial", 24, "bold"), 
            text_color="#25a249"
        )
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="n")

        # Load Inventory Button
        self.load_button = ctk.CTkButton(
            self, 
            text="Refresh Books", 
            command=self.load_books, 
            width=150,
            fg_color="#2196f3",
            hover_color="#1976d2"
        )
        self.load_button.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        # Add Book Button
        self.add_book_button = ctk.CTkButton(
            self, 
            text="Add Book", 
            command=self.open_add_book_window, 
            width=150,
            fg_color="#25a249",
            hover_color="#1e8138"
        )
        self.add_book_button.grid(row=1, column=1, padx=20, pady=10, sticky="e")

        # Scrollable Frame for Book List
        self.book_list_frame = ctk.CTkScrollableFrame(
            self, 
            width=800, 
            height=430, 
            fg_color="white", 
            corner_radius=10
        )
        self.book_list_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        # Configure layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Dictionary to map book IDs to widgets for easy updates
        self.book_widgets = {}
        
        # Load books initially
        self.load_books()

    def load_books(self):
        """Fetch current book inventory from the database and display it."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT book_id, title, author, genre, publication_year, 
                       total_copies, available_copies 
                FROM books
                ORDER BY title
            """)
            books = cursor.fetchall()
            cursor.close()
            conn.close()

            # Clear existing data
            for widget in self.book_list_frame.winfo_children():
                widget.destroy()
            
            # Create header row
            self.create_book_header()

            # Display books
            if books:
                for i, book in enumerate(books):
                    bg_color = "#f9f9f9" if i % 2 == 0 else "white"
                    self.display_book_row(book, i+1, bg_color)
            else:
                no_books_label = ctk.CTkLabel(
                    self.book_list_frame,
                    text="No books in the library. Add some books to get started!",
                    font=("Arial", 14),
                    text_color="#777"
                )
                no_books_label.grid(row=1, column=0, columnspan=7, padx=10, pady=20)

        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"Error fetching books: {err}", icon="error")
    
    def create_book_header(self):
        """Create the header row for the book list."""
        headers = ["Title", "Author", "Genre", "Year", "Total", "Available", "Actions"]
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                self.book_list_frame,
                text=header,
                font=("Arial", 14, "bold"),
                text_color="#25a249"
            )
            header_label.grid(row=0, column=i, padx=10, pady=(5, 10), sticky="w")
        
        # Add a separator
        separator = ctk.CTkFrame(self.book_list_frame, height=1, fg_color="#ddd")
        separator.grid(row=0, column=0, columnspan=7, padx=10, pady=(30, 0), sticky="ews")

    def display_book_row(self, book, row, bg_color):
        """Display a single book row."""
        book_id = book["book_id"]
        
        # Create a frame for this row with alternating background color
        row_frame = ctk.CTkFrame(self.book_list_frame, fg_color=bg_color, corner_radius=0)
        row_frame.grid(row=row, column=0, columnspan=7, padx=5, pady=2, sticky="ew")
        
        # Title
        title_label = ctk.CTkLabel(
            row_frame, 
            text=book["title"],
            font=("Arial", 12),
            text_color="#333",
            width=150
        )
        title_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Author
        author_label = ctk.CTkLabel(
            row_frame, 
            text=book["author"],
            font=("Arial", 12),
            text_color="#333",
            width=120
        )
        author_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Genre
        genre_label = ctk.CTkLabel(
            row_frame, 
            text=book["genre"] if book["genre"] else "N/A",
            font=("Arial", 12),
            text_color="#333",
            width=100
        )
        genre_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        # Year
        year_label = ctk.CTkLabel(
            row_frame, 
            text=str(book["publication_year"]) if book["publication_year"] else "N/A",
            font=("Arial", 12),
            text_color="#333",
            width=50
        )
        year_label.grid(row=0, column=3, padx=10, pady=5, sticky="w")
        
        # Total Copies
        total_label = ctk.CTkLabel(
            row_frame, 
            text=str(book["total_copies"]),
            font=("Arial", 12),
            text_color="#333",
            width=50
        )
        total_label.grid(row=0, column=4, padx=10, pady=5, sticky="w")
        
        # Available Copies
        available_label = ctk.CTkLabel(
            row_frame, 
            text=str(book["available_copies"]),
            font=("Arial", 12),
            text_color="#333" if book["available_copies"] > 0 else "#f44336",
            width=70
        )
        available_label.grid(row=0, column=5, padx=10, pady=5, sticky="w")
        
        # Action Buttons Frame
        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        action_frame.grid(row=0, column=6, padx=10, pady=5, sticky="e")
        
        # Edit Button
        edit_button = ctk.CTkButton(
            action_frame,
            text="Edit",
            command=lambda b=book: self.open_edit_book_window(b),
            width=60,
            height=25,
            fg_color="#2196f3",
            hover_color="#1976d2",
            corner_radius=6
        )
        edit_button.grid(row=0, column=0, padx=(0, 5))
        
        # Delete Button
        delete_button = ctk.CTkButton(
            action_frame,
            text="Delete",
            command=lambda b_id=book_id: self.delete_book(b_id),
            width=60,
            height=25,
            fg_color="#f44336",
            hover_color="#d32f2f",
            corner_radius=6
        )
        delete_button.grid(row=0, column=1)
        
        # Save widgets to dictionary
        self.book_widgets[book_id] = {
            "row_frame": row_frame,
            "title_label": title_label,
            "author_label": author_label,
            "genre_label": genre_label,
            "year_label": year_label,
            "total_label": total_label,
            "available_label": available_label,
            "edit_button": edit_button,
            "delete_button": delete_button
        }
        
    def open_edit_book_window(self, book):
        """Open a window to edit a book's details."""
        edit_window = ctk.CTkToplevel(self)
        edit_window.title(f"Edit Book: {book['title']}")
        edit_window.geometry("500x550")
        center_window(edit_window, width=500, height=550)
        
        # Create a frame to organize the content
        form_frame = ctk.CTkFrame(edit_window)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(form_frame, text="Book Title:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        title_entry = ctk.CTkEntry(form_frame, width=300)
        title_entry.insert(0, book['title'])
        title_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Author
        ctk.CTkLabel(form_frame, text="Author:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        author_entry = ctk.CTkEntry(form_frame, width=300)
        author_entry.insert(0, book['author'])
        author_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Genre
        ctk.CTkLabel(form_frame, text="Genre:", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        genre_entry = ctk.CTkEntry(form_frame, width=300)
        genre_entry.insert(0, book['genre'] if book['genre'] else "")
        genre_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # Publication Year
        ctk.CTkLabel(form_frame, text="Publication Year:", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        year_entry = ctk.CTkEntry(form_frame, width=300)
        year_entry.insert(0, str(book['publication_year']) if book['publication_year'] else "")
        year_entry.grid(row=3, column=1, padx=10, pady=10)
        
        # Total Copies
        ctk.CTkLabel(form_frame, text="Total Copies:", font=("Arial", 14)).grid(row=4, column=0, padx=10, pady=10, sticky="w")
        copies_entry = ctk.CTkEntry(form_frame, width=300)
        copies_entry.insert(0, str(book['total_copies']))
        copies_entry.grid(row=4, column=1, padx=10, pady=10)
        
        # Available Copies (read-only - computed from borrowed books)
        ctk.CTkLabel(form_frame, text="Available Copies:", font=("Arial", 14)).grid(row=5, column=0, padx=10, pady=10, sticky="w")
        available_entry = ctk.CTkEntry(form_frame, width=300, state="disabled")
        available_entry.insert(0, str(book['available_copies']))
        available_entry.grid(row=5, column=1, padx=10, pady=10)
        
        def save_changes():
            # Get values from entries
            title = title_entry.get().strip()
            author = author_entry.get().strip()
            genre = genre_entry.get().strip()
            year_str = year_entry.get().strip()
            copies_str = copies_entry.get().strip()
            
            # Validate inputs
            errors = []
            
            if not title:
                errors.append("Title is required.")
            
            if not author:
                errors.append("Author is required.")
            
            try:
                year = int(year_str) if year_str else None
                if year and (year < 1000 or year > datetime.now().year):
                    errors.append(f"Publication year must be between 1000 and {datetime.now().year}.")
            except ValueError:
                errors.append("Publication year must be a number.")
                year = None
            
            try:
                total_copies = int(copies_str) if copies_str else 1
                if total_copies < 1:
                    errors.append("Number of copies must be at least 1.")
                # Calculate new available copies
                available_copies = total_copies - (book['total_copies'] - book['available_copies'])
                if available_copies < 0:
                    errors.append("Cannot reduce total copies below the number of books currently borrowed.")
            except ValueError:
                errors.append("Number of copies must be a number.")
                return
            
            if errors:
                CTkMessagebox(title="Validation Error", message="\n".join(errors), icon="warning")
                return
            
            try:
                conn = connect_to_database()
                cursor = conn.cursor()
                
                # Update the book in the database
                query = """
                    UPDATE books 
                    SET title = %s, author = %s, genre = %s, publication_year = %s, 
                        total_copies = %s, available_copies = %s
                    WHERE book_id = %s
                """
                cursor.execute(query, (title, author, genre, year, total_copies, available_copies, book['book_id']))
                conn.commit()
                cursor.close()
                conn.close()
                
                # Update UI
                self.load_books()
                
                CTkMessagebox(title="Success", message="Book updated successfully!", icon="check")
                edit_window.destroy()
                
            except mysql.connector.Error as err:
                CTkMessagebox(title="Database Error", message=f"Error updating book: {err}", icon="error")
                
        # Update button
        update_button = ctk.CTkButton(
            form_frame,
            text="Save Changes",
            command=save_changes,
            width=300,
            fg_color="#25a249",
            hover_color="#1e8138"
        )
        update_button.grid(row=6, column=0, columnspan=2, padx=10, pady=20)
        
    def delete_book(self, book_id):
        """Delete a book from the database."""
        confirm = CTkMessagebox(
            title="Delete Confirmation",
            message="Are you sure you want to delete this book? This action cannot be undone.",
            icon="question",
            option_1="Yes",
            option_2="No"
        )
        
        if confirm.get() != "Yes":
            return
            
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Check if book is currently borrowed
            cursor.execute("SELECT COUNT(*) FROM borrowed_books WHERE book_id = %s AND return_date IS NULL", (book_id,))
            borrowed_count = cursor.fetchone()[0]
            
            if borrowed_count > 0:
                CTkMessagebox(
                    title="Cannot Delete",
                    message="This book cannot be deleted because it is currently borrowed by one or more users.",
                    icon="warning"
                )
                cursor.close()
                conn.close()
                return
            
            # Delete the book
            cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Update UI
            if book_id in self.book_widgets:
                for widget in self.book_widgets[book_id].values():
                    widget.destroy()
                del self.book_widgets[book_id]
            
            self.load_books()
            
            CTkMessagebox(title="Success", message="Book deleted successfully!", icon="info")
            
        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"Error deleting book: {err}", icon="error")

    def open_add_book_window(self):
        """Open a new window to add a book."""
        add_window = ctk.CTkToplevel(self)
        add_window.title("Add New Book")
        add_window.geometry("500x550")
        center_window(add_window, width=500, height=550)
        
        # Create a frame to organize the content
        form_frame = ctk.CTkFrame(add_window)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(form_frame, text="Book Title:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        title_entry = ctk.CTkEntry(form_frame, width=300)
        title_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Author
        ctk.CTkLabel(form_frame, text="Author:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        author_entry = ctk.CTkEntry(form_frame, width=300)
        author_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # ISBN
        ctk.CTkLabel(form_frame, text="ISBN:", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        isbn_entry = ctk.CTkEntry(form_frame, width=300)
        isbn_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # Genre
        ctk.CTkLabel(form_frame, text="Genre:", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        genre_entry = ctk.CTkEntry(form_frame, width=300)
        genre_entry.grid(row=3, column=1, padx=10, pady=10)
        
        # Publication Year
        ctk.CTkLabel(form_frame, text="Publication Year:", font=("Arial", 14)).grid(row=4, column=0, padx=10, pady=10, sticky="w")
        year_entry = ctk.CTkEntry(form_frame, width=300)
        year_entry.grid(row=4, column=1, padx=10, pady=10)
        
        # Publisher
        ctk.CTkLabel(form_frame, text="Publisher:", font=("Arial", 14)).grid(row=5, column=0, padx=10, pady=10, sticky="w")
        publisher_entry = ctk.CTkEntry(form_frame, width=300)
        publisher_entry.grid(row=5, column=1, padx=10, pady=10)
        
        # Total Copies
        ctk.CTkLabel(form_frame, text="Total Copies:", font=("Arial", 14)).grid(row=6, column=0, padx=10, pady=10, sticky="w")
        copies_entry = ctk.CTkEntry(form_frame, width=300)
        copies_entry.insert(0, "1")  # Default value
        copies_entry.grid(row=6, column=1, padx=10, pady=10)
        
        def save_book():
            # Get values from entries
            title = title_entry.get().strip()
            author = author_entry.get().strip()
            isbn = isbn_entry.get().strip()
            genre = genre_entry.get().strip()
            year_str = year_entry.get().strip()
            publisher = publisher_entry.get().strip()
            copies_str = copies_entry.get().strip()
            
            # Validate inputs
            errors = []
            
            if not title:
                errors.append("Title is required.")
            
            if not author:
                errors.append("Author is required.")
            
            try:
                year = int(year_str) if year_str else None
                if year and (year < 1000 or year > datetime.now().year):
                    errors.append(f"Publication year must be between 1000 and {datetime.now().year}.")
            except ValueError:
                errors.append("Publication year must be a number.")
                year = None
            
            try:
                copies = int(copies_str) if copies_str else 1
                if copies < 1:
                    errors.append("Number of copies must be at least 1.")
            except ValueError:
                errors.append("Number of copies must be a number.")
                copies = 1
            
            if errors:
                CTkMessagebox(title="Validation Error", message="\n".join(errors), icon="warning")
                return
            
            try:
                conn = connect_to_database()
                cursor = conn.cursor()
                
                # Insert the book into the database
                query = """
                    INSERT INTO books (title, author, isbn, genre, publication_year, 
                                       publisher, total_copies, available_copies)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (title, author, isbn, genre, year, publisher, copies, copies))
                conn.commit()
                cursor.close()
                conn.close()
                
                # Refresh the book list
                self.load_books()
                
                CTkMessagebox(title="Success", message="Book added successfully!", icon="check")
                add_window.destroy()
                
            except mysql.connector.Error as err:
                CTkMessagebox(title="Database Error", message=f"Error adding book: {err}", icon="error")
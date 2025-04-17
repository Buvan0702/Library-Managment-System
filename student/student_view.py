import tkinter as tk
import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import messagebox
import mysql.connector
from CTkMessagebox import CTkMessagebox
import os
import re

from student.student_nav import StudentNavigationFrame
from utils import connect_to_database, center_window

class StudentDashboard(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.title("Library Management System - Student Dashboard")
        self.geometry("900x600")
        center_window(self)

        # Configure layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initialize navigation and frames, pass sign-out command to navigation frame
        self.navigation_frame = StudentNavigationFrame(master=self, signout_command=self.sign_out)
        self.navigation_frame.grid(row=0, column=0, sticky="ns")

        # Get user info
        self.user_info = self.get_user_info()
        
        # Initialize frames
        self.home_frame = HomeFrame(master=self, user_info=self.user_info)
        self.browse_books_frame = BrowseBooksFrame(master=self, user_id=self.user_id)
        self.borrowed_books_frame = BorrowedBooksFrame(master=self, user_id=self.user_id)
        self.fines_frame = FinesFrame(master=self, user_id=self.user_id)

        # Display the default frame (Home)
        self.show_frame("home")

    def get_user_info(self):
        """Get the user's information from the database."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(query, (self.user_id,))
            user_info = cursor.fetchone()
            cursor.close()
            conn.close()
            return user_info
        except mysql.connector.Error as err:
            print(f"Database Error: {err}")
            return None

    def show_frame(self, frame_name):
        """Display the selected frame using grid."""
        # Hide all frames
        self.home_frame.grid_forget()
        self.browse_books_frame.grid_forget()
        self.borrowed_books_frame.grid_forget()
        self.fines_frame.grid_forget()

        # Show the selected frame
        if frame_name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "browse_books":
            self.browse_books_frame.grid(row=0, column=1, sticky="nsew")
            self.browse_books_frame.load_books()  # Reload books when showing the frame
        elif frame_name == "borrowed_books":
            self.borrowed_books_frame.grid(row=0, column=1, sticky="nsew")
            self.borrowed_books_frame.load_borrowed_books()  # Reload when viewing
        elif frame_name == "fines":
            self.fines_frame.grid(row=0, column=1, sticky="nsew")
            self.fines_frame.load_fines()  # Reload when viewing

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
    def __init__(self, master, user_info):
        super().__init__(master)
        self.user_info = user_info
        self.configure(fg_color="#f0f0f0")
        
        # Create an inner frame for content organization
        self.inner_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=30, pady=20)
        
        # Welcome message
        self.welcome_label = ctk.CTkLabel(
            self.inner_frame,
            text=f"Welcome, {self.user_info['first_name']} {self.user_info['last_name']}!",
            font=("Arial", 24, "bold"),
            text_color="#25a249"
        )
        self.welcome_label.pack(pady=(30, 20))
        
        # Statistics frame
        self.stats_frame = ctk.CTkFrame(self.inner_frame, fg_color="#f9f9f9", corner_radius=10)
        self.stats_frame.pack(pady=20, padx=40, fill="x")
        
        # Get stats from database
        self.borrowed_count, self.due_soon_count, self.overdue_count, self.pending_fines = self.get_user_stats()
        
        # Books borrowed
        self.borrowed_label = ctk.CTkLabel(
            self.stats_frame,
            text=f"Books Borrowed: {self.borrowed_count}",
            font=("Arial", 14),
            text_color="#333"
        )
        self.borrowed_label.pack(pady=10)
        
        # Books due soon (in next 3 days)
        self.due_soon_label = ctk.CTkLabel(
            self.stats_frame,
            text=f"Books Due Soon: {self.due_soon_count}",
            font=("Arial", 14),
            text_color="#ff9800"
        )
        self.due_soon_label.pack(pady=10)
        
        # Overdue books
        self.overdue_label = ctk.CTkLabel(
            self.stats_frame,
            text=f"Overdue Books: {self.overdue_count}",
            font=("Arial", 14),
            text_color="#f44336"
        )
        self.overdue_label.pack(pady=10)
        
        # Pending fines
        self.fines_label = ctk.CTkLabel(
            self.stats_frame,
            text=f"Pending Fines: ${self.pending_fines:.2f}",
            font=("Arial", 14),
            text_color="#f44336" if self.pending_fines > 0 else "#333"
        )
        self.fines_label.pack(pady=10)
        
        # Quick actions section
        self.actions_label = ctk.CTkLabel(
            self.inner_frame,
            text="Quick Actions",
            font=("Arial", 18, "bold"),
            text_color="#25a249"
        )
        self.actions_label.pack(pady=(20, 10))
        
        # Quick action buttons
        self.actions_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        self.actions_frame.pack(pady=10)
        
        # Browse books button
        self.browse_button = ctk.CTkButton(
            self.actions_frame,
            text="Browse Books",
            command=lambda: master.show_frame("browse_books"),
            width=150,
            height=40,
            fg_color="#25a249",
            hover_color="#1e8138"
        )
        self.browse_button.grid(row=0, column=0, padx=10, pady=10)
        
        # View borrowed books button
        self.borrowed_button = ctk.CTkButton(
            self.actions_frame,
            text="My Borrowed Books",
            command=lambda: master.show_frame("borrowed_books"),
            width=150,
            height=40,
            fg_color="#2196f3",
            hover_color="#1976d2"
        )
        self.borrowed_button.grid(row=0, column=1, padx=10, pady=10)
        
        # View fines button
        self.fines_button = ctk.CTkButton(
            self.actions_frame,
            text="View & Pay Fines",
            command=lambda: master.show_frame("fines"),
            width=150,
            height=40,
            fg_color="#ff9800",
            hover_color="#f57c00"
        )
        self.fines_button.grid(row=0, column=2, padx=10, pady=10)
        
    def get_user_stats(self):
        """Get the user's statistics from the database."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Books currently borrowed
            cursor.execute(
                "SELECT COUNT(*) FROM borrowed_books WHERE user_id = %s AND return_date IS NULL",
                (self.user_info['user_id'],)
            )
            borrowed_count = cursor.fetchone()[0]
            
            # Books due soon (in next 3 days)
            today = datetime.now().date()
            three_days_later = today + timedelta(days=3)
            cursor.execute(
                "SELECT COUNT(*) FROM borrowed_books WHERE user_id = %s AND return_date IS NULL "
                "AND due_date BETWEEN %s AND %s",
                (self.user_info['user_id'], today, three_days_later)
            )
            due_soon_count = cursor.fetchone()[0]
            
            # Overdue books
            cursor.execute(
                "SELECT COUNT(*) FROM borrowed_books WHERE user_id = %s AND return_date IS NULL "
                "AND due_date < %s",
                (self.user_info['user_id'], today)
            )
            overdue_count = cursor.fetchone()[0]
            
            # Pending fines
            cursor.execute(
                "SELECT SUM(amount) FROM fines WHERE user_id = %s AND paid = FALSE",
                (self.user_info['user_id'],)
            )
            pending_fines = cursor.fetchone()[0] or 0.00
            
            cursor.close()
            conn.close()
            
            return borrowed_count, due_soon_count, overdue_count, pending_fines
            
        except mysql.connector.Error as err:
            print(f"Database Error: {err}")
            return 0, 0, 0, 0.00


class BrowseBooksFrame(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.master = master
        self.user_id = user_id
        self.configure(fg_color="#f0f0f0")
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Browse Books",
            font=("Arial", 24, "bold"),
            text_color="#25a249"
        )
        self.title_label.pack(pady=(20, 10))
        
        # Search bar frame
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.pack(pady=10, fill="x", padx=20)
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Search by title, author, or genre",
            width=400,
            height=40
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        
        # Search button
        self.search_button = ctk.CTkButton(
            self.search_frame,
            text="Search",
            command=self.search_books,
            width=100,
            height=40,
            fg_color="#25a249",
            hover_color="#1e8138"
        )
        self.search_button.pack(side="left")
        
        # Genre filter frame
        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.pack(pady=10, fill="x", padx=20)
        
        # Genre filter label
        self.filter_label = ctk.CTkLabel(
            self.filter_frame,
            text="Filter by Genre:",
            font=("Arial", 14),
            text_color="#333"
        )
        self.filter_label.pack(side="left", padx=(0, 10))
        
        # Genre buttons will be added dynamically
        self.genre_buttons = []
        
        # Books display frame
        self.books_frame = ctk.CTkScrollableFrame(
            self,
            width=800,
            height=400,
            fg_color="white",
            corner_radius=10
        )
        self.books_frame.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Initialize with all books
        self.load_books()
        
    def load_books(self, search_term=None, genre_filter=None):
        """Load books from the database with optional search and filter."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            
            # First get all available genres for the filter buttons
            cursor.execute("SELECT DISTINCT genre FROM books WHERE genre IS NOT NULL AND genre != ''")
            genres = [row['genre'] for row in cursor.fetchall()]
            
            # Update genre filter buttons
            self.update_genre_buttons(genres, current_filter=genre_filter)
            
            # Construct the query based on search and filter
            query = """
                SELECT book_id, title, author, genre, publication_year, 
                       total_copies, available_copies 
                FROM books
                WHERE 1=1
            """
            params = []
            
            if search_term:
                query += " AND (title LIKE %s OR author LIKE %s OR genre LIKE %s)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern, search_pattern])
            
            if genre_filter:
                query += " AND genre = %s"
                params.append(genre_filter)
                
            query += " ORDER BY title"
            
            cursor.execute(query, params)
            books = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Clear existing books
            for widget in self.books_frame.winfo_children():
                widget.destroy()
                
            if books:
                # Display books
                for i, book in enumerate(books):
                    self.create_book_card(book, i)
            else:
                # No books found message
                no_books_label = ctk.CTkLabel(
                    self.books_frame,
                    text="No books found matching your criteria.",
                    font=("Arial", 14),
                    text_color="#777"
                )
                no_books_label.pack(pady=50)
                
        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"Error fetching books: {err}", icon="error")
            
    def update_genre_buttons(self, genres, current_filter=None):
        """Update the genre filter buttons."""
        # Clear existing buttons
        for button in self.genre_buttons:
            button.destroy()
        self.genre_buttons = []
        
        # Add "All" button
        all_button = ctk.CTkButton(
            self.filter_frame,
            text="All",
            command=lambda: self.load_books(search_term=self.search_entry.get()),
            width=80,
            height=30,
            fg_color="#25a249" if current_filter is None else "#dddddd",
            hover_color="#1e8138",
            text_color="white" if current_filter is None else "black"
        )
        all_button.pack(side="left", padx=5)
        self.genre_buttons.append(all_button)
        
        # Add genre buttons
        for genre in genres:
            genre_button = ctk.CTkButton(
                self.filter_frame,
                text=genre,
                command=lambda g=genre: self.load_books(search_term=self.search_entry.get(), genre_filter=g),
                width=80,
                height=30,
                fg_color="#25a249" if current_filter == genre else "#dddddd",
                hover_color="#1e8138",
                text_color="white" if current_filter == genre else "black"
            )
            genre_button.pack(side="left", padx=5)
            self.genre_buttons.append(genre_button)
            
    def search_books(self):
        """Search books based on the search entry."""
        search_term = self.search_entry.get().strip()
        self.load_books(search_term=search_term if search_term else None)
        
    def create_book_card(self, book, index):
        """Create a card display for a book."""
        card_bg = "#f9f9f9" if index % 2 == 0 else "white"
        
        card_frame = ctk.CTkFrame(
            self.books_frame,
            fg_color=card_bg,
            corner_radius=10,
            border_width=1,
            border_color="#dddddd"
        )
        card_frame.pack(fill="x", padx=10, pady=5, ipady=5)
        
        # Title
        title_label = ctk.CTkLabel(
            card_frame,
            text=book['title'],
            font=("Arial", 16, "bold"),
            text_color="#25a249"
        )
        title_label.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        
        # Author
        author_label = ctk.CTkLabel(
            card_frame,
            text=f"by {book['author']}",
            font=("Arial", 14),
            text_color="#555"
        )
        author_label.grid(row=1, column=0, padx=15, pady=0, sticky="w")
        
        # Additional info
        info_text = f"Genre: {book['genre'] if book['genre'] else 'N/A'}"
        if book['publication_year']:
            info_text += f" | Year: {book['publication_year']}"
        info_label = ctk.CTkLabel(
            card_frame,
            text=info_text,
            font=("Arial", 12),
            text_color="#777"
        )
        info_label.grid(row=2, column=0, padx=15, pady=(0, 5), sticky="w")
        
        # Availability status
        availability_text = f"Available: {book['available_copies']}/{book['total_copies']}"
        availability_color = "#4caf50" if book['available_copies'] > 0 else "#f44336"
        availability_label = ctk.CTkLabel(
            card_frame,
            text=availability_text,
            font=("Arial", 12, "bold"),
            text_color=availability_color
        )
        availability_label.grid(row=3, column=0, padx=15, pady=(0, 10), sticky="w")
        
        # Borrow button
        borrow_button = ctk.CTkButton(
            card_frame,
            text="Borrow",
            command=lambda: self.borrow_book(book),
            width=100,
            height=30,
            fg_color="#25a249" if book['available_copies'] > 0 else "#dddddd",
            hover_color="#1e8138",
            state="normal" if book['available_copies'] > 0 else "disabled"
        )
        borrow_button.grid(row=0, column=1, rowspan=4, padx=15, pady=10, sticky="e")
        
        # Configure grid
        card_frame.grid_columnconfigure(0, weight=1)
        
    def borrow_book(self, book):
        """Handle the process of borrowing a book."""
        if book['available_copies'] <= 0:
            CTkMessagebox(title="Not Available", message="This book is currently not available for borrowing.", icon="warning")
            return
            
        # Check if user already has the book
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM borrowed_books WHERE user_id = %s AND book_id = %s AND return_date IS NULL",
                (self.user_id, book['book_id'])
            )
            already_borrowed = cursor.fetchone()[0] > 0
            
            if already_borrowed:
                CTkMessagebox(title="Already Borrowed", message="You have already borrowed this book.", icon="warning")
                cursor.close()
                conn.close()
                return
                
            # Check if user has unpaid fines
            cursor.execute(
                "SELECT SUM(amount) FROM fines WHERE user_id = %s AND paid = FALSE",
                (self.user_id,)
            )
            unpaid_fines = cursor.fetchone()[0] or 0
            
            if unpaid_fines > 0:
                confirm = CTkMessagebox(
                    title="Unpaid Fines",
                    message=f"You have ${unpaid_fines:.2f} in unpaid fines. You need to pay your fines before borrowing more books. Go to fines page?",
                    icon="warning",
                    option_1="Yes",
                    option_2="No"
                )
                if confirm.get() == "Yes":
                    self.master.show_frame("fines")
                cursor.close()
                conn.close()
                return
                
            # Calculate due date (2 weeks from now)
            borrow_date = datetime.now()
            due_date = borrow_date + timedelta(days=14)
            
            # Add borrow record
            cursor.execute(
                "INSERT INTO borrowed_books (user_id, book_id, borrow_date, due_date) VALUES (%s, %s, %s, %s)",
                (self.user_id, book['book_id'], borrow_date, due_date)
            )
            
            # Update available copies
            cursor.execute(
                "UPDATE books SET available_copies = available_copies - 1 WHERE book_id = %s",
                (book['book_id'],)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            CTkMessagebox(
                title="Success",
                message=f"You have successfully borrowed '{book['title']}'. Please return it by {due_date.strftime('%Y-%m-%d')}.",
                icon="check"
            )
            
            # Refresh the book list
            self.load_books()
            
        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"Error borrowing book: {err}", icon="error")


class BorrowedBooksFrame(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.user_id = user_id
        self.configure(fg_color="#f0f0f0")
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="My Borrowed Books",
            font=("Arial", 24, "bold"),
            text_color="#25a249"
        )
        self.title_label.pack(pady=(20, 10))
        
        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self,
            text="Refresh",
            command=self.load_borrowed_books,
            width=100,
            height=30,
            fg_color="#2196f3",
            hover_color="#1976d2"
        )
        self.refresh_button.pack(pady=5)
        
        # Borrowed books frame
        self.borrowed_frame = ctk.CTkScrollableFrame(
            self,
            width=800,
            height=450,
            fg_color="white",
            corner_radius=10
        )
        self.borrowed_frame.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Load borrowed books
        self.load_borrowed_books()
        
    def load_borrowed_books(self):
        """Load the user's borrowed books from the database."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT bb.borrow_id, bb.book_id, b.title, b.author, bb.borrow_date, 
                       bb.due_date, bb.return_date
                FROM borrowed_books bb
                JOIN books b ON bb.book_id = b.book_id
                WHERE bb.user_id = %s
                ORDER BY bb.borrow_date DESC
            """
            cursor.execute(query, (self.user_id,))
            borrowed_books = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Clear existing books
            for widget in self.borrowed_frame.winfo_children():
                widget.destroy()
                
            if borrowed_books:
                # Create sections for current and past borrows
                current_borrows = [book for book in borrowed_books if book['return_date'] is None]
                past_borrows = [book for book in borrowed_books if book['return_date'] is not None]
                
                # Current borrows section
                if current_borrows:
                    self.create_section_header("Currently Borrowed Books")
                    for i, book in enumerate(current_borrows):
                        self.create_borrowed_book_card(book, i, is_current=True)
                
                # Past borrows section
                if past_borrows:
                    self.create_section_header("Previously Borrowed Books")
                    for i, book in enumerate(past_borrows):
                        self.create_borrowed_book_card(book, i, is_current=False)
            else:
                # No books borrowed message
                no_books_label = ctk.CTkLabel(
                    self.borrowed_frame,
                    text="You haven't borrowed any books yet.",
                    font=("Arial", 14),
                    text_color="#777"
                )
                no_books_label.pack(pady=50)
                
        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"Error fetching borrowed books: {err}", icon="error")
            
    def create_section_header(self, text):
        """Create a header for a section of borrowed books."""
        header_frame = ctk.CTkFrame(self.borrowed_frame, fg_color="#f9f9f9", corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=(10, 5))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text=text,
            font=("Arial", 16, "bold"),
            text_color="#25a249"
        )
        header_label.pack(pady=10)
        
    def create_borrowed_book_card(self, book, index, is_current):
        """Create a card display for a borrowed book."""
        card_bg = "#f9f9f9" if index % 2 == 0 else "white"
        
        card_frame = ctk.CTkFrame(
            self.borrowed_frame,
            fg_color=card_bg,
            corner_radius=10,
            border_width=1,
            border_color="#dddddd"
        )
        card_frame.pack(fill="x", padx=10, pady=5, ipady=5)
        
        # Title
        title_label = ctk.CTkLabel(
            card_frame,
            text=book['title'],
            font=("Arial", 16, "bold"),
            text_color="#333"
        )
        title_label.grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")
        
        # Author
        author_label = ctk.CTkLabel(
            card_frame,
            text=f"by {book['author']}",
            font=("Arial", 14),
            text_color="#555"
        )
        author_label.grid(row=1, column=0, columnspan=2, padx=15, pady=0, sticky="w")
        
        # Borrow date
        borrow_date = book['borrow_date'].strftime('%Y-%m-%d') if book['borrow_date'] else "N/A"
        borrow_label = ctk.CTkLabel(
            card_frame,
            text=f"Borrowed: {borrow_date}",
            font=("Arial", 12),
            text_color="#777"
        )
        borrow_label.grid(row=2, column=0, padx=15, pady=(5, 0), sticky="w")
        
        # Due date or return date
        if is_current:
            due_date = book['due_date'].strftime('%Y-%m-%d') if book['due_date'] else "N/A"
            today = datetime.now().date()
            is_overdue = book['due_date'].date() < today if book['due_date'] else False
            
            date_label = ctk.CTkLabel(
                card_frame,
                text=f"Due: {due_date}",
                font=("Arial", 12, "bold" if is_overdue else "normal"),
                text_color="#f44336" if is_overdue else "#777"
            )
            date_label.grid(row=2, column=1, padx=15, pady=(5, 0), sticky="w")
            
            # Calculate days left or overdue
            if book['due_date']:
                days_diff = (book['due_date'].date() - today).days
                if days_diff >= 0:
                    status_text = f"{days_diff} days left"
                    status_color = "#4caf50"
                else:
                    status_text = f"{abs(days_diff)} days overdue"
                    status_color = "#f44336"
                    
                status_label = ctk.CTkLabel(
                    card_frame,
                    text=status_text,
                    font=("Arial", 12, "bold"),
                    text_color=status_color
                )
                status_label.grid(row=3, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="w")
            
            # Return button
            return_button = ctk.CTkButton(
                card_frame,
                text="Return Book",
                command=lambda: self.return_book(book),
                width=150,
                height=35,
                fg_color="#2196f3",
                hover_color="#1976d2"
            )
            return_button.grid(row=0, column=2, rowspan=4, padx=15, pady=10, sticky="e")
        else:
            # Return date for past borrows
            return_date = book['return_date'].strftime('%Y-%m-%d') if book['return_date'] else "N/A"
            date_label = ctk.CTkLabel(
                card_frame,
                text=f"Returned: {return_date}",
                font=("Arial", 12),
                text_color="#777"
            )
            date_label.grid(row=2, column=1, padx=15, pady=(5, 0), sticky="w")
            
            # Due date for context
            due_date = book['due_date'].strftime('%Y-%m-%d') if book['due_date'] else "N/A"
            status_label = ctk.CTkLabel(
                card_frame,
                text=f"Due date was: {due_date}",
                font=("Arial", 12),
                text_color="#777"
            )
            status_label.grid(row=3, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="w")
        
        # Configure grid
        card_frame.grid_columnconfigure(2, weight=1)
        
    def return_book(self, book):
        """Handle the process of returning a book."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Get today's date
            return_date = datetime.now()
            
            # Update the borrowed_books record with return date
            cursor.execute(
                "UPDATE borrowed_books SET return_date = %s WHERE borrow_id = %s",
                (return_date, book['borrow_id'])
            )
            
            # Update the book's available copies
            cursor.execute(
                "UPDATE books SET available_copies = available_copies + 1 WHERE book_id = %s",
                (book['book_id'],)
            )
            
            # Check if the book is overdue and create a fine if needed
            if book['due_date'] and return_date.date() > book['due_date'].date():
                days_overdue = (return_date.date() - book['due_date'].date()).days
                fine_amount = days_overdue * 0.50  # $0.50 per day overdue
                
                cursor.execute(
                    "INSERT INTO fines (user_id, borrow_id, amount, paid) VALUES (%s, %s, %s, FALSE)",
                    (self.user_id, book['borrow_id'], fine_amount)
                )
                
                conn.commit()
                cursor.close()
                conn.close()
                
                # Show message with fine information
                CTkMessagebox(
                    title="Book Returned with Fine",
                    message=f"Book returned successfully, but it was {days_overdue} days overdue. A fine of ${fine_amount:.2f} has been added to your account.",
                    icon="warning"
                )
            else:
                conn.commit()
                cursor.close()
                conn.close()
                
                # Show success message
                CTkMessagebox(
                    title="Book Returned",
                    message="Book returned successfully!",
                    icon="check"
                )
            
            # Reload the borrowed books list
            self.load_borrowed_books()
            
        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"Error returning book: {err}", icon="error")


class FinesFrame(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.user_id = user_id
        self.configure(fg_color="#f0f0f0")
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Fines & Payments",
            font=("Arial", 24, "bold"),
            text_color="#25a249"
        )
        self.title_label.pack(pady=(20, 5))
        
        # Total fines display
        self.total_fines_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.total_fines_frame.pack(pady=10, padx=20, fill="x")
        
        self.total_fines_label = ctk.CTkLabel(
            self.total_fines_frame,
            text="Loading...",
            font=("Arial", 16, "bold"),
            text_color="#f44336"
        )
        self.total_fines_label.pack(pady=10)
        
        self.pay_all_button = ctk.CTkButton(
            self.total_fines_frame,
            text="Pay All Fines",
            command=self.pay_all_fines,
            width=150,
            height=35,
            fg_color="#f44336",
            hover_color="#d32f2f"
        )
        self.pay_all_button.pack(pady=10)
        
        # Create tabs for pending and paid fines
        self.tabs_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tabs_frame.pack(fill="x", padx=20, pady=5)
        
        self.pending_tab_button = ctk.CTkButton(
            self.tabs_frame,
            text="Pending Fines",
            command=lambda: self.show_tab("pending"),
            width=150,
            height=35,
            fg_color="#25a249",
            hover_color="#1e8138"
        )
        self.pending_tab_button.pack(side="left", padx=5)
        
        self.paid_tab_button = ctk.CTkButton(
            self.tabs_frame,
            text="Payment History",
            command=lambda: self.show_tab("paid"),
            width=150,
            height=35,
            fg_color="#dddddd",
            hover_color="#bbbbbb",
            text_color="black"
        )
        self.paid_tab_button.pack(side="left", padx=5)
        
        # Create frames for each tab
        self.pending_frame = ctk.CTkScrollableFrame(
            self,
            width=800,
            height=400,
            fg_color="white",
            corner_radius=10
        )
        
        self.paid_frame = ctk.CTkScrollableFrame(
            self,
            width=800,
            height=400,
            fg_color="white",
            corner_radius=10
        )
        
        # Initially show pending fines
        self.pending_frame.pack(expand=True, fill="both", padx=20, pady=10)
        self.current_tab = "pending"
        
        # Load fines data
        self.load_fines()
        
    def show_tab(self, tab_name):
        """Switch between pending and paid tabs."""
        if tab_name == self.current_tab:
            return
            
        if tab_name == "pending":
            self.paid_frame.pack_forget()
            self.pending_frame.pack(expand=True, fill="both", padx=20, pady=10)
            self.pending_tab_button.configure(fg_color="#25a249", text_color="white")
            self.paid_tab_button.configure(fg_color="#dddddd", text_color="black")
        else:  # tab_name == "paid"
            self.pending_frame.pack_forget()
            self.paid_frame.pack(expand=True, fill="both", padx=20, pady=10)
            self.pending_tab_button.configure(fg_color="#dddddd", text_color="black")
            self.paid_tab_button.configure(fg_color="#25a249", text_color="white")
            
        self.current_tab = tab_name
        
    def load_fines(self):
        """Load fines data from the database."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            
            # Get total unpaid fines
            cursor.execute(
                "SELECT SUM(amount) AS total FROM fines WHERE user_id = %s AND paid = FALSE",
                (self.user_id,)
            )
            result = cursor.fetchone()
            total_unpaid = result['total'] if result and result['total'] else 0.00
            
            # Update total fines display
            self.total_fines_label.configure(
                text=f"Total Pending Fines: ${total_unpaid:.2f}"
            )
            
            # Disable pay all button if no fines
            if total_unpaid <= 0:
                self.pay_all_button.configure(state="disabled")
            else:
                self.pay_all_button.configure(state="normal")
            
            # Get pending fines with book details
            cursor.execute("""
                SELECT f.fine_id, f.amount, f.borrow_id, 
                       b.title, bb.due_date, bb.return_date
                FROM fines f
                JOIN borrowed_books bb ON f.borrow_id = bb.borrow_id
                JOIN books b ON bb.book_id = b.book_id
                WHERE f.user_id = %s AND f.paid = FALSE
                ORDER BY f.fine_id DESC
            """, (self.user_id,))
            pending_fines = cursor.fetchall()
            
            # Get paid fines with book details
            cursor.execute("""
                SELECT f.fine_id, f.amount, f.borrow_id, f.payment_date,
                       b.title, bb.due_date, bb.return_date
                FROM fines f
                JOIN borrowed_books bb ON f.borrow_id = bb.borrow_id
                JOIN books b ON bb.book_id = b.book_id
                WHERE f.user_id = %s AND f.paid = TRUE
                ORDER BY f.payment_date DESC
            """, (self.user_id,))
            paid_fines = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Clear existing items
            for widget in self.pending_frame.winfo_children():
                widget.destroy()
                
            for widget in self.paid_frame.winfo_children():
                widget.destroy()
                
            # Display pending fines
            if pending_fines:
                self.create_header_row(self.pending_frame, include_payment_date=False)
                for i, fine in enumerate(pending_fines):
                    self.create_fine_row(self.pending_frame, fine, i, is_pending=True)
            else:
                no_fines_label = ctk.CTkLabel(
                    self.pending_frame,
                    text="You have no pending fines.",
                    font=("Arial", 14),
                    text_color="#777"
                )
                no_fines_label.pack(pady=50)
                
            # Display paid fines
            if paid_fines:
                self.create_header_row(self.paid_frame, include_payment_date=True)
                for i, fine in enumerate(paid_fines):
                    self.create_fine_row(self.paid_frame, fine, i, is_pending=False)
            else:
                no_history_label = ctk.CTkLabel(
                    self.paid_frame,
                    text="You have no payment history.",
                    font=("Arial", 14),
                    text_color="#777"
                )
                no_history_label.pack(pady=50)
                
        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"Error loading fines: {err}", icon="error")
            
    def create_header_row(self, parent, include_payment_date):
        """Create a header row for the fines table."""
        header_frame = ctk.CTkFrame(parent, fg_color="#f5f5f5", corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=(0, 5))
        
        columns = ["Book Title", "Due Date", "Return Date", "Amount"]
        if include_payment_date:
            columns.append("Payment Date")
        if not include_payment_date:  # Add action column for pending fines
            columns.append("Action")
            
        for i, column in enumerate(columns):
            header_label = ctk.CTkLabel(
                header_frame,
                text=column,
                font=("Arial", 12, "bold"),
                text_color="#333"
            )
            header_label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
            
        # Configure grid
        for i in range(len(columns)):
            header_frame.grid_columnconfigure(i, weight=1)
            
    def create_fine_row(self, parent, fine, index, is_pending):
        """Create a row for a fine in the table."""
        row_bg = "#f9f9f9" if index % 2 == 0 else "white"
        
        row_frame = ctk.CTkFrame(parent, fg_color=row_bg, corner_radius=0)
        row_frame.pack(fill="x", padx=0, pady=0)
        
        # Book title
        title_label = ctk.CTkLabel(
            row_frame,
            text=fine['title'],
            font=("Arial", 12),
            text_color="#333"
        )
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Due date
        due_date = fine['due_date'].strftime('%Y-%m-%d') if fine['due_date'] else "N/A"
        due_label = ctk.CTkLabel(
            row_frame,
            text=due_date,
            font=("Arial", 12),
            text_color="#333"
        )
        due_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Return date
        return_date = fine['return_date'].strftime('%Y-%m-%d') if fine['return_date'] else "N/A"
        return_label = ctk.CTkLabel(
            row_frame,
            text=return_date,
            font=("Arial", 12),
            text_color="#333"
        )
        return_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        # Amount
        amount_label = ctk.CTkLabel(
            row_frame,
            text=f"${fine['amount']:.2f}",
            font=("Arial", 12, "bold"),
            text_color="#f44336" if is_pending else "#333"
        )
        amount_label.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        if is_pending:
            # Pay button for pending fines
            pay_button = ctk.CTkButton(
                row_frame,
                text="Pay",
                command=lambda: self.pay_fine(fine['fine_id']),
                width=80,
                height=30,
                fg_color="#25a249",
                hover_color="#1e8138"
            )
            pay_button.grid(row=0, column=4, padx=10, pady=10, sticky="w")
        else:
            # Payment date for paid fines
            payment_date = fine['payment_date'].strftime('%Y-%m-%d') if fine['payment_date'] else "N/A"
            payment_label = ctk.CTkLabel(
                row_frame,
                text=payment_date,
                font=("Arial", 12),
                text_color="#4caf50"
            )
            payment_label.grid(row=0, column=4, padx=10, pady=10, sticky="w")
            
        # Configure grid
        for i in range(5):
            row_frame.grid_columnconfigure(i, weight=1)
            
    def pay_fine(self, fine_id):
        """Handle payment for a single fine."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Update fine as paid with payment date
            cursor.execute(
                "UPDATE fines SET paid = TRUE, payment_date = %s WHERE fine_id = %s",
                (datetime.now(), fine_id)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            CTkMessagebox(
                title="Payment Successful",
                message="Your fine has been paid successfully.",
                icon="check"
            )
            
            # Reload fines data
            self.load_fines()
            
        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"Error processing payment: {err}", icon="error")
    
    def pay_all_fines(self):
        """Handle payment for all pending fines."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Get total unpaid fines
            cursor.execute(
                "SELECT SUM(amount) AS total FROM fines WHERE user_id = %s AND paid = FALSE",
                (self.user_id,)
            )
            result = cursor.fetchone()
            total_unpaid = result[0] if result and result[0] else 0.00
            
            if total_unpaid <= 0:
                CTkMessagebox(
                    title="No Fines",
                    message="You don't have any pending fines to pay.",
                    icon="info"
                )
                cursor.close()
                conn.close()
                return
                
            # Confirm payment
            confirm = CTkMessagebox(
                title="Confirm Payment",
                message=f"Are you sure you want to pay all your fines (${total_unpaid:.2f})?",
                icon="question",
                option_1="Yes",
                option_2="No"
            )
            
            if confirm.get() != "Yes":
                cursor.close()
                conn.close()
                return
                
            # Update all fines as paid
            payment_date = datetime.now()
            cursor.execute(
                "UPDATE fines SET paid = TRUE, payment_date = %s WHERE user_id = %s AND paid = FALSE",
                (payment_date, self.user_id)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            CTkMessagebox(
                title="Payment Successful",
                message=f"All your fines (${total_unpaid:.2f}) have been paid successfully.",
                icon="check"
            )
            
            # Reload fines data
            self.load_fines()
            
        except mysql.connector.Error as err:
            CTkMessagebox(title="Database Error", message=f"Error processing payment: {err}", icon="error")
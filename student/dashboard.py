import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import subprocess
import os
from datetime import datetime
from utils import connect_db, load_user_session, clear_user_session, format_date, is_overdue, calculate_fine

# ------------------- Dashboard Functions -------------------
def get_user_summary(user_id):
    """Get summary data for dashboard"""
    connection = connect_db()
    if not connection:
        return {"books_borrowed": 0, "due_books": 0, "pending_fines": "$0.00"}
    
    try:
        cursor = connection.cursor()
        
        # Get count of borrowed books
        cursor.execute(
            "SELECT COUNT(*) FROM Loans WHERE user_id = %s AND return_date IS NULL", 
            (user_id,)
        )
        books_borrowed = cursor.fetchone()[0]
        
        # Get count of overdue books
        cursor.execute(
            "SELECT COUNT(*) FROM Loans WHERE user_id = %s AND return_date IS NULL AND due_date < CURDATE()", 
            (user_id,)
        )
        due_books = cursor.fetchone()[0]
        
        # Get sum of unpaid fines
        cursor.execute("""
            SELECT COALESCE(SUM(f.amount), 0) 
            FROM Fines f
            JOIN Loans l ON f.loan_id = l.loan_id
            WHERE l.user_id = %s AND f.paid = 0
        """, (user_id,))
        pending_fines = cursor.fetchone()[0]
        
        print(f"User summary loaded: {books_borrowed} books, {due_books} overdue, ${pending_fines:.2f} in fines")
        
        return {
            "books_borrowed": books_borrowed,
            "due_books": due_books,
            "pending_fines": f"${pending_fines:.2f}"
        }
    except Exception as err:
        print(f"Error getting user summary: {err}")
        return {"books_borrowed": 0, "due_books": 0, "pending_fines": "$0.00"}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_user_borrowed_books(user_id):
    """Get all books borrowed by a user"""
    connection = connect_db()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                l.loan_id,
                b.book_id, 
                b.title, 
                b.author, 
                l.loan_date, 
                l.due_date,
                l.return_date
            FROM 
                Books b
            JOIN 
                Loans l ON b.book_id = l.book_id
            WHERE 
                l.user_id = %s AND
                l.return_date IS NULL
            ORDER BY 
                l.due_date
        """, (user_id,))
        
        results = cursor.fetchall()
        print(f"Borrowed books: {len(results)} books found for user {user_id}")
        return results
    except Exception as err:
        print(f"Error getting borrowed books: {err}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def search_books(query=""):
    """Search for books based on query, or get all books if query is empty"""
    connection = connect_db()
    if not connection:
        print("Database connection failed in search_books")
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        if query and len(query.strip()) > 0:
            # Search with filter
            search_query = f"%{query}%"
            
            cursor.execute("""
                SELECT 
                    b.book_id, 
                    b.title, 
                    b.author, 
                    b.isbn,
                    b.publication_year,
                    b.genre,
                    b.available_copies
                FROM 
                    Books b
                WHERE 
                    b.title LIKE %s OR 
                    b.author LIKE %s OR 
                    b.genre LIKE %s OR
                    b.isbn LIKE %s
                ORDER BY 
                    b.title
            """, (search_query, search_query, search_query, search_query))
        else:
            # Get all books
            cursor.execute("""
                SELECT 
                    b.book_id, 
                    b.title, 
                    b.author, 
                    b.isbn,
                    b.publication_year,
                    b.genre,
                    b.available_copies
                FROM 
                    Books b
                ORDER BY 
                    b.title
                LIMIT 20
            """)
        
        results = cursor.fetchall()
        print(f"Search results: {len(results)} books found")
        return results
    except Exception as err:
        print(f"Error in search_books: {err}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def return_book(loan_id, user_id):
    """Return a borrowed book"""
    connection = connect_db()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # First get the book_id for this loan to update available copies
        cursor.execute("SELECT book_id, due_date FROM Loans WHERE loan_id = %s", (loan_id,))
        result = cursor.fetchone()
        
        if not result:
            print(f"No loan found with ID {loan_id}")
            return False
        
        book_id, due_date = result
        
        # Update loan return date
        cursor.execute(
            "UPDATE Loans SET return_date = CURDATE() WHERE loan_id = %s AND user_id = %s", 
            (loan_id, user_id)
        )
        
        # Check if any rows were affected
        if cursor.rowcount == 0:
            print(f"No rows updated for loan {loan_id}")
            return False
        
        # Increment available copies
        cursor.execute(
            "UPDATE Books SET available_copies = available_copies + 1 WHERE book_id = %s", 
            (book_id,)
        )
        
        # Check if the book is overdue and create fine if needed
        if is_overdue(due_date):
            from datetime import datetime, timedelta
            
            days_overdue = (datetime.now() - due_date).days if isinstance(due_date, datetime) else \
                          (datetime.now() - datetime.strptime(str(due_date), '%Y-%m-%d')).days
                          
            fine_amount = days_overdue * 0.50  # $0.50 per day
            
            # Create fine record
            cursor.execute(
                "INSERT INTO Fines (loan_id, amount, description, paid) VALUES (%s, %s, %s, 0)",
                (loan_id, fine_amount, f"Late return fine: {days_overdue} days")
            )
        
        connection.commit()
        return True
    except Exception as err:
        print(f"Error returning book: {err}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
# ------------------- Library User Dashboard Class -------------------
class LibraryApp:
    def __init__(self, root, start_page=None):
        self.root = root
        self.root.title("Library Management System - User Dashboard")
        self.root.geometry("1200x700")
        
        # Set appearance mode and default color theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        
        # Load user session
        self.user = load_user_session()
        if not self.user:
            messagebox.showerror("Session Error", "No active user session found.")
            self.logout()
            return
        
        print(f"User session loaded successfully: {self.user['first_name']} {self.user['last_name']}")
        
        # Initialize frames dictionary to keep track of different pages
        self.frames = {}
        
        # Create main grid layout
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Show appropriate start page
        if start_page == "borrowed":
            self.show_borrowed_books()
        elif start_page == "fines":
            self.show_fines()
        elif start_page == "profile":
            self.show_profile()
        else:
            # By default, show dashboard
            self.show_dashboard()
    
    def run_browse_script(self):
        """Run the browse.py script"""
        self.root.destroy()
        from student.browse import run_browse
        run_browse()
    
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
        self.menu_buttons = {}
        menu_items = [
            ("🏠 Dashboard", self.show_dashboard),
            ("🔍 Search Books", self.run_browse_script),
            ("📖 My Borrowed Books", self.show_borrowed_books),
            ("💰 Fines & Fees", self.show_fines),
            ("👤 My Profile", self.show_profile),
            ("🚪 Logout", self.logout)
        ]

        for text, command in menu_items:
            button = ctk.CTkButton(sidebar, text=text, font=ctk.CTkFont(size=12), 
                                  fg_color="transparent", text_color="white", anchor="w",
                                  hover_color="#0d4f29", corner_radius=0, height=40,
                                  command=command)
            button.pack(fill="x", pady=2)
            self.menu_buttons[text] = button
    
    def highlight_active_menu(self, active_text):
        """Highlight the active menu button"""
        for text, button in self.menu_buttons.items():
            if text == active_text:
                button.configure(fg_color="#0d4f29")
            else:
                button.configure(fg_color="transparent")
    
    def create_main_content(self):
        """Create the main content area"""
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#f0f5f0", corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
    
    def clear_main_frame(self):
        """Clear all widgets from the main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    # ------------------- Page Navigation -------------------
    def show_dashboard(self):
        """Show the dashboard page"""
        print("Loading dashboard...")
        self.clear_main_frame()
        self.highlight_active_menu("🏠 Dashboard")
        
        # Dashboard Title
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        dash_title = ctk.CTkLabel(title_frame, text="Your Library Dashboard", 
                                 font=ctk.CTkFont(size=20, weight="bold"))
        dash_title.pack(pady=10)

        # Separator line
        separator_frame = ctk.CTkFrame(self.main_frame, height=1, fg_color="#d1d1d1")
        separator_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        # Get user summary data
        summary_data = get_user_summary(self.user['user_id'])
        
        # Dashboard Summary Boxes
        summary_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        summary_frame.grid(row=2, column=0, sticky="ew", pady=20)
        summary_frame.grid_columnconfigure(0, weight=1)
        summary_frame.grid_columnconfigure(1, weight=1)
        summary_frame.grid_columnconfigure(2, weight=1)

        summary_boxes = [
            ("Books Borrowed", str(summary_data["books_borrowed"])),
            ("Due Books", str(summary_data["due_books"])),
            ("Pending Fines", summary_data["pending_fines"])
        ]

        for i, (title, value) in enumerate(summary_boxes):
            box_frame = ctk.CTkFrame(summary_frame, fg_color="white", border_width=1, border_color="#d1d1d1", corner_radius=5)
            box_frame.grid(row=0, column=i, padx=10, sticky="nsew", ipadx=15, ipady=15)
            
            summary_title = ctk.CTkLabel(box_frame, text=title, font=ctk.CTkFont(size=12))
            summary_title.pack(anchor="center")
            
            # Make the value red if it's a positive number of due books or a non-zero fine
            text_color = "#d9534f" if ((title == "Due Books" and value != "0") or 
                                      (title == "Pending Fines" and value != "$0.00")) else "black"
            
            summary_value = ctk.CTkLabel(box_frame, text=value, 
                                        font=ctk.CTkFont(size=24, weight="bold"),
                                        text_color=text_color)
            summary_value.pack(anchor="center", pady=10)

        # Quick Search Box
        search_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        search_frame.grid(row=3, column=0, sticky="ew", pady=10)

        search_label = ctk.CTkLabel(search_frame, text="🔍 Quick Search", 
                                   font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
        search_label.pack(anchor="w", pady=(10, 5))

        search_entry_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_entry_frame.pack(fill="x")

        search_entry = ctk.CTkEntry(search_entry_frame, placeholder_text="Enter book title, author, or genre", 
                                   font=ctk.CTkFont(size=12), height=35, border_width=1, border_color="#d1d1d1")
        search_entry.pack(side="left", fill="x", expand=True)

        search_button = ctk.CTkButton(search_entry_frame, text="🔍 Search", font=ctk.CTkFont(size=12), 
                                     fg_color="#116636", hover_color="#0d4f29", corner_radius=3, height=35,
                                     command=lambda: self.show_search_results(search_entry.get()))
        search_button.pack(side="left", padx=(10, 0))
        
        # Bind Enter key to search function
        search_entry.bind("<Return>", lambda event: self.show_search_results(search_entry.get()))
        
        # Get borrowed books for the preview section
        borrowed_books = get_user_borrowed_books(self.user['user_id'])
        
        # Recent Borrowed Books Section
        books_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        books_frame.grid(row=4, column=0, sticky="nsew", pady=10)
        books_frame.grid_rowconfigure(1, weight=1)
        books_frame.grid_columnconfigure(0, weight=1)

        books_label = ctk.CTkLabel(books_frame, text="📚 Recent Borrowed Books", 
                                  font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
        books_label.grid(row=0, column=0, sticky="w", pady=(20, 10))
        
        # Button to view all borrowed books
        view_all_button = ctk.CTkButton(books_frame, text="View All", font=ctk.CTkFont(size=12), 
                                      fg_color="#116636", hover_color="#0d4f29", corner_radius=3, height=30,
                                      command=self.show_borrowed_books)
        view_all_button.grid(row=0, column=1, sticky="e", pady=(20, 10))

        # Custom styling for ttk.Treeview
        style = ttk.Style()
        style.theme_use("clam")  # Use clam theme as base
        style.configure("Treeview", background="white", fieldbackground="white", foreground="black")
        style.configure("Treeview.Heading", background="#f0f0f0", foreground="black", font=("Arial", 10, "bold"))
        style.map("Treeview", background=[("selected", "#116636")], foreground=[("selected", "white")])

        # Create the treeview with columns
        columns = ("Title", "Author", "Due Date", "Status", "Action")
        borrowed_books_tree = ttk.Treeview(books_frame, columns=columns, show="headings", height=5)
        borrowed_books_tree.grid(row=1, column=0, columnspan=2, sticky="nsew")

        # Configure columns
        borrowed_books_tree.column("Title", width=250, anchor="w")
        borrowed_books_tree.column("Author", width=200, anchor="w")
        borrowed_books_tree.column("Due Date", width=100, anchor="center")
        borrowed_books_tree.column("Status", width=100, anchor="center")
        borrowed_books_tree.column("Action", width=150, anchor="center")

        # Configure column headings
        for col in columns:
            borrowed_books_tree.heading(col, text=col)

        # Add data and store loan_ids
        self.dashboard_loan_ids = {}
        
        if borrowed_books:
            for book in borrowed_books[:5]:  # Show max 5 books
                due_date = book['due_date'].strftime('%Y-%m-%d') if isinstance(book['due_date'], datetime) else str(book['due_date'])
                
                status = "Overdue" if is_overdue(due_date) else "On Time"
                status_text = status
                
                item_id = borrowed_books_tree.insert("", "end", values=(
                    book['title'], 
                    book['author'], 
                    format_date(due_date), 
                    status_text,
                    ""
                ))
                
                self.dashboard_loan_ids[item_id] = book['loan_id']
            
            
            def on_return_click(tree_item):
                loan_id = self.dashboard_loan_ids.get(tree_item)
                if loan_id:
                    if return_book(loan_id, self.user['user_id']):
                        messagebox.showinfo("Success", "Book returned successfully!")
                        self.show_dashboard()  # Refresh dashboard
                    else:
                        messagebox.showerror("Error", "Failed to return book.")
            
            def create_return_buttons():
                for item in borrowed_books_tree.get_children():
                    bbox = borrowed_books_tree.bbox(item, column="Action")
                    if bbox:
                        button_frame = ctk.CTkFrame(borrowed_books_tree, fg_color="transparent")
                        button_frame.place(x=bbox[0] + 30, y=bbox[1])
                        
                        return_button = ctk.CTkButton(
                            button_frame, 
                            text="↩ Return", 
                            fg_color="#116636", 
                            hover_color="#0d4f29",
                            corner_radius=3, 
                            width=80, 
                            height=25, 
                            font=ctk.CTkFont(size=10),
                            command=lambda i=item: on_return_click(i)
                        )
                        return_button.pack()
            
            # Schedule creation of buttons after treeview is ready
            self.root.after(100, create_return_buttons)
        else:
            # No borrowed books message
            no_books_message = borrowed_books_tree.insert("", "end", values=(
                "You haven't borrowed any books yet.", "", "", "", ""
            ))
            
    def show_search_results(self, query):
        """Switch to the browse page with the search query"""
        self.root.destroy()
        from student.browse import run_browse_with_search
        run_browse_with_search(query)
    
    def show_borrowed_books(self):
        """Show the borrowed books page"""
        self.root.destroy()
        from student.borrowed import run_borrowed
        run_borrowed()
    
    def show_fines(self):
        """Show the fines page"""
        self.root.destroy()
        from student.fines import run_fines
        run_fines()
    
    def show_profile(self):
        """Show the profile page"""
        self.root.destroy()
        from student.profile import run_profile
        run_profile()
    
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
            print(f"Error during logout: {e}")
            messagebox.showerror("Error", f"Failed to logout: {e}")
            self.root.destroy()

# ------------------- Run Dashboard Function -------------------
def run_dashboard():
    """Run the dashboard application"""
    root = ctk.CTk()
    app = LibraryApp(root)
    root.mainloop()

# ------------------- Main Execution -------------------
if __name__ == "__main__":
    run_dashboard()
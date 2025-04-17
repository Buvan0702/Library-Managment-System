import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime

from utils import connect_db

def get_books(search_term=""):
    """Get all books with optional search"""
    connection = connect_db()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        if search_term:
            query = """
                SELECT 
                    book_id, title, author, genre, isbn, publication_year, 
                    available_copies, total_copies, 
                    (total_copies - available_copies) AS borrowed_copies
                FROM 
                    Books
                WHERE 
                    title LIKE %s OR author LIKE %s OR genre LIKE %s OR isbn LIKE %s
                ORDER BY 
                    title
            """
            search_param = f"%{search_term}%"
            cursor.execute(query, (search_param, search_param, search_param, search_param))
        else:
            query = """
                SELECT 
                    book_id, title, author, genre, isbn, publication_year, 
                    available_copies, total_copies, 
                    (total_copies - available_copies) AS borrowed_copies
                FROM 
                    Books
                ORDER BY 
                    title
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

def add_book(title, author, genre, isbn, publication_year, total_copies, description=""):
    """Add a new book"""
    connection = connect_db()
    if not connection:
        return False, "Database connection failed"
    
    try:
        cursor = connection.cursor()
        
        # Check if book with same ISBN already exists
        cursor.execute("SELECT book_id FROM Books WHERE isbn = %s", (isbn,))
        if cursor.fetchone():
            return False, "A book with this ISBN already exists"
        
        # Insert the new book
        cursor.execute(
            """
            INSERT INTO Books (
                title, author, genre, isbn, publication_year, 
                total_copies, available_copies, description
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (title, author, genre, isbn, publication_year, total_copies, total_copies, description)
        )
        
        connection.commit()
        return True, "Book added successfully"
    except Exception as err:
        return False, f"Database Error: {err}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_book(book_id, title, author, genre, isbn, publication_year, total_copies, description=""):
    """Update an existing book"""
    connection = connect_db()
    if not connection:
        return False, "Database connection failed"
    
    try:
        cursor = connection.cursor()
        
        # Check if book exists
        cursor.execute("SELECT available_copies FROM Books WHERE book_id = %s", (book_id,))
        result = cursor.fetchone()
        if not result:
            return False, "Book not found"
        
        available_copies = result[0]
        
        # Calculate new available copies
        borrowed_copies = total_copies - available_copies
        new_available = max(0, total_copies - borrowed_copies)
        
        # Update the book
        cursor.execute(
            """
            UPDATE Books SET 
                title = %s, author = %s, genre = %s, isbn = %s, 
                publication_year = %s, total_copies = %s, 
                available_copies = %s, description = %s
            WHERE book_id = %s
            """,
            (title, author, genre, isbn, publication_year, 
             total_copies, new_available, description, book_id)
        )
        
        connection.commit()
        return True, "Book updated successfully"
    except Exception as err:
        return False, f"Database Error: {err}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def delete_book(book_id):
    """Delete a book"""
    connection = connect_db()
    if not connection:
        return False, "Database connection failed"
    
    try:
        cursor = connection.cursor()
        
        # Check if book is currently borrowed
        cursor.execute(
            "SELECT COUNT(*) FROM Loans WHERE book_id = %s AND return_date IS NULL", 
            (book_id,)
        )
        
        if cursor.fetchone()[0] > 0:
            return False, "Cannot delete book: it is currently borrowed by users"
        
        # Delete the book
        cursor.execute("DELETE FROM Books WHERE book_id = %s", (book_id,))
        
        connection.commit()
        return True, "Book deleted successfully"
    except Exception as err:
        return False, f"Database Error: {err}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# ------------------- UI Functions -------------------
def show_books_management(content_frame):
    """Show the book management page in the provided content frame"""
    # Clear content area
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    # Create book management title
    title = ctk.CTkLabel(
        content_frame, 
        text="Book Management",
        font=ctk.CTkFont(size=24, weight="bold"),
        anchor="w"
    )
    title.pack(anchor="w", padx=30, pady=(20, 10))
    
    # Search and Add Book Bar
    action_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    action_frame.pack(fill="x", padx=30, pady=(10, 20))
    
    # Search box
    search_var = tk.StringVar()
    search_entry = ctk.CTkEntry(
        action_frame,
        width=400,
        height=40,
        placeholder_text="Search by title, author, genre or ISBN",
        textvariable=search_var
    )
    search_entry.pack(side="left")
    
    def perform_search():
        search_term = search_var.get()
        populate_books_table(books_tree, search_term)
    
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
    
    # Add New Book Button
    add_button = ctk.CTkButton(
        action_frame,
        text="+ Add New Book",
        width=150,
        height=40,
        fg_color="#2196f3",
        hover_color="#1976d2",
        command=lambda: show_book_form(content_frame, books_tree)
    )
    add_button.pack(side="right")
    
    # Bind Enter key to search
    search_entry.bind("<Return>", lambda event: perform_search())
    
    # Books Table
    table_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
    
    # Create scrollable table
    # Style for treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="white", fieldbackground="white", foreground="black")
    style.configure("Treeview.Heading", background="#f0f0f0", foreground="black", font=("Arial", 10, "bold"))
    style.map("Treeview", background=[("selected", "#116636")], foreground=[("selected", "white")])
    
    # Table columns
    books_columns = ("ID", "Title", "Author", "Genre", "ISBN", "Year", "Available", "Total", "Actions")
    
    # Create treeview
    books_tree = ttk.Treeview(
        table_frame, 
        columns=books_columns, 
        show="headings", 
        height=20,
        selectmode="browse"
    )
    books_tree.pack(side="left", fill="both", expand=True)
    
    # Add a scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=books_tree.yview)
    scrollbar.pack(side="right", fill="y")
    books_tree.configure(yscrollcommand=scrollbar.set)
    
    # Configure column widths and headings
    column_widths = {
        "ID": 50,
        "Title": 250,
        "Author": 150,
        "Genre": 100,
        "ISBN": 100,
        "Year": 60,
        "Available": 70,
        "Total": 60,
        "Actions": 120
    }
    
    for col in books_columns:
        books_tree.heading(col, text=col)
        books_tree.column(col, width=column_widths.get(col, 100), anchor="w" if col != "Actions" else "center")
    
    # Initial load of books
    populate_books_table(books_tree)

def populate_books_table(books_tree, search_term=""):
    """Populate the books table with data"""
    # Clear existing data
    for item in books_tree.get_children():
        books_tree.delete(item)
    
    # Get books data
    books = get_books(search_term)
    
    # Insert books into table
    for book in books:
        item_id = books_tree.insert("", "end", values=(
            book['book_id'],
            book['title'],
            book['author'],
            book['genre'],
            book['isbn'],
            book['publication_year'],
            book['available_copies'],
            book['total_copies'],
            ""  # Actions column will be filled with buttons
        ))
        
    # Add buttons to the Actions column
    add_book_action_buttons(books_tree)

def add_book_action_buttons(books_tree):
    """Add edit and delete buttons to the books table"""
    for item in books_tree.get_children():
        # Get the book ID
        book_id = books_tree.item(item, 'values')[0]
        
        # Get bounding box for action column
        col_idx = 8  # "Actions" column index
        bbox = books_tree.bbox(item, column=col_idx)
        
        if bbox:  # If visible
            # Create a frame for the buttons
            button_frame = ctk.CTkFrame(books_tree, fg_color="transparent")
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
                command=lambda b_id=book_id: show_book_form(books_tree.master.master, books_tree, b_id)
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
                command=lambda b_id=book_id: confirm_delete_book(books_tree, b_id)
            )
            delete_button.pack(side="left")

def show_book_form(content_frame, books_tree, book_id=None):
    """Show form to add or edit a book"""
    # Create a dialog window
    dialog = ctk.CTkToplevel(content_frame)
    dialog.title("Add New Book" if book_id is None else "Edit Book")
    dialog.geometry("600x550")
    dialog.resizable(False, False)
    dialog.grab_set()  # Make it modal
    
    # Center the dialog on screen
    dialog_x = content_frame.winfo_rootx() + (content_frame.winfo_width() // 2) - 300
    dialog_y = content_frame.winfo_rooty() + (content_frame.winfo_height() // 2) - 275
    dialog.geometry(f"+{dialog_x}+{dialog_y}")
    
    # Book data (empty for new, populated for edit)
    book_data = {}
    if book_id:
        # Fetch book data for editing
        books = get_books()
        for book in books:
            if str(book['book_id']) == str(book_id):
                book_data = book
                break
    
    # Form frame
    form_frame = ctk.CTkFrame(dialog)
    form_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    form_title = ctk.CTkLabel(
        form_frame,
        text="Add New Book" if book_id is None else "Edit Book",
        font=ctk.CTkFont(size=20, weight="bold")
    )
    form_title.pack(pady=(0, 20))
    
    # Input fields frame
    input_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    input_frame.pack(fill="x", pady=10)
    
    # Configure grid
    input_frame.grid_columnconfigure(1, weight=1)
    
    # Title field
    ctk.CTkLabel(input_frame, text="Title:", anchor="e", width=100).grid(row=0, column=0, padx=(20, 10), pady=10, sticky="e")
    title_entry = ctk.CTkEntry(input_frame, width=400, height=30)
    title_entry.grid(row=0, column=1, padx=(0, 20), pady=10, sticky="ew")
    if 'title' in book_data:
        title_entry.insert(0, book_data['title'])
    
    # Author field
    ctk.CTkLabel(input_frame, text="Author:", anchor="e", width=100).grid(row=1, column=0, padx=(20, 10), pady=10, sticky="e")
    author_entry = ctk.CTkEntry(input_frame, width=400, height=30)
    author_entry.grid(row=1, column=1, padx=(0, 20), pady=10, sticky="ew")
    if 'author' in book_data:
        author_entry.insert(0, book_data['author'])
    
    # Genre field
    ctk.CTkLabel(input_frame, text="Genre:", anchor="e", width=100).grid(row=2, column=0, padx=(20, 10), pady=10, sticky="e")
    genre_entry = ctk.CTkEntry(input_frame, width=400, height=30)
    genre_entry.grid(row=2, column=1, padx=(0, 20), pady=10, sticky="ew")
    if 'genre' in book_data:
        genre_entry.insert(0, book_data['genre'])
    
    # ISBN field
    ctk.CTkLabel(input_frame, text="ISBN:", anchor="e", width=100).grid(row=3, column=0, padx=(20, 10), pady=10, sticky="e")
    isbn_entry = ctk.CTkEntry(input_frame, width=400, height=30)
    isbn_entry.grid(row=3, column=1, padx=(0, 20), pady=10, sticky="ew")
    if 'isbn' in book_data:
        isbn_entry.insert(0, book_data['isbn'])
    
    # Publication Year field
    ctk.CTkLabel(input_frame, text="Year:", anchor="e", width=100).grid(row=4, column=0, padx=(20, 10), pady=10, sticky="e")
    year_entry = ctk.CTkEntry(input_frame, width=400, height=30)
    year_entry.grid(row=4, column=1, padx=(0, 20), pady=10, sticky="ew")
    if 'publication_year' in book_data:
        year_entry.insert(0, str(book_data['publication_year']))
    
    # Total Copies field
    ctk.CTkLabel(input_frame, text="Total Copies:", anchor="e", width=100).grid(row=5, column=0, padx=(20, 10), pady=10, sticky="e")
    copies_entry = ctk.CTkEntry(input_frame, width=400, height=30)
    copies_entry.grid(row=5, column=1, padx=(0, 20), pady=10, sticky="ew")
    if 'total_copies' in book_data:
        copies_entry.insert(0, str(book_data['total_copies']))
    
    # Description field
    ctk.CTkLabel(input_frame, text="Description:", anchor="e", width=100).grid(row=6, column=0, padx=(20, 10), pady=10, sticky="ne")
    description_text = ctk.CTkTextbox(input_frame, width=400, height=100)
    description_text.grid(row=6, column=1, padx=(0, 20), pady=10, sticky="ew")
    if 'description' in book_data:
        description_text.insert("1.0", book_data.get('description', ''))
    
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
    def save_book():
        # Validate input
        title = title_entry.get().strip()
        author = author_entry.get().strip()
        genre = genre_entry.get().strip()
        isbn = isbn_entry.get().strip()
        year_str = year_entry.get().strip()
        copies_str = copies_entry.get().strip()
        description = description_text.get("1.0", "end-1c").strip()
        
        # Basic validation
        if not title or not author or not genre or not isbn:
            error_label.configure(text="Title, author, genre and ISBN are required")
            return
        
        try:
            year = int(year_str)
            if year < 1000 or year > datetime.now().year:
                error_label.configure(text=f"Invalid year. Must be between 1000 and {datetime.now().year}")
                return
        except ValueError:
            error_label.configure(text="Year must be a valid number")
            return
        
        try:
            copies = int(copies_str)
            if copies < 1:
                error_label.configure(text="Total copies must be at least 1")
                return
        except ValueError:
            error_label.configure(text="Total copies must be a valid number")
            return
        
        # Save/update the book
        if book_id:  # Update existing book
            success, message = update_book(book_id, title, author, genre, isbn, year, copies, description)
        else:  # Add new book
            success, message = add_book(title, author, genre, isbn, year, copies, description)
        
        if success:
            dialog.destroy()
            populate_books_table(books_tree)  # Refresh the table
            messagebox.showinfo("Success", message)
        else:
            error_label.configure(text=message)
    
    save_button = ctk.CTkButton(
        button_frame,
        text="Save" if book_id is None else "Update",
        font=ctk.CTkFont(size=14),
        fg_color="#116636",
        hover_color="#0d4f29",
        width=100,
        height=35,
        command=save_book
    )
    save_button.pack(side="right", padx=5)

def confirm_delete_book(books_tree, book_id):
    """Show confirmation dialog before deleting a book"""
    # Find book title
    book_title = ""
    for item in books_tree.get_children():
        values = books_tree.item(item, 'values')
        if str(values[0]) == str(book_id):
            book_title = values[1]
            break
    
    result = messagebox.askyesno(
        "Confirm Delete", 
        f"Are you sure you want to delete the book:\n\n{book_title}?\n\nThis action cannot be undone."
    )
    
    if result:
        success, message = delete_book(book_id)
        if success:
            messagebox.showinfo("Success", message)
            populate_books_table(books_tree)  # Refresh the table
        else:
            messagebox.showerror("Error", message)
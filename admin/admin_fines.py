import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime

from utils import connect_db, format_date

def get_all_fines():
    """Get all fines information"""
    connection = connect_db()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                f.fine_id,
                f.loan_id,
                f.amount,
                f.description,
                f.paid,
                f.payment_date,
                b.title,
                u.first_name,
                u.last_name,
                u.email,
                l.due_date,
                l.return_date
            FROM 
                Fines f
            JOIN 
                Loans l ON f.loan_id = l.loan_id
            JOIN 
                Books b ON l.book_id = b.book_id
            JOIN 
                Users u ON l.user_id = u.user_id
            ORDER BY 
                f.paid, f.fine_id DESC
        """)
        
        return cursor.fetchall()
    except Exception as err:
        messagebox.showerror("Database Error", str(err))
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def process_fine_payment(fine_id):
    """Mark a fine as paid"""
    connection = connect_db()
    if not connection:
        return False, "Database connection failed"
    
    try:
        cursor = connection.cursor()
        
        # Check if fine exists and is unpaid
        cursor.execute("SELECT paid FROM Fines WHERE fine_id = %s", (fine_id,))
        result = cursor.fetchone()
        
        if not result:
            return False, "Fine not found"
        
        if result[0] == 1:  # Already paid
            return False, "This fine has already been paid"
        
        # Mark fine as paid
        cursor.execute(
            "UPDATE Fines SET paid = 1, payment_date = CURDATE() WHERE fine_id = %s", 
            (fine_id,)
        )
        
        connection.commit()
        return True, "Fine marked as paid successfully"
    except Exception as err:
        return False, f"Database Error: {err}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def cancel_fine(fine_id):
    """Delete a fine record"""
    connection = connect_db()
    if not connection:
        return False, "Database connection failed"
    
    try:
        cursor = connection.cursor()
        
        # Check if fine exists
        cursor.execute("SELECT fine_id FROM Fines WHERE fine_id = %s", (fine_id,))
        if not cursor.fetchone():
            return False, "Fine not found"
        
        # Delete the fine
        cursor.execute("DELETE FROM Fines WHERE fine_id = %s", (fine_id,))
        
        connection.commit()
        return True, "Fine cancelled successfully"
    except Exception as err:
        return False, f"Database Error: {err}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# ------------------- UI Functions -------------------
def show_fines_management(content_frame):
    """Show the fines management page in the provided content frame"""
    # Clear content area
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    # Create fines management title
    title = ctk.CTkLabel(
        content_frame, 
        text="Fines Management",
        font=ctk.CTkFont(size=24, weight="bold"),
        anchor="w"
    )
    title.pack(anchor="w", padx=30, pady=(20, 20))
    
    # Fines statistics frame
    stats_frame = ctk.CTkFrame(content_frame, fg_color="white", corner_radius=10)
    stats_frame.pack(fill="x", padx=30, pady=(0, 20))
    
    # Get fines info for stats
    all_fines = get_all_fines()
    pending_fines = [f for f in all_fines if not f['paid']]
    total_pending = sum(float(f['amount']) for f in pending_fines)
    
    # Create stats display
    stats_label = ctk.CTkLabel(
        stats_frame,
        text="Outstanding Fines:",
        font=ctk.CTkFont(size=16, weight="bold"),
        anchor="w"
    )
    stats_label.pack(side="left", padx=20, pady=20)
    
    amount_label = ctk.CTkLabel(
        stats_frame,
        text=f"${total_pending:.2f}",
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color="#d32f2f",
        anchor="e"
    )
    amount_label.pack(side="right", padx=20, pady=20)
    
    # Create tabs for different views
    tabview = ctk.CTkTabview(content_frame, height=500)
    tabview.pack(fill="both", expand=True, padx=30, pady=(0, 20))
    
    # Add tabs
    all_tab = tabview.add("All Fines")
    pending_tab = tabview.add("Pending Fines")
    paid_tab = tabview.add("Paid Fines")
    
    # Configure tabs to expand
    for tab in [all_tab, pending_tab, paid_tab]:
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
    
    # Style for treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="white", fieldbackground="white", foreground="black")
    style.configure("Treeview.Heading", background="#f0f0f0", foreground="black", font=("Arial", 10, "bold"))
    style.map("Treeview", background=[("selected", "#116636")], foreground=[("selected", "white")])
    
    # Table columns
    fines_columns = ("ID", "Book", "User", "Email", "Amount", "Description", "Status", "Date", "Actions")
    column_widths = {
        "ID": 50,
        "Book": 200,
        "User": 150,
        "Email": 200,
        "Amount": 80,
        "Description": 200,
        "Status": 80,
        "Date": 100,
        "Actions": 100
    }
    
    # Create tables for each tab
    tables = {}
    
    for tab_name, tab in [("all", all_tab), ("pending", pending_tab), ("paid", paid_tab)]:
        # Create frame for table
        table_frame = ctk.CTkFrame(tab, fg_color="transparent")
        table_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Create treeview
        tree = ttk.Treeview(
            table_frame, 
            columns=fines_columns, 
            show="headings", 
            height=20,
            selectmode="browse"
        )
        tree.pack(side="left", fill="both", expand=True)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Configure column widths and headings
        for col in fines_columns:
            tree.heading(col, text=col)
            tree.column(col, width=column_widths.get(col, 100), anchor="w" if col != "Actions" else "center")
        
        # Store tree in dictionary
        tables[tab_name] = tree
    
    # Populate tables with data
    populate_fines_tables(tables, all_fines)
    
    # Refresh button
    refresh_btn = ctk.CTkButton(
        content_frame,
        text="Refresh Data",
        font=ctk.CTkFont(size=14),
        fg_color="#116636",
        hover_color="#0d4f29",
        width=120,
        height=35,
        command=lambda: refresh_fines_data(tables)
    )
    refresh_btn.place(relx=0.95, rely=0.07, anchor="e")

def populate_fines_tables(tables, fines=None):
    """Populate the fines tables with data"""
    if fines is None:
        fines = get_all_fines()
    
    # Clear existing data
    for tree in tables.values():
        for item in tree.get_children():
            tree.delete(item)
    
    # Process each fine
    for fine in fines:
        status = "Paid" if fine['paid'] else "Pending"
        date = fine['payment_date'] if fine['paid'] else fine['due_date']
        
        if isinstance(date, datetime):
            date = date.strftime('%Y-%m-%d')
        
        # Create row data
        row_data = (
            fine['fine_id'],
            fine['title'],
            f"{fine['first_name']} {fine['last_name']}",
            fine['email'],
            f"${float(fine['amount']):.2f}",
            fine['description'],
            status,
            format_date(date),
            ""  # Actions column will be filled with buttons
        )
        
        # Insert into all fines table
        item_id = tables["all"].insert("", "end", values=row_data, tags=(status.lower(),))
        
        # Insert into appropriate status table
        if fine['paid']:
            tables["paid"].insert("", "end", values=row_data, tags=("paid",))
        else:
            tables["pending"].insert("", "end", values=row_data, tags=("pending",))
    
    # Configure tag colors
    for tree in tables.values():
        tree.tag_configure("paid", background="#E8F5E9")
        tree.tag_configure("pending", background="#FFEBEE")
    
    # Add action buttons
    for tab_name, tree in tables.items():
        add_fine_action_buttons(tree, tab_name)

def add_fine_action_buttons(tree, tab_type):
    """Add action buttons to the fines table"""
    for item in tree.get_children():
        # Get values
        values = tree.item(item, 'values')
        fine_id = values[0]
        status = values[6]  # Status column
        
        # Get bounding box for action column
        col_idx = 8  # "Actions" column index
        bbox = tree.bbox(item, column=col_idx)
        
        if bbox:  # If visible
            # Create a frame for the buttons
            button_frame = ctk.CTkFrame(tree, fg_color="transparent")
            button_frame.place(x=bbox[0], y=bbox[1], width=100, height=bbox[3])
            
            if status == "Pending" or tab_type == "pending":
                # Show process payment button for pending fines
                pay_button = ctk.CTkButton(
                    button_frame, 
                    text="Pay",
                    width=40,
                    height=20,
                    fg_color="#4CAF50",
                    hover_color="#388E3C",
                    corner_radius=4,
                    font=ctk.CTkFont(size=10),
                    command=lambda f_id=fine_id: process_payment(tree, f_id)
                )
                pay_button.pack(side="left", padx=(0, 5))
                
                # Show cancel button for pending fines
                cancel_button = ctk.CTkButton(
                    button_frame, 
                    text="Cancel",
                    width=40,
                    height=20,
                    fg_color="#FF5252",
                    hover_color="#D32F2F",
                    corner_radius=4,
                    font=ctk.CTkFont(size=10),
                    command=lambda f_id=fine_id: cancel_fine_action(tree, f_id)
                )
                cancel_button.pack(side="left")
            elif status == "Paid" or tab_type == "paid":
                # Show "Paid" text for already paid fines
                paid_label = ctk.CTkLabel(
                    button_frame,
                    text="✓ Paid",
                    font=ctk.CTkFont(size=10),
                    text_color="#4CAF50"
                )
                paid_label.pack()

def process_payment(tree, fine_id):
    """Process payment for a fine"""
    result = messagebox.askyesno(
        "Confirm Payment", 
        f"Are you sure you want to mark fine #{fine_id} as paid?"
    )
    
    if result:
        success, message = process_fine_payment(fine_id)
        if success:
            messagebox.showinfo("Success", message)
            refresh_fines_data({tree}) 
        else:
            messagebox.showerror("Error", message)

def cancel_fine_action(tree, fine_id):
    """Cancel a fine"""
    result = messagebox.askyesno(
        "Confirm Cancellation", 
        f"Are you sure you want to cancel fine #{fine_id}?\nThis will permanently delete the fine record."
    )
    
    if result:
        success, message = cancel_fine(fine_id)
        if success:
            messagebox.showinfo("Success", message)
            refresh_fines_data({tree})
        else:
            messagebox.showerror("Error", message)

def refresh_fines_data(tables):
    """Refresh fines data in tables"""
    fines = get_all_fines()
    populate_fines_tables(tables, fines)
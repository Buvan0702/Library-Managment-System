import customtkinter as ctk
from PIL import Image
import os

class StudentNavigationFrame(ctk.CTkFrame):
    def __init__(self, master=None, signout_command=None):
        super().__init__(master, corner_radius=0)
        
        # Configure grid layout with no space between buttons
        self.grid_rowconfigure(4, weight=1)  # Row 4 will take remaining space
        self.grid_columnconfigure(0, weight=1)

        # Load images for icons and store them as instance variables
        image_path = os.path.join(".", "images")
        
        # Store each image as an instance variable to keep it in memory
        self.home_image = ctk.CTkImage(
            light_image=Image.open(os.path.join(image_path, "home_icon.png")) if os.path.exists(os.path.join(image_path, "home_icon.png")) else None,
            dark_image=Image.open(os.path.join(image_path, "home_icon.png")) if os.path.exists(os.path.join(image_path, "home_icon.png")) else None, 
            size=(20, 20)
        )
        self.browse_books_image = ctk.CTkImage(
            light_image=Image.open(os.path.join(image_path, "book_icon.png")) if os.path.exists(os.path.join(image_path, "book_icon.png")) else None, 
            size=(20, 20)
        )
        self.borrowed_image = ctk.CTkImage(
            light_image=Image.open(os.path.join(image_path, "borrow_icon.png")) if os.path.exists(os.path.join(image_path, "borrow_icon.png")) else None, 
            size=(20, 20)
        )
        self.fines_image = ctk.CTkImage(
            light_image=Image.open(os.path.join(image_path, "fine_icon.png")) if os.path.exists(os.path.join(image_path, "fine_icon.png")) else None, 
            size=(20, 20)
        )

        # Navigation label
        self.navigation_label = ctk.CTkLabel(
            self, 
            text="Student Dashboard", 
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#25a249"  # Green color
        )
        self.navigation_label.grid(row=0, column=0, padx=20, pady=20)

        # Navigation buttons
        self.home_button = ctk.CTkButton(
            self, 
            corner_radius=0, 
            height=40, 
            border_spacing=10, 
            text="Home",
            fg_color="transparent", 
            text_color=("gray10", "gray90"), 
            hover_color=("gray70", "gray30"),
            image=self.home_image, 
            anchor="w", 
            command=lambda: master.show_frame("home")
        )
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.browse_books_button = ctk.CTkButton(
            self, 
            corner_radius=0, 
            height=40, 
            border_spacing=10, 
            text="Browse Books",
            fg_color="transparent", 
            text_color=("gray10", "gray90"), 
            hover_color=("gray70", "gray30"),
            image=self.browse_books_image, 
            anchor="w", 
            command=lambda: master.show_frame("browse_books")
        )
        self.browse_books_button.grid(row=2, column=0, sticky="ew")

        self.borrowed_books_button = ctk.CTkButton(
            self, 
            corner_radius=0, 
            height=40, 
            border_spacing=10, 
            text="My Borrowed Books",
            fg_color="transparent", 
            text_color=("gray10", "gray90"), 
            hover_color=("gray70", "gray30"),
            image=self.borrowed_image, 
            anchor="w", 
            command=lambda: master.show_frame("borrowed_books")
        )
        self.borrowed_books_button.grid(row=3, column=0, sticky="ew")

        self.fines_button = ctk.CTkButton(
            self, 
            corner_radius=0, 
            height=40, 
            border_spacing=10, 
            text="Fines & Fees",
            fg_color="transparent", 
            text_color=("gray10", "gray90"), 
            hover_color=("gray70", "gray30"),
            image=self.fines_image, 
            anchor="w", 
            command=lambda: master.show_frame("fines")
        )
        self.fines_button.grid(row=4, column=0, sticky="ew")

        # Add Sign Out Button at the bottom
        self.signout_button = ctk.CTkButton(
            self, 
            text="Sign Out", 
            command=signout_command, 
            fg_color="#cc0000",
            hover_color="#ff3333", 
            corner_radius=10
        )
        self.signout_button.grid(row=5, column=0, padx=20, pady=20, sticky="s")
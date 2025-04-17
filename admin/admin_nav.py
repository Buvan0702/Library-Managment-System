import customtkinter as ctk
from PIL import Image
import os

class AdminNavigationFrame(ctk.CTkFrame):
    def __init__(self, master=None, signout_command=None):
        super().__init__(master, corner_radius=0)

        # Configure grid layout to place Sign Out button at the bottom
        self.grid_rowconfigure(5, weight=1)  # Empty row for spacing
        self.grid_columnconfigure(0, weight=1)
        
        # Load icons for navigation buttons
        icon_path = os.path.join(".", "images")
        
        # Keep images in memory
        self.home_image = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, "home_icon.png")) if os.path.exists(os.path.join(icon_path, "home_icon.png")) else None,
                                      dark_image=Image.open(os.path.join(icon_path, "home_icon.png")) if os.path.exists(os.path.join(icon_path, "home_icon.png")) else None, 
                                      size=(20, 20))
        self.user_management_image = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, "user_icon.png")) if os.path.exists(os.path.join(icon_path, "user_icon.png")) else None, 
                                                size=(20, 20))
        self.book_management_image = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, "book_icon.png")) if os.path.exists(os.path.join(icon_path, "book_icon.png")) else None, 
                                                size=(20, 20))
        self.reports_image = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, "report_icon.png")) if os.path.exists(os.path.join(icon_path, "report_icon.png")) else None, 
                                        size=(20, 20))

        # Admin Dashboard label
        self.navigation_label = ctk.CTkLabel(
            self, 
            text="Admin Dashboard", 
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#25a249"  # Green color
        )
        self.navigation_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

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

        self.user_management_button = ctk.CTkButton(
            self, 
            corner_radius=0, 
            height=40, 
            border_spacing=10, 
            text="User Management",
            fg_color="transparent", 
            text_color=("gray10", "gray90"), 
            hover_color=("gray70", "gray30"),
            image=self.user_management_image, 
            anchor="w", 
            command=lambda: master.show_frame("user_management")
        )
        self.user_management_button.grid(row=2, column=0, sticky="ew")

        self.book_management_button = ctk.CTkButton(
            self, 
            corner_radius=0, 
            height=40, 
            border_spacing=10, 
            text="Book Management",
            fg_color="transparent", 
            text_color=("gray10", "gray90"), 
            hover_color=("gray70", "gray30"),
            image=self.book_management_image, 
            anchor="w", 
            command=lambda: master.show_frame("book_management")
        )
        self.book_management_button.grid(row=3, column=0, sticky="ew")

        self.reports_button = ctk.CTkButton(
            self, 
            corner_radius=0, 
            height=40, 
            border_spacing=10, 
            text="Reports",
            fg_color="transparent", 
            text_color=("gray10", "gray90"), 
            hover_color=("gray70", "gray30"),
            image=self.reports_image, 
            anchor="w", 
            command=lambda: master.show_frame("reports")
        )
        self.reports_button.grid(row=4, column=0, sticky="ew")

        # Sign Out Button placed at the bottom
        self.signout_button = ctk.CTkButton(
            self, 
            text="Sign Out", 
            command=signout_command, 
            fg_color="#cc0000",
            hover_color="#ff3333", 
            corner_radius=10
        )
        self.signout_button.grid(row=6, column=0, padx=20, pady=20, sticky="s")
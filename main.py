import customtkinter as ctk
from login_signup import LoginWindow
from utils import connect_to_database, center_window, create_tables
from PIL import Image, ImageTk
import os

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class LibraryManagementApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("900x600")
        center_window(self)  # Center the main application window

        # Start with the landing page
        self.show_landing_page()

    def show_landing_page(self):
        """Display the landing page."""
        self.clear_window()
        landing_page = LandingPage(master=self)
        landing_page.pack(expand=True, fill="both")

    def show_login_window(self):
        """Display the login window."""
        self.clear_window()
        login_window = LoginWindow(master=self)
        login_window.pack(expand=True, fill="both")

    def clear_window(self):
        """Clear all widgets from the window."""
        for widget in self.winfo_children():
            widget.destroy()


# Landing Page
class LandingPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(fg_color="white")

        # Background Image (replace with your actual image path)
        bg_image_path = os.path.join("images", "landing_page.png")
        if os.path.exists(bg_image_path):
            pil_image = Image.open(bg_image_path).resize((900, 600))
            self.background_image = ctk.CTkImage(light_image=pil_image, size=(900, 600))
            
            # Background Label
            self.bg_label = ctk.CTkLabel(self, image=self.background_image, text="")
            self.bg_label.place(relwidth=1, relheight=1)
        else:
            # Fallback if image is not found
            self.configure(fg_color="#25a249")  # Green background as fallback
            
            # Create a title label
            self.title_label = ctk.CTkLabel(
                self, 
                text="Library Management System",
                font=("Arial", 32, "bold"),
                text_color="white"
            )
            self.title_label.place(relx=0.5, rely=0.3, anchor="center")
            
            # Create a subtitle label
            self.subtitle_label = ctk.CTkLabel(
                self, 
                text="Manage your library efficiently",
                font=("Arial", 18),
                text_color="white"
            )
            self.subtitle_label.place(relx=0.5, rely=0.4, anchor="center")
       
        # Get Started Button
        self.get_started_button = ctk.CTkButton(
            self,
            text="Get Started",
            command=self.open_login_window,
            width=200,
            height=50,
            corner_radius=10,
            fg_color="#25a249",  # Green color
            hover_color="#1e8138",
            font=("Arial", 14, "bold")
        )
        self.get_started_button.place(relx=0.5, rely=0.8, anchor="center")  

    def open_login_window(self):
        """Open the login window."""
        self.master.show_login_window()


# Main function to start the application
def main():
    # Create necessary tables
    create_tables()

    # Start the application
    app = LibraryManagementApp()
    app.mainloop()


if __name__ == "__main__":
    main()
import customtkinter
from src.gui.main_window import MainWindow

if __name__ == "__main__":
    from PIL import Image, ImageTk

    # Set dark theme (alternative: "light")
    customtkinter.set_appearance_mode("dark")
    # Load custom color theme from JSON configuration
    customtkinter.set_default_color_theme("assets/json/custom_theme.json")
    
    # Create root window
    root = customtkinter.CTk()
    
    # Load and set application icon
    icon = Image.open("assets/img/Logo_UAA__cropped_.ico")
    photo = ImageTk.PhotoImage(icon)
    root.title("SHAPEMETRICS")
    root.iconphoto(False, photo)
    
    # Set window dimensions
    root.geometry('1400x900')
    
    # Create and display main application window
    app = MainWindow(root)
    app.pack(fill='both', expand='True')
    
    # Start application event loop
    root.mainloop()
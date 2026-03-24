import customtkinter
from src.gui.gui import wPrincipal

if __name__ == "__main__":
    from PIL import Image, ImageTk

    customtkinter.set_appearance_mode("dark") # O "light"
    customtkinter.set_default_color_theme("assets/json/custom_theme.json")
    root = customtkinter.CTk()
    #customtkinter.set_appearance_mode("light")  # Cambiar a tema claro
    ico = Image.open("assets/img/Logo_UAA__cropped_.ico")
    photo = ImageTk.PhotoImage(ico)
    # Crear una ventana raíz (root) para la aplicación
    root.title("SHAPEMETRICS")
    root.iconphoto(False, photo)
    # Configurar las dimensiones de la ventana raíz
    # Configurar la ventana para que esté en modo pantalla completa
    root.geometry('1400x900')
    app = wPrincipal(root)
    # Empaquetar la instancia de 'wLogin' en la ventana raíz para mostrarla
    app.pack(fill='both', expand='True')
    root.mainloop()
import inspect
import numpy as np
from customtkinter import *
from src.logic import chain_codes
from src.logic import tools
# Importaciones necesarias para integrar Matplotlib con Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import ListedColormap
from matplotlib.figure import Figure
import datetime

def list_chain_codes(module):
    """
    Extract available chain code functions from a module.
    """
    # Get all functions from the module
    functions = inspect.getmembers(module, inspect.isfunction)
    
    # Filter out private/internal functions (those starting with _)
    return [name for name, _ in functions if not name.startswith('_')]

def change_btn_state(button, state):
    """
    Update button state and adjust colors for disabled/enabled appearance.
    """
    if state == "disabled":
        # Apply gray tones (light for light theme, dark for dark theme)
        button.configure(state="disabled", fg_color=("#D1D1D1", "#3E3E3E"))
    else:
        # Restore original blue color from theme configuration
        button.configure(state="normal", fg_color=("#6ea6e7", "#4A90E2"))

class MainWindow(CTkFrame):
    """
    Main application window with image processing and chain code generation interface.
    """
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.binary_matrix = None # Image data for processing
        self.title_font = ("Arial", 50)
        # Handle window close event
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.text_font = ("Arial", 20)
        self.create_widgets()

    def create_widgets(self):
        """
        Build the user interface components and layout.
        """
        self.combobox_var = StringVar(value="No Selection")

        # Configure grid weights for responsive layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Right panel expands vertically

        # Left sidebar for actions
        self.actions_frame = CTkFrame(self, width=220, corner_radius=0)
        self.actions_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Actions panel header
        CTkLabel(self.actions_frame, text="Actions", font=self.title_font).pack(pady=(20, 30))

        # Upload image button
        self.btn_upload = CTkButton(self.actions_frame, text="Load Image", command=self.upload_image, font=self.title_font)
        self.btn_upload.pack(pady=10, padx=20, fill="x")
        
        # Spacing
        CTkLabel(self.actions_frame, text=" ", font=self.title_font).pack(pady=(20, 20))

        # View contour button
        self.btn_outline = CTkButton(self.actions_frame, text="View Contour", font=self.title_font, command=self.process_outline)
        self.btn_outline.pack(pady=10, padx=20, fill="x")
        change_btn_state(self.btn_outline, state="disabled")

        # Chain code type selector dropdown
        self.combobox_chain_class = CTkComboBox(self.actions_frame, values=list_chain_codes(chain_codes),
                                         command=self.on_combobox_change, variable=self.combobox_var,
                                         fg_color="#3B8ED0", border_color="#3B8ED0", button_color="#3B8ED0",
                                         text_color="white", dropdown_text_color="white", dropdown_fg_color="#3B8ED0",
                                         corner_radius=6, border_width=2, height=60, font=self.title_font)
        self.combobox_chain_class.set("No Selection")
        self.combobox_chain_class.pack(pady=10, padx=20, fill="x")
        change_btn_state(self.combobox_chain_class, state="disabled")

        # Generate chain code button
        self.btn_chain_generator = CTkButton(self.actions_frame, text="Generate Chain", font=self.title_font)
        self.btn_chain_generator.pack(pady=10, padx=20, fill="x")
        change_btn_state(self.btn_chain_generator, state="disabled")

        # Calculate descriptor button
        self.btn_descriptor = CTkButton(self.actions_frame, text="Descriptor", font=self.title_font)
        self.btn_descriptor.pack(pady=10, padx=20, fill="x")
        change_btn_state(self.btn_descriptor, state="disabled")

        # Compress chain button
        self.btn_compressor = CTkButton(self.actions_frame, text="Compression", font=self.title_font)
        self.btn_compressor.pack(pady=10, padx=20, fill="x")
        change_btn_state(self.btn_compressor, state="disabled")

        # Right panel for visualization
        self.visualization_frame = CTkFrame(self)
        self.visualization_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.visualization_frame.grid_rowconfigure(0, weight=1)  # Canvas area expands
        self.visualization_frame.grid_columnconfigure(0, weight=1)
        
        # Dedicated frame for matplotlib canvas
        self.frame_canvas = CTkFrame(self.visualization_frame, fg_color="transparent")
        self.frame_canvas.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Initialize empty matplotlib canvas
        self.canvas_matplotlib = None
        
        # Placeholder message before image is loaded
        self.label_canvas_placeholder = CTkLabel(self.frame_canvas, text="Load an image to visualize", 
                                                    font=("Roboto", 18), text_color="gray")
        self.label_canvas_placeholder.pack(expand=True)

        # Log output area for messages and status
        self.textbox_log = CTkTextbox(self.visualization_frame, width=800, height=200, corner_radius=10,
                                         border_width=2, border_color="gray", font=("Consolas", 12))
        self.textbox_log.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Set log to read-only by default
        self.textbox_log.configure(state="disabled")
        
        # Initial welcome message
        self.log_message("System initialized. Ready to process images.")

    def on_combobox_change(self, choice):
        """
        Handle chain code type selection change.
        """
        self.log_message(f"Chain code selected: {self.combobox_var.get()}")

    def log_message(self, message):
        """
        Write timestamped message to the log display.
        """
        self.textbox_log.configure(state="normal")
        # Add timestamp prefix to each message
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S] ")
        self.textbox_log.insert("end", timestamp + message + "\n")
        self.textbox_log.see("end")  # Auto-scroll to latest message
        self.textbox_log.configure(state="disabled")

    def upload_image(self):
        """
        Open file dialog to load and process an image.
        """
        # Open file dialog filtered for image files
        file_path = filedialog.askopenfilename(
            title="Select image to process",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif"),
                ("All files", "*.*")
            ]
        )
        
        # User cancelled the dialog
        if not file_path:
            self.log_message("Image load cancelled by user.")
            return
        
        # Process image and convert to binary
        self.binary_matrix = tools.process_and_binarize(file_path)
        # Validate result is a proper numpy array
        if type(self.binary_matrix) != np.ndarray or self.binary_matrix is None:
            self.log_message(f"Error loading image: {self.binary_matrix}")
            return
        
        # Enable all processing buttons
        self.log_message(f"Image loaded: {file_path}")
        change_btn_state(self.btn_outline, state="normal")
        change_btn_state(self.btn_chain_generator, state="normal")
        change_btn_state(self.btn_descriptor, state="normal")
        change_btn_state(self.btn_compressor, state="normal")
        change_btn_state(self.combobox_chain_class, state="normal")
        self.display_on_canvas(self.binary_matrix)

    def process_outline(self):
        """
        Calculate the contour and overlay it in red on the loaded image.
        """
        if self.binary_matrix is None:
            return
            
        # Get contour dictionary from logic module
        outline_data = tools.find_outline(self.binary_matrix)
        
        contour_matrix = outline_data["contour"]
        perimeter = outline_data["perimeter"]
        
        # Display combining base matrix and overlay matrix in red
        self.display_on_canvas(
            self.binary_matrix, 
            overlay_matrix=contour_matrix, 
            overlay_color="red", # You can change this color easily
            title=f"Image Contour (Perimeter: {perimeter})"
        )
        
        self.log_message(f"Contour displayed in red. Perimeter: {perimeter}")

    def display_on_canvas(self, base_matrix, overlay_matrix=None, overlay_color="red", title="Image"):
        """
        Render a base binary matrix and an optional color overlay onto the canvas.
        """
        # Clear existing canvas
        if self.canvas_matplotlib:
            self.canvas_matplotlib.get_tk_widget().destroy()
            
        self.label_canvas_placeholder.pack_forget()

        # Setup figure and colors (keeping the dark background)
        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#2B2B2B') 
        
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2B2B2B')
        
        # 1. DRAW BASE IMAGE (Grayscale)
        # Background is black (0), Object is white (1)
        ax.imshow(base_matrix, cmap="gray", vmin=0, vmax=1)
        
        # 2. DRAW OVERLAY IMAGE (Contour in Red)
        if overlay_matrix is not None:
            # Create a custom colormap:
            # 0 (no contour) will be transparent
            # 1 (contour) will be the specified overlay_color (red)
            # In RGBA: (red, green, blue, alpha/transparency)
            colors = [(0, 0, 0, 0), overlay_color] 
            custom_cmap = ListedColormap(colors)
            
            # Layer the contour over the base image
            ax.imshow(overlay_matrix, cmap=custom_cmap, vmin=0, vmax=1)
        
        # Final canvas setup
        ax.axis('off') 
        ax.set_title(title, color="white")
        fig.tight_layout()

        # Embed into CustomTkinter Frame
        self.canvas_matplotlib = FigureCanvasTkAgg(fig, master=self.frame_canvas)
        self.canvas_matplotlib.draw()
        
        tk_widget = self.canvas_matplotlib.get_tk_widget()
        tk_widget.pack(fill="both", expand=True)

    def generate_chain(self):
        """
        Generate chain code using selected method.
        """
        chain_type = self.combobox_var.get()
        # Only proceed if a valid chain type is selected
        if chain_type != "No Selection":
            print(chain_type)

    def close(self):
        """
        Cleanup and close the application.
        """
        self.quit()
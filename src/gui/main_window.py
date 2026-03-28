import inspect
import tkinter as tk
import numpy as np
from customtkinter import *
from src.logic import chain_codes
from src.logic import tools
# Importaciones necesarias para integrar Matplotlib con Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import ListedColormap
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import datetime
import json

def list_chain_codes(module):
    """
    Extract available chain code functions from a module.
    """
    # Get all functions from the module
    functions = inspect.getmembers(module, inspect.isfunction)
    
    # Filter out private/internal functions (those starting with _)
    return {name.upper(): func for name, func in functions if not name.startswith('_')}

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
        self.actual_chain = []
        self.actual_probability = {}
        self.img_perimeter = None
        self.actual_entropy = 0.0
        self.cc_functions = list_chain_codes(chain_codes)
        self.title_font = ("Arial", 50)
        # Handle window close event
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.text_font = ("Arial", 20)
        self.create_menu_bar()
        self.create_widgets()

    def create_menu_bar(self):
        self.menu_bar = tk.Menu(self, name='apple')

        self.m_files = tk.Menu(self.menu_bar, tearoff=0)
        self.m_files.add_command(label="Load Image",
                                  command=self.upload_image)
        self.m_files.add_command(label="Load Chain Code")
        self.m_files.add_separator()
        self.m_files.add_command(label="Save Chain Code", command=self.save_chain_code)
        self.m_files.add_command(label="Save Histogram")
        self.menu_bar.add_cascade(menu=self.m_files, label="Files")

        self.m_tools = tk.Menu(self.menu_bar, tearoff=0)
        self.m_tools.add_command(label="Calc Contour",
                                 command=self.process_outline)
        self.m_tools.add_command(label="Calc Descriptor")
        self.m_tools.add_separator()
        self.m_t_cc = tk.Menu(self.m_tools, tearoff=0)
        for key in list(self.cc_functions.keys()):
            self.m_t_cc.add_command(label=key)
        self.m_tools.add_cascade(menu=self.m_t_cc, label="Chain Codes")
        self.m_tools.add_command(label="Generate Histogram", command=self.generate_histogram)
        self.menu_bar.add_cascade(menu=self.m_tools, label="Tools")
        self.m_help = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(menu=self.m_help, label="Help")

        self.root.config(menu = self.menu_bar)

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
        self.combobox_chain_class = CTkComboBox(self.actions_frame, values=list(self.cc_functions.keys()),
                                         command=self.on_combobox_change, variable=self.combobox_var,
                                         fg_color="#3B8ED0", border_color="#3B8ED0", button_color="#3B8ED0",
                                         text_color="white", dropdown_text_color="white", dropdown_fg_color="#3B8ED0",
                                         corner_radius=6, border_width=2, height=60, font=self.title_font)
        self.combobox_chain_class.set("No Selection")
        self.combobox_chain_class.pack(pady=10, padx=20, fill="x")
        change_btn_state(self.combobox_chain_class, state="disabled")

        # Generate chain code button
        self.btn_chain_generator = CTkButton(self.actions_frame, text="Generate Chain", font=self.title_font, command=self.generate_chain)
        self.btn_chain_generator.pack(pady=10, padx=20, fill="x")
        change_btn_state(self.btn_chain_generator, state="disabled")

        # Calculate descriptor button
        self.btn_descriptor = CTkButton(self.actions_frame, text="Descriptor", font=self.title_font, command=self.generate_entropy)
        self.btn_descriptor.pack(pady=10, padx=20, fill="x")
        change_btn_state(self.btn_descriptor, state="disabled")

        # Compress chain button 
        self.btn_compressor = CTkButton(self.actions_frame, text="Compression", font=self.title_font, command=self.arithmetic_compression)
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
                                         border_width=2, border_color="gray", font=("Consolas", 25))
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
        self.img_perimeter = outline_data["perimeter"]
        
        # Display combining base matrix and overlay matrix in red
        self.display_on_canvas(
            self.binary_matrix, 
            overlay_matrix=contour_matrix, 
            overlay_color="red", # You can change this color easily
            title=f"Image Contour (Perimeter: {self.img_perimeter})"
        )
        
        self.log_message(f"Contour displayed in red. Perimeter: {self.img_perimeter}")

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
        if chain_type == "No Selection":
            self.log_message("No code chain selected")
            return
        try:
            ccf = self.cc_functions[chain_type.upper()]
            self.actual_chain = ccf(self.binary_matrix)
            lenght = len(self.actual_chain)
            self.log_message(f"Chain: {self.actual_chain}")
            self.log_message(f"Length of the chain: {lenght}")
        except Exception as error:
            self.log_message(f"Error: {error}")   

    def generate_histogram(self):
        """
        Calculates stats and triggers the embedded UI plot.
        """
        if not hasattr(self, 'actual_chain') or not self.actual_chain:
            self.log_message("Error")
            return

        self.log_message("Generating Histograms")        

        # Calculate data
        total_symbol = len(self.actual_chain)
        from collections import Counter
        frequency = dict(Counter(self.actual_chain))
        probabilities = {sym: freq / total_symbol for sym, freq in frequency.items()}
        
        self.actual_probability = probabilities # Save for compression
        
        try:
            # Call the internal display function with both dicts
            self.display_histogram_plot(frequency, probabilities)
            self.log_message(f" Statistics dashboard generated")
        except Exception as e:
            self.log_message(f"Display Error: {e}")

    def display_histogram_plot(self, frequency_dict, probability_dict):
        """
        Integrates the histograms
        """
        if self.canvas_matplotlib:
            self.canvas_matplotlib.get_tk_widget().destroy()
        self.label_canvas_placeholder.pack_forget()

        fig = tools.plot_histograms(frequency_dict, probability_dict)
        
        fig.patch.set_facecolor('#2B2B2B')
        for ax in fig.get_axes():
            ax.set_facecolor('#2B2B2B')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            ax.grid(True, linestyle='--', alpha=0.3, color='gray')

        self.canvas_matplotlib = FigureCanvasTkAgg(fig, master=self.frame_canvas)
        self.canvas_matplotlib.draw()
        
        tk_widget = self.canvas_matplotlib.get_tk_widget()
        tk_widget.pack(fill="both", expand=True)

    def generate_entropy(self):
        """
        generate the shannon entropy
        """
        if not hasattr(self, 'actual_chain') or not self.actual_chain:
            self.log_message("Error: First generate the chain code")

        entropy = tools.calculate_entropy(self.actual_chain)
        self.log_message(F"SHANNON ENTROPY \n Result: {entropy: .4} bits")
    

    def arithmetic_compression(self):
        """
        Calculate arithmetic compression
        """   
        if not getattr(self, 'actual_chain', None) or not getattr(self, 'actual_probability', None):            
            self.log_message("Error: Missing chain code or probability data.")
            return 
        #Call the mathematical function to return a single number
        avg_bits_ari = tools.lenght_compression_arithmetic(self.actual_chain, self.actual_probability)
        #Huffman compression
        avg_len, total_bits, huffman_code = tools.length_huffman_compression(self.actual_chain, self.actual_probability)        
        tree_str = "\n".join([f"[{sym}] -> {huffman_code[sym]}" for sym in sorted(huffman_code.keys())])
        
        huffman_report = (
            f"Average length chain code by arithmetic compression: {avg_bits_ari:.4f} \n"
            f"  Huffman Compression \n"
            f"  Generated tree: \n {tree_str} \n"
            f"  Average length: {avg_len: .4f} bits/symbol \n"
            f"  Total accumulated bits: {total_bits: .4f} bits"
        )
        self.log_message(huffman_report)

    def save_chain_code(self):
        """
        Export the current chain code and metadata to a JSON file.
        """
        # Verify that there is data to save
        if not hasattr(self, 'actual_chain') or self.actual_chain is None:
            self.log_message("Error: No chain code to export. Generate it first.")
            return
        if not hasattr(self, "img_perimeter") or self.img_perimeter is None:
            self.log_message("Error: No perimeter of image")
            return

        # Open the native 'Save As' dialog
        file_path = filedialog.asksaveasfilename(
            title="Save Chain Code",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="chain_code_result.json"
        )

        # If the user cancels the dialog
        if not file_path:
            return

        # Structure the metadata and data
        data_to_save = {
            "metadata": {
                "export_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "algorithm": self.combobox_var.get(),
                # Retrieve the perimeter if it was saved during the outline process
                "perimeter": getattr(self, 'img_perimeter'), 
                "chain_length": len(self.actual_chain)
            },
            "chain_code": self.actual_chain
        }

        # Write to the file
        try:
            with open(file_path, 'w', encoding='utf-8') as json_file:
                # indent=4 makes the JSON easily readable by humans
                json.dump(data_to_save, json_file, indent=4)
                
            file_name = os.path.basename(file_path)
            self.log_message(f"Success: Data exported to {file_name}")
            
        except Exception as e:
            self.log_message(f"Error saving file: {e}")

    def close(self):
        """
        Cleanup and close the application.
        """
        self.quit()
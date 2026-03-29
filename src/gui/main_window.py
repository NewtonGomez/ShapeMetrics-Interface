import inspect
import tkinter as tk
import numpy as np
from customtkinter import *
from src.logic import chain_codes
from src.logic import decoding_functions
from src.logic import tools
# Importaciones necesarias para integrar Matplotlib con Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import ListedColormap
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import datetime
import json

def list_functions(module):
    """
    Extract available functions from a module and normalize their names.
    
    Args:
        module: The module to inspect for functions
        
    Returns:
        dict: Dictionary with uppercase function names as keys and function objects as values
    """
    # Extract all public functions (non-private, non-dunder) from the module
    functions = inspect.getmembers(module, inspect.isfunction)
    
    # Normalize to uppercase for consistent command matching, filter stdlib functions
    return {name.upper(): func for name, func in functions if not name.startswith('_')}

def change_button_state(button, state):
    """
    Update button state and visual appearance.
    
    Args:
        button: The CTkButton widget to modify
        state (str): Either 'disabled' or 'normal'
    """
    if state == "disabled":
        # Apply disabled appearance with gray-tone colors for both light/dark themes
        button.configure(state="disabled", fg_color=("#D1D1D1", "#3E3E3E"))
    else:
        # Restore enabled appearance with theme-consistent blue color
        button.configure(state="normal", fg_color=("#6ea6e7", "#4A90E2"))

class MainWindow(CTkFrame):
    """
    Main application window with image processing and chain code generation interface.
    Provides tools for loading images, computing chain codes, and analyzing shape descriptors.
    """
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        
        # Image processing data
        self.binary_matrix = None  # Processed binary image as numpy array
        self.current_chain = []    # Current chain code sequence
        self.current_probability = {}  # Symbol probability distribution
        self.image_perimeter = None  # Perimeter value computed from contour
        self.current_entropy = 0.0  # Shannon entropy measurement
        self.image_histogram = None  # Cached histogram figure for export
        
        # Function mappings and styling
        self.chain_code_functions = list_functions(chain_codes)
        self.title_font = ("Arial", 50)
        self.text_font = ("Arial", 20)
        
        # Setup event handlers
        root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        # Build interface
        self.create_menu_bar()
        self.create_widgets()

    def create_menu_bar(self):
        """
        Build the application menu bar with file, tools, and help menus.
        """
        self.menu_bar = tk.Menu(self, name='apple')

        # FILE MENU - Image and data I/O operations
        self.menu_files = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_files.add_command(label="Load Image", command=self.upload_image)
        self.menu_files.add_command(label="Load Chain Code", command=self.load_chain_code)
        self.menu_files.add_separator()
        self.menu_files.add_command(label="Save Chain Code", command=self.save_chain_code)
        self.menu_files.add_command(label="Save Histogram", command=self.save_histogram)
        self.menu_bar.add_cascade(menu=self.menu_files, label="Files")

        # TOOLS MENU - Image processing and analysis operations
        self.menu_tools = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_tools.add_command(label="Calc Contour", command=self.process_outline)
        self.menu_tools.add_command(label="Calc Descriptor")
        self.menu_tools.add_separator()
        
        # Chain Code submenu - dynamically populated with available algorithms
        self.menu_tools_chains = tk.Menu(self.menu_tools, tearoff=0)
        for algorithm_name in list(self.chain_code_functions.keys()):
            self.menu_tools_chains.add_command(label=algorithm_name)
        self.menu_tools.add_cascade(menu=self.menu_tools_chains, label="Chain Codes")
        self.menu_tools.add_command(label="Generate Histogram", command=self.generate_histogram)
        self.menu_bar.add_cascade(menu=self.menu_tools, label="Tools")
        
        # HELP MENU - Documentation and support
        self.menu_help = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(menu=self.menu_help, label="Help")

        self.root.config(menu=self.menu_bar)

    def create_widgets(self):
        """
        Build the UI layout with left action panel and right visualization area.
        Initializes all buttons, dropdowns, and display components.
        """
        self.combobox_variable = StringVar(value="No Selection")

        # Configure responsive grid layout (column 1 expands horizontally)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Main content area expands vertically

        # ======== LEFT SIDEBAR ========
        # Control panel with action buttons and settings
        self.actions_frame = CTkFrame(self, width=220, corner_radius=0)
        self.actions_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Panel header
        CTkLabel(self.actions_frame, text="Actions", font=self.title_font).pack(pady=(20, 30))

        # Load image button
        self.button_upload = CTkButton(
            self.actions_frame, text="Load Image", 
            command=self.upload_image, font=self.title_font
        )
        self.button_upload.pack(pady=10, padx=20, fill="x")
        
        # Vertical spacing
        CTkLabel(self.actions_frame, text=" ", font=self.title_font).pack(pady=(20, 20))

        # Display contour overlay button
        self.button_outline = CTkButton(
            self.actions_frame, text="View Contour", 
            font=self.title_font, command=self.process_outline
        )
        self.button_outline.pack(pady=10, padx=20, fill="x")
        change_button_state(self.button_outline, state="disabled")

        # Chain code algorithm selector dropdown
        self.combobox_chain_type = CTkComboBox(
            self.actions_frame, 
            values=list(self.chain_code_functions.keys()),
            command=self.on_chain_type_selected, 
            variable=self.combobox_variable,
            fg_color="#3B8ED0", border_color="#3B8ED0", button_color="#3B8ED0",
            text_color="white", dropdown_text_color="white", dropdown_fg_color="#3B8ED0",
            corner_radius=6, border_width=2, height=60, font=self.title_font
        )
        self.combobox_chain_type.set("No Selection")
        self.combobox_chain_type.pack(pady=10, padx=20, fill="x")
        change_button_state(self.combobox_chain_type, state="disabled")

        # Compute chain code button
        self.button_chain_generator = CTkButton(
            self.actions_frame, text="Generate Chain", 
            font=self.title_font, command=self.generate_chain
        )
        self.button_chain_generator.pack(pady=10, padx=20, fill="x")
        change_button_state(self.button_chain_generator, state="disabled")

        # Compute shape descriptor button
        self.button_descriptor = CTkButton(
            self.actions_frame, text="Descriptor", 
            font=self.title_font, command=self.generate_entropy
        )
        self.button_descriptor.pack(pady=10, padx=20, fill="x")
        change_button_state(self.button_descriptor, state="disabled")

        # Compression analysis button
        self.button_compressor = CTkButton(
            self.actions_frame, text="Compression", 
            font=self.title_font, command=self.arithmetic_compression
        )
        self.button_compressor.pack(pady=10, padx=20, fill="x")
        change_button_state(self.button_compressor, state="disabled")

        # ======== RIGHT VISUALIZATION PANEL ========
        # Main display area for images and plots
        self.visualization_frame = CTkFrame(self)
        self.visualization_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.visualization_frame.grid_rowconfigure(0, weight=1)  # Plot area expands
        self.visualization_frame.grid_columnconfigure(0, weight=1)  # Canvas expands horizontally
        
        # Container for matplotlib embedded figure
        self.frame_canvas = CTkFrame(self.visualization_frame, fg_color="transparent")
        self.frame_canvas.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Cached matplotlib canvas widget
        self.canvas_matplotlib = None
        
        # Placeholder label (hidden when plot is displayed)
        self.label_canvas_placeholder = CTkLabel(
            self.frame_canvas, text="Load an image to visualize", 
            font=("Roboto", 18), text_color="gray"
        )
        self.label_canvas_placeholder.pack(expand=True)

        # System log output area
        self.textbox_log = CTkTextbox(
            self.visualization_frame, width=800, height=200, corner_radius=10,
            border_width=2, border_color="gray", font=("Consolas", 25)
        )
        self.textbox_log.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Read-only by default (manipulated via log_message method)
        self.textbox_log.configure(state="disabled")
        
        # Welcome message
        self.log_message("System initialized. Ready to process images.")

    def on_chain_type_selected(self, choice):
        """
        Handle user selection of a chain code algorithm from the dropdown.
        Logs the selection for debugging and reference.
        """
        selected_type = self.combobox_variable.get()
        self.log_message(f"Chain code algorithm selected: {selected_type}")

    def log_message(self, message):
        """
        Append a timestamped message to the log display.
        
        Args:
            message (str): The message to log
        """
        # Temporarily enable editing to add new text
        self.textbox_log.configure(state="normal")
        
        # Prepend timestamp for chronological reference
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S] ")
        self.textbox_log.insert("end", timestamp + message + "\n")
        
        # Auto-scroll to show the latest message
        self.textbox_log.see("end")
        
        # Re-enable read-only mode
        self.textbox_log.configure(state="disabled")

    def upload_image(self):
        """
        Load an image file via file dialog, binarize it, and enable processing.
        """
        # Open native file chooser (filtered for image formats)
        file_path = filedialog.askopenfilename(
            title="Select image to process",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif"),
                ("All files", "*.*")
            ]
        )
        
        # User cancelled the dialog without selecting a file
        if not file_path:
            self.log_message("Image load cancelled by user.")
            return
        
        # Process the image: load, convert to grayscale, and binarize
        self.binary_matrix = tools.process_and_binarize(file_path)
        
        # Validate the result is a valid numpy array
        if not isinstance(self.binary_matrix, np.ndarray) or self.binary_matrix is None:
            self.log_message(f"Error loading image: {self.binary_matrix}")
            return
        
        # Successfully loaded: enable UI controls and display image
        self.log_message(f"Image loaded: {file_path}")
        change_button_state(self.button_outline, state="normal")
        change_button_state(self.button_chain_generator, state="normal")
        change_button_state(self.button_descriptor, state="normal")
        change_button_state(self.combobox_chain_type, state="normal")
        
        # Display the uploaded image
        self.display_on_canvas(self.binary_matrix)
        self.log_message(f"Image dimensions: {self.binary_matrix.shape}")

    def process_outline(self):
        """
        Compute and display the shape contour overlaid on the original image.
        Calculates perimeter as a bonus metric.
        """
        # Ensure an image has been loaded
        if self.binary_matrix is None:
            return
            
        # Call image processing tool to extract contour
        outline_data = tools.find_outline(self.binary_matrix)
        
        contour_matrix = outline_data["contour"]
        self.image_perimeter = outline_data["perimeter"]
        
        # Render with red overlay for visual contrast
        self.display_on_canvas(
            self.binary_matrix, 
            overlay_matrix=contour_matrix, 
            overlay_color="red",
            title=f"Image Contour (Perimeter: {self.image_perimeter})"
        )
        
        self.log_message(f"Contour displayed (red overlay). Perimeter: {self.image_perimeter}")

    def display_on_canvas(self, base_matrix, overlay_matrix=None, overlay_color="red", title="Image"):
        """
        Render a binary image with optional colored overlay onto the visualization canvas.
        
        Args:
            base_matrix (np.ndarray): Base image to display (grayscale, 0-1 or 0-255)
            overlay_matrix (np.ndarray, optional): Binary mask to overlay with color
            overlay_color (str, optional): Color name or hex for overlay (default: 'red')
            title (str, optional): Figure title (default: 'Image')
        """
        # Destroy previous canvas if it exists
        if self.canvas_matplotlib:
            self.canvas_matplotlib.get_tk_widget().destroy()
            
        # Hide placeholder message
        self.label_canvas_placeholder.pack_forget()

        # Create matplotlib figure with dark theme
        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#2B2B2B')  # Dark gray background
        
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2B2B2B')
        
        # Draw the base image in grayscale (uint8: 0-255)
        ax.imshow(base_matrix, cmap="gray", vmin=0, vmax=255)
        
        # Layer a colored overlay if provided
        if overlay_matrix is not None:
            # Normalize overlay matrix to [0-1] range for proper colormap indexing
            # This ensures: 0=transparent background, 1=colored contour pixels
            #normalized_overlay = overlay_matrix.astype(float) / 255.0
            
            # Create custom colormap with transparent and colored states
            # RGBA format: (red, green, blue, alpha)
            # Index 0 = transparent (no contour), Index 1 = colored (contour line)
            colors = [(0, 0, 0, 0), overlay_color]
            custom_cmap = ListedColormap(colors)
            
            # Display normalized overlay using [0-1] color mapping
            ax.imshow(overlay_matrix, cmap=custom_cmap, vmin=0, vmax=255)
        
        # Configure axes appearance
        ax.axis('off')  # Hide axes and ticks
        ax.set_title(title, color="white")
        fig.tight_layout()

        # Embed matplotlib figure into CustomTkinter frame
        self.canvas_matplotlib = FigureCanvasTkAgg(fig, master=self.frame_canvas)
        self.canvas_matplotlib.draw()
        
        # Add to widget hierarchy and expand
        tk_widget = self.canvas_matplotlib.get_tk_widget()
        tk_widget.pack(fill="both", expand=True)

    def generate_chain(self):
        """
        Compute and display chain code using the selected algorithm.
        """
        # Get user's selected chain code algorithm
        chain_type_name = self.combobox_variable.get()
        
        # Validate selection
        if chain_type_name == "No Selection":
            self.log_message("Please select a chain code algorithm first.")
            return
            
        try:
            # Retrieve the corresponding algorithm function
            algorithm_function = self.chain_code_functions[chain_type_name.upper()]
            
            # Execute the algorithm on the loaded binary image
            self.current_chain = algorithm_function(self.binary_matrix)
            chain_length = len(self.current_chain)
            
            # Log the results
            self.log_message(f"Chain code generated: {self.current_chain}")
            self.log_message(f"Chain length: {chain_length} symbols")
            
        except Exception as error:
            self.log_message(f"Error generating chain: {error}")   

    def generate_histogram(self):
        """
        Compute symbol frequency distribution and display histogram plot.
        Enables compression analysis after calculation.
        """
        # Ensure a chain code has been generated
        if not hasattr(self, 'current_chain') or not self.current_chain:
            self.log_message("Error: Generate a chain code first.")
            return

        self.log_message("Computing frequency distribution and generating histograms...")        

        # Calculate frequency and probability from current chain
        total_symbols = len(self.current_chain)
        from collections import Counter
        frequency_distribution = dict(Counter(self.current_chain))
        probability_distribution = {sym: freq / total_symbols for sym, freq in frequency_distribution.items()}
        
        # Cache probabilities for later use in compression analysis
        self.current_probability = probability_distribution
        
        try:
            # Render histogram with frequency and probability data
            self.display_histogram_plot(frequency_distribution, probability_distribution)
            self.log_message("Histogram and statistics rendered successfully.")
            
        except Exception as error:
            self.log_message(f"Error rendering histogram: {error}")
            return

        # Enable compression analysis button now that histogram exists
        change_button_state(self.button_compressor, state="normal")

    def display_histogram_plot(self, frequency_dict, probability_dict):
        """
        Render histograms for symbol frequency and probability distribution.
        
        Args:
            frequency_dict (dict): Symbol -> count mapping
            probability_dict (dict): Symbol -> probability mapping
        """
        # Clear previous visualization if it exists
        if self.canvas_matplotlib:
            self.canvas_matplotlib.get_tk_widget().destroy()
        self.label_canvas_placeholder.pack_forget()

        # Generate histogram figure from tools module
        fig = tools.plot_histograms(frequency_dict, probability_dict)
        self.image_histogram = fig  # Cache for later export
        
        # Apply dark theme styling to all axes
        fig.patch.set_facecolor('#2B2B2B')  # Figure background
        for axis in fig.get_axes():
            axis.set_facecolor('#2B2B2B')  # Subplot background
            axis.tick_params(colors='white')  # Tick labels white
            axis.xaxis.label.set_color('white')  # X-axis label
            axis.yaxis.label.set_color('white')  # Y-axis label
            axis.title.set_color('white')  # Plot title
            axis.grid(True, linestyle='--', alpha=0.3, color='gray')  # Grid lines

        # Embed figure into CustomTkinter canvas
        self.canvas_matplotlib = FigureCanvasTkAgg(fig, master=self.frame_canvas)
        self.canvas_matplotlib.draw()
        
        # Add to widget hierarchy and expand
        tk_widget = self.canvas_matplotlib.get_tk_widget()
        tk_widget.pack(fill="both", expand=True)

    def generate_entropy(self):
        """
        Calculate and display Shannon entropy of the current chain code.
        Entropy measures the information content and randomness of the sequence.
        """
        # Validate that a chain code exists
        if not hasattr(self, 'current_chain') or not self.current_chain:
            self.log_message("Error: Generate a chain code before computing entropy.")
            return

        # Compute Shannon entropy using information theory formula
        entropy_value = tools.calculate_entropy(self.current_chain)
        
        # Display result with 4 decimal precision
        self.log_message(f"\nSHANNON ENTROPY ANALYSIS\nResult: {entropy_value:.4f} bits/symbol")
    

    def arithmetic_compression(self):
        """
        Analyze compression efficiency using arithmetic and Huffman coding schemes.
        Provides rate-distortion metrics for the current chain code.
        """
        # Validate required data for compression analysis
        if not getattr(self, 'current_chain', None) or not getattr(self, 'current_probability', None):            
            self.log_message("Error: Missing chain code or probability distribution.")
            return
            
        # Compute arithmetic coding average bits per symbol
        arithmetic_avg_bits = tools.lenght_compression_arithmetic(self.current_chain, self.current_probability)
        
        # Compute Huffman coding statistics and code tree
        huffman_avg_bits, huffman_total_bits, huffman_codebook = tools.length_huffman_compression(
            self.current_chain, self.current_probability
        )
        
        # Format Huffman code assignments as human-readable text
        huffman_tree_text = "\n".join(
            [f"[{sym}] -> {huffman_codebook[sym]}" for sym in sorted(huffman_codebook.keys())]
        )
        
        # Compile comprehensive compression report
        compression_report = (
            f"\nCOMPRESSION ANALYSIS REPORT\n"
            f"─────────────────────────────\n"
            f"Arithmetic Coding:\n"
            f"  Average bits per symbol: {arithmetic_avg_bits:.4f}\n\n"
            f"Huffman Coding:\n"
            f"  Code Tree:\n{huffman_tree_text}\n\n"
            f"  Average bits per symbol: {huffman_avg_bits:.4f}\n"
            f"  Total bits for full chain: {huffman_total_bits:.4f}"
        )
        self.log_message(compression_report)

    def save_chain_code(self):
        """
        Export the current chain code and analysis metadata to a JSON file.
        """
        # Validate that chain code and perimeter data exist
        if not hasattr(self, 'current_chain') or not self.current_chain:
            self.log_message("Error: No chain code to export. Generate it first.")
            return
        if not hasattr(self, "image_perimeter") or self.image_perimeter is None:
            self.log_message("Error: Image perimeter not computed. Run 'View Contour' first.")
            return

        # Open native file save dialog
        file_path = filedialog.asksaveasfilename(
            title="Save Chain Code",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="chain_code_result.json"
        )

        # User cancelled save dialog
        if not file_path:
            return
            
        # Extract image dimensions from binary matrix
        image_height, image_width = 0, 0
        if self.binary_matrix is not None:
            # np.ndarray.shape returns (rows, cols) -> (height, width)
            image_height, image_width = self.binary_matrix.shape[:2]
            
        # Assemble metadata and serializable data
        data_to_export = {
            "metadata": {
                "export_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "algorithm": self.combobox_variable.get(),
                "perimeter": getattr(self, 'image_perimeter'), 
                "image_width": int(image_width),
                "image_height": int(image_height),
                "chain_length": len(self.current_chain)
            },
            "chain_code": self.current_chain
        }

        # Write JSON with pretty printing for readability
        try:
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(data_to_export, json_file, indent=4)
                
            file_name = os.path.basename(file_path)
            self.log_message(f"Success: Chain code exported to {file_name}")
            
        except Exception as error:
            self.log_message(f"Error saving file: {error}")

    def save_histogram(self):
        """
        Export the current histogram figure as an image file.
        Supports PNG, PDF, and JPEG formats.
        """
        # Validate that a histogram has been generated
        if not getattr(self, 'image_histogram', None):
            self.log_message("Error: No histogram available. Generate one first.")
            return

        # Open native file save dialog with format selection
        file_path = filedialog.asksaveasfilename(
            title="Save Histogram",
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("PDF Document", "*.pdf"),
                ("JPEG Image", "*.jpg"),
                ("All files", "*.*")
            ],
            initialfile="histogram_metrics.png"
        )

        # User cancelled save dialog
        if not file_path:
            return

        # Export figure while preserving dark theme styling
        try:
            self.image_histogram.savefig(
                file_path, 
                facecolor=self.image_histogram.get_facecolor(),  # Maintain background color
                edgecolor='none',
                bbox_inches='tight'  # Minimize whitespace padding
            )
            
            file_name = os.path.basename(file_path)
            self.log_message(f"Success: Histogram exported to {file_name}")
            
        except Exception as error:
            self.log_message(f"Error exporting histogram: {error}")
    
    def load_chain_code(self):
        """
        Load a previously exported chain code from JSON file, reconstruct the image,
        and display it for further analysis.
        """
        # Open native file open dialog filtered for JSON files
        file_path = filedialog.askopenfilename(
            title="Load Chain Code JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return

        try:
            # Parse JSON file to extract metadata and chain code
            with open(file_path, 'r', encoding='utf-8') as json_file:
                loaded_data = json.load(json_file)

            metadata = loaded_data.get("metadata", {})
            chain_code = loaded_data.get("chain_code", [])
            algorithm_name = metadata.get("algorithm", "").upper()  # e.g., "F4", "3OT"

            # Validate chain code is present
            if not chain_code:
                self.log_message("Error: JSON file does not contain a valid chain code.")
                return

            self.log_message(f"JSON loaded successfully.")
            self.log_message(f"Algorithm: {algorithm_name} | Chain length: {len(chain_code)}")

            # Build decoder function registry
            all_decoding_functions = list_functions(decoding_functions)
            decoder_registry = {}
            for function_name, function_obj in all_decoding_functions.items():
                # Match decoder functions naming pattern: DECODE_X_TO_MATRIX
                if function_name.startswith("DECODE_") and function_name.endswith("_TO_MATRIX"):
                    # Extract algorithm code (e.g., "F4" from "DECODE_F4_TO_MATRIX")
                    algorithm_code = function_name.replace("DECODE_", "").replace("_TO_MATRIX", "")
                    decoder_registry[algorithm_code] = function_obj

            # Reconstruct image using the appropriate decoder
            if algorithm_name in decoder_registry:
                self.log_message(f"Reconstructing image using {algorithm_name} decoder...")
                
                # Special handling for 3OT (returns closure status)
                if algorithm_name == "3OT":
                    reconstructed_image, is_properly_closed = decoder_registry[algorithm_name](chain_code)
                    if not is_properly_closed:
                        self.log_message("Warning: 3OT code did not close perfectly. Showing contour only.")
                else:
                    reconstructed_image = decoder_registry[algorithm_name](chain_code)

                # Cache reconstructed image and display
                self.binary_matrix = reconstructed_image
                self.display_on_canvas(self.binary_matrix, title=f"Reconstructed: {algorithm_name}")
                
                self.log_message("Image reconstruction successful.")
                self.log_message(f"Image dimensions: {self.binary_matrix.shape}")

                # Enable control buttons for analysis of reconstructed image
                change_button_state(self.button_outline, state="normal")
                change_button_state(self.button_chain_generator, state="normal")
                change_button_state(self.button_descriptor, state="normal")
                change_button_state(self.combobox_chain_type, state="normal")
                
            else:
                self.log_message(f"Error: No decoder available for algorithm '{algorithm_name}'.")

        except Exception as error:
            self.log_message(f"Error loading or decoding JSON file: {error}")

    def on_window_close(self):
        """
        Handle application shutdown: cleanup resources and exit gracefully.
        """
        self.quit()
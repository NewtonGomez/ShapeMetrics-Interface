import inspect
from customtkinter import *
from src.logic import chain_codes
# Importaciones necesarias para integrar Matplotlib con Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import datetime # Opcional: para poner la hora en el log

def list_chain_codes(modulo):
    # Retorna una lista de tuplas (nombre, objeto_funcion)
    funciones = inspect.getmembers(modulo, inspect.isfunction)
    
    # Retornar solo los nombres que no sean internos
    return [nombre for nombre, objeto in funciones if not nombre.startswith('_')]

def change_btn_state(boton, state):
    """
    Cambia el state del botón y ajusta su color de fondo manualmente
    para simular un 'disabled_fg_color'.
    """
    if state == "disabled":
        # Aplicamos los tonos grises (Claro para Light, Oscuro para Dark)
        boton.configure(state="disabled", fg_color=("#D1D1D1", "#3E3E3E"))
    else:
        # Restauramos el color azul original definido en tu JSON
        boton.configure(state="normal", fg_color=("#6ea6e7", "#4A90E2"))

class wPrincipal(CTkFrame):
    def __init__(self,root):
        super().__init__(root)
        self.root = root
        self.fuenteTitulos = ("Arial", 50)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.fuenteTexto = ("Arial", 20)
        self.widgets()

    def widgets(self):
        self.combobox_var = StringVar(value="Sin Seleccion")

        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1) # El panel derecho ocupa todo el alto

        # =========================================================================
        # 1. PANEL IZQUIERDO (ACCIONES)
        # =========================================================================
        self.frame_acciones = CTkFrame(self, width=220, corner_radius=0)
        self.frame_acciones.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        CTkLabel(self.frame_acciones, text="Acciones", font=self.fuenteTitulos).pack(pady=(20, 30))

        self.btn_cargar = CTkButton(self.frame_acciones, text="Cargar Imagen", command=self.upload_image, font=self.fuenteTitulos)
        self.btn_cargar.pack(pady=10, padx=20, fill="x")
        
        CTkLabel(self.frame_acciones, text=" ", font=self.fuenteTitulos).pack(pady=(20, 20))

        self.btn_contorno = CTkButton(self.frame_acciones, text="Ver Contorno", font=self.fuenteTitulos)
        self.btn_contorno.pack(pady=10, padx=20, fill="x")

        self.combobox = CTkComboBox(self.frame_acciones, values=list_chain_codes(chain_codes),
                                         fg_color="#3B8ED0", border_color="#3B8ED0", button_color="#3B8ED0",
                                         text_color="white", dropdown_text_color="white", dropdown_fg_color="#3B8ED0",
                                         corner_radius=6, border_width=2, height=60, font=self.fuenteTitulos)
        self.combobox.set("Sin Selección")
        self.combobox.pack(pady=10, padx=20, fill="x")

        self.btn_cadena = CTkButton(self.frame_acciones, text="Generar Cadena", font=self.fuenteTitulos)
        self.btn_cadena.pack(pady=10, padx=20, fill="x")

        self.btn_descriptor = CTkButton(self.frame_acciones, text="Descriptor", font=self.fuenteTitulos)
        self.btn_descriptor.pack(pady=10, padx=20, fill="x")

        self.btn_compresion = CTkButton(self.frame_acciones, text="Compresion", font=self.fuenteTitulos)
        self.btn_compresion.pack(pady=10, padx=20, fill="x")

        self.frame_visualizacion = CTkFrame(self)
        self.frame_visualizacion.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.frame_visualizacion.grid_rowconfigure(0, weight=1) # El canvas ocupa la mayoría
        self.frame_visualizacion.grid_columnconfigure(0, weight=1)

        # ---------------------------------------------------------
        # A. EL CANVAS DE MATPLOTLIB
        # ---------------------------------------------------------
        # Necesitamos un marco dedicado para el canvas
        self.frame_canvas = CTkFrame(self.frame_visualizacion, fg_color="transparent")
        self.frame_canvas.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Inicializamos el canvas vacío (sin imagen aún)
        self.canvas_matplotlib = None
        
        # Label placeholder antes de cargar imagen
        self.label_canvas_placeholder = CTkLabel(self.frame_canvas, text="Cargue una imagen para visualizar", 
                                                    font=("Roboto", 18), text_color="gray")
        self.label_canvas_placeholder.pack(expand=True)

        self.textbox_log = CTkTextbox(self.frame_visualizacion, width=800, height=200, corner_radius=10,
                                         border_width=2, border_color="gray", font=("Consolas", 12))
        self.textbox_log.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Hacemos que el log sea de solo lectura por defecto
        self.textbox_log.configure(state="disabled") 
        
        # Mensaje de bienvenida inicial en el Log
        self.log_message("Sistema iniciado. Listo para procesar imágenes.")

    def log_message(self, message):
            """Función helper para escribir en el log abajo"""
            # 1. Habilitar la edición temporalmente
            self.textbox_log.configure(state="normal")
            
            # 2. Obtener hora actual (opcional)
            timestamp = datetime.datetime.now().strftime("[%H:%M:%S] ")
            
            # 3. Insertar el mensaje al final
            self.textbox_log.insert("end", timestamp + message + "\n")
            
            # 4. Auto-scroll al final para ver el último mensaje
            self.textbox_log.see("end") 
            
            # 5. Volver a deshabilitar la edición para el usuario
            self.textbox_log.configure(state="disabled")

    def upload_image(self):
        change_btn_state(self.btn_outline, state="normal")
        change_btn_state(self.btn_chain_generator, state="normal")
        change_btn_state(self.btn_descriptor, state="normal")
        change_btn_state(self.btn_compressor, state="normal")
        change_btn_state(self.cmbx_chain_class, state="normal")
        pass

    def generate_chain(self):
        type_code = self.combobox_var.get()
        if type_code != "Sin Seleccion":
            print(type_code)

    def close(self):
        self.quit()
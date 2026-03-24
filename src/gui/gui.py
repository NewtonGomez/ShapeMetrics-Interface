import inspect
from customtkinter import *
from src.logic import chain_codes

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

        CTkLabel(self, text="Acciones", font=self.fuenteTitulos).grid(row=1, column=1, sticky=NSEW, pady=50, padx=50)
        CTkButton(self, text='Cargar Imagen', font=self.fuenteTitulos, compound='left', command=self.upload_image).grid(row=2, column=1, sticky=NSEW, pady=10, padx=50)

        CTkLabel(self, text=" ", font=self.fuenteTitulos).grid(row=3, column=1, sticky=NSEW, pady=50, padx=50)

        self.btn_outline = CTkButton(self, text='Ver Contorno', font=self.fuenteTitulos, compound='left', command=self.upload_image)
        self.btn_outline.grid(row=4, column=1, sticky=NSEW, pady=10, padx=50)
        change_btn_state(self.btn_outline, state="disabled")

        self.cmbx_chain_class = CTkComboBox(self, values=list_chain_codes(chain_codes), font=self.fuenteTitulos, variable=self.combobox_var, height=50)
        self.cmbx_chain_class.grid(row=5, column=1, sticky=NSEW, pady=10, padx=50)
        change_btn_state(self.cmbx_chain_class, state="disabled")
        
        self.btn_chain_generator = CTkButton(self, text='Generar Cadena', font=self.fuenteTitulos, compound='left', command=self.generate_chain)
        self.btn_chain_generator.grid(row=6, column=1, sticky=NSEW, pady=10, padx=50)
        change_btn_state(self.btn_chain_generator, state="disabled")
        
        self.btn_descriptor = CTkButton(self, text='Descriptor', font=self.fuenteTitulos, compound='left', command=self.upload_image, state="DISABLED")
        self.btn_descriptor.grid(row=7, column=1, sticky=NSEW, pady=10, padx=50)
        change_btn_state(self.btn_descriptor, state="disabled")
        
        self.btn_compressor = CTkButton(self, text='Compresion', font=self.fuenteTitulos, compound='left', command=self.upload_image, state="DISABLED")
        self.btn_compressor.grid(row=8, column=1, sticky=NSEW, pady=10, padx=50)
        change_btn_state(self.btn_compressor, state="disabled")

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
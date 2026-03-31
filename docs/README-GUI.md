# README-GUI: Documentación de la Interfaz Gráfica

## Descripción General

El módulo `src/gui/main_window.py` implementa la interfaz gráfica de usuario (GUI) de ShapeMetrics-Interface utilizando CustomTkinter. Proporciona una experiencia interactiva para cargar imágenes, procesar códigos de cadena de Freeman y analizar propiedades morfológicas de formas digitales.

La interfaz utiliza un diseño de dos paneles:
- **Panel izquierdo**: Controles y acciones del usuario
- **Panel derecho**: Visualización de resultados y registro de eventos

---

## Arquitectura de la Interfaz

### Estructura de Clases

#### Clase `MainWindow`

Hereda de `CTkFrame` y representa la ventana principal de la aplicación. Gestiona:

- **Datos de procesamiento**: matrices binarias, códigos de cadena, distribuciones de probabilidad
- **Estado de controles**: habilitación/deshabilitación de botones según el contexto
- **Visualización**: renderización de imágenes, histogramas y gráficos en Matplotlib
- **Interacción**: respuesta a eventos del usuario (clics, selecciones, carga de archivos)

### Estructura de Datos Internas

```python
self.binary_matrix      # np.ndarray: Imagen binaria procesada
self.current_chain      # list: Secuencia actual de códigos de cadena
self.current_probability # dict: Distribución de probabilidad de símbolos
self.image_perimeter    # float: Perímetro calculado del contorno
self.current_entropy    # float: Entropía de Shannon
self.image_histogram    # Figure: Figura de Matplotlib almacenada en caché
```

---

## Componentes de la Interfaz

### 1. Barra de Menús

Implementada mediante `create_menu_bar()`, contiene tres menús principales:

#### Menú "Files" (Archivos)
- **Load Image**: Abre un diálogo para cargar una imagen
- **Load Chain Code**: Carga un código de cadena desde un archivo JSON
- **Save Chain Code**: Exporta el código de cadena actual a JSON
- **Save Histogram**: Exporta el histograma a formato PNG/PDF/JPEG

#### Menú "Tools" (Herramientas)
- **Calc Contour**: Calcula y visualiza el contorno de la forma
- **Calc Descriptor**: Calcula descriptores geométricos
- **Chain Codes**: Submenu dinámico con algoritmos disponibles
- **Generate Histogram**: Genera distribución de frecuencias

#### Menú "Help" (Ayuda)
Reservado para documentación y soporte

### 2. Panel Lateral Izquierdo (Actions Frame)

Contiene controles interactivos organizados verticalmente:

#### Botones de Acción

| Botón | Comando | Estado Inicial | Dependencias |
|-------|---------|---|---|
| **Load Image** | `upload_image()` | Habilitado | Ninguna |
| **View Contour** | `process_outline()` | **Deshabilitado** | Imagen cargada |
| **Generate Chain** | `generate_chain()` | **Deshabilitado** | Imagen cargada + Algoritmo seleccionado |
| **Descriptor** | `generate_entropy()` | **Deshabilitado** | Código de cadena generado |
| **Compression** | `arithmetic_compression()` | **Deshabilitado** | Histograma generado |

#### ComboBox de Selección

Desplegable dinámico que lista los algoritmos de códigos de cadena disponibles en `src/logic/chain_codes.py`. Se puebla automáticamente mediante `list_functions(chain_codes)`.

### 3. Panel Derecho (Visualization Frame)

Área de visualización dividida en dos secciones:

#### Lienzo de Matplotlib
- Incrustado en CustomTkinter mediante `FigureCanvasTkAgg`
- Muestra:
  - Imágenes cargadas en escala de grises
  - Contornos superpuestos en color rojo
  - Histogramas de frecuencia y probabilidad
- Tema oscuro adaptado automáticamente

#### Cuadro de Texto de Registro
- Log de eventos con marca de tiempo
- Mensajes del sistema, errores y resultados
- Desplazamiento automático hacia el final
- Modo lectura por defecto (edición restringida)

---

## Flujo de Trabajo Principal

### 1. Carga de Imagen

```
Usuario selecciona "Load Image"
    ↓
upload_image()
    ↓
Diálogo de archivo (filtro: *.png, *.jpg, *.jpeg, *.bmp, *.tiff, *.gif)
    ↓
tools.process_and_binarize(file_path)
    ↓
Conversion: RGB → Escala de grises → Binaria (0-255)
    ↓
display_on_canvas() + Habilitar controles
```

**Variables afectadas:**
- `self.binary_matrix`: Se rellena con la imagen binaria procesada

### 2. Visualización de Contorno

```
Usuario selecciona "View Contour"
    ↓
process_outline()
    ↓
tools.find_outline(self.binary_matrix)
    ↓
Retorna: {"outline_matrix": ..., "perimeter": ...}
    ↓
display_on_canvas(base_matrix, overlay_matrix, overlay_color="red")
```

**Variables afectadas:**
- `self.image_perimeter`: Se establece con el perímetro calculado

### 3. Generación de Código de Cadena

```
Usuario selecciona algoritmo (ej: CHAIN_F4) y presiona "Generate Chain"
    ↓
generate_chain()
    ↓
Recupera función de self.chain_code_functions
    ↓
algorithm_function(self.binary_matrix) → lista de códigos
    ↓
Almacena resultado y registra longitud
```

**Variables afectadas:**
- `self.current_chain`: Lista de símbolos de código de cadena

### 4. Generación de Histograma

```
Usuario presiona "Generate Histogram"
    ↓
generate_histogram()
    ↓
Calcula frequencia: Contador(self.current_chain)
    ↓
Calcula probabilidad: P(símbolo) = frecuencia / total
    ↓
display_histogram_plot(freq_dict, prob_dict)
    ↓
tools.plot_histograms() → Figure de Matplotlib
    ↓
Renderiza en canvas + Habilita "Compression"
```

**Variables afectadas:**
- `self.current_probability`: Distribución de probabilidad
- `self.image_histogram`: Figura almacenada para exportación

### 5. Cálculo de Descriptores

```
Usuario presiona "Descriptor"
    ↓
generate_entropy()
    ↓
Calcula: 
  - Shannon Entropy H(X)
  - Perímetro (desde F4)
  - Área (píxeles)
  - Perímetro de Contacto
  - Compacidad Discreta
  - Característica de Euler
    ↓
Genera reporte formateado
    ↓
log_message(report)
```

### 6. Análisis de Compresión

```
Usuario presiona "Compression"
    ↓
arithmetic_compression()
    ↓
Calcula:
  - Código Aritmético: bits_promedio = -Σ P(x) log₂(P(x))
  - Código Huffman: construcción del árbol + asignación de códigos
    ↓
Genera tabla de códigos Huffman
    ↓
Calcula bits totales para la cadena
    ↓
log_message(compression_report)
```

---

## Serialización y Persistencia

### Guardar Código de Cadena

```
Menú "Files" → "Save Chain Code"
    ↓
Diálogo de guardado
    ↓
Archivo JSON con metadatos e índices
```

**Archivo exportado incluye:**
- Metadatos: Algoritmo, fecha, dimensiones, perímetro
- Secuencia de códigos de cadena

### Cargar Código de Cadena

```
Menú "Files" → "Load Chain Code"
    ↓
Seleccionar archivo JSON
    ↓
Automáticamente detecta algoritmo y decodifica
    ↓
Imagen reconstruida mostrada en canvas
```

### Exportar Histograma

```
Menú "Files" → "Save Histogram"
    ↓
Seleccionar formato (PNG/PDF/JPEG)
    ↓
Archivo guardado con tema oscuro aplicado
```

---

## Notas de Uso

### Estados de Botones

- **Botones deshabilitados** (grises): Esperar a completar paso anterior
  - "View Contour" requiere imagen cargada
  - "Generate Chain" requiere imagen + algoritmo seleccionado
  - "Descriptor" requiere código de cadena
  - "Compression" requiere histograma

- **Botones habilitados** (azules): Listos para ejecutar

### Ventana de Registro (Log)

- Muestra todos los eventos con marca de tiempo
- Se desplaza automáticamente
- Usar para verificar que cada operación fue exitosa

### Combinaciones de Algoritmos

Puedes:
1. Cargar imagen → Generar F4 → Analizar
2. Cargar imagen → Generar F8 → Analizar
3. Cargar código JSON (F4) → Ver contorno → Generar descriptores
4. Cargar código F4 → Generar nuevo F8 desde la reconstruida

---

**Última actualización:** Marzo 2026

**Autores:** ENRIQUE GOMEZ, VICTORIA GALVAN
- **Botones habilitados**: #4A90E2 (azul temático)
- **Botones deshabilitados**: #3E3E3E (gris oscuro)
- **Overlay de contorno**: Rojo predeterminado (personalizable)
- **Texto**: Blanco (#FFFFFF)

### Fuentes

- **Títulos**: Arial 50px
- **Texto general**: Arial 20px
- **Log del sistema**: Consolas 25px

---

## Extensibilidad

### Agregar Nuevo Algoritmo

1. Implementar función en `src/logic/chain_codes.py`:
   ```python
   def chain_new_algorithm(binary_img):
       # Retorna: list de códigos
       return chain_result
   ```

2. Automáticamente aparecerá en el ComboBox mediante:
   ```python
   self.chain_code_functions = list_functions(chain_codes)
   ```

### Agregar Nuevo Decodificador

1. Implementar en `src/logic/decoding_functions.py`:
   ```python
   def decode_new_algorithm_to_matrix(chain_code):
       # Retorna: np.ndarray imagen reconstruida
       return reconstructed_image
   ```

2. Será descubierto automáticamente en `load_chain_code()`

---

## Referencias Técnicas

### Dependencias Utilizadas

- **customtkinter**: Interfaz moderna con tema
- **matplotlib**: Visualización de gráficos y imágenes
- **numpy**: Manipulación de matrices de imágenes
- **Pillow**: Carga y procesamiento de archivos de imagen
- **tkinter**: Diálogos de archivo nativos

### Convenciones de Código

- Métodos utilizar nombres descriptivos en snake_case
- Documentación mediante docstrings de triple comilla
- Validaciones al inicio de métodos
- Mensajes de log informativos para debugging

---

## Notas de Implementación

### Gestión de Memoria

- Canvas de Matplotlib anterior se destruye explícitamente: `canvas_matplotlib.get_tk_widget().destroy()`
- Figuras se almacenan en caché para exportación: `self.image_histogram`

### Compatibilidad Multiplataforma

- Diálogos de archivo utilizan `filedialog.askopenfilename()` (nativo por OS)
- Rutas se manejan con separadores nativos
- Timestamps sin zona horaria (local del sistema)

### Seguridad

- JSON se parsea y valida antes de usar
- Rutas de archivo se validan antes de abrir
- Estado de botones previene operaciones inválidas

---

**Última actualización:** Marzo 2026

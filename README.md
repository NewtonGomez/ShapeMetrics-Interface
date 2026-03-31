# ShapeMetrics-Interface

## Descripción

ShapeMetrics-Interface es una aplicación de escritorio desarrollada en Python que implementa algoritmos de procesamiento digital de imágenes para el análisis morfológico de formas. El proyecto integra técnicas avanzadas de codificación de cadenas de Freeman (Freeman Chain Codes) con una interfaz gráfica intuitiva basada en CustomTkinter, permitiendo a los usuarios analizar y caracterizar objetos binarios en imágenes digitales.

Esta herramienta fue desarrollada como producto académico para la asignatura de Nuevos Paradigmas Tecnológicos, implementando principios de procesamiento de imágenes, análisis de contornos y representación compacta de formas geométricas.

## Autores

- **ENRIQUE GOMEZ** - *ing.enrique_gomez@outlook.com*
- **VICTORIA GALVAN** - *galvand.victoria@gmail.com*

## Tabla de Contenidos

- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Módulos de Lógica](#módulos-de-lógica)
- [Interfaz Gráfica](#interfaz-gráfica)
- [Licencia](#licencia)

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Dependencias

El proyecto depende de las siguientes librerías:

| Librería | Versión | Propósito |
|----------|---------|-----------|
| customtkinter | 5.2.2 | Framework para interfaz gráfica moderna |
| numpy | 2.2.6 | Computación numérica y manipulación de arrays |
| Pillow | 12.0.0 | Procesamiento de imágenes digitales |
| matplotlib | 3.10.7 | Visualización de datos y gráficos |

## Instalación

### 1. Clonar o descargar el repositorio

```bash
git clone https://github.com/NewtonGomez/ShapeMetrics-Interface.git
```

### 2. Crear un entorno virtual (recomendado)

```bash
python -m venv venv
```

Activar el entorno virtual:

- **En macOS/Linux:**
```bash
source venv/bin/activate
```

- **En Windows:**
```bash
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Uso

Para ejecutar la aplicación:

```bash
python main.py
```

La aplicación abrirá una ventana gráfica desde la cual se pueden cargar imágenes binarias y procesar mediante los algoritmos implementados. La interfaz cuenta con un tema personalizado (tema oscuro por defecto) y utiliza el logo de la Universidad Autónoma de Aguascalientes como icono.

## Estructura del Proyecto

```
ShapeMetrics-Interface/
├── main.py                          # Punto de entrada principal de la aplicación
├── requirements.txt                 # Dependencias del proyecto
├── README.md                        # Este archivo
├── assets/                          # Recursos visuales y configuración
│   ├── img/                         # Imágenes e iconos
│   │   └── Logo_UAA__cropped_.ico  # Icono de la aplicación
│   └── json/                        # Configuraciones en formato JSON
│       └── custom_theme.json        # Tema personalizado para la interfaz
├── src/                             # Código fuente principal
│   ├── __init__.py                  # Inicializador del paquete
│   ├── gui/                         # Módulo de interfaz gráfica
│   │   ├── __init__.py
│   │   └── main_window.py          # Ventana principal de la aplicación
│   └── logic/                       # Módulo de lógica y algoritmos
│       ├── chain_codes.py          # Implementación de códigos de cadena de Freeman
│       ├── decoding_functions.py   # Funciones de decodificación de cadenas
│       └── tools.py                 # Funciones utilitarias diversos
├── tests/                           # Suite de pruebas unitarias
│   ├── test_ccs.py                 # Pruebas para códigos de cadena


```

### Descripción de Directorios Principales

#### `src/gui/`
Contiene la interfaz gráfica de usuario (GUI) desarrollada con CustomTkinter. Esta capa de presentación gestiona las interacciones del usuario, la visualización de resultados y la renderización de gráficos.

**Para más información sobre la implementación y funcionalidades de la interfaz gráfica, consulte:** [README-GUI.md](./docs/README-GUI.md)

#### `src/logic/`
Contiene los algoritmos de procesamiento digital de imágenes y análisis morfológico. Implementa técnicas avanzadas de codificación de cadenas y funciones relacionadas para el análisis de contornos y formas.

**Para una documentación detallada sobre los algoritmos implementados, consulte:** [README-LOGIC.md](./docs/README-LOGIC.md)

#### `assets/`
Almacena recursos estáticos del proyecto, incluyendo imágenes e iconos de la aplicación, así como archivos de configuración JSON para personalización de la interfaz.

#### `tests/`
Contiene la suite de pruebas unitarias para validar la correctitud de los algoritmos implementados.

## Módulos de Lógica

El módulo `src/logic/` implementa los algoritmos fundamentales del proyecto. Para comprender en detalle el funcionamiento de cada algoritmo, incluyendo:

- **Códigos de Cadena de Freeman (4-direccional y 8-direccional)**
- **Funciones de decodificación y análisis de contornos**
- **Herramientas auxiliares de procesamiento de imágenes**

**Consulte la documentación completa:** [README-LOGIC.md](./docs/README-LOGIC.md)

### Documentación Especializada

Para profundizar en temas específicos:

| Documento | Contenido |
|-----------|----------|
| [README-CHAIN-CODES.md](./docs/README-CHAIN-CODES.md) | Algoritmos detallados de codificación Freeman (F4, F8, AF8, VCC, 3OT) |
| [README-TOOLS.md](./docs/README-TOOLS.md) | Funciones de procesamiento, descriptores morfológicos, entropía y compresión |
| [README-DECODING.md](./docs/README-DECODING.md) | Algoritmos inversos para reconstrucción de imágenes desde códigos |

## Interfaz Gráfica

La interfaz gráfica proporciona una experiencia interactiva para trabajar con los algoritmos. Para detalles sobre:

- **Cómo cargar y procesar imágenes**
- **Cómo utilizar cada funcionalidad disponible**
- **Descripción de componentes visuales**
- **Guía de usuario de la aplicación**

**Consulte la documentación completa:** [README-GUI.md](./docs/README-GUI.md)

## Licencia

Este proyecto se distribuye bajo una licencia específica. Para conocer los términos y condiciones, consulte: [LICENSE](./LICENSE)

---

**Nota:** Este proyecto fue desarrollado como trabajo académico para la Universidad Autónoma de Aguascalientes. Última actualización: Marzo 2026.

# README-LOGIC: Documentación del Módulo de Lógica

## Descripción General

El módulo `src/logic/` contiene la implementación de algoritmos fundamentales para el procesamiento digital de imágenes y análisis morfológico de formas. Este módulo es el núcleo matemático de ShapeMetrics-Interface, integrando técnicas avanzadas de:

- **Codificación de Cadenas de Freeman**: Representación compacta de contornos
- **Procesamiento de Imágenes**: Binarización, detección de contornos, análisis de conectividad
- **Descriptores Morfológicos**: Cálculo de propiedades geométricas e información-teóricas
- **Compresión de Datos**: Análisis de compresión mediante códigos aritmético y Huffman
- **Decodificación de Cadenas**: Reconstrucción de imágenes desde códigos

---

## Arquitectura del Módulo

```
src/logic/
├── chain_codes.py           # Generación de códigos de cadena Freeman
├── decoding_functions.py    # Decodificación y reconstrucción de imágenes
└── tools.py                 # Utilitarios de procesamiento e análisis
```

### Flujo de Procesamiento

```
Imagen Binaria
      ↓
[chain_codes.py] → Códigos de Cadena
      ↓
[tools.py] → Análisis (Entropía, Descriptores, Compresión)
      ↓
[GUI - Visualización y Registro]


Código de Cadena (JSON)
      ↓
[decoding_functions.py] → Matriz Reconstruida
      ↓
[tools.py] → Análisis
      ↓
[GUI - Visualización]
```

---

## Componentes Principales

### 1. `chain_codes.py`

**Propósito:** Implementar cinco variantes de códigos de cadena de Freeman para representación compacta de contornos.

**Algoritmos Disponibles:**

1. **F4**: 4-direccional (2 bits/símbolo) - Máxima simplicidad
2. **F8**: 8-direccional (3 bits/símbolo) - Mejor aproximación de suavidad
3. **AF8**: Codificación relativa de F8 - Mejor compresibilidad
4. **VCC**: Variable-Length Closure Code - Compresión media
5. **3OT**: Three-State - Máxima compresión

**Para documentación matemática completa:** Ver [README-CHAIN-CODES.md](./README-CHAIN-CODES.md)

---

### 2. `tools.py`

**Propósito:** Funciones auxiliares de procesamiento de imágenes y cálculo de descriptores.

**Categorías Principales:**

- **Procesamiento**: Binarización, detección de contornos, reordenamiento
- **Conectividad**: Componentes conexas, agujeros topológicos
- **Descriptores**: Área, perímetro, compacidad, Euler
- **Información**: Entropía de Shannon, compresión Huffman y aritmética
- **Visualización**: Histogramas de frecuencia y probabilidad

**Para algoritmos matemáticos detallados:** Ver [README-TOOLS.md](./README-TOOLS.md)

---

### 3. `decoding_functions.py`

**Propósito:** Implementar algoritmos inversos para reconstruir imágenes desde códigos de cadena.

**Flujo de Decodificación:**

```
Código de Cadena (F4/F8/AF8/VCC/3OT)
           ↓
Conversión a formato base (F4 o F8)
           ↓
Dibujado de contorno + Bounding box
           ↓
Relleno de interior (Flood-Fill)
           ↓
Imagen Binaria Reconstruida
```

**Funciones Clave:**
- Conversiones: `af8_to_f8()`, `vcc_to_f4()`, `c3ot_to_f4()`
- Dibujado: `f4_to_matrix()`, `f8_to_matrix()`
- Relleno: `fill_shape()` (flood-fill 4-conectividad)
- Decodificadores: `decode_f4_to_matrix()`, `decode_f8_to_matrix()`, etc.

**Para algoritmos matemáticos detallados:** Ver [README-DECODING.md](./README-DECODING.md)

---

## Flujos de Trabajo Integrados

### Flujo 1: Codificación e Importación

```
1. Usuario cargaImagen
   ↓
   tools.process_and_binarize()
   ↓
2. Usuario selecciona algoritmo (F4/F8/AF8/VCC/3OT)
   ↓
   chain_codes.chain_xx()
   ↓
3. Código de cadena genera (lista de enteros)
   ↓
   tools.calculate_entropy()
   ↓
4. Análisis calculado (descriptores, compresión)
```

### Flujo 2: Decodificación y Reconstrucción

```
1. Usuario carga JSON con cadena
   ↓
2. Identifica algoritmo desde metadatos
   ↓
   decoding_functions.decode_XX_to_matrix()
   ↓
3. Imagen binaria reconstruida
   ↓
   tools.find_outline()
   ↓
4. Contorno detectado para análisis
```

### Flujo 3: Compresión

```
1. Código de cadena generado
   ↓
2. Histograma calculado
   ↓
   tools.plot_histograms()
   ↓
3. Distribución visualizada
   ↓
   tools.length_huffman_compression()
   tools.lenght_compression_arithmetic()
   ↓
4. Comparación de compresión
```

---

## Enlaces de Documentación Especializada

Para información detallada sobre los algoritmos matemáticos, funciones específicas, parámetros de configuración y casos especiales, consultar:

| Documento | Contenido |
|-----------|----------|
| [README-CHAIN-CODES.md](./README-CHAIN-CODES.md) | Algoritmos F4, F8, AF8, VCC, 3OT: pseudocódigo, ejemplos, análisis de compresión |
| [README-TOOLS.md](./README-TOOLS.md) | Procesamiento de imágenes, descriptores geométricos, entropía, compresión Huffman y aritmética |
| [README-DECODING.md](./README-DECODING.md) | Algoritmos inversos, conversiones de formatos, flood-fill, reconstrucción y validación |
| [README-GUI.md](./README-GUI.md) | Guía de uso de la interfaz gráfica |

---

**Última actualización:** Marzo 2026

**Autores:** ENRIQUE GOMEZ, VICTORIA GALVAN

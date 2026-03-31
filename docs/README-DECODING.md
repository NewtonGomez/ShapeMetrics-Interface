# README-DECODING: Algoritmos de Decodificación y Reconstrucción de Imágenes

## Descripción General

El módulo `decoding_functions.py` implementa los **algoritmos inversos** que permiten reconstruir imágenes binarias a partir de códigos de cadena de Freeman. Este proceso es crítico para:

- Validar códigos de cadena importados
- Recuperar imágenes originales desde representaciones compactas
- Verificar integridad de datos almacenados

El flujo general es:

$$\text{Código de Cadena} \to \text{Conversión a F4/F8} \to \text{Dibujar Contorno} \to \text{Llenar Forma} \to \text{Imagen Binaria}$$

---

## Arquitectura del Decodificador

### Capas de Procesamiento

```
┌─────────────────────────────────────────┐
│ Código Comprimido (AF8/VCC/3OT)        │
│ o Código Base (F4/F8)                  │
└─────────────────────┬───────────────────┘
                      ↓
┌─────────────────────────────────────────┐
│ CAPA 1: Conversión                      │
│ af8_to_f8 / vcc_to_f4 / c3ot_to_f4    │
└─────────────────────┬───────────────────┘
                      ↓
┌─────────────────────────────────────────┐
│ CAPA 2: Dibujado de Contorno           │
│ f4_to_matrix / f8_to_matrix            │
│ (Simula trayectoria + Bounding Box)    │
└─────────────────────┬───────────────────┘
                      ↓
┌─────────────────────────────────────────┐
│ CAPA 3: Relleno de Interior            │
│ fill_shape (Flood-Fill)                │
└─────────────────────┬───────────────────┘
                      ↓
┌─────────────────────────────────────────┐
│ Imagen Binaria Reconstruida            │
│ (Matriz 255 interior, 0 fondo)         │
└─────────────────────────────────────────┘
```

---

## 1. Funciones de Conversión Formato

### 1.1 Conversión AF8 → F8

#### Fundamento Matemático

AF8 codifica cambios **relativos** de dirección. Para recuperar F8 (direcciones **absolutas**):

$$F8[i] = (F8[i-1] + AF8[i]) \bmod 8$$

Donde la indexación es **cíclica**: $F8[-1] = F8[P-1]$ (último elemento)

**Indeterminación:** Sin conocer la dirección inicial $F8[-1]$, existen **8 posibles interpretaciones** de F8.

#### Estrategia de Resolución

Se prueban **todos los 8 valores iniciales posibles** y se valida:
1. El último valor de F8 debe coincidir con el valor inicial (cierre cíclico)
2. La trayectoria debe **cerrar perfectamente**: $\sum \vec{d}_{F8[i]} = \vec{0}$

#### Algoritmo

**Pseudocódigo:**
```
procedimiento af8_to_f8(cadena_af8):
    movimientos = {
        0:(0,1), 1:(1,1), 2:(1,0), 3:(1,-1),
        4:(0,-1), 5:(-1,-1), 6:(-1,0), 7:(-1,1)
    }
    
    // Probar los 8 posibles valores iniciales
    para dirección_inicial = 0 hasta 7:
        f8 = []
        anterior = dirección_inicial
        
        // Decodificar con esta semilla
        para símbolo_relativo en cadena_af8:
            actual = (anterior + símbolo_relativo) % 8
            f8.añadir(actual)
            anterior = actual
        
        // Validaciones de cierre
        si f8 no vacío Y f8[-1] == dirección_inicial:
            // Verificar si la trayectoria cierra
            x, y = 0, 0
            para dirección en f8:
                dx, dy = movimientos[dirección]
                x += dx
                y += dy
            
            si x == 0 Y y == 0:
                retornar f8  // Solución encontrada
    
    // Fallback: devolver mejor aproximación
    f8 = []
    anterior = 0
    para símbolo_relativo en cadena_af8:
        actual = (anterior + símbolo_relativo) % 8
        f8.añadir(actual)
        anterior = actual
    
    retornar f8
```

#### Ejemplo Práctico

**AF8 entrada**: `[1, 0, 1, 1, 0, 1, 1]`

**Prueba con dirección inicial = 0:**
- Elemento 0: $(0 + 1) \bmod 8 = 1$ → F8[0] = 1
- Elemento 1: $(1 + 0) \bmod 8 = 1$ → F8[1] = 1
- Elemento 2: $(1 + 1) \bmod 8 = 2$ → F8[2] = 2
- Elemento 3: $(2 + 1) \bmod 8 = 3$ → F8[3] = 3
- Elemento 4: $(3 + 0) \bmod 8 = 3$ → F8[4] = 3
- Elemento 5: $(3 + 1) \bmod 8 = 4$ → F8[5] = 4
- Elemento 6: $(4 + 1) \bmod 8 = 5$ → F8[6] = 5
- Validación: ¿F8[-1] (=5) == dirección_inicial (0)? **NO** → Rechazar

**Prueba con dirección inicial = 4:**
- ...cálculos similares...
- Resultado: F8 = `[5, 5, 6, 7, 7, 0, 1]`
- Validación: ¿F8[-1] (=1) == dirección_inicial (4)? **NO** → Rechazar

(**En casos reales, se encuentra una semilla que valida correctamente**)

### 1.2 Conversión VCC → F4

#### Fundamento Matemático

VCC codifica **cambios de dirección** en F4. La conversión usa una **tabla de transiciones**:

$$\begin{array}{c|cccc}
\text{(Dir Anterior, Símbolo VCC)} & \to & \text{Nueva Dirección} \\
\hline
(0, 0) & \to & 0 & \text{(continúa derecha)} \\
(0, 1) & \to & 1 & \text{(giro a abajo)} \\
(0, 2) & \to & 3 & \text{(giro a arriba)} \\
(0, 3) & \to & 0 & \text{(continúa derecha)} \\
(1, 1) & \to & 2 & \text{(giro a izquierda)} \\
\ldots & & & \\
\end{array}$$

#### Algoritmo

**Pseudocódigo:**
```
procedimiento vcc_to_f4(cadena_vcc, dirección_inicial=0):
    tabla_transiciones = {
        (0, 1): 1,  (0, 2): 3,  (0, 0): 0,
        (1, 1): 2,  (1, 2): 0,  (1, 3): 1,
        (2, 1): 3,  (2, 2): 1,  (2, 3): 2,
        (3, 1): 0,  (3, 2): 2,  (3, 3): 3
        // Nota: símbolo 0 (sin cambio) no aparece en tabla, implica repetir dirección
    }
    
    f4 = []
    dirección_anterior = dirección_inicial
    
    para símbolo_vcc en cadena_vcc:
        si símbolo_vcc == 0:
            nueva_dirección = dirección_anterior
        sino si (dirección_anterior, símbolo_vcc) en tabla_transiciones:
            nueva_dirección = tabla_transiciones[(dirección_anterior, símbolo_vcc)]
        sino:
            nueva_dirección = dirección_anterior  // Fallback
        
        f4.añadir(nueva_dirección)
        dirección_anterior = nueva_dirección
    
    retornar f4
```

#### Determinismo

A diferencia de AF8→F8, VCC→F4 es **determinístico** si se proporciona dirección inicial (típicamente 0).

### 1.3 Conversión 3OT → F4 (Más Complejo)

#### Fundamento Matemático - Ambigüedad Crítica

El símbolo `1` en 3OT es **ambiguo**. Puede significar:

- **Opción A**: Regresa a dirección de referencia
- **Opción B**: Giro izquierda: $(anterior + 1) \bmod 4$
- **Opción C**: Giro derecha: $(anterior + 3) \bmod 4$

El decodificador debe **probar combinaciones** para encontrar la que cierra la forma.

#### Estrategia Multi-Fase

Se ejecutan estrategias en orden de complejidad creciente:

**Fase 1: Interpretaciones Globales Simples**
- Todos los `1` = opción A (referencia)
- Todos los `1` = opción B (izquierda)
- Todos los `1` = opción C (derecha)

**Fase 2: Patrones Alternados**
- Alternancia: A, B, A, B, ...
- Alternancia: A, C, A, C, ...

**Fase 3: Tolerancia Relajada**
- Aceptar si cierra con distancia Manhattan ≤ 2

**Fase 4: Mejor Aproximación**
- Retornar la F4 que más cerca cierra (fallback)

#### Algoritmo Detallado

**Pseudocódigo:**
```
procedimiento c3ot_to_f4(cadena_3ot):
    si cadena_3ot vacía:
        retornar [], FALSO
    
    función simular(primer_paso, primer_giro_delta, elecciones_símbolo_1):
        """
        Simula decodificación con parámetros específicos.
        primer_paso: dirección inicial (0-3)
        primer_giro_delta: +1 (izquierda) o +3 (derecha) para primer cambio
        elecciones_símbolo_1: lista de decisiones para cada símbolo 1
                             (0=referencia, 1=+1, 2=+3)
        """
        f4 = [primer_paso]
        referencia = primer_paso
        anterior = primer_paso
        cambio_ocurrió = FALSO
        índice_elección = 0
        
        para símbolo en cadena_3ot:
            si símbolo == 0:
                actual = anterior  // Sin cambio: continúa
            
            sino si símbolo == 2 Y NO cambio_ocurrió:
                actual = (anterior + primer_giro_delta) % 4
                cambio_ocurrió = VERDADERO
                referencia = anterior
            
            sino si símbolo == 1:
                // SÍMBOLO AMBIGUO: usar tabla de elecciones
                elección = elecciones_símbolo_1[índice_elección] 
                           si índice_elección < longitud(elecciones_símbolo_1)
                           sino 0
                índice_elección += 1
                
                si elección == 0:
                    actual = referencia
                sino si elección == 1:
                    actual = (anterior + 1) % 4
                sino:
                    actual = (anterior + 3) % 4
                
                referencia = anterior
            
            sino si símbolo == 2:
                actual = (referencia + 2) % 4  // Opuesta a referencia
                referencia = anterior
            
            sino:
                actual = anterior  // Por defecto
            
            f4.añadir(actual)
            anterior = actual
        
        retornar f4
    
    // Contar símbolos 1 para determinar decisiones necesarias
    cantidad_unos = contar(1 en cadena_3ot)
    
    // FASE 1: Estrategias simples
    para estrategia en [todos_0, todos_1, todos_2]:
        para paso_inicial en rango(4):
            para delta_giro en [1, 3]:
                elecciones = generar_elecciones(estrategia, cantidad_unos)
                f4 = simular(paso_inicial, delta_giro, elecciones)
                si cierra_perfectamente(f4):
                    retornar f4, VERDADERO
    
    // FASE 2: Patrones alternados
    para patrón_alternancia en [A-B, A-C]:
        para paso_inicial en rango(4):
            para delta_giro en [1, 3]:
                elecciones = generar_patrón(patrón_alternancia, cantidad_unos)
                f4 = simular(paso_inicial, delta_giro, elecciones)
                si cierra_perfectamente(f4):
                    retornar f4, VERDADERO
    
    // FASE 3: Tolerancia relajada
    para paso_inicial en rango(4):
        para delta_giro en [1, 3]:
            para estrategia en [todos_0, todos_1, todos_2]:
                elecciones = generar_elecciones(estrategia, cantidad_unos)
                f4 = simular(paso_inicial, delta_giro, elecciones)
                si cierra_aprox(f4, tolerancia=2):
                    retornar f4, VERDADERO
    
    // FASE 4: Mejor aproximación
    mejor_f4 = NULO
    mejor_distancia = INFINITO
    
    para paso_inicial en rango(4):
        para delta_giro en [1, 3]:
            para estrategia en [todos_0, todos_1, todos_2]:
                elecciones = generar_elecciones(estrategia, cantidad_unos)
                f4 = simular(paso_inicial, delta_giro, elecciones)
                distancia = calcular_distancia_cierre(f4)
                
                si distancia < mejor_distancia:
                    mejor_distancia = distancia
                    mejor_f4 = f4
    
    retornar mejor_f4, FALSO  // No cierra perfectamente pero es mejor aproximación
```

#### Complejidad

Sin la ambigüedad, sería $O(P)$. Con ambigüedad:

$$\text{Complejidad} = O(8 \times 8 \times 3^n)$$

Donde $n$ = número de símbolos `1` en la cadena.

Para cadenas típicas ($n \ll P$), la fase de fallback usualmente resuelve rápidamente.

---

## 2. Funciones de Dibujado: Simulación de Trayectoria

### 2.1 F4 a Matriz

#### Proceso en Dos Fases

**Fase 1: Simulación de Trayectoria**

Partiendo de $(0, 0)$, se simulan todos los movimientos F4:

$$\vec{p}_i = \vec{p}_{i-1} + \vec{d}_{F4[i]}$$

Donde $\vec{d}$ es el vector de desplazamiento para cada dirección.

$$\text{Desplazamientos F4: } \begin{cases}
0 \to (1, 0) \\
1 \to (0, 1) \\
2 \to (-1, 0) \\
3 \to (0, -1)
\end{cases}$$

**Fase 2: Cálculo de Bounding Box**

$$\text{min\_x} = \min_i(p_{i,x}), \quad \max\_x = \max_i(p_{i,x})$$
$$\text{min\_y} = \min_i(p_{i,y}), \quad \max\_y = \max_i(p_{i,y})$$

$$\text{ancho} = \max\_x - \min\_x + 1$$
$$\text{alto} = \max\_y - \min\_y + 1$$

**Fase 3: Creación de Matriz**

Matriz de tamaño $(alto + 2 \cdot padding) \times (ancho + 2 \cdot padding)$

Mapeo de coordenadas lógicas a índices de matriz:

$$\text{col}_{matriz} = x - \min\_x + padding$$
$$\text{fila}_{matriz} = y - \min\_y + padding$$

Importante: En NumPy, `matriz[fila, col]` = `matriz[y, x]`

#### Algoritmo

**Pseudocódigo:**
```
procedimiento f4_to_matrix(cadena_f4, padding=10):
    desplazamientos = {0:(1,0), 1:(0,1), 2:(-1,0), 3:(0,-1)}
    
    // Fase 1: Simular trayectoria
    x, y = 0, 0
    coordenadas = [(x, y)]
    
    para dirección en cadena_f4:
        dx, dy = desplazamientos[dirección]
        x += dx
        y += dy
        coordenadas.añadir((x, y))
    
    // Fase 2: Bounding box
    xs = [coord[0] para coord en coordenadas]
    ys = [coord[1] para coord en coordenadas]
    
    min_x = mínimo(xs)
    max_x = máximo(xs)
    min_y = mínimo(ys)
    max_y = máximo(ys)
    
    ancho = max_x - min_x + 1
    alto = max_y - min_y + 1
    
    // Fase 3: Crear matriz
    altura_final = alto + 2 * padding
    ancho_final = ancho + 2 * padding
    
    matriz = ceros((altura_final, ancho_final), tipo=uint8)
    
    // Dibujar contorno
    para (coord_x, coord_y) en coordenadas:
        col_ajustada = coord_x - min_x + padding
        fila_ajustada = coord_y - min_y + padding
        
        // CRÍTICO: matriz[fila, col] en NumPy
        matriz[fila_ajustada, col_ajustada] = 255
    
    retornar matriz
```

#### Ejemplo Práctico

**F4 entrada**: `[0, 0, 1, 1, 2, 3, 3]` (perímetro 7)

**Simulación:**
| Paso | Dir | dx, dy | x, y |
|------|-----|--------|------|
| 0 | - | - | (0, 0) |
| 1 | 0 | (1, 0) | (1, 0) |
| 2 | 0 | (1, 0) | (2, 0) |
| 3 | 1 | (0, 1) | (2, 1) |
| 4 | 1 | (0, 1) | (2, 2) |
| 5 | 2 | (-1, 0) | (1, 2) |
| 6 | 3 | (0, -1) | (1, 1) |
| 7 | 3 | (0, -1) | (1, 0) |

**Bounding box**: 
- $\min_x = 0, \max_x = 2$ → ancho = 3
- $\min_y = 0, \max_y = 2$ → alto = 3
- Con padding=1: matriz de 5×5

### 2.2 F8 a Matriz

Idéntico a F4 pero con 8 direcciones:

$$\text{Desplazamientos F8: } \begin{cases}
0 \to (0, 1) & \text{(derecha)} \\
1 \to (1, 1) & \text{(abajo-derecha)} \\
2 \to (1, 0) & \text{(abajo)} \\
3 \to (1, -1) & \text{(abajo-izquierda)} \\
4 \to (0, -1) & \text{(izquierda)} \\
5 \to (-1, -1) & \text{(arriba-izquierda)} \\
6 \to (-1, 0) & \text{(arriba)} \\
7 \to (-1, 1) & \text{(arriba-derecha)}
\end{cases}$$

**Nota**: Los desplazamientos F8 en el código pueden variar en representación. Verificar implementación específica.

---

## 3. Algoritmo Flood-Fill: Relleno de Interior

### Fundamento Matemático

El algoritmo identifica la región **exterior** (fondo) usando conectividad 4-vecindario, luego invierte para marcar el **interior**.

#### Conectividad 4-Vecindario

Cada píxel $(r, c)$ tiene 4 vecinos:

$$\text{Vecinos}_{N4} = \{(r-1,c), (r+1,c), (r,c-1), (r,c+1)\}$$

### Algoritmo: Flood-Fill desde Borde

**Pseudocódigo:**
```
procedimiento fill_shape(matriz_binaria):
    filas, columnas = dimensiones(matriz_binaria)
    
    // Matriz para marcar píxeles exteriores
    exterior = ceros((filas, columnas), tipo=uint8)
    
    // Inicializar: marcar (0,0) como exterior
    pila = [(0, 0)]
    exterior[0, 0] = 255
    
    // Vecinos en 4-conectividad (N4)
    movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    // Flood-fill: propagar exterior desde (0, 0)
    mientras pila no vacía:
        fila, col = pila.pop()
        
        para (dr, dc) en movimientos:
            nueva_fila, nueva_col = fila + dr, col + dc
            
            // Validar límites
            si 0 <= nueva_fila < filas Y 0 <= nueva_col < columnas:
                // Si es píxel de fondo (0) sin marcar
                si matriz_binaria[nueva_fila, nueva_col] == 0 Y exterior[nueva_fila, nueva_col] == 0:
                    exterior[nueva_fila, nueva_col] = 255
                    pila.añadir((nueva_fila, nueva_col))
    
    // Invertir: interior son píxeles NO marcados como exterior
    imagen_llena = ceros_como(matriz_binaria)
    imagen_llena[exterior == 0] = 255
    
    retornar imagen_llena
```

### Propiedad Topológica

Para un contorno **cerrado**:

$$\text{Interior} = \{\text{Todos los píxeles}\} \setminus \text{Exterior}$$

$$\text{Pertenece al interior} \iff \text{No alcanzable desde borde}$$

### Complejidad

$$\text{Complejidad} = O(A)$$

Donde $A$ = área total (número de píxeles).

Cada píxel se procesa como máximo una vez.

### Ejemplo Gráfico

**Matriz (contorno de cuadrado):**
```
255 255 255 255 255
255   0   0   0 255
255   0   0   0 255
255   0   0   0 255
255 255 255 255 255
```

**Paso 1: Flood-fill desde (0,0)**
```
✓✓✓✓✓        (exterior marcado)
✓ . . . ✓
✓ . . . ✓
✓ . . . ✓
✓✓✓✓✓
```

**Paso 2: Invertir**
```
0 0 0 0 0
0 255 255 255 0
0 255 255 255 0
0 255 255 255 0
0 0 0 0 0
```

---

## 4. Funciones Decodificadores Principales

### 4.1 Decodificador F4

$$\text{Entrada: } F4 = [d_0, d_1, \ldots, d_{P-1}]$$

$$\text{Salida: } \text{Matriz binaria llena}$$

**Pasos:**
1. `f4_to_matrix(f4)` → Dibuja solo contorno
2. `fill_shape(contorno)` → Llena interior

```python
def decode_f4_to_matrix(f4_chain):
    contorno = f4_to_matrix(f4_chain)
    llena = fill_shape(contorno)
    return llena
```

### 4.2 Decodificador F8

Idéntico a F4 pero usando `f8_to_matrix`:

```python
def decode_f8_to_matrix(f8_chain):
    contorno = f8_to_matrix(f8_chain)
    llena = fill_shape(contorno)
    return llena
```

### 4.3 Decodificador AF8

**Pasos:**
1. `af8_to_f8(af8)` → Convierte a F8
2. `f8_to_matrix(f8)` → Dibuja contorno
3. `fill_shape(contorno)` → Llena interior

```python
def decode_af8_to_matrix(af8_chain):
    f8 = af8_to_f8(af8_chain)
    contorno = f8_to_matrix(f8)
    llena = fill_shape(contorno)
    return llena
```

### 4.4 Decodificador VCC

**Pasos:**
1. `vcc_to_f4(vcc)` → Convierte a F4
2. `f4_to_matrix(f4)` → Dibuja contorno
3. `fill_shape(contorno)` → Llena interior

```python
def decode_vcc_to_matrix(vcc_chain):
    f4 = vcc_to_f4(vcc_chain)
    contorno = f4_to_matrix(f4)
    llena = fill_shape(contorno)
    return llena
```

### 4.5 Decodificador 3OT

**Especial**: Retorna tupla `(matriz, es_cerrado)`

**Pasos:**
1. `c3ot_to_f4(3ot)` → Convierte a F4, retorna `(f4, es_cerrado)`
2. Si no cierra: retorna solo contorno
3. Si cierra: dibuja contorno y llena interior

```python
def decode_3ot_to_matrix(c3ot_chain):
    f4, es_cerrado = c3ot_to_f4(c3ot_chain)
    
    if not es_cerrado:
        contorno = f4_to_matrix(f4)
        return contorno, False
    
    contorno = f4_to_matrix(f4)
    llena = fill_shape(contorno)
    return llena, True
```

---

## 5. Funciones Utilitarias

### 5.1 `closes_f4_shape(f4_chain, tolerance=0)`

Valida si una cadena F4 forma un **contorno cerrado**.

#### Fórmula de Cierre

Una cadena cierra si la suma vectorial es cero:

$$\sum_{i=0}^{P-1} \vec{d}_{F4[i]} = (0, 0)$$

O equivalentemente (con tolerancia):

$$|\sum_{i=0}^{P-1} \vec{d}_{F4[i]}|_{\infty} \leq \text{tolerancia}$$

Donde $|\cdot|_{\infty}$ es la norma de Chebyshev (distancia Manhattan).

#### Algoritmo

```python
def closes_f4_shape(f4_chain, tolerance=0):
    x, y = 0, 0
    moves = {0:(1,0), 1:(0,1), 2:(-1,0), 3:(0,-1)}
    
    for direction in f4_chain:
        dx, dy = moves[direction]
        x += dx
        y += dy
    
    return (abs(x) + abs(y)) <= tolerance
```

### 5.2 Funciones de Solo Contorno

Retornan solo el contorno sin relleno:

```python
def get_contour_f4(f4_chain):
    return f4_to_matrix(f4_chain)

def get_contour_f8(f8_chain):
    return f8_to_matrix(f8_chain)
```

---

## Validaciones y Casos Especiales

### Cadenas Mal Formadas

| Problema | Comportamiento | Solución |
|----------|---|---|
| Cadena vacía | Matriz vacía o [[0]] | Validar antes de decodificar |
| No cierra | Contorno abierto | 3OT retorna `(contorno, False)` |
| Ambigua (AF8, 3OT) | Mejor aproximación | Fases de resolución en orden |

### Índices y Convenciones

**Crítico para evitar transposiciones:**

- Coordenadas lógicas: $(x, y)$ = (horizontal, vertical)
- Índices NumPy: `matriz[fila, col]` = `matriz[y, x]`
- Mapeo: `fila = y`, `col = x`

### Bounding Box Óptimo

Sin padding, la matriz tiene tamaño:

$$\text{Altura} = \max_y - \min_y + 1$$
$$\text{Ancho} = \max_x - \min_x + 1$$

El padding es **opcional** para separación visual:

$$\text{Altura Final} = \text{Altura} + 2 \cdot padding$$
$$\text{Ancho Final} = \text{Ancho} + 2 \cdot padding$$

---

## Integración en la GUI

### Flujo desde `main_window.py`

```python
# Cargar JSON con cadena
loaded_data = json.load(json_file)
algo_name = loaded_data["metadata"]["algorithm"]  # ej: "CHAIN_F4"
chain_code = loaded_data["chain_code"]

# Buscar decodificador
decoder = decoder_registry.get(algo_name)

# Decodificar
if algo_name == "CHAIN_3OT":
    imagen, es_cerrado = decoder(chain_code)
    if not es_cerrado:
        log("Advertencia: 3OT no cerró perfectamente")
else:
    imagen = decoder(chain_code)

# Mostrar
self.display_on_canvas(imagen)
```

---

## Complejidad Computacional

| Operación | Complejidad | Nota |
|-----------|-------------|------|
| `af8_to_f8` | $O(8 \times P)$ | Prueba 8 semillas |
| `vcc_to_f4` | $O(P)$ | Determinístico |
| `c3ot_to_f4` | $O(8 \times 8 \times 3^n)$ | $n$ = cantidad de 1s |
| `f4_to_matrix` | $O(P)$ | Simula trayectoria |
| `f8_to_matrix` | $O(P)$ | Simula trayectoria |
| `fill_shape` | $O(A)$ | $A$ = área total |
| **Total decodificación** | $O(P + A)$ | Dominated por lleno |

Para objetos típicos: **Lineal en perímetro + área**

---

## Referencias Matemáticas

### Topología Digital

- Morgenthaler, D. G., & Rosenfeld, A. (1981). "Surfaces in three-dimensional digital images." 
  *Information and Control*, 51(3), 227-247.

### Algoritmos de Flood-Fill

- Foley, J. D., van Dam, A., Feiner, S. K., & Hughes, J. F. (1990). 
  *Computer Graphics: Principles and Practice* (2nd ed.). Addison-Wesley.

### Códigos de Freeman y Decodificación

- Freeman, H. (1974). "Computer processing of line-drawing images." 
  *ACM Computing Surveys*, 6(1), 57-97.

---

**Última actualización:** Marzo 2026

**Autores:** ENRIQUE GOMEZ, VICTORIA GALVAN

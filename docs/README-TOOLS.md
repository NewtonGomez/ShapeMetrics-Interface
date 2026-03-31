# README-TOOLS: Algoritmos de Procesamiento e Análisis en tools.py

## Descripción General

El módulo `tools.py` contiene funciones auxiliares fundamentales para:

1. **Procesamiento de Imágenes**: Carga, binarización, padding
2. **Análisis de Conectividad**: Componentes conexas, agujeros
3. **Detección de Contornos**: Búsqueda de bordes, rastreo ordenado
4. **Descriptores Morfológicos**: Área, perímetro, compacidad, Euler
5. **Teoría de Información**: Entropía de Shannon, compresión Huffman y aritmética
6. **Visualización**: Generación de histogramas académicos

---

## 1. Procesamiento de Imágenes

### 1.1 Binarización con Padding

#### Función: `process_and_binarize(filename, threshold=128, padding=2)`

**Fundamentación Matemática**

Convierte una imagen RGB a imagen binaria mediante umbralización:

$$\text{Imagen Binaria}[i,j] = \begin{cases} 
255 & \text{si } \text{Imagen Gris}[i,j] > \text{threshold} \\
0 & \text{en caso contrario}
\end{cases}$$

**Necesidad de Padding**

Sin padding, objetos que tocan los bordes de la imagen pueden causar detección incorrecta de contornos. El padding asegura que **todo objeto está rodeado de fondo**:

$$\text{Imagen Padded} = \text{pad}(\text{Imagen Binaria}, \text{padding}, \text{modo}=\text{cero})$$

**Pasos del Algoritmo**

```
procedimiento process_and_binarize(archivo, threshold=128, padding=2):
    1. Abrir imagen desde archivo
    2. imagen_gris = convertir_a_escala_grises(imagen)
    3. matriz_numpy = convertir_a_array(imagen_gris)
    
    4. // Umbralización
    5. matriz_binaria = (matriz_numpy > threshold) * 255
    
    6. // Padding
    7. si padding > 0:
    8.     matriz_padded = np.pad(
    9.         matriz_binaria, 
    10.        padding, 
    11.        modo='constante', 
    12.        valores_constante=0
    13.    )
    14.    retornar matriz_padded
    15. sino:
    16.    retornar matriz_binaria
```

**Ejemplo**

**Imagen original (5×5):**
```
200 100  50  80 150
190 220  60  70 140
100 180 200 190 100
80  60  200 210 90
150 140 100 120 200
```

**Con threshold=128:**
```
255   0   0   0 255
255 255   0   0 255
  0 255 255 255   0
  0   0 255 255   0
255 255   0   0 255
```

**Con padding=1:**
```
  0   0   0   0   0   0   0
  0 255   0   0   0 255   0
  0 255 255   0   0 255   0
  0   0 255 255 255   0   0
  0   0   0 255 255   0   0
  0 255 255   0   0 255   0
  0   0   0   0   0   0   0
```

---

## 2. Análisis de Conectividad

### 2.1 Componentes Conexas

#### Función: `connected_components(matrix, neighbor=4) → int`

**Concepto Fundamental**

Define vecindarios para conectividad:

$$\text{Vecinos}_{N4}[i,j] = \{(i-1,j), (i+1,j), (i,j-1), (i,j+1)\}$$

$$\text{Vecinos}_{N8}[i,j] = \text{Vecinos}_{N4} \cup \{(i-1,j-1), (i-1,j+1), (i+1,j-1), (i+1,j+1)\}$$

**Componente Conexa**

Conjunto maximal de píxeles de objeto unidos por vecindario:

$$C_k = \{p_1, p_2, \ldots, p_n\} : \forall i, \exists \text{ camino conectado desde } p_i \text{ a otros}$$

**Algoritmo: Flood-Fill con DFS**

```
procedimiento connected_components(matriz, neighbor=4):
    filas, columnas = dimensiones(matriz)
    visitados = matriz_ceros(filas, columnas)
    num_componentes = 0
    
    // Definir movimientos según conectividad
    si neighbor == 4:
        movimientos = [(0,1), (0,-1), (-1,0), (1,0)]
    sino si neighbor == 8:
        movimientos = movimientos_N4 + [(-1,-1), (-1,1), (1,-1), (1,1)]
    
    // Escanear toda la matriz
    para i = 1 hasta filas-2:
        para j = 1 hasta columnas-2:
            // Encontrar píxel de objeto no visitado
            si matriz[i][j] == 1 Y NO visitados[i][j]:
                num_componentes += 1
                
                // DFS desde este píxel
                pila = [(i, j)]
                visitados[i][j] = VERDADERO
                
                mientras pila no vacía:
                    fila_actual, col_actual = pila.pop()
                    
                    // Revisar todos los vecinos
                    para (dr, dc) en movimientos:
                        próxima_fila = fila_actual + dr
                        próxima_col = col_actual + dc
                        
                        // Validar límites y estado
                        si (0 <= próxima_fila < filas Y 
                            0 <= próxima_col < columnas Y
                            matriz[próxima_fila][próxima_col] == 1 Y
                            NO visitados[próxima_fila][próxima_col]):
                            
                            visitados[próxima_fila][próxima_col] = VERDADERO
                            pila.añadir((próxima_fila, próxima_col))
    
    retornar num_componentes
```

**Complejidad**

$$\text{Complejidad} = O(filas \times columnas)$$

Cada píxel se procesa como máximo una vez.

**Ejemplo Práctico**

```
Matriz (1=objeto, 0=fondo):
1 1 0 0
1 1 0 1
0 0 0 1
1 0 0 0

Componentes (N4):
A A 0 0
A A 0 B
0 0 0 B
C 0 0 0

Resultado: 3 componentes (A, B, C)

Con N8:
A A 0 0
A A 0 A
0 0 0 A
C 0 0 0

Resultado: 2 componentes (A, C)
```

### 2.2 Conteo de Agujeros

#### Función: `calculate_holes(binary_matrix) → int`

**Concepto Topológico**

Un agujero (hole) es una región de fondo **completamente encerrada** por píxeles de objeto.

**Algoritmo en Dos Fases**

**Fase 1: Marcar Fondo Exterior**

Flood-fill desde los bordes de la imagen usando N4-conectividad:

```
procedimiento marcar_exterior(matriz):
    filas, columnas = dimensiones(matriz)
    exterior = matriz_falso(filas, columnas)
    pila = []
    
    // Inicializar desde bordes (N4)
    para i en rango(filas):
        para j en [0, columnas-1]:  // Columnas izquierda y derecha
            si matriz[i][j] == 0 Y NO exterior[i][j]:
                exterior[i][j] = VERDADERO
                pila.añadir((i, j))
    
    para j en rango(columnas):
        para i en [0, filas-1]:  // Filas superior e inferior
            si matriz[i][j] == 0 Y NO exterior[i][j]:
                exterior[i][j] = VERDADERO
                pila.añadir((i, j))
    
    // Flood-fill desde bordes
    movimientos = [(-1,0), (1,0), (0,-1), (0,1)]  // N4
    
    mientras pila no vacía:
        fila, col = pila.pop()
        para (dr, dc) en movimientos:
            próxima_fila, próxima_col = fila + dr, col + dc
            si (0 <= próxima_fila < filas Y
                0 <= próxima_col < columnas Y
                matriz[próxima_fila][próxima_col] == 0 Y
                NO exterior[próxima_fila][próxima_col]):
                
                exterior[próxima_fila][próxima_col] = VERDADERO
                pila.añadir((próxima_fila, próxima_col))
    
    retornar exterior
```

**Fase 2: Contar Componentes de Píxeles No Marcados**

Los píxeles de fondo NO marcados son agujeros. Se cuentan sus componentes conexas (N4):

$$\text{pixels_agujeros} = \{p : \text{matriz}[p] == 0 \text{ Y NO exterior}[p]\}$$

$$H = \text{número de componentes conexas en pixels_agujeros}$$

**Ejemplo Visual**

**Matriz 7×7 con 1 agujero:**
```
Matriz:            Exterior (E):      Agujeros:
1 1 1 1 1 1 1      E E E E E E E      . . . . . . .
1 0 1 1 1 0 1      E . E E E . E      . H . . . H .
1 1 1 1 1 1 1      E E E E E E E      . . . . . . .
1 1 1 0 0 0 1      E E E . . . E      . . . A A A .
1 1 1 0 0 0 1      E E E . . . E      . . . A A A .
1 1 1 0 0 0 1      E E E . . . E      . . . A A A .
1 1 1 1 1 1 1      E E E E E E E      . . . . . . .

Resultado:
- H (píxeles 1-1-1 en borde) = No son agujeros (alcanzables desde exterior)
- A (píxeles en el centro) = 1 agujero (no alcanzable desde exterior)
Total: 1 agujero
```

---

## 3. Detección de Contornos

### 3.1 Búsqueda de Bordes

#### Función: `find_outline(matrix) → dict`

**Concepto: Píxel de Borde**

Un píxel de objeto es **píxel de borde** si al menos un vecino N4 es píxel de fondo:

$$\text{IsBorde}[i,j] = \begin{cases}
\text{VERDADERO} & \text{si } \text{matriz}[i,j] = 1 \text{ Y } \sum_{k=0}^{3} \text{Vecino}_{N4}[k] < 4 \\
\text{FALSO} & \text{en caso contrario}
\end{cases}$$

**Suma de Vecindario N4**

$$\text{SumaVecinos}[i,j] = \text{matriz}[i-1,j] + \text{matriz}[i+1,j] + \text{matriz}[i,j-1] + \text{matriz}[i,j+1]$$

- Si suma = 4: píxel interior (rodeado de objeto)
- Si suma < 4: píxel de borde (tiene vecino fondo)

**Algoritmo de Búsqueda**

```
procedimiento find_outline(matriz):
    filas, columnas = dimensiones(matriz)
    outline = matriz_ceros(filas, columnas)
    conteo_outline = 0
    
    // Normalizar entrada (0/1 o 0/255)
    norm = matriz si max(matriz) <= 1 sino (matriz > 127)
    
    // Fase 1: Identificar píxeles de borde
    para i = 1 hasta filas-2:
        para j = 1 hasta columnas-2:
            si norm[i][j] == 0:
                continuar  // Saltar píxeles de fondo
            
            suma_vecinos = norm[i-1,j] + norm[i+1,j] + norm[i,j-1] + norm[i,j+1]
            
            si suma_vecinos < 4:
                outline[i][j] = 1
                conteo_outline += 1
    
    // Fase 2: Rastreo ordenado (Moore Neighborhood Tracing)
    contorno_ordenado = []
    inicio = NULO
    
    // Encontrar punto de inicio
    para i = 0 hasta filas-1:
        para j = 0 hasta columnas-1:
            si outline[i][j] == 1:
                inicio = (i, j)
                romper
        si inicio != NULO:
            romper
    
    si inicio != NULO:
        vecinos_8 = [
            (0,1), (1,1), (1,0), (1,-1),
            (0,-1), (-1,-1), (-1,0), (-1,1)
        ]
        visitados = conjunto_vacío()
        fila_actual, col_actual = inicio
        dirección_anterior = 6  // Comienza "mirando" arriba
        
        contorno_ordenado.añadir((col_actual, fila_actual))  // (x, y)
        visitados.añadir((fila_actual, col_actual))
        
        // Rastreo por hasta 2*conteo_outline iteraciones
        para _ = 1 hasta conteo_outline * 2:
            encontrado = FALSO
            inicio_búsqueda = (dirección_anterior + 5) % 8  // Busca diagonal-atrás primero
            
            para k = 0 hasta 7:
                dir_índice = (inicio_búsqueda + k) % 8
                dr, dc = vecinos_8[dir_índice]
                próxima_fila = fila_actual + dr
                próxima_col = col_actual + dc
                
                si (0 <= próxima_fila < filas Y
                    0 <= próxima_col < columnas Y
                    outline[próxima_fila][próxima_col] == 1 Y
                    (próxima_fila, próxima_col) NO en visitados):
                    
                    contorno_ordenado.añadir((próxima_col, próxima_fila))  // (x, y)
                    visitados.añadir((próxima_fila, próxima_col))
                    dirección_anterior = dir_índice
                    fila_actual, col_actual = próxima_fila, próxima_col
                    encontrado = VERDADERO
                    romper
            
            si NO encontrado:
                romper
    
    // Restaurar rango de valores original
    outline_matrix = outline * 255 si max(matriz) > 1 sino outline
    
    retornar {
        "contour": contorno_ordenado,
        "perimeter": conteo_outline,
        "outline_matrix": outline_matrix
    }
```

**Complejidad**

- Fase 1 (búsqueda de bordes): $O(\text{filas} \times \text{columnas})$
- Fase 2 (rastreo): $O(P)$ donde $P$ = perímetro

**Total: $O(A)$ donde $A$ = área**

### 3.2 Importancia: Moore Neighborhood Tracing

El rastreo de Moore garantiza que los puntos del contorno se **ordenen secuencialmente**, crucial para:
- Generación de códigos de cadena F8
- Visualización correcta del contorno
- Análisis de la forma

---

## 4. Descriptores Morfológicos

### 4.1 Área

#### Función: `calculate_area(binary_matrix) → int`

**Definición**

$$A = \sum_{i,j} [\text{matriz}[i,j] == 255]$$

Número total de píxeles de objeto en la imagen.

**Implementación**

```python
area = int(np.sum(binary_matrix == 255))
```

**Complejidad: $O(A)$**

### 4.2 Perímetro desde F4

#### Función: `calculate_perimeter_f4(f4_chain) → int`

**Definición**

En un código F4, cada símbolo representa exactamente **1 paso de perímetro**:

$$P = \text{longitud}(\text{cadena F4}) = \sum_{i} 1$$

**Justificación Matemática**

Cada dirección F4 recorre exactamente 1 píxel ortogonal:

$$P_{\text{F4}} = P_{\text{Manhattan}} = \sum_{i} \sqrt{(dx_i)^2 + (dy_i)^2} = \sum_{i} 1$$

(Donde $(dx_i, dy_i) \in \{(±1,0), (0,±1)\}$)

**Implementación**

```python
perimeter = len(f4_chain)
```

**Nota**: Para F8, dividir por número de diagonales tendría menor precisión. F4 es más directo.

### 4.3 Perímetro de Contacto

#### Función: `calculate_contact_perimeter(binary_matrix) → int`

**Concepto**

Número de adyacencias entre píxeles de objeto y fondo en N4-conectividad:

$$P_c = \sum_{p \text{ objeto}} \#\{\text{vecinos N4 de } p \text{ que son fondo}\}$$

**Algoritmo**

```
procedimiento calculate_contact_perimeter(matriz):
    filas, columnas = dimensiones(matriz)
    norm = matriz == 255  // Normalizar a binaria
    contacto = 0
    
    para i = 0 hasta filas-1:
        para j = 0 hasta columnas-1:
            si norm[i][j] == 1:  // Píxel de objeto
                // Revisar 4 vecinos
                para (di, dj) en [(-1,0), (1,0), (0,-1), (0,1)]:
                    ni, nj = i + di, j + dj
                    
                    // Si vecino es fondo o fuera de límites (= fondo)
                    si (ni < 0 O ni >= filas O nj < 0 O nj >= columnas):
                        contacto += 1  // Borde de imagen = fondo
                    sino si norm[ni][nj] == 0:
                        contacto += 1  // Vecino fondo
    
    retornar contacto
```

**Ejemplo**

```
Matriz 3×3:
1 1 0
1 1 0
0 0 0

Píxel (0,0): vecinos fondo = 2 (arriba, izquierda)
Píxel (0,1): vecinos fondo = 2 (arriba, derecha)
Píxel (1,0): vecinos fondo = 2 (izquierda, abajo)
Píxel (1,1): vecinos fondo = 2 (derecha, abajo)

Perímetro de Contacto = 2 + 2 + 2 + 2 = 8
```

**Propiedad**

$$P_c = 2 \times P_{\text{F4}} \text{ para formas simples}$$

(Cada píxel de borde contribuye 2 vecinos fondo en promedio)

### 4.4 Compacidad Discreta

#### Función: `calculate_discrete_compactness(area, perimeter) → float`

**Definición**

Medida normalizada de redondez:

$$C = \frac{A - P/4}{A - \sqrt{A}}$$

Donde:
- $A$ = área
- $P$ = perímetro F4

**Rango**

$$C \in [0, 1]$$

- $C = 1$: Círculo perfecto (forma más redonda)
- $C < 1$: Formas irregulares
- $C \to 0$: Formas muy alargadas

**Derivación**

Para un círculo de área $A$:
$$P = 2\pi r = 2\sqrt{\pi A}$$

Para un cuadrado de área $A$:
$$P = 4\sqrt{A}$$

La fórmula normaliza entre estos extremos.

**Implementación**

```
procedimiento calculate_discrete_compactness(área, perímetro):
    si área <= 0:
        retornar 0.0
    
    sqrt_n = raíz_cuadrada(área)
    denominador = área - sqrt_n
    
    si denominador == 0:
        retornar 0.0
    
    numerador = área - (perímetro / 4)
    retornar numerador / denominador
```

**Ejemplo Práctico**

| Forma | Área | Perímetro | Compacidad |
|-------|------|-----------|-----------|
| Círculo (r=10) | 314 | 63 | 0.95 |
| Cuadrado (10×10) | 100 | 40 | 0.88 |
| Rectángulo (5×20) | 100 | 50 | 0.67 |
| Línea (1×100) | 100 | 200 | 0.02 |

### 4.5 Característica de Euler

#### Función: `calculate_euler(binary_matrix) → tuple`

**Definición Topológica**

$$\chi = C - H$$

Donde:
- $C$ = número de componentes conexas (8-conectividad)
- $H$ = número de agujeros (4-conectividad)

**Significado Topológico**

$$\chi = 1 - \text{genus}$$

Para superficies 2D:
- $\chi = 1$: Objeto simple sin agujeros (género 0)
- $\chi = 0$: Objeto con 1 agujero (género 1)
- $\chi = -1$: Objeto con 2 agujeros (género 2)
- $\chi = -n$: Objeto con $n$ agujeros

**Algoritmo**

```
procedimiento calculate_euler(matriz_binaria):
    norm = matriz_binaria == 255
    
    // Componentes conexas (8-vecindario)
    C = connected_components(norm, neighbor=8)
    
    // Agujeros (topología inversa con 4-vecindario)
    H = calculate_holes(matriz_binaria)
    
    euler_característica = C - H
    
    retornar (euler_característica, C, H)
```

**Ejemplo Visual**

```
Caso 1: Círculo sólido
████████
████████
████████
████████
χ = 1 - 0 = 1 ✓ (simple)

Caso 2: Anillo (donut)
████████
█░░░░░░█
█░░░░░░█
████████
χ = 1 - 1 = 0 ✓ (1 agujero)

Caso 3: Objeto con múltiples huecos
████████████
█░░░░░░░░░█
█░░░░░░░░░█
█░████░░░░█
█░████░░░░█
█░░░░░░░░░█
████████████
χ = 1 - 2 = -1 ✓ (2 agujeros)
```

---

## 5. Teoría de Información: Entropía y Compresión

### 5.1 Entropía de Shannon

#### Función: `calculate_entropy(chain) → float`

**Definición Fundamental**

$$H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$$

Mide la **incertidumbre promedio** de una variable aleatoria en bits/símbolo.

**Interpretación**

- $H = 0$: Sin incertidumbre (solo 1 símbolo)
- $H = \log_2(n)$: Máxima incertidumbre (distribución uniforme sobre $n$ símbolos)

**Algoritmo**

```
procedimiento calculate_entropy(cadena):
    si cadena vacía:
        retornar 0.0
    
    total_símbolos = longitud(cadena)
    frecuencias = contador(cadena)  // Contar ocurrencias
    
    entropía = 0.0
    para símbolo, frecuencia en frecuencias.items():
        probabilidad = frecuencia / total_símbolos
        
        si probabilidad > 0:
            entropía -= probabilidad * log₂(probabilidad)
    
    retornar entropía
```

**Ejemplo Práctico**

**Cadena 1**: `[0, 0, 0, 0, 0, 0, 0, 0]`
- P(0) = 1.0, P(1) = 0.0
- $H = -1.0 \times \log_2(1.0) - 0 = 0$ bits/símbolo
- **Interpretación**: Totalmente predecible

**Cadena 2**: `[0, 1, 0, 1, 0, 1, 0, 1]`
- P(0) = 0.5, P(1) = 0.5
- $H = -0.5 \times \log_2(0.5) - 0.5 \times \log_2(0.5) = 1.0$ bit/símbolo
- **Interpretación**: Máxima entropía para 2 símbolos

**Cadena 3**: `[0, 0, 0, 1, 2, 0, 0, 3]`
- P(0) = 0.5, P(1) = 0.125, P(2) = 0.125, P(3) = 0.125
- $H = -0.5 \times 1.0 - 3 \times (0.125 \times \log_2(0.125))$
- $H \approx 1.61$ bits/símbolo

### 5.2 Compresión Aritmética (Límite Teórico)

#### Función: `lenght_compression_arithmetic(chain, probability_dict) → float`

**Fundamentación**

La compresión aritmética alcanza el límite teónico de Shannon:

$$L_a = \sum_{i=1}^{n} P(x_i) \times (-\log_2 P(x_i)) = H(X)$$

**Implementación**

```
procedimiento lenght_compression_arithmetic(cadena, dict_probabilidades):
    si cadena vacía O dict_probabilidades vacío:
        retornar 0.0
    
    longitud_promedio = 0.0
    
    para símbolo, probabilidad en dict_probabilidades.items():
        si probabilidad > 0:
            log₂_prob = log_natural(probabilidad) / log_natural(2)
            longitud_promedio += probabilidad * (-log₂_prob)
    
    retornar longitud_promedio
```

**Propiedad**

$$L_a = H(X) \text{ exactamente}$$

Es el **límite inferior teórico** de compresión sin pérdidas.

### 5.3 Compresión Huffman

#### Función: `length_huffman_compression(chain, probability_dict) → tuple`

**Concepto: Árbol de Huffman**

Construye un árbol binario donde símbolos frecuentes tienen **códigos cortos**:

$$L_h = \sum_{i=1}^{n} P(x_i) \times \text{profundidad}(x_i)$$

**Propiedades Matemáticas**

1. **Optimalidad**: Huffman es óptimo entre códigos de longitud fija
2. **Cota de Entropía**:
$$H(X) \leq L_h < H(X) + 1$$

3. **Ganancia de compresión**:
$$\text{Ganancia} = \frac{L_h}{L_{\text{original}}} = \frac{L_h}{8}$$

(Asumiendo 8 bits/símbolo en representación original)

**Algoritmo de Construcción**

```
procedimiento length_huffman_compression(cadena, dict_probabilidades):
    si cadena vacía O dict_probabilidades vacío:
        retornar 0.0, 0, {}
    
    // Fase 1: Inicializar heap con hojas
    heap = []
    contador_id = 0
    
    para símbolo, probabilidad en dict_probabilidades.items():
        si probabilidad > 0:
            nodo = [probabilidad, contador_id, [[símbolo, ""]]]
            heap.heappush(nodo)
            contador_id += 1
    
    // Fase 2: Construir árbol
    mientras longitud(heap) > 1:
        nodo_bajo = heap.heappop()     // Probabilidad más baja
        nodo_alto = heap.heappop()     // Segunda más baja
        
        // Asignar códigos: 0 a la rama izquierda, 1 a derecha
        para símbolo_par en nodo_bajo[2]:
            símbolo_par[1] = '0' + símbolo_par[1]
        
        para símbolo_par en nodo_alto[2]:
            símbolo_par[1] = '1' + símbolo_par[1]
        
        // Crear nodo padre
        nueva_probabilidad = nodo_bajo[0] + nodo_alto[0]
        nodos_combinados = nodo_bajo[2] + nodo_alto[2]
        
        nodo_padre = [nueva_probabilidad, contador_id, nodos_combinados]
        heap.heappush(nodo_padre)
        contador_id += 1
    
    // Fase 3: Extraer códigos
    nodo_final = heap.heappop()[2]
    
    longitud_promedio = 0.0
    total_bits = 0
    códigos_huffman = {}
    total_símbolos = longitud(cadena)
    
    para símbolo, código_bits en nodo_final:
        longitud_promedio += dict_probabilidades[símbolo] * longitud(código_bits)
        códigos_huffman[símbolo] = código_bits
        
        frecuencia = redondear(dict_probabilidades[símbolo] * total_símbolos)
        total_bits += frecuencia * longitud(código_bits)
    
    retornar longitud_promedio, total_bits, códigos_huffman
```

**Ejemplo Paso a Paso**

**Distribución**: P(0)=0.5, P(1)=0.25, P(2)=0.15, P(3)=0.1

**Paso 1: Heap inicial**
```
P(3)=0.10 [3, ""]
P(2)=0.15 [2, ""]
P(1)=0.25 [1, ""]
P(0)=0.50 [0, ""]
```

**Paso 2: Combinar más bajos**
```
Combinar P(3) + P(2) = 0.25
        ├─ [3, "0"]
        └─ [2, "1"]

Heap actualizado:
P(1)=0.25 [1, ""]
P(0.25)=0.25 [árbol 2-3]
P(0)=0.50 [0, ""]
```

**Paso 3: Combinar siguientes dos más bajos**
```
Combinar P(1) + P(0.25) = 0.50
        ├─ [1, "0"]
        └─ [árbol 2-3, "1"]
           ├─ [3, "10"]
           └─ [2, "11"]

Heap actualizado:
P(0)=0.50 [0, ""]
P(0.50)=0.50 [árbol anterior]
```

**Paso 4: Combinar finales**
```
Raíz:
        ├─ [0, "0"]
        └─ [árbol anterior, "1"]
           ├─ [1, "10"]
           └─ [árbol, "11"]
              ├─ [3, "110"]
              └─ [2, "111"]
```

**Códigos finales**:
- 0 → "0" (1 bit)
- 1 → "10" (2 bits)
- 2 → "111" (3 bits)
- 3 → "110" (3 bits)

**Longitud promedio**:
$$L_h = 0.5 \times 1 + 0.25 \times 2 + 0.15 \times 3 + 0.1 \times 3 = 0.5 + 0.5 + 0.45 + 0.3 = 1.75 \text{ bits/símbolo}$$

**Comparación**:
- Entropía: $H(X) = 1.71$ bits/símbolo
- Huffman: $L_h = 1.75$ bits/símbolo
- Original: $L_0 = 8$ bits/símbolo
- Compresión: $1.75 / 8 = 21.875\%$ del tamaño original

**Complejidad**

- Construcción del árbol: $O(n \log n)$ donde $n$ = número de símbolos únicos
- Extracción de códigos: $O(n)$
- **Total: $O(n \log n)$**

---

## 6. Visualización: Histogramas

### 6.1 Función `plot_histograms(frequency_dict, probability_dict) → Figure`

**Componentes**

Genera una figura Matplotlib con dos subplots:

1. **Histograma de Frecuencias** (arriba): Barras de conteos absolutos
2. **Gráfico de Distribución de Probabilidad** (abajo): Línea con marcadores

**Características Académicas**

- Tema blanco (fondo claro para reportes)
- Colores estándar (#4A90E2 azul académico)
- Grid sutil (líneas punteadas)
- Títulos y etiquetas precisas
- Ejes compartidos (sharex=True)

**Algoritmo**

```
procedimiento plot_histograms(dict_frecuencias, dict_probabilidades):
    si dict_frecuencias vacío O dict_probabilidades vacío:
        retornar NULO
    
    símbolos = ordenar(lista(dict_frecuencias.claves))
    frecuencias = [dict_frecuencias[s] para s en símbolos]
    probabilidades = [dict_probabilidades[s] para s en símbolos]
    
    figura, (eje_freq, eje_prob) = crear_subplots(2, 1, sharex=VERDADERO)
    
    // Configurar colores
    color_primario = '#4A90E2'
    color_texto = '#000000'
    color_grid = '#E0E0E0'
    
    // Subplot 1: Histograma de frecuencias
    eje_freq.barras(símbolos, frecuencias, color=color_primario)
    eje_freq.título("1. Symbol Frequency (Count)")
    eje_freq.ylabel("Frequency (Count)")
    eje_freq.grid(VERDADERO, estilo='--', color=color_grid)
    eje_freq.quitar_spinas(['top', 'right'])
    
    // Subplot 2: Línea de probabilidades
    eje_prob.plot(símbolos, probabilidades, 
                  color=color_primario, marcador='o', tamaño_línea=2.5)
    eje_prob.título("2. Symbol Probability Distribution")
    eje_prob.ylabel("Probability")
    eje_prob.xlabel("Chain Code Symbol")
    eje_prob.grid(VERDADERO, estilo='--', color=color_grid)
    eje_prob.quitar_spinas(['top', 'right'])
    
    figura.suptitle("Chain Code Analysis Dashboard")
    figura.tight_layout()
    
    retornar figura
```

---

## 7. Integración en Flujo General

### Secuencia de Llamadas

```
Usuario carga imagen
    ↓
process_and_binarize()
    → matriz binaria con padding
    ↓
find_outline()
    → contorno + perímetro (píxeles de borde)
    ↓
chain_codes.chain_f4/f8/etc()
    → código de cadena
    ↓
calculate_entropy(cadena)
    → H(X) en bits/símbolo
    ↓
length_huffman_compression(cadena, probabilidades)
    → códigos Huffman + longitud promedio
    ↓
calculate_area(matriz)
calculate_perimeter_f4(cadena_f4)
calculate_discrete_compactness(área, perímetro)
    → Descriptores geométricos
    ↓
calculate_euler(matriz)
    → Característica de Euler
    ↓
Mostrar en GUI: histograma + descriptores
```

---

## Complejidad General

| Operación | Complejidad | Dominante |
|-----------|-------------|-----------|
| `process_and_binarize` | $O(A)$ | Lectura de imagen |
| `find_outline` | $O(A)$ | Escaneo + rastreo |
| Cálculos de descriptores | $O(A)$ | Suma de píxeles |
| `calculate_entropy` | $O(P)$ | Conteo de símbolos |
| `length_huffman_compression` | $O(n \log n)$ | Construcción árbol |
| `calculate_holes` | $O(A)$ | Flood-fill |
| **Total por ciclo** | $O(A + n \log n)$ | Escaneo de imagen |

Donde $A$ = área total, $P$ = perímetro, $n$ = símbolos únicos

---

## Referencias Matemáticas

### Teoría de Información

- Shannon, C. E. (1948). "A mathematical theory of communication." 
  *Bell System Technical Journal*, 27(3), 379-423.
- Huffman, D. A. (1952). "A method for the construction of minimum-redundancy codes." 
  *Proceedings of the IRE*, 40(9), 1098-1101.

### Morfología Digital

- Rosenfeld, A., & Kak, A. C. (1982). Digital Picture Processing (2nd ed.). 
  Academic Press.
- Serra, J. (1982). Image Analysis and Mathematical Morphology. Academic Press.

### Topología Discreta

- Kovalevsky, V. A. (1989). "Finite topology as applied to image analysis." 
  *Computer Vision, Graphics, and Image Processing*, 46(2), 141-161.

---

**Última actualización:** Marzo 2026

**Autores:** ENRIQUE GOMEZ, VICTORIA GALVAN

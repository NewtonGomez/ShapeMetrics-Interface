# README-CHAIN-CODES: Algoritmos Matemáticos de Codificación de Freeman

## Descripción General

Los códigos de Freeman son técnicas fundamentales en procesamiento digital de imágenes para representar contornos de objetos de forma compacta. Este documento detalla los **cinco algoritmos de codificación implementados** en `chain_codes.py`:

1. **F4** (Freeman 4-direccional)
2. **F8** (Freeman 8-direccional)
3. **AF8** (Absolute Freeman 8 / Freeman Relativo)
4. **VCC** (Variable-Length Closure Code)
5. **3OT** (Three-State Chain Code)

---

## 1. Código Freeman 4-Direccional (F4)

### Fundamentación Matemática

El código F4 representa un contorno usando movimientos discretos en **4 direcciones ortogonales**. Cada dirección se codifica como un dígito numérico:

$$\text{Direcciones F4: } \begin{cases} 
0 = \text{Derecha} & \quad \vec{d}_0 = (1, 0) \\
1 = \text{Abajo} & \quad \vec{d}_1 = (0, 1) \\
2 = \text{Izquierda} & \quad \vec{d}_2 = (-1, 0) \\
3 = \text{Arriba} & \quad \vec{d}_3 = (0, -1)
\end{cases}$$

Donde cada tupla $(dx, dy)$ representa el desplazamiento en píxeles.

### Algoritmo de Generación

#### Paso 1: Búsqueda del Punto de Inicio

Se localiza el **primer píxel de borde** que cumple:
- Es píxel de objeto (valor = 255)
- Tiene al menos un píxel de fondo adyacente
- Se escanea de arriba a abajo, de izquierda a derecha

**Pseudocódigo:**
```
procedimiento encontrar_inicio(imagen_binaria):
    imagen_padded = pad(imagen_binaria, padding=1)
    para cada píxel (y, x) en imagen_padded:
        si imagen_padded[y, x] == 255:
            si imagen_padded[y-1, x] == 0 O imagen_padded[y, x-1] == 0:
                retornar (x, y)
    retornar NULO
```

#### Paso 2: Rastreo de Contorno (Contour Tracing)

Desde el punto de inicio, se traza el contorno usando el **algoritmo de giro-izquierda** (left-turn rule):

1. **Dirección inicial**: Comienza mirando hacia la derecha (dirección = 0)
2. **Búsqueda cíclica**: En cada iteración:
   - Intenta girar a la izquierda (counterclockwise)
   - Busca un píxel de objeto en 4 direcciones
   - Se mueve en la primera dirección válida encontrada

**Pseudocódigo:**
```
procedimiento chain_f4(imagen_binaria):
    punto_inicio = encontrar_inicio(imagen_binaria)
    si punto_inicio == NULO:
        retornar []
    
    x, y = punto_inicio
    dirección_actual = 0  // Apunta a derecha inicialmente
    cadena = []
    
    para iteración = 1 hasta 10000:
        // Movimiento en dirección actual
        dx, dy = desplazamientos[dirección_actual]
        x += dx
        y += dy
        
        cadena.añadir(dirección_actual)
        
        // Validar cierre
        si (x, y) == punto_inicio:
            romper  // Contorno completo
        
        // Girar a la izquierda primero (counterclockwise)
        dirección_actual = (dirección_actual + 3) % 4
        
        // Buscar siguiente píxel válido
        para intento = 1 hasta 4:
            dx, dy = desplazamientos[dirección_actual]
            
            // Seleccionar píxel a verificar según dirección
            si dirección_actual == 0: // Derecha
                px, py = x, y
            sino si dirección_actual == 1: // Abajo
                px, py = x - 1, y
            sino si dirección_actual == 2: // Izquierda
                px, py = x - 1, y - 1
            sino: // Arriba
                px, py = x, y - 1
            
            si imagen[py, px] == 255:
                romper  // Píxel válido encontrado
            
            // Girar a la derecha (clockwise)
            dirección_actual = (dirección_actual + 1) % 4
    
    retornar cadena
```

### Propiedades Matemáticas

#### Eficiencia de Compresión

**Tamaño de F4 original (sin comprimir):**
$$L_{\text{F4 bits}} = P \cdot \log_2(4) = P \cdot 2 \text{ bits}$$

Donde $P$ = perímetro (número de pasos)

**Comparación con almacenamiento de matriz:**
$$\text{Ratio} = \frac{L_{\text{F4 bits}}}{H \cdot W \cdot 8} = \frac{2P}{8HW}$$

Para objetos donde $P \ll HW$, la compresión es muy significativa.

#### Propiedad de Cierre

Una cadena F4 válida debe satisfacer:

$$\sum_{i=0}^{P-1} \vec{d}_{c_i} = \vec{0}$$

Es decir, la suma vectorial de todos los desplazamientos debe ser cero:

$$\sum_{i: c_i=0} 1 = \sum_{i: c_i=2} 1 \quad \text{(derecha = izquierda)}$$

$$\sum_{i: c_i=1} 1 = \sum_{i: c_i=3} 1 \quad \text{(abajo = arriba)}$$

### Ejemplo Práctico

Considere un cuadrado de 3×3 píxeles:
```
255 255 255
255 255 255
255 255 255
```

Rastreo desde esquina superior-izquierda:
- Inicio: (0, 0)
- Secuencia: 0 → 1 → 1 → 0 → 0 → 3 → 3 → 2 → 2
- **F4 Result**: `[0, 1, 1, 0, 0, 3, 3, 2, 2]`
- **Perímetro**: 9 píxeles
- **Bits requeridos**: 9 × 2 = 18 bits

---

## 2. Código Freeman 8-Direccional (F8)

### Fundamentación Matemática

F8 extiende F4 incluyendo **movimientos diagonales**, permitiendo conectividad 8-vecindario:

$$\text{Direcciones F8: } \begin{cases}
0 = \text{Derecha} & \quad \vec{d}_0 = (1, 0) &&\\
1 = \text{Abajo-Derecha} & \quad \vec{d}_1 = (1, 1) &&\\
2 = \text{Abajo} & \quad \vec{d}_2 = (0, 1) &&\\
3 = \text{Abajo-Izquierda} & \quad \vec{d}_3 = (-1, 1) &&\\
4 = \text{Izquierda} & \quad \vec{d}_4 = (-1, 0) &&\\
5 = \text{Arriba-Izquierda} & \quad \vec{d}_5 = (-1, -1) &&\\
6 = \text{Arriba} & \quad \vec{d}_6 = (0, -1) &&\\
7 = \text{Arriba-Derecha} & \quad \vec{d}_7 = (1, -1) &&
\end{cases}$$

### Algoritmo de Generación

**Diferencia principal**: F8 obtiene los puntos del contorno desde `tools.find_outline()`, que ya proporciona una lista ordenada de píxeles de borde.

**Pseudocódigo:**
```
procedimiento chain_f8(imagen_binaria):
    contorno_datos = find_outline(imagen_binaria)
    puntos_contorno = contorno_datos["contour"]  // Lista ordenada (x, y)
    
    si puntos_contorno es NULO o vacío:
        retornar []
    
    tabla_direcciones = {
        (0, 1): 0,    (1, 1): 1,    (1, 0): 2,    (1, -1): 3,
        (0, -1): 4,   (-1, -1): 5,  (-1, 0): 6,   (-1, 1): 7
    }
    
    cadena = []
    
    para i = 0 hasta longitud(puntos_contorno)-1:
        punto_actual = puntos_contorno[i]
        punto_siguiente = puntos_contorno[(i + 1) % longitud(puntos_contorno)]
        
        // Calcular vector desplazamiento
        dx = punto_siguiente.x - punto_actual.x
        dy = punto_siguiente.y - punto_actual.y
        
        // Mapear a dirección
        si (dy, dx) está en tabla_direcciones:
            cadena.añadir(tabla_direcciones[(dy, dx)])
    
    // Rotar para alineación basada en punto de inicio
    si cadena no vacía:
        cadena = cadena[-1:] + cadena[:-1]  // Rotación circular
    
    retornar cadena
```

### Comparación F4 vs F8

| Aspecto | F4 | F8 |
|--------|----|----|
| **Direcciones** | 4 | 8 |
| **Bits/símbolo** | 2 | 3 |
| **Contornos suaves** | Escalonado | Natural |
| **Puntos muestreados** | Más puntos | Menos puntos |
| **Compresibilidad** | Media | Mejor (menos símbolos) |

#### Análisis de Distancia

**Distancia F4** (Manhattan/L1):
$$d_{\text{F4}} = |x_1 - x_2| + |y_1 - y_2|$$

**Distancia F8** (Chebyshev/L∞):
$$d_{\text{F8}} = \max(|x_1 - x_2|, |y_1 - y_2|)$$

Para una línea diagonal, F8 requiere **menos símbolos** que F4:
- F4: «dirección, dirección, dirección, dirección» (4 síbolos)
- F8: «diagonal» (1 símbolo)

---

## 3. Código Freeman Relativo (AF8)

### Fundamentación Matemática

AF8 codifica **cambios de dirección relativos** en lugar de direcciones absolutas:

$$\text{AF8}[i] = (F8[i] - F8[i-1]) \bmod 8$$

Donde los índices son **cíclicos**: el elemento anterior del primero es el último.

Alternativamente:
$$\text{AF8}[i] = \text{giro relativo desde } F8[i-1] \text{ hasta } F8[i]$$

### Matriz de Transformación

Para convertir F8 a AF8 se usa una tabla de búsqueda:

$$\begin{array}{c|cccccccc}
  & 0 & 1 & 2 & 3 & 4 & 5 & 6 & 7 \\
\hline
0 & 0 & 1 & 2 & 3 & 4 & 5 & 6 & 7 \\
1 & 7 & 0 & 1 & 2 & 3 & 4 & 5 & 6 \\
2 & 6 & 7 & 0 & 1 & 2 & 3 & 4 & 5 \\
3 & 5 & 6 & 7 & 0 & 1 & 2 & 3 & 4 \\
4 & 4 & 5 & 6 & 7 & 0 & 1 & 2 & 3 \\
5 & 3 & 4 & 5 & 6 & 7 & 0 & 1 & 2 \\
6 & 2 & 3 & 4 & 5 & 6 & 7 & 0 & 1 \\
7 & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 0 \\
\end{array}$$

**Lectura**: Fila = $F8[i-1]$, Columna = $F8[i]$, Celda = $AF8[i]$

### Algoritmo de Generación

**Pseudocódigo:**
```
procedimiento chain_af8(imagen_binaria):
    f8 = chain_f8(imagen_binaria)
    
    si f8 vacío o longitud(f8) < 2:
        retornar []
    
    tabla_busqueda = [
        [0,1,2,3,4,5,6,7],
        [7,0,1,2,3,4,5,6],
        ...  // 8 filas como en matriz anterior
    ]
    
    af8 = []
    para i = 0 hasta longitud(f8)-1:
        dirección_anterior = f8[i - 1]  // Cíclico: i=0 → f8[-1]
        dirección_actual = f8[i]
        
        giro_relativo = tabla_busqueda[dirección_anterior][dirección_actual]
        af8.añadir(giro_relativo)
    
    retornar af8
```

### Propiedades de Compresión

AF8 típicamente logra **mejor compresión que F8** porque:

1. **Menor varianza**: Los valores de giro están en rango [0, 7] pero **concentrados** alrededor de cambios pequeños
2. **Distribución sesgada**: En contornos suaves, predominan valores 0 (sin giro) y 1-2 (giros pequeños)

**Entropía de Shannon:**
$$H_{\text{F8}} = -\sum_{d=0}^{7} P(d) \log_2 P(d)$$

$$H_{\text{AF8}} = -\sum_{r=0}^{7} P(r) \log_2 P(r)$$

Típicamente: $H_{\text{AF8}} < H_{\text{F8}}$ porque AF8 tiene menor variedad de valores.

### Ejemplo de Transformación

**F8 original**: `[0, 0, 1, 2, 2, 3, 4]`

**AF8 calculado**:
- $AF8[0] = (0 - 4) \bmod 8 = 4$ (giro 4 pasos desde anterior 4)
- $AF8[1] = (0 - 0) \bmod 8 = 0$ (sin giro)
- $AF8[2] = (1 - 0) \bmod 8 = 1$ (giro 1 paso)
- $AF8[3] = (2 - 1) \bmod 8 = 1$ (giro 1 paso)
- $AF8[4] = (2 - 2) \bmod 8 = 0$ (sin giro)
- $AF8[5] = (3 - 2) \bmod 8 = 1$ (giro 1 paso)
- $AF8[6] = (4 - 3) \bmod 8 = 1$ (giro 1 paso)

**AF8 resultado**: `[4, 0, 1, 1, 0, 1, 1]`

---

## 4. Código de Cierre Variable (VCC)

### Fundamentación Matemática

VCC simplifica F4 codificando solo **cambios de dirección**, no direcciones absolutas:

$$\text{Símbolos VCC: } \begin{cases}
0 = \text{Sin cambio (continúa en mismo sentido)} \\
1 = \text{Giro sin cambiar referencia} \\
2 = \text{Cambio de referencia / Dirección opuesta} \\
3 = \text{(No utilizado en nuestra implementación, fusionado con 2)}
\end{cases}$$

### Lógica de Clasificación

Dada una secuencia F4, VCC analiza **transiciones de dirección**:

**Tabla de Transiciones:**

$$\begin{array}{c|cccc}
\text{De/A} & 0 & 1 & 2 & 3 \\
\hline
0 & 0 & 1 & 2 & 2 \\
1 & 2 & 0 & 1 & 2 \\
2 & 2 & 2 & 0 & 1 \\
3 & 2 & 1 & 2 & 0 \\
\end{array}$$

**Interpretación:**
- **0**: Continuar en la misma dirección (sin giro)
- **1**: Giro 90° (a izquierda o derecha)
- **2**: Giro 180° o cambio más complejo

### Algoritmo de Generación

**Pseudocódigo:**
```
procedimiento chain_vcc(imagen_binaria):
    f4 = chain_f4(imagen_binaria)
    
    tabla_transiciones = {
        (0,0): 0,  (0,1): 1,  (0,3): 2,
        (1,0): 2,  (1,1): 0,  (1,2): 1,
        (2,1): 2,  (2,2): 0,  (2,3): 1,
        (3,0): 1,  (3,2): 2,  (3,3): 0
    }
    
    vcc = []
    para i = 0 hasta longitud(f4)-1:
        dirección_anterior = f4[i - 1]  // Cíclico
        dirección_actual = f4[i]
        
        símbolo = tabla_transiciones.obtener(
            (dirección_anterior, dirección_actual), 
            valor_por_defecto=0
        )
        vcc.añadir(símbolo)
    
    retornar vcc
```

### Análisis de Compresión

**Ventaja**: VCC usa **3 símbolos** (0, 1, 2) vs. 4 de F4.

$$L_{\text{VCC bits}} = P \cdot \log_2(3) \approx P \cdot 1.585 \text{ bits}$$

$$L_{\text{F4 bits}} = P \cdot 2$$

**Ratio**: $\frac{1.585}{2} = 0.79$ → VCC es ~21% más compacto que F4

Sin embargo, la distribución de símbolos puede variar:
- Formas suaves → Predominan 0s → Mayor compresión
- Formas angulares → Más variedad → Menor compresión

### Ejemplo Práctico

**F4 original**: `[0, 0, 1, 1, 2, 3, 3, 0]` (perímetro 8)

**VCC calculado**:
- $i=0$: $(3 \to 0)$ = 1 (giro desde arriba a derecha)
- $i=1$: $(0 \to 0)$ = 0 (continúa derecha)
- $i=2$: $(0 \to 1)$ = 1 (giro a abajo)
- $i=3$: $(1 \to 1)$ = 0 (continúa abajo)
- $i=4$: $(1 \to 2)$ = 1 (giro a izquierda)
- $i=5$: $(2 \to 3)$ = 1 (giro a arriba)
- $i=6$: $(3 \to 3)$ = 0 (continúa arriba)
- $i=7$: $(3 \to 0)$ = 1 (giro a derecha para cerrar)

**VCC resultado**: `[1, 0, 1, 0, 1, 1, 0, 1]`

---

## 5. Código de Tres Estados (3OT)

### Fundamentación Matemática

3OT es la forma **más compacta**, simplificando VCC a **solo 3 símbolos** mediante clasificación según cambios relativos:

$$\text{Símbolos 3OT: } \begin{cases}
0 = \text{Sin cambio (sigue recto)} \\
1 = \text{Giro o cambio de referencia} \\
2 = \text{Primera transición o dirección opuesta}
\end{cases}$$

### Algoritmo de Generación

3OT mantiene un **estado de referencia** que cambia según las transiciones:

**Pseudocódigo:**
```
procedimiento chain_3ot(imagen_binaria):
    f4 = chain_f4(imagen_binaria)
    
    si longitud(f4) < 2:
        retornar []
    
    cadena_3ot = []
    referencia = f4[0]  // Referencia inicial
    anterior = f4[0]
    cambio_dirección_ocurrió = FALSO
    
    // Procesar dirección actual vs anterior
    para i = 1 hasta longitud(f4)-1:
        dirección_actual = f4[i]
        
        si dirección_actual == anterior:
            cadena_3ot.añadir(0)  // Sin cambio
        sino:
            si NO cambio_dirección_ocurrió:
                cadena_3ot.añadir(2)  // Primera transición
                cambio_dirección_ocurrió = VERDADERO
            sino si dirección_actual == referencia:
                cadena_3ot.añadir(1)  // Regresa a referencia
                referencia = anterior
            sino si (dirección_actual - referencia) % 4 == 2:
                cadena_3ot.añadir(2)  // Dirección opuesta
                referencia = anterior
            sino:
                cadena_3ot.añadir(1)  // Otro giro
                referencia = anterior
        
        anterior = dirección_actual
    
    // Manejar cierre circular
    dirección_actual = f4[0]
    
    si dirección_actual == anterior:
        cadena_3ot.añadir(0)
    sino si NO cambio_dirección_ocurrió:
        cadena_3ot.añadir(2)
    sino si dirección_actual == referencia:
        cadena_3ot.añadir(1)
    sino si (dirección_actual - referencia) % 4 == 2:
        cadena_3ot.añadir(2)
    sino:
        cadena_3ot.añadir(1)
    
    retornar cadena_3ot
```

### Propiedades de Compresión

**Tamaño en bits:**
$$L_{\text{3OT bits}} = P \cdot \log_2(3) \approx P \cdot 1.585 \text{ bits}$$

Similar a VCC, pero con estructura diferente que favorece:
- **Contornos suaves**: Muchos 0s → excelente compresión
- **Esquinas agudas**: Más 2s → compresión moderada

**Ventaja sobre F4:**
$$\text{Compresión} = 1 - \frac{L_{\text{3OT}}}{L_{\text{F4}}} = 1 - \frac{1.585}{2} \approx 20.75\%$$

### Ejemplo Práctico

**F4 original**: `[0, 0, 1, 1, 2, 3, 3, 0]`

**3OT calculado**:

| i | dirección | anterior | referencia | símbolo | razón |
|---|-----------|----------|-----------|---------|-------|
| - | - | 0 | 0 | - | Inicialización |
| 1 | 0 | 0 | 0 | **0** | Sin cambio |
| 2 | 1 | 0 | 0 | **2** | Primera transición |
| 3 | 1 | 1 | 0 | **0** | Sin cambio |
| 4 | 2 | 1 | 1 | **2** | Opuesta (2-1=1, |1-1|≠2) o giro |
| 5 | 3 | 2 | 2 | **1** | Giro |
| 6 | 3 | 3 | 2 | **0** | Sin cambio |
| 7 | 0 | 3 | 2 | **1** | Giro para cerrar |

**3OT resultado**: `[0, 2, 0, 2, 1, 0, 1]` (7 símbolo)

---

## Comparación General de Algoritmos

### Tabla Resumen

| Aspecto | F4 | F8 | AF8 | VCC | 3OT |
|---------|----|----|-----|-----|-----|
| **Símbolos únicos** | 4 | 8 | 8 | 3 | 3 |
| **Bits/símbolo** | 2 | 3 | 3 | 1.58 | 1.58 |
| **Tipo** | Absoluto | Absoluto | Relativo | Relativo | Relativo |
| **Compresión aprox.** | 100% | 150% | 75%-125% | 79% | 79% |
| **Contornos suaves** | Escalonado | Excelente | Muy bueno | Bueno | Bueno |
| **Fácil decodificar** | Sí | Sí | Sí* | Sí* | Sí* |
| **Deambigüedad** | 1 | 1 | Múltiple | 1 | Múltiple |

*Requiere información adicional

### Gráfico de Eficiencia

```
Bits por símbolo vs Compresibilidad:

F4 (2 bits)                    ████
F8/AF8 (3 bits)                ██████
VCC (1.585 bits)               ███
3OT (1.585 bits)               ███

Mejor compresión ←─────────────────→ Más fácil decodificar
(VCC/3OT)                             (F4/F8)
```

---

## Integración en el Código

### Función `list_functions()` en `main_window.py`

Los algoritmos se descubren dinámicamente:

```python
self.chain_code_functions = list_functions(chain_codes)
# Retorna: {
#     'CHAIN_F4': <función>,
#     'CHAIN_F8': <función>,
#     'CHAIN_AF8': <función>,
#     'CHAIN_VCC': <función>,
#     'CHAIN_3OT': <función>
# }
```

### Selección en la GUI

El usuario elige desde un ComboBox que se puebla automáticamente.

---

## Casos de Uso

### F4: Simplemente efectivo
- **Cuándo usar**: Objetos con bordes principalmente ortogonales
- **Ejemplo**: Caracteres poligonales, formas arquitectónicas

### F8: Representación fiel
- **Cuándo usar**: Contornos suaves y redondeados
- **Ejemplo**: Objetos naturales, letras cursivas

### AF8: Análisis de curvatura
- **Cuándo usar**: Cuando interesa el perfil de cambios de dirección
- **Ejemplo**: Análisis de giros, esquinas

### VCC: Balance compresión-claridad
- **Cuándo usar**: Aplicaciones con restricciones de almacenamiento
- **Ejemplo**: Bases de datos de formas, sistemas embebidos

### 3OT: Máxima compresión
- **Cuándo usar**: Cuando el espacio es crítico
- **Ejemplo**: Transmisión de datos, almacenamiento masivo

---

## Referencias Matemáticas

### Autores Originales

- Freeman, H. (1961). "On the encoding of arbitrary geometric configurations." 
  *IEEE Transactions on Electronic Computers*, EC-10(2), 260-268.

### Extensiones

- Bribiesca, E. (1997). "A new chain code." *Pattern Recognition*, 30(2), 235-251.
  (Introduce VCC y variantes)

### Teoría de Información

- Shannon, C. E. (1948). "A mathematical theory of communication." 
  *Bell System Technical Journal*, 27, 379-423, 623-656.

---

**Última actualización:** Marzo 2026

**Autores:** ENRIQUE GOMEZ, VICTORIA GALVAN

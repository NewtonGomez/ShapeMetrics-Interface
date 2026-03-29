
import numpy as np

# =============================
# PURE MATHEMATICAL LOGIC
# =============================

def fill_shape(binary_matrix):
    """
    Fill the interior of a closed contour using Flood Fill algorithm.
    
    Args:
        binary_matrix (np.ndarray): Binary image with contour (0 or 255)
        
    Returns:
        np.ndarray: Filled image (interior marked with 255)
    """
    rows, cols = binary_matrix.shape
    exterior = np.zeros((rows, cols), dtype=np.uint8)
    
    stack = [(0, 0)]
    exterior[0, 0] = 255
    
    movements = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    while stack:
        r, c = stack.pop()
        
        for dr, dc in movements:
            nr, nc = r + dr, c + dc
            
            if 0 <= nr < rows and 0 <= nc < cols:
                if binary_matrix[nr, nc] == 0 and exterior[nr, nc] == 0:
                    exterior[nr, nc] = 255
                    stack.append((nr, nc))
    
    filled_img = np.zeros_like(binary_matrix)
    filled_img[exterior == 0] = 255
    
    return filled_img


def af8_to_f8(af8_chain):
    """
    Convert AF8 (relative) chain to F8 (absolute) by testing initial directions.
    
    Args:
        af8_chain (list): Relative AF8 chain (0-7)
        
    Returns:
        list: Absolute F8 chain
    """
    moves = {0:(0,1), 1:(1,1), 2:(1,0), 3:(1,-1),
            4:(0,-1), 5:(-1,-1), 6:(-1,0), 7:(-1,1)}

    for initial_direction in range(8):
        f8 = []
        current_state = initial_direction

        for relative_symbol in af8_chain:
            current_state = (current_state + relative_symbol) % 8
            f8.append(current_state)

        x, y = 0, 0
        for direction in f8:
            dx, dy = moves[direction]
            x += dx
            y += dy

        if x == 0 and y == 0:
            return f8

    return f8


def closes_f4_shape(f4_chain):
    """
    Verify if an F4 chain generates a closed contour.
    
    Args:
        f4_chain (list): F4 chain (0-3)
        
    Returns:
        bool: True if shape closes, False otherwise
    """
    x, y = 0, 0
    moves = {0:(0,1), 1:(1,0), 2:(0,-1), 3:(-1,0)}

    for direction in f4_chain:
        dx, dy = moves[direction]
        x += dx
        y += dy

    return x == 0 and y == 0


def vcc_to_f4(vcc_chain, initial_direction=0):
    """
    Convert VCC (variable-length code) chain to F4 (absolute directions).
    
    Args:
        vcc_chain (list): VCC chain with symbols 1, 2, 3
        initial_direction (int): Starting direction (0-3)
        
    Returns:
        list: Absolute F4 directions
    """
    vcc_table = {
        (0, 1): 1, (0, 2): 3, (0, 3): 0,
        (1, 1): 2, (1, 2): 0, (1, 3): 1,
        (2, 1): 3, (2, 2): 1, (2, 3): 2,
        (3, 1): 0, (3, 2): 2, (3, 3): 3
    }

    f4 = []
    previous_direction = initial_direction

    for symbol in vcc_chain:
        if (previous_direction, symbol) in vcc_table:
            new_f4 = vcc_table[(previous_direction, symbol)]
            f4.append(new_f4)
            previous_direction = new_f4
        else:
            f4.append(previous_direction)

    return f4


def c3ot_to_f4(c3ot_chain):
    """
    Convert 3OT (3-option turn) chain to F4 by testing initial directions.
    
    Args:
        c3ot_chain (list): 3OT chain with symbols 0=straight, 1=left, 2=right
        
    Returns:
        tuple: (f4_chain, is_closed)
    """
    for initial_direction in range(4):
        f4 = []
        current_direction = initial_direction

        for symbol in c3ot_chain:
            if symbol == 0:
                new_direction = current_direction
            elif symbol == 1:
                new_direction = (current_direction + 1) % 4
            elif symbol == 2:
                new_direction = (current_direction + 3) % 4
            else:
                new_direction = current_direction

            f4.append(new_direction)
            current_direction = new_direction

        if closes_f4_shape(f4):
            return f4, True

    return f4, False


# =============================
# INTELLIGENT DRAWING ENGINES (BOUNDING BOX)
# =============================

def f4_to_matrix(f4_chain, padding=10):
    """
    Generate matrix from F4 chain with automatic bounding box calculation.
    
    The function:
    1. Simulates the path based on F4 directions starting at (0,0)
    2. Finds min/max coordinates
    3. Creates a matrix sized to fit the shape with padding
    4. Draws the contour (value 255)
    
    Args:
        f4_chain (list): F4 directions (0-3)
        padding (int): Padding in pixels around the shape
        
    Returns:
        np.ndarray: Binary matrix with contour drawn
    """
    moves = {0:(0,1), 1:(1,0), 2:(0,-1), 3:(-1,0)}
    
    # Simulate path to find bounding box
    x, y = 0, 0
    coordinates = [(x, y)]
    
    for direction in f4_chain:
        dx, dy = moves[direction]
        x += dx
        y += dy
        coordinates.append((x, y))
    
    # Find bounding box
    all_x = [coord[0] for coord in coordinates]
    all_y = [coord[1] for coord in coordinates]
    
    min_x = min(all_x)
    max_x = max(all_x)
    min_y = min(all_y)
    max_y = max(all_y)
    
    # Calculate absolute dimensions
    height = max_x - min_x + 1
    width = max_y - min_y + 1
    
    # Create matrix with padding
    final_height = height + 2 * padding
    final_width = width + 2 * padding
    
    matrix = np.zeros((final_height, final_width), dtype=np.uint8)
    
    # Draw contour with adjusted coordinates
    for coord_x, coord_y in coordinates:
        adj_x = coord_x - min_x + padding
        adj_y = coord_y - min_y + padding
        matrix[adj_x, adj_y] = 255
    
    return matrix


def f8_to_matrix(f8_chain, padding=10):
    """
    Generate matrix from F8 chain with automatic bounding box calculation.
    
    The function:
    1. Simulates the path based on F8 directions starting at (0,0)
    2. Finds min/max coordinates
    3. Creates a matrix sized to fit the shape with padding
    4. Draws the contour (value 255)
    
    Args:
        f8_chain (list): F8 directions (0-7)
        padding (int): Padding in pixels around the shape
        
    Returns:
        np.ndarray: Binary matrix with contour drawn
    """
    moves = {0:(0,1), 1:(1,1), 2:(1,0), 3:(1,-1),
            4:(0,-1), 5:(-1,-1), 6:(-1,0), 7:(-1,1)}
    
    # Simulate path to find bounding box
    x, y = 0, 0
    coordinates = [(x, y)]
    
    for direction in f8_chain:
        dx, dy = moves[direction]
        x += dx
        y += dy
        coordinates.append((x, y))
    
    # Find bounding box
    all_x = [coord[0] for coord in coordinates]
    all_y = [coord[1] for coord in coordinates]
    
    min_x = min(all_x)
    max_x = max(all_x)
    min_y = min(all_y)
    max_y = max(all_y)
    
    # Calculate absolute dimensions
    height = max_x - min_x + 1
    width = max_y - min_y + 1
    
    # Create matrix with padding
    final_height = height + 2 * padding
    final_width = width + 2 * padding
    
    matrix = np.zeros((final_height, final_width), dtype=np.uint8)
    
    # Draw contour with adjusted coordinates
    for coord_x, coord_y in coordinates:
        adj_x = coord_x - min_x + padding
        adj_y = coord_y - min_y + padding
        matrix[adj_x, adj_y] = 255
    
    return matrix


# =============================
# DECODER FUNCTIONS (PURE LOGIC)
# =============================

def decode_f4_to_matrix(f4_chain):
    """
    Decode F4 chain to filled matrix.
    
    Args:
        f4_chain (list): F4 directions (0-3)
        
    Returns:
        np.ndarray: Filled binary matrix
    """
    contour = f4_to_matrix(f4_chain)
    filled = fill_shape(contour)
    return filled


def decode_f8_to_matrix(f8_chain):
    """
    Decode F8 chain to filled matrix.
    
    Args:
        f8_chain (list): F8 directions (0-7)
        
    Returns:
        np.ndarray: Filled binary matrix
    """
    contour = f8_to_matrix(f8_chain)
    filled = fill_shape(contour)
    return filled


def decode_af8_to_matrix(af8_chain):
    """
    Decode AF8 chain to filled matrix.
    
    Args:
        af8_chain (list): Relative AF8 directions (0-7)
        
    Returns:
        np.ndarray: Filled binary matrix
    """
    f8_chain = af8_to_f8(af8_chain)
    contour = f8_to_matrix(f8_chain)
    filled = fill_shape(contour)
    return filled


def decode_vcc_to_matrix(vcc_chain):
    """
    Decode VCC chain to filled matrix.
    
    Args:
        vcc_chain (list): VCC chain with symbols 1, 2, 3
        
    Returns:
        np.ndarray: Filled binary matrix
    """
    f4_chain = vcc_to_f4(vcc_chain)
    contour = f4_to_matrix(f4_chain)
    filled = fill_shape(contour)
    return filled


def decode_3ot_to_matrix(c3ot_chain):
    """
    Decode 3OT chain to filled matrix.
    
    Args:
        c3ot_chain (list): 3OT chain with symbols 0=straight, 1=left, 2=right
        
    Returns:
        tuple: (filled_matrix, is_closed) where is_closed indicates if shape properly closes
    """
    f4_chain, is_closed = c3ot_to_f4(c3ot_chain)
    
    if not is_closed:
        contour = f4_to_matrix(f4_chain)
        return contour, False
    
    contour = f4_to_matrix(f4_chain)
    filled = fill_shape(contour)
    return filled, True


# =============================
# UTILITY FUNCTIONS (PURE LOGIC)
# =============================

def get_contour_f4(f4_chain):
    """
    Get only the contour (not filled) from F4 chain.
    
    Args:
        f4_chain (list): F4 directions (0-3)
        
    Returns:
        np.ndarray: Matrix with contour drawn (value 255)
    """
    return f4_to_matrix(f4_chain)


def get_contour_f8(f8_chain):
    """
    Get only the contour (not filled) from F8 chain.
    
    Args:
        f8_chain (list): F8 directions (0-7)
        
    Returns:
        np.ndarray: Matrix with contour drawn (value 255)
    """
    return f8_to_matrix(f8_chain)


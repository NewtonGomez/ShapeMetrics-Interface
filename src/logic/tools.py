import numpy as np
import os
from PIL import Image

def reorder_contour(contour):
    """
    Reorder contour points to start from top-left and traverse clockwise.
    """
    if contour is None or contour.size == 0:
        return None

    points = contour.reshape(-1, 2)

    # Find starting point: topmost, then leftmost
    start_idx = min(range(len(points)), key=lambda i: (points[i][1], points[i][0]))

    # Rotate list to start from that point
    points = np.concatenate((points[start_idx:], points[:start_idx]), axis=0)

    # Reverse order to make it clockwise
    points = points[::-1]

    return points.reshape((-1, 1, 2))

def save_matrix_to_csv(matrix_data:np.ndarray, filename: str):
    filename = filename.split(".")[0]
    if not filename.endswith('.csv'):
        filename = f"{filename}.csv"

    np.savetxt(filename, matrix_data, delimiter=",", fmt='%g')
    
    print(f"File saved successfully: {filename}")

def process_and_binarize(filename, input_folder="samples", threshold=128):
    input_path = os.path.join(input_folder, filename)

    try:
        with Image.open(input_path) as img:
            img.seek(0)
            gray_img = img.convert('L')
            np_array = np.array(gray_img)
            
            binary_array = (np_array > threshold).astype(int)
            
            return binary_array
    except Exception as e:
        print(e)

def connected_components(matrix:np.ndarray, neighbor:int = 4) -> int:
    rows, cols = matrix.shape
    visited_position = np.zeros((rows,cols), dtype=bool)

    if neighbor == 4:
        movements:list[tuple] = [(0,1), (0,-1), (-1,0), (1, 0)] 
    elif neighbor == 8:
        movements:list[tuple] = [(0,1), (0,-1), (-1,0), (1, 0), 
                                   (-1, 1), (-1, -1), (1, 1), (1, -1)] 
    else:
        return TypeError("Vecindad no permitida")
    
    num_objects:int = 0
    for i in range(1, rows-1):
        for j in range(1, cols-1):
            if matrix[i][j] == 1 and not visited_position[i][j]:
                num_objects += 1

                pile = [(i, j)]
                visited_position[i][j] = True

                while pile:
                    actual_row, actual_col = pile.pop()

                    for dr, dc in movements:
                        nr, nc = actual_row + dr, actual_col + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if matrix[nr][nc] == 1 and not visited_position[nr][nc]:
                                visited_position[nr][nc] = True
                                pile.append((nr, nc))

    return num_objects

def find_outline(matrix:np.ndarray) -> dict:
    rows, cols = matrix.shape
    cont_outline = 0
    outline = np.zeros((rows, cols), dtype=int)
    for i in range(1, rows-1):
        for j in range(1, cols-1):
            if matrix[i][j] == 0:
                continue

            neighborhood_sum = (matrix[i, j-1] + matrix[i, j+1] + 
                                   matrix[i-1, j] + matrix[i+1, j])
            if neighborhood_sum < 4:
                outline[i][j] = 1
                cont_outline += 1
            else:
                outline[i][j] = 0
    return {"contorno": reorder_contour(outline), "perimetro":cont_outline}
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

def save_matrix_to_csv(matrix_data: np.ndarray, filename: str):
    """
    Save matrix data to CSV file.
    """
    # Remove existing extension if present
    filename = filename.split(".")[0]
    
    # Ensure CSV extension
    if not filename.endswith('.csv'):
        filename = f"{filename}.csv"

    # Write matrix to file with comma delimiter
    np.savetxt(filename, matrix_data, delimiter=",", fmt='%g')
    
    print(f"File saved successfully: {filename}")

def process_and_binarize(filename, threshold=128):
    """
    Load image, convert to grayscale, and apply binary threshold.
    """
    try:
        # Load image and convert to single channel
        with Image.open(filename) as img:
            img.seek(0)
            gray_img = img.convert('L')
            np_array = np.array(gray_img)
            
            # Convert to binary: 1 if pixel > threshold, 0 otherwise
            binary_array = (np_array > threshold).astype(int)
            
            return binary_array
    except Exception as e:
        # Return exception object on failure
        return e

def connected_components(matrix: np.ndarray, neighbor: int = 4) -> int:
    """
    Count number of connected components in binary matrix.
    """
    rows, cols = matrix.shape
    visited = np.zeros((rows, cols), dtype=bool)

    # Define movement directions based on connectivity type
    if neighbor == 4:
        movements: list[tuple] = [(0, 1), (0, -1), (-1, 0), (1, 0)]
    elif neighbor == 8:
        movements: list[tuple] = [(0, 1), (0, -1), (-1, 0), (1, 0),
                                   (-1, 1), (-1, -1), (1, 1), (1, -1)]
    else:
        return TypeError("Invalid neighborhood type")
    
    num_objects: int = 0
    
    # Scan image for unvisited foreground pixels
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            # Found new unvisited foreground pixel
            if matrix[i][j] == 1 and not visited[i][j]:
                num_objects += 1

                # Use stack-based flood fill to mark all connected pixels
                stack = [(i, j)]
                visited[i][j] = True

                while stack:
                    current_row, current_col = stack.pop()

                    # Check all neighbors
                    for dr, dc in movements:
                        next_row, next_col = current_row + dr, current_col + dc
                        # Verify bounds and foreground/unvisited condition
                        if 0 <= next_row < rows and 0 <= next_col < cols:
                            if matrix[next_row][next_col] == 1 and not visited[next_row][next_col]:
                                visited[next_row][next_col] = True
                                stack.append((next_row, next_col))

    return num_objects

def find_outline(matrix: np.ndarray) -> dict:
    """
    Detect object outline/edges using neighborhood analysis.
    """
    rows, cols = matrix.shape
    outline_count = 0
    outline = np.zeros((rows, cols), dtype=int)
    
    # Scan interior pixels (skip borders)
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            # Skip background pixels
            if matrix[i][j] == 0:
                continue

            # Sum 4-neighborhood values
            neighborhood_sum = (matrix[i, j - 1] + matrix[i, j + 1] +
                               matrix[i - 1, j] + matrix[i + 1, j])
            
            # Edge pixel: has at least one background neighbor
            if neighborhood_sum < 4:
                outline[i][j] = 1
                outline_count += 1
            else:
                # Interior pixel: all neighbors are foreground
                outline[i][j] = 0
    
    return {"contour": reorder_contour(outline), "perimeter": outline_count}
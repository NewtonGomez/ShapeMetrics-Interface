import numpy as np
import os
import math
from collections import Counter
from PIL import Image
import heapq
import matplotlib.pyplot as plt

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
            binary_array = ((np_array > threshold)*255).astype(int)
            
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
    #rows, cols = matrix.shape
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
            if neighborhood_sum < 1020:
                outline[i][j] = 1
                outline_count += 1
            else:
                # Interior pixel: all neighbors are foreground
                outline[i][j] = 0
    
    return {"contour": outline, "perimeter": outline_count}

def plot_histograms(frequency_dict, probability_dict):
    """
    Generates two stacked, plots.
    """
    if not frequency_dict or not probability_dict:
        print("Error")
        return

    # Extract and sort symbols for the X-axis
    symbols = sorted(list(frequency_dict.keys()))
    
    # Extract frequencies and probabilities matching the sorted symbols
    frequencies = [frequency_dict[sym] for sym in symbols]
    probabilities = [probability_dict[sym] for sym in symbols]

    plt.style.use('default')
    
    # Create two subplots stacked vertically (sharex=True aligns the X-axes)
    fig, (ax_freq, ax_prob) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Custom background color 
    fig.patch.set_facecolor('white') 
    ax_freq.set_facecolor('white')
    ax_prob.set_facecolor('white')

    # Colors
    primary_color = '#4A90E2' # Standard solid blue for academic charts
    text_color = '#000000'    # Pure black for maximum readability
    grid_color = '#E0E0E0'    # Light gray for a subtle grid

    # Frquency
    ax_freq.bar(symbols, frequencies, width=0.8, facecolor=primary_color, alpha=1.0, edgecolor=primary_color, linewidth=0.5)
    
    # Titles and labels 
    ax_freq.set_title("1. Symbol Frequency (Count)", fontsize=14, fontweight='bold', color=text_color, y=1.02)
    ax_freq.set_ylabel("Frequency (Count)", color=text_color, fontsize=13, fontweight='bold')
    ax_freq.tick_params(axis='y', labelcolor=text_color, colors=text_color)
    
    # Configure a minimal grid
    ax_freq.grid(True, linestyle='--', color=grid_color, alpha=0.7)
    # Hide top/right spines
    ax_freq.spines['top'].set_visible(False)
    ax_freq.spines['right'].set_visible(False)

    # Bottom plot
    # Draw line with markers (points) using the same primary color
    ax_prob.plot(symbols, probabilities, color=primary_color, marker='o', markersize=9, linewidth=2.5, markerfacecolor=primary_color, markeredgecolor=primary_color, markeredgewidth=1)
    
    # Titles and labels for Probability plot
    ax_prob.set_title("2. Symbol Probability Distribution", fontsize=14, fontweight='bold', color=text_color, y=1.02)
    ax_prob.set_ylabel("Probability", color=text_color, fontsize=13, fontweight='bold')
    ax_prob.tick_params(axis='y', labelcolor=text_color, colors=text_color)
    
    # Common X-axis label
    ax_prob.set_xlabel("Chain Code Symbol", fontsize=13, fontweight='bold', color=text_color)
    ax_prob.set_xticks(symbols)
    ax_prob.tick_params(axis='x', labelcolor=text_color, colors=text_color)

    # Configure a minimal grid for the bottom plot
    ax_prob.grid(True, linestyle='--', color=grid_color, alpha=0.7)
    # Hide top/right spines
    ax_prob.spines['top'].set_visible(False)
    ax_prob.spines['right'].set_visible(False)
    
    # Ensure the Y-axis for probability starts at 0
    ax_prob.set_ylim(bottom=0)
    plt.suptitle("Chain Code Analysis: Frequency and Probability Dashboard", fontsize=16, fontweight='bold', color=text_color, y=0.98)
    fig.tight_layout(rect=[0, 0.03, 1, 0.96]) 

    plt.suptitle("Chain Code Analysis", fontsize=16, fontweight='bold', color=text_color, y=0.98)
    fig.tight_layout(rect=[0, 0.03, 1, 0.96])
    
    return fig


def calculate_entropy(chain):
    """
    Calculate the Shannon entropy
    Returns: The Shannon entropy limit
    """
    if not chain:
        return 0.0
    
    total_symbol = len(chain)
    frequency = dict(Counter(chain))
    probability = {sym: freq / total_symbol for sym, freq in frequency.items()}
    entropy = -sum(
        p * math.log2(p)
        for p in probability.values()
        if p > 0 
        )

    return entropy

def lenght_compression_arithmetic(chain, probability_dict):
    """
    Calculate the theoretical average length of the arithmetic compression.
    Step-by-step mathematical implementation (Shannon's Entropy limit).
    Based on G. Langdon and J. Rissanen (1981).
    """
    # If the chain or the dictionary is empty, return 0.0
    if not chain or not probability_dict:
        return 0.0

    average_length = 0.0

    # Iterate through the dictionary symbol by symbol
    for symbol in probability_dict:
        prob = probability_dict[symbol]
        
        # Probability must be greater than 0 for the logarithm to exist
        if prob > 0:
            # Apply the mathematical change of base rule for base 2 logarithm:
            # log2(P) = ln(P) / ln(2)
            log2_prob = math.log(prob) / math.log(2)
            
            # Multiply the probability by its negative logarithm
            symbol_calculation = prob * (-log2_prob)
            
            # Add it to the total (Summation)
            average_length = average_length + symbol_calculation

    return average_length

#me dio dislexia arriba y en otras partes del código porque yo escribo "lenght" en lugar de length y no me acuerdo en donde

def length_huffman_compression(chain, probability_dict):
    """
    Calculate the average length using the Huffman tree.
    Return: average_length, dictionary_with_codes
    """
    if not chain or not probability_dict:
        return 0.0, 0, {}

    #We prepare the heap (tree data structure) probability, symbol and bits
    # An unique id avoid errors in heap when probabilities tie
    heap = []
    counter_id = 0
    for sym, prob in probability_dict.items():
        if prob > 0:
            heapq.heappush(heap, [prob, counter_id, [[sym, ""]]])
            counter_id += 1

    #Tree Huffman development
    while len(heap) > 1:
        low = heapq.heappop(heap)
        up = heapq.heappop(heap)

        #We asign "0" to the left branch and "1" to the right branch
        for pair in low[2]:
            pair[1] = '0' + pair[1]
        for pair in up[2]:
            pair[1] = '1' + pair[1]

        #we join the branches and bring it to the heap
        new_prob = low[0] + up[0]
        combinate_node = low[2] + up[2]

        heapq.heappush(heap, [new_prob, counter_id, combinate_node])
        counter_id += 1

    #Bring final results
    final_node = heapq.heappop(heap)[2]
    mean_length = 0.0
    total_bits = 0
    huffman_code = {}

    total_symbols = len(chain)
    
    for symbol, bits in final_node:
        mean_length += probability_dict[symbol] * len(bits)
        huffman_code[symbol] = bits

        freq = round (probability_dict[symbol]* total_symbols)
        total_bits += freq * len(bits)

    return mean_length, total_bits, huffman_code    
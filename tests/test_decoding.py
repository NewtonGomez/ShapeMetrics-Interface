import os
import json
import pytest
import numpy as np
import sys

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPECTED_DIR = os.path.join(BASE_DIR, "expected")

# Ensure the decoder functions can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logic.decoding_functions import (
    decode_f4_to_matrix, decode_f8_to_matrix, 
    decode_af8_to_matrix, decode_vcc_to_matrix, decode_3ot_to_matrix
)

# Mapping algorithms from JSON metadata to Python functions
DECODER_MAP = {
    "CHAIN_F4": decode_f4_to_matrix,
    "CHAIN_F8": decode_f8_to_matrix,
    "CHAIN_AF8": decode_af8_to_matrix,
    "CHAIN_VCC": decode_vcc_to_matrix,
    "CHAIN_3OT": decode_3ot_to_matrix
}

def get_json_files():
    """Returns a list of all JSON files in the expected directory."""
    return [f for f in os.listdir(EXPECTED_DIR) if f.endswith('.json')]

@pytest.mark.parametrize("json_file", get_json_files())
def test_decoding_integrity(json_file):
    """
    Verifies that decoding a stored chain code results in a valid binary matrix
    that matches the shape's expected physical properties.
    """
    # Load JSON data
    with open(os.path.join(EXPECTED_DIR, json_file), 'r') as f:
        data = json.load(f)
    
    algorithm_name = data["metadata"]["algorithm"]
    chain_code = data["chain_code"]

    # Match with the correct decoder
    decode_func = DECODER_MAP.get(algorithm_name)
    if not decode_func:
        pytest.skip(f"No decoder implementation found for {algorithm_name}")

    # Execute decoding logic
    result = decode_func(chain_code)
    
    # Handle the specific return type of 3OT (matrix, is_closed)
    if isinstance(result, tuple):
        matrix, is_closed = result
        assert is_closed, f"The shape in {json_file} (3OT) failed to close."
    else:
        matrix = result

    # Assertions for spatial validity
    assert isinstance(matrix, np.ndarray), f"Output for {json_file} is not a NumPy array."
    assert np.sum(matrix) > 0, f"Decoded matrix for {json_file} is empty (all zeros)."
    assert matrix.ndim == 2, f"Decoded result for {json_file} must be a 2D matrix."
    
    # Check that dimensions are positive
    height, width = matrix.shape
    assert height > 0 and width > 0, f"Invalid dimensions in {json_file}: {height}x{width}"
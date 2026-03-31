import sys
import os
import pytest
import inspect
import json

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
EXPECTED_DIR = os.path.join(BASE_DIR, "expected")

# Append parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logic import chain_codes
from src.logic.tools import process_and_binarize

# Discovery: Get all image files and all public chain code functions
IMAGE_FILES = [f for f in os.listdir(DATA_DIR) if f.endswith('.gif')]
PUBLIC_FUNCTIONS = [
    (name, func)
    for name, func in inspect.getmembers(chain_codes, inspect.isfunction)
    if not name.startswith('_')
]

def get_test_combinations():
    """Generates a list of (image_file, function_name, function_object)."""
    combinations = []
    for img in IMAGE_FILES:
        for func_name, func in PUBLIC_FUNCTIONS:
            combinations.append((img, func_name, func))
    return combinations

@pytest.mark.parametrize("image_file, func_name, func", get_test_combinations())
def test_validate_chain_code_output(image_file, func_name, func):
    """
    Validates that the output of a specific chain code function matches
    the pre-calculated JSON reference for a given image.
    """
    # Prepare Paths
    image_path = os.path.join(DATA_DIR, image_file)
    base_name = os.path.splitext(image_file)[0]
    
    # Map function name to JSON suffix (e.g., chain_f4 -> CHAIN_F4)
    algo_suffix = func_name.replace("chain_", "CHAIN_").upper()
    json_filename = f"{base_name}-{algo_suffix}.json"
    json_path = os.path.join(EXPECTED_DIR, json_filename)

    # Skip if the specific expected output doesn't exist yet
    if not os.path.exists(json_path):
        pytest.skip(f"Reference file not found: {json_filename}")

    # Process image and run function
    binarized_image = process_and_binarize(image_path)
    actual_chain = func(binarized_image)

    # Load expected data and compare
    with open(json_path, 'r') as f:
        expected_data = json.load(f)
    
    expected_chain = expected_data["chain_code"]
    
    assert actual_chain == expected_chain, f"Mismatch in {func_name} for {image_file}"
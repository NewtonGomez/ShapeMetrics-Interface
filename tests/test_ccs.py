import sys
import os
import pytest
import inspect

# Append the parent directory to sys.path to resolve imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logic import chain_codes
from src.logic.tools import process_and_binarize

# Define the path to the sample image
TEST_IMAGE_PATH = "/Users/enriquegomez/Library/CloudStorage/OneDrive-UniversidadAutónomadeAguascalientes/Estudios de Posgrado/Segundo Semestre/Nuevos Paradigmas Tecnologicos/Tarea 1/Tarea_1_2D/samples/car-08.gif"

# Create a fixture to process the image once per module execution
@pytest.fixture(scope="module")
def processed_image():
    """
    Loads and binarizes the image. The 'module' scope ensures 
    this expensive operation runs only once for all tests in this file.
    """
    return process_and_binarize(TEST_IMAGE_PATH)

# Extract all public functions from the chain_codes module
# We create a list of tuples containing (function_name, function_object)
PUBLIC_FUNCTIONS = [
    (name, func)
    for name, func in inspect.getmembers(chain_codes, inspect.isfunction)
    if not name.startswith('_')
]

# Parametrize the test to iterate over every function found
@pytest.mark.parametrize("func_name, func", PUBLIC_FUNCTIONS)
def test_chain_code_functions_execute_without_errors(func_name, func, processed_image):
    """
    Smoke test to verify that each function in the chain_codes module
    can execute and process a binarized image without throwing an error.
    """
    try:
        # Act: Execute the function with the processed image
        result = func(processed_image)
        
        # Optional: Print the result for manual inspection
        print(f"\n{func_name} executed successfully. Output: {result}")
        
    except Exception as e:
        # Assert: If any error occurs, explicitly fail the test with a clear message
        pytest.fail(f"Function '{func_name}' raised an unexpected exception: {e}")
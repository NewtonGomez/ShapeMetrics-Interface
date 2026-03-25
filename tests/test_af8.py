import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logic.chain_codes import chain_af8
from src.logic.tools import process_and_binarize

def test_chain_af8():
    image_path ="/Users/enriquegomez/Library/CloudStorage/OneDrive-UniversidadAutónomadeAguascalientes/Estudios de Posgrado/Segundo Semestre/Nuevos Paradigmas Tecnologicos/Tarea 1/Tarea_1_2D/samples/car-08.gif"
    image = process_and_binarize(image_path)
    cc = chain_af8(image)
    print(cc)
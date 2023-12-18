import numpy as np

def bitarray_to_ndarray(bitarray):
    return np.array([int(bit) for bit in bitarray], dtype=bool)

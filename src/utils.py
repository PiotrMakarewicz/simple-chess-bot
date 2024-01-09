import numpy as np
import chess

def bitarray_to_ndarray(bitarray):
    return np.array([int(bit) for bit in bitarray], dtype=bool)

def contains_pawn(board):
    for color in [chess.WHITE, chess.BLACK]:
        if board.pieces(chess.PAWN, color):
            return True
    return False

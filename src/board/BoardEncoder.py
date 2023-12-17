import chess
from bitstring import BitArray


class BoardEncoder:
    @staticmethod
    def __side_to_move_bit(board):
        return BitArray(bool=board.turn, length=1)
    
    @staticmethod
    def __piece_squares_bits(board):
        bits = BitArray(length=0)
        for piece_type in chess.PIECE_TYPES:
            for color in chess.COLORS:
                square_set = board.pieces(piece_type, color)
                squares_bits = BitArray(f'uint64={int(square_set)}')
                bits.append(squares_bits)
        return bits
    
    @staticmethod
    def __en_passant_bits(board):
        mask = 0 
        if board.has_legal_en_passant():
            mask |= 1 << (63 - int(board.ep_square))
        return BitArray(f'uint64={int(mask)}')
    
    @staticmethod
    def __castling_bit(board, square):
        return BitArray(bool=bool(board.castling_rights & square))

    @staticmethod
    def __castling_bits(board): 
        return BoardEncoder.__castling_bit(board, chess.BB_A1) \
             + BoardEncoder.__castling_bit(board, chess.BB_H1) \
             + BoardEncoder.__castling_bit(board, chess.BB_A8) \
             + BoardEncoder.__castling_bit(board, chess.BB_H8)
    
    @staticmethod
    def encode(board):
        side_to_move = BoardEncoder.__side_to_move_bit(board)
        piece_squares = BoardEncoder.__piece_squares_bits(board)
        en_passant = BoardEncoder.__en_passant_bits(board)
        castling = BoardEncoder.__castling_bits(board)
        return side_to_move + piece_squares + en_passant + castling

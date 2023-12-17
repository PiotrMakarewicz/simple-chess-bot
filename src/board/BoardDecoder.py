import chess

class BoardDecoder:
    @staticmethod
    def __side_to_move_bit(board, bits):
        board.turn = bool(bits[0])
        return board, bits[1:]
    
    @staticmethod
    def __piece_squares_bits(board, bits):
        for piece_type in chess.PIECE_TYPES:
            for color in chess.COLORS:
                for square in chess.SQUARES:
                    if bits[square]:
                        board.set_piece_at(square, chess.Piece(piece_type, color))
                bits = bits[64:]
        return board, bits
    
    @staticmethod
    def __en_passant_bits(board, bits):
        for square in chess.SQUARES:
            if bits[square]:
                board.ep_square = square
                break
        return board, bits[64:]
    
    @staticmethod
    def __castling_bits(board, bits):
        for i, square in enumerate([chess.BB_A1, chess.BB_H1, chess.BB_A8, chess.BB_H8]):
            if bits[i]:
                board.castling_rights |= square
        return board, bits[4:]

    @staticmethod
    def decode(bits):
        board = chess.Board()
        board.clear()
        
        board, bits = BoardDecoder.__side_to_move_bit(board, bits)
        board, bits = BoardDecoder.__piece_squares_bits(board, bits)
        board, bits = BoardDecoder.__en_passant_bits(board, bits)
        board, _ = BoardDecoder.__castling_bits(board, bits)
        return board

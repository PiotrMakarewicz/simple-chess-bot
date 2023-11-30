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


def test():
    fen_positions = [
        'B2B2RN/2Nn4/8/1P1p2PK/8/b3p1k1/p7/1Q1r4 w - - 0 1',
        '4b3/b2p1pQ1/2rpk3/7p/8/p2pP3/1p1K2P1/4N3 b - - 0 1',
        '8/pk6/1N1PP1b1/8/pP1p2P1/6P1/1P1n3r/2B1K3 w - - 0 1',
        '5b2/6pr/5p2/6p1/1P1r1PN1/p1p3k1/7n/B1R1K3 b - - 0 1',
        '5N2/3r2R1/2RqPPP1/3p4/1kp3p1/4p1P1/1K6/n7 w - - 0 1',
        '8/8/Pp4P1/3P2p1/PPKP4/3P2p1/1pk3b1/2b1n3 w - - 0 1',
        '3Br3/knP1r2P/7b/8/4B1p1/2R1NN2/2P2K2/n7 b - - 0 1',
        '4N3/1P1N1P1p/6k1/2R4p/2pp4/p3B1Kb/6BP/8 w - - 0 1',
        '2n5/P1K2kp1/8/1pp2P2/2pb1P2/4Ppp1/4qn2/8 w - - 0 1',
        'rnbqkb1r/pp1p1ppp/5n2/2pPp3/2P5/8/PP2PPPP/RNBQKBNR w KQkq e6 0 4'
    ]

    for fen in fen_positions:
        board = chess.Board(fen)
        bits = BoardEncoder.encode(board)
        board_decoded = BoardDecoder.decode(bits)

        assert board.turn == board_decoded.turn
        for square in chess.SQUARES:
            board.piece_at(square) == board_decoded.piece_at(square)
        assert board.ep_square == board_decoded.ep_square
        assert board.castling_rights == board_decoded.castling_rights

    print('Encoding/decoding works correctly')


if __name__ == '__main__':
    test()

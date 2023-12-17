import chess
from BoardDecoder import BoardDecoder
from BoardEncoder import BoardEncoder

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

import chess
from chess import pgn
from copy import deepcopy
from montecarlo.MonteCarloNode import MonteCarloNode
from board.BoardEncoder import BoardEncoder
from interactive.estimator import ModelBasedEvaluator, SyzygyEvaluator
import pickle
from stockfish import Stockfish


USE_MODEL_EVALUATOR = True  # False for Syzygy, True for model
USE_STOCKFISH_FOR_TESTING = True  # false to allowing typing in moves interactively

KQ_K_MODEL = '../models/model-20231218192512.pkl'
KQ_OR_KP_K_MODEL = '../models/model-20240109150324.pkl'

evaluator = None
mc_node = None
EXPLORATION_ITERATIONS = 2000

def human_turn(board):
    move = None
    while not move:
        uci = input('Enter move (UCI notation): ')
        try:
            _board = deepcopy(board)
            _board.push_uci(uci)
            move = _board.peek()
        except Exception as e:
            print('Invalid move. Error: ', e)
    return move, _board

def load_model_evaluator(load_path=KQ_K_MODEL):
    global evaluator
    with open(load_path, 'rb') as file:
        model = pickle.load(file)
        evaluator = ModelBasedEvaluator(model)

def load_syzygy_evaluator():
    global evaluator
    load_path = '../tables/standard/3-4-5'
    tablebase = chess.syzygy.open_tablebase(load_path)
    evaluator = SyzygyEvaluator(tablebase)

def ai_turn(board):
    global mc_node, evaluator
    if mc_node is None:
        mc_node = MonteCarloNode(root_board=board,
                         is_leaf=board.is_game_over(),
                         parent=None,
                         node_board=board, 
                         move_stack=[],
                         evaluation_func=lambda board: evaluator.evaluate(board),
                         player_color=board.turn)
    else:
        last_move = board.peek()
        mc_node = mc_node.child[last_move]
    
    for _ in range(EXPLORATION_ITERATIONS):
        mc_node.explore()

    move, mc_node = mc_node.next()
    return move, mc_node.node_board

stockfish = Stockfish(parameters={
        "Debug Log File": "",
        "Contempt": 0,
        "Min Split Depth": 0,
        "Threads": 4, # More threads will make the engine stronger, but should be kept at less than the number of logical processors on your computer.
        "Ponder": "false",
        "Hash": 4096,
        "MultiPV": 1,
        "Skill Level": 20,
        "Move Overhead": 10,
        "Minimum Thinking Time": 20,
        "Slow Mover": 100,
        "UCI_Chess960": "false",
        "UCI_LimitStrength": "false",
        "UCI_Elo": 1350
    })
stockfish.set_elo_rating(3500)

def stockfish_turn(board):
    global stockfish
    stockfish.set_fen_position(board.fen())
    move = stockfish.get_best_move()
    board.push_uci(move)
    print(f"Stockfish played: {move}")
    return chess.Move.from_uci(move), board

def opponent_turn(board):
    if USE_STOCKFISH_FOR_TESTING:
        return stockfish_turn(board)
    else:
        return human_turn(board)


def print_pgn(board):
    pgn_game = pgn.Game().from_board(board)
    print(pgn_game)


KQ_K_FEN = '8/8/8/8/3K4/8/3k4/3q4 w - - 0 1' # king + queen vs king
KP_K_FEN = 'k7/8/8/8/8/8/4P3/7K w - - 0 1' # king + pawn vs king

def play():
    starting_fen = KP_K_FEN
    board = chess.Board(starting_fen)
    print(board)

    while not board.is_game_over():
        move, board = ai_turn(board)
        print(f'AI played: {move.uci()}')
        print(board)
        if board.is_game_over():
            break
        move, board = opponent_turn(board)
        print(board)
        
    print("Game finished!")
    print(board.result())
    print("Game length: ", board.fullmove_number)
    print_pgn(board)
    

# def collect_positions_for_training(n_games=100000):
#     starting_fen = KQ_K_FEN
#     board = chess.Board(starting_fen)
#     print(board)
#     positions = []
#     while not board.is_game_over():
#         move, board = ai_turn(board)
#         print(f'AI played: {move.uci()}')
#         print(board)
#         positions.append(BoardEncoder.encode(board))
#         if board.is_game_over():
#             break
#         move, board = opponent_turn(board)
#         print(board)
#         positions.append(BoardEncoder.encode(board))
        
#     print("Game finished!")
#     print(board.result())
#     print("Game length: ", board.fullmove_number)
#     print_pgn(board)
#     return positions

if __name__ == '__main__':
    if USE_MODEL_EVALUATOR:
        load_model_evaluator()
    else:
        load_syzygy_evaluator()
    play()

import chess
from copy import deepcopy
from montecarlo.MonteCarloNode import MonteCarloNode
from board.BoardEncoder import BoardEncoder
from utils import bitarray_to_ndarray
import pickle


model = None
mc_node = None
EXPLORATION_ITERATIONS = 1000

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

def load_model():
    global model
    load_path = '../models/model-20231218192512.pkl'
    with open(load_path, 'rb') as file:
        model = pickle.load(file)

def get_estimation(model, board):
    X = bitarray_to_ndarray(BoardEncoder.encode(board)).reshape(1, -1)
    return model.predict(X)[0]

def ai_turn(board):
    global mc_node, model
    if mc_node is None:
        mc_node = MonteCarloNode(root_board=board,
                         is_leaf=board.is_game_over(),
                         parent=None,
                         node_board=board, 
                         move_stack=[],
                         evaluation_func=lambda board: get_estimation(model, board))
    else:
        last_move = board.peek()
        mc_node = mc_node.child[last_move]
    
    for i in range(EXPLORATION_ITERATIONS):
        mc_node.explore()

    move, mc_node = mc_node.next()
    return move, mc_node.node_board

def play():
    starting_fen = '8/8/8/8/3K4/8/3k4/3q4 w - - 0 1'
    board = chess.Board(starting_fen)
    print(board)

    while not board.is_game_over():
        move, board = human_turn(board)
        print(board)
        if board.is_game_over():
            break
        move, board = ai_turn(board)
        print(f'AI played: {move.uci()}')
        print(board)
        
    print("Game finished!")
    print(board.result())

if __name__ == '__main__':
    load_model()
    play()

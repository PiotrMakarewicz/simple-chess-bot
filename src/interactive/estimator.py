from chess import syzygy
import chess
from board.BoardEncoder import BoardEncoder
from utils import bitarray_to_ndarray

class Evaluator:
    def evaluate():  # this should evaluate the position from the perspective of white
        raise NotImplementedError()
    
class ModelBasedEvaluator(Evaluator):
    def __init__(self, model):
        self.model = model
    
    def evaluate(self, board):
        turn_factor = -1 if board.turn == chess.WHITE else 1
        if board.is_game_over():
            if board.outcome().result() == '1/2-1/2':
                return 0
            elif board.outcome().winner == chess.WHITE:
                return 1000 * turn_factor
            else:
                return -1000 * turn_factor
        X = bitarray_to_ndarray(BoardEncoder.encode(board)).reshape(1, -1)
        return self.model.predict(X)[0]*turn_factor


class SyzygyEvaluator(Evaluator):
    def __init__(self, tablebase: syzygy.Tablebase):
        self.tablebase = tablebase
    
    def evaluate(self, board):
        score = self.do_evaluate(board)
        if score < 0:
            print("Negative score: ", score)
            print(board)
            raise Exception("Negative score")
        return score
    
    def do_evaluate(self, board):
        turn_factor = -1 if board.turn == chess.WHITE else 1

        if board.is_game_over():
            if board.outcome().result() == '1/2-1/2':
                return 0
            elif board.outcome().winner == chess.WHITE:
                return 1000 * turn_factor
            else:
                return -1000 * turn_factor
        

        dtz = self.tablebase.probe_dtz(board)
        if dtz > 0:
            return (max(101 - dtz, 50)) * turn_factor
        elif dtz < 0:
            return (min(-101-dtz, -50)) * turn_factor
        return 0
    
    


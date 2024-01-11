from copy import deepcopy

MAX_DEPTH = 50

max_cache = {}
min_cache = {}


def search(board, evaluator):
    return max_value(board, evaluator, -10000, 10000, 0)


def get_new_board(board, action):
    new_board = deepcopy(board)
    new_board.push(action)
    return new_board


def max_value(board, evaluator, alpha, beta, depth):
    printed, color = str(board), board.turn
    if (printed, color) in max_cache:
        return max_cache[(printed, color)]
    if board.is_game_over() or depth == MAX_DEPTH:
        return None, evaluator.evaluate(board)

    max_action = None
    max_value = -10000

    for action in board.legal_moves:
        new_board = get_new_board(board, action)
        mv = min_value(new_board, evaluator, alpha, beta, depth+1)
        if mv >= max_value:
            max_action = action
            max_value = mv
        if mv >= beta:
            max_cache[(printed, color)] = (max_action, max_value)
            return max_action, max_value
        alpha = max(alpha, max_value)
    max_cache[(printed, color)] = (max_action, max_value)
    return max_action, max_value


def min_value(board, evaluator, alpha, beta, depth):
    printed, color = str(board), board.turn
    if (printed, color) in min_cache:
        return min_cache[(printed, color)]
    if board.is_game_over() or depth == MAX_DEPTH:
        return -1 * evaluator.evaluate(board)

    min_value = 10000

    for action in board.legal_moves:
        new_board = get_new_board(board, action)
        _, mv = max_value(new_board, evaluator, alpha, beta, depth+1)
        if mv <= min_value:
            min_value = mv
        if min_value <= alpha:
            min_cache[(printed, color)] = min_value
            return min_value
        beta = min(beta, min_value)
    min_cache[(printed, color)] = min_value
    return min_value

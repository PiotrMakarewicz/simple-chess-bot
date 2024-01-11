from chess.polyglot import zobrist_hash

MAX_DEPTH = 10000

max_cache = {}
min_cache = {}


def search(board, evaluator):
    return max_value(board, evaluator, -10000, 10000, 0)


def max_value(board, evaluator, alpha, beta, depth):
    hash = zobrist_hash(board)
    if hash in max_cache:
        return max_cache[hash]
    if board.is_game_over() or depth == MAX_DEPTH:
        return None, evaluator.evaluate(board)

    max_action = None
    max_value = -10000

    for action in board.legal_moves:
        board.push(action)
        mv = min_value(board, evaluator, alpha, beta, depth+1)
        board.pop()
        if mv >= max_value:
            max_action = action
            max_value = mv
        if mv >= beta:
            break
        alpha = max(alpha, max_value)
    max_cache[hash] = (max_action, max_value)
    return max_action, max_value


def min_value(board, evaluator, alpha, beta, depth):
    hash = zobrist_hash(board)
    if hash in min_cache:
        return min_cache[hash]
    if board.is_game_over() or depth == MAX_DEPTH:
        value = -1 * evaluator.evaluate(board)
        min_cache[hash] = value
        return value

    min_value = 10000

    for action in board.legal_moves:
        board.push(action)
        _, mv = max_value(board, evaluator, alpha, beta, depth+1)
        board.pop()
        min_value = min(min_value, mv)
        if min_value <= alpha:
            break
        beta = min(beta, min_value)
    min_cache[hash] = min_value
    return min_value

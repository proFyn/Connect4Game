# minimax.py
from board import  checkwin, board
from heuristic import evaluate_board
import numpy as np
def minimax(is_maximizing, depth, alpha, beta):
    winner = checkwin()

    if winner == 2:
        return 1000
    if winner == 1:
        return -1000
    if np.all(board != 0):
        return 0
    if depth == 0:
        return evaluate_board()

    if is_maximizing:
        best = -float("inf")

        for col in range(1, 8):
            for row in range(5, -1, -1):
                if board[row, col-1] == 0:

                    board[row, col-1] = 2
                    score = minimax(False, depth-1, alpha, beta)
                    board[row, col-1] = 0

                    best = max(best, score)
                    alpha = max(alpha, best)

                    break

            if alpha >= beta:
                break

        return best

    else:
        best = float("inf")

        for col in range(1, 8):
            for row in range(5, -1, -1):
                if board[row, col-1] == 0:

                    board[row, col-1] = 1
                    score = minimax(True, depth-1, alpha, beta)
                    board[row, col-1] = 0

                    best = min(best, score)
                    beta = min(beta, best)

                    break

            if alpha >= beta:
                break

        return best
    





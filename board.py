# board.py

import numpy as np

board = np.zeros((6,7),dtype=int)

def checkboard():
    print("\n==========================")
    print("  1 2 3 4 5 6 7")
    for r in board:
        print("| " + " ".join(map(str, r)) + " |")

def play(col, value ):
    col -= 1  
    if col < 0 or col >= 7:
        print("choose column between 1 and 7 ")
        return False

    for row in range(5, -1, -1):
        if board[row, col] == 0:
            board[row, col] = value
            return True

    print("column is full")
    return False

def checkwin():
    rows, cols = board.shape
    for i in range(rows):
        for j in range(cols - 3):
            if (board[i, j:j+4] == 1).all():
                return 1
            if (board[i, j:j+4] == 2).all():
                return 2

    for j in range(cols):
        for i in range(rows - 3):
            if (board[i:i+4, j] == 1).all():
                return 1
            if (board[i:i+4, j] == 2).all():
                return 2
    # diagonal ↘
    for i in range(rows - 3):
        for j in range(cols - 3):
            if (board[i, j] == board[i+1, j+1] == board[i+2, j+2] == board[i+3, j+3]) and board[i, j] != 0:
                return board[i, j]

    # diagonal ↗
    for i in range(3, rows):
        for j in range(cols - 3):
            if (board[i, j] == board[i-1, j+1] == board[i-2, j+2] == board[i-3, j+3]) and board[i, j] != 0:
                return board[i, j]
    return False




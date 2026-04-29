
# players.py
from board import checkboard, play, checkwin, board
from minimax import minimax
import random


def player(n):
    checkboard()
    print(f"=== player {n} ===")
    while True:
        col = input("choose column (1-7) or q to quit : ")
        if col == "q":
            print("game exited")
            exit()
        try:
            col = int(col)
        except:
            print("invalid input")
            continue

        if play(col, n):
            break

    if checkwin():
        checkboard()
        print(f"player {n} won")
        return False

    return True 

def ai_player(n,level):
    
    print(f"=== AI player {n} ===")



    # =========================
    # EASY MODE (random)
    # =========================
    valid_cols = [c for c in range(1, 8) if board[0, c-1] == 0]
    if level == 1:
        col = random.choice(valid_cols)
        play(col, n)

        if checkwin():
            checkboard()
            print(f"AI player {n} won")
            return False

        return True
    
    # =========================
    # HARD MODE (minimax)
    # =========================
    best_score = -float("inf")
    best_col = None
    for col in range(1, 8):

        for row in range(5, -1, -1):
            if board[row, col-1] == 0:

                board[row, col-1] = n
                score = minimax(False, level-1, -float("inf"), float("inf"))  
                board[row, col-1] = 0

                if score > best_score:
                    best_score = score
                    best_col = col

                break
    if best_col is not None:
        play(best_col, n)
   


    if checkwin():
        checkboard()
        print(f"AI player {n} won")
        return False

    return True



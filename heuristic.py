from board import  board


def evaluate_board():
    score = 0
    rows, cols = board.shape

    def window_score(window, player):
        s = 0

        if window.count(player) == 3 and window.count(0) == 1:
            s += 100
        elif window.count(player) == 2 and window.count(0) == 2:
           if   window[0] == window[1] == player or \
                window[1] == window[2] == player or \
                window[2] == window[3] == player:
            s += 10  
        else:
            opp = 1 if player == 2 else 2
            if window.count(opp) == 0:
                s += 3  
           
        return s 

    # =========================
    # Horizontal
    # =========================
    for r in range(rows):
        row = list(board[r, :])
        for c in range(cols - 3):
            window = row[c:c+4]
            score += window_score(window, 2)
            score -= window_score(window, 1)

    # =========================
    # Vertical
    # =========================
    for c in range(cols):
        col = list(board[:, c])
        for r in range(rows - 3):
            window = col[r:r+4]
            score += window_score(window, 2)
            score -= window_score(window, 1)

    # =========================
    # Diagonal ↘
    # =========================
    for r in range(rows - 3):
        for c in range(cols - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += window_score(window, 2)
            score -= window_score(window, 1)

    # =========================
    # Diagonal ↗
    # =========================
    for r in range(3, rows):
        for c in range(cols - 3):
            window = [board[r-i][c+i] for i in range(4)]
            score += window_score(window, 2)
            score -= window_score(window, 1)

    return score
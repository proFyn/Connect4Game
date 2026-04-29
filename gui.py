import tkinter as tk
from tkinter import messagebox
import threading
import random
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from board import board, checkboard, play, checkwin
from minimax import minimax
from heuristic import evaluate_board
from vars import setDiff

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
ROWS, COLS = 6, 7
CELL   = 140        # px per cell
RADIUS = 44       # disc radius
PAD    = 16         # board padding

W = COLS * CELL + PAD * 2
H = ROWS * CELL + PAD * 2 + CELL   # extra row on top for the drop indicator

BG        = "#0d1117"
BOARD_COL = "#1c2a3a"
EMPTY     = "#0a1825"
P1_COL    = "#ff0015"   #   – human
P2_COL    = "#11f900"   #  – AI
HOVER_COL = "#ffffff"
TEXT_COL  = "#e6edf3"

FONT_TITLE  = ("Helvetica", 18, "bold")
FONT_STATUS = ("Helvetica", 13)


# ─────────────────────────────────────────────────────────────────────────────
# Difficulty picker 
# ─────────────────────────────────────────────────────────────────────────────
def pick_difficulty(root):
    """Modal window; blocks until user picks a level. Returns 1-4."""
    level = tk.IntVar(value=2)
    win = tk.Toplevel(root)
    win.title("Connect 4")
    win.configure(bg=BG)
    win.resizable(False, False)
    win.grab_set()

    tk.Label(win, text="Select difficulty", font=FONT_TITLE,
             bg=BG, fg=TEXT_COL).pack(padx=40, pady=(28, 12))

    options = [("Easy",   1), ("Medium", 2), ("Hard", 3), ("Expert", 4)]
    for label, val in options:
        tk.Radiobutton(
            win, text=label, variable=level, value=val,
            font=FONT_STATUS, bg=BG, fg=TEXT_COL,
            selectcolor="#2d3a4a", activebackground=BG,
            activeforeground=TEXT_COL, indicatoron=True,
        ).pack(anchor="w", padx=48, pady=2)

    def confirm():
        win.destroy()

    tk.Button(
        win, text="Start Game", command=confirm,
        font=FONT_STATUS, bg=P1_COL, fg="white",
        relief="flat", padx=20, pady=6, cursor="hand2",
    ).pack(pady=(18, 28))

    win.wait_window()
    return level.get()


# ─────────────────────────────────────────────────────────────────────────────
# Main GUI class
# ─────────────────────────────────────────────────────────────────────────────
class Connect4GUI:
    def __init__(self, root, level):
        self.root  = root
        self.level = level
        self.hover_col = None       # column mouse is over (0-indexed)
        self.game_over = False
        self.ai_thinking = False

        root.title("Connect 4")
        root.configure(bg=BG)
        root.resizable(False, False)

        # ── status label ──────────────────────────────────────────────────────
        self._diff_names = {1: "Easy", 2: "Medium", 3: "Hard", 4: "Expert"}
        self.status_var = tk.StringVar(
            value=f"Your turn  ·  AI: {self._diff_names[level]}")
        tk.Label(root, textvariable=self.status_var,
                 font=FONT_STATUS, bg=BG, fg=TEXT_COL,
                 pady=6).pack()

        # ── canvas ────────────────────────────────────────────────────────────
        self.canvas = tk.Canvas(root, width=W, height=H,
                                bg=BG, highlightthickness=0)
        self.canvas.pack(padx=20, pady=(0, 10))

        # ── bottom bar: difficulty selector + restart ─────────────────────────
        bar = tk.Frame(root, bg=BG)
        bar.pack(pady=(0, 16))

        tk.Label(bar, text="Difficulty:", font=FONT_STATUS,
                 bg=BG, fg=TEXT_COL).pack(side="left", padx=(0, 8))

        diff_names = ["Easy", "Medium", "Hard", "Expert"]
        self.diff_var = tk.StringVar(value=diff_names[level - 1])
        diff_menu = tk.OptionMenu(bar, self.diff_var, *diff_names,
                                  command=self._on_diff_change)
        diff_menu.config(font=FONT_STATUS, bg=BOARD_COL, fg=TEXT_COL,
                         activebackground="#2d3a4a", activeforeground=TEXT_COL,
                         relief="flat", bd=0, highlightthickness=0,
                         cursor="hand2", indicatoron=True)
        diff_menu["menu"].config(font=FONT_STATUS, bg=BOARD_COL, fg=TEXT_COL,
                                 activebackground=P1_COL,
                                 activeforeground="white", bd=0)
        diff_menu.pack(side="left", padx=(0, 16))

        tk.Button(
            bar, text="↺  New Game", command=self.restart,
            font=FONT_STATUS, bg=BOARD_COL, fg=TEXT_COL,
            relief="flat", padx=16, pady=5, cursor="hand2",
            activebackground="#2d3a4a", activeforeground=TEXT_COL,
        ).pack(side="left")

        # ── events ────────────────────────────────────────────────────────────
        self.canvas.bind("<Motion>",   self._on_mouse_move)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Leave>",    self._on_leave)

        self.draw_board()

    # ── coordinate helpers ───────────────────────────────────────────────────
    def cell_center(self, row, col):
        """Canvas coords for the center of a board cell (row/col 0-indexed)."""
        x = PAD + col * CELL + CELL // 2
        y = PAD + CELL + row * CELL + CELL // 2   # +CELL for the top indicator row
        return x, y

    def col_from_x(self, x):
        """Return 0-indexed column from canvas x, or None if outside board."""
        col = (x - PAD) // CELL
        if 0 <= col < COLS:
            return int(col)
        return None

    # ── drawing ──────────────────────────────────────────────────────────────
    def draw_board(self):
        c = self.canvas
        c.delete("all")

        # board background
        c.create_rectangle(PAD, PAD + CELL, W - PAD, H - PAD,
                            fill=BOARD_COL, outline="", width=0)

        # discs
        for row in range(ROWS):
            for col in range(COLS):
                x, y = self.cell_center(row, col)
                val = board[row, col]
                color = EMPTY if val == 0 else (P1_COL if val == 1 else P2_COL)
                c.create_oval(x - RADIUS, y - RADIUS,
                              x + RADIUS, y + RADIUS,
                              fill=color, outline="")

        # hover indicator (top row)
        if self.hover_col is not None and not self.game_over and not self.ai_thinking:
            x = PAD + self.hover_col * CELL + CELL // 2
            y = PAD + CELL // 2
            c.create_oval(x - RADIUS * 0.55, y - RADIUS * 0.55,
                          x + RADIUS * 0.55, y + RADIUS * 0.55,
                          fill=P1_COL, outline="")

    # ── event handlers ────────────────────────────────────────────────────────
    def _on_mouse_move(self, event):
        col = self.col_from_x(event.x)
        if col != self.hover_col:
            self.hover_col = col
            self.draw_board()

    def _on_leave(self, event):
        self.hover_col = None
        self.draw_board()

    def _on_click(self, event):
        if self.game_over or self.ai_thinking:
            return
        col = self.col_from_x(event.x)
        if col is None:
            return
        col_1idx = col + 1          # play() uses 1-indexed columns
        if not play(col_1idx, 1):   # column full or invalid
            return
        self.draw_board()

        winner = checkwin()
        if winner:
            self._end_game(f"🎉  You win!")
            return
        if self._is_draw():
            self._end_game("🤝  Draw!")
            return

        self._run_ai()

    # ── AI turn ───────────────────────────────────────────────────────────────
    def _run_ai(self):
        """Run AI in a background thread so the GUI doesn't freeze."""
        self.ai_thinking = True
        self.status_var.set("AI is thinking…")
        self.draw_board()

        def ai_work():
            col = self._ai_choose()
            self.root.after(0, lambda: self._ai_play(col))

        threading.Thread(target=ai_work, daemon=True).start()

    def _ai_choose(self):
        """Returns best 1-indexed column for AI (player 2)."""
        # Easy: random
        if self.level == 1:
            valid = [c for c in range(1, 8) if board[0, c - 1] == 0]
            return random.choice(valid)

        # Medium / Hard / Expert: minimax
        best_score = -float("inf")
        best_col   = None
        for col in range(1, 8):
            for row in range(5, -1, -1):
                if board[row, col - 1] == 0:
                    board[row, col - 1] = 2
                    score = minimax(False, self.level - 1,
                                    -float("inf"), float("inf"))
                    board[row, col - 1] = 0
                    if score > best_score:
                        best_score = score
                        best_col   = col
                    break

        return best_col

    def _ai_play(self, col):
        if col is None:
            return
        play(col, 2)
        self.ai_thinking = False
        self.draw_board()

        winner = checkwin()
        if winner:
            self._end_game("🤖  AI wins!")
            return
        if self._is_draw():
            self._end_game("🤝  Draw!")
            return

        self.status_var.set("Your turn")

    # ── game-state helpers ────────────────────────────────────────────────────
    def _is_draw(self):
        import numpy as np
        return bool((board != 0).all())

    def _end_game(self, message):
        self.game_over = True
        self.status_var.set(message)
        self.draw_board()

    def _on_diff_change(self, selection):
        name_to_level = {"Easy": 1, "Medium": 2, "Hard": 3, "Expert": 4}
        self.level = name_to_level[selection]
        # apply immediately; restart so the new level takes effect cleanly
        self.restart()

    # ── restart ───────────────────────────────────────────────────────────────
    def restart(self):
        board[:] = 0            # reset the shared numpy board in-place
        self.game_over   = False
        self.ai_thinking = False
        self.hover_col   = None
        self.status_var.set(f"Your turn  ·  AI: {self._diff_names[self.level]}")
        self.draw_board()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    root.withdraw()                 # hide main window while picking difficulty
    level = pick_difficulty(root)
    root.deiconify()

    Connect4GUI(root, level)
    root.mainloop()


if __name__ == "__main__":
    main()
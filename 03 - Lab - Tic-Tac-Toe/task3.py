from random import randrange

class TicTacToe:
    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.winner = None
        self.move = None
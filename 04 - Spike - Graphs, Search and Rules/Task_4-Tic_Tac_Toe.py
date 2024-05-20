from random import randrange
import random
import math
import time
from random import shuffle

class TicTacToe(object):


    def __init__(self):
        self.board = [[' ']*3 for _ in range(3)]
        self.players = {'x': 'AI 1', 'o': 'AI 2'}
        self.winner = None
        self.current_player = 'x'
        self.col = self.row = 0
        self.render_board()
        print("Welcome to Tic Tac Toe game")
        self.score = None
        self.scores = {
            'x': 1,
            'o': -1,
            'tie': 0
        }


    HR = '-' * 40

        

    def check_winner(self):
        board = self.board
        # Check rows
        for row in board:
            if row[0] == row[1] == row[2] and row[0] != ' ':
                return row[0]

        # Check columns
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] and board[0][col] != ' ':
                return board[0][col]

        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] and board[0][0] != ' ':
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] and board[0][2] != ' ':
            return board[0][2]

        # Check for a tie (draw)
        if all(cell != " " for row in board for cell in row):
            return "tie"

        return None
#----------------------------------------------------------------------------------------------------------
    def get_possible_move(self, board):
        possible_moves = []
        for row in range(3):
             for col in range(3):
                 if (board[row][col] == ' '):
                     possible_moves.append((row, col))
        return possible_moves

    # Get Total Random Moves----------------------------------------------------------------------------------
    def get_total_random_moves(self):
        board = self.board
        current_player = self.current_player
        possible_moves = self.get_possible_move(board)
        shuffle(possible_moves) #make the move become totally random

        return possible_moves[0]

    #Get random move with minimax (efficiency) -------------------------------------------------------------------
    def get_efficient_move(self):
        board = self.board
        current_player = self.current_player
        possible_moves = self.get_possible_move(board)
        best_score = -math.inf
        best_move = (None, None)

        for move in possible_moves:
            # simulate the move
            board[move[0]][move[1]] = current_player
            score = self.minimax(board, 0, False)
            # undo the move
            board[move[0]][move[1]] = " "

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    #Minimax function
    def minimax(self, board, depth, is_maximize):
        result = self.check_winner()
        if result == self.current_player:
            return 1
        elif result is not None:
            return -1
        elif result == "tie":
            return 0

        if is_maximize:
            best_score = -math.inf
            for move in self.get_possible_move(board):
                board[move[0]][move[1]] = self.current_player
                score = self.minimax(board, depth + 1, False)
                board[move[0]][move[1]] = ' '
                best_score = max(best_score, score)
            return best_score

        else:
            best_score = math.inf
            for move in self.get_possible_move(board):
                board[move[0]][move[1]] = 'x' if self.current_player == 'o' else 'o'
                score = self.minimax(board, depth + 1, True)
                board[move[0]][move[1]] = ' '
                best_score = max(best_score, score)
                return best_score

        return best_score

    # Get improved random move ------------------------------------------------------------------------------------------------
    def get_effective_moves(self):
        board = self.board
        current_player = self.current_player
        possible_moves = self.get_possible_move(board)
        win_moves = []
        block_moves = []
        for move in possible_moves:
            #simulate the move
            board[move[0]][move[1]] = current_player
            if self.check_winner() == self.current_player:
                win_moves.append(move)
            board[move[0]][move[1]] = ' '

            #simulate opponent's move
            opponent_player = 'x' if current_player == 'o' else 'o'
            board[move[0]][move[1]] = opponent_player
            if self.check_winner() == opponent_player:
                block_moves.append(move)
            board[move[0]][move[1]] = ' '

        if win_moves:
            return random.choice(win_moves)
        elif block_moves:
            return random.choice(block_moves)
        else:
            return random.choice(possible_moves)

    def process_input(self):
        if self.current_player == 'x':
            self.row, self.col = self.get_effective_moves()
        else:
            self.row, self.col = self.get_total_random_moves()

    def update(self):
        self.board[self.row][self.col] = self.current_player
        self.winner = self.check_winner()
        self.current_player = 'o' if self.current_player == 'x' else 'x'

    def render_board(self):
        '''Display the current game board to screen.'''
        board = self.board
        print('    %s | %s | %s' % (board[0][0], board[0][1], board[0][2]))
        print('   -----------')
        print('    %s | %s | %s' % (board[1][0], board[1][1], board[1][2]))
        print('   -----------')
        print('    %s | %s | %s' % (board[2][0], board[2][1], board[2][2]))

        # pretty print the current player name
        if self.winner is None:
            print('The current player is: %s' % self.players[self.current_player])

    def show_gameresult(self):
        '''Show the game result winner/tie details'''
        print(self.HR)
        if self.winner == 'tie':
            print('TIE!')
        else:
            print('%s is the WINNER!!!' % self.players[self.winner])
        print(self.HR)
        print('Game over. Goodbye')
            


if __name__ == '__main__':
    # create instance (~ "new") object of type TicTacToe class
    game = TicTacToe()

    # Standard game loop structure
    while game.winner is None:
        time.sleep(1)
        game.process_input()
        game.update()
        game.render_board()

    # Some pretty messages for the result
    game.show_gameresult()
        
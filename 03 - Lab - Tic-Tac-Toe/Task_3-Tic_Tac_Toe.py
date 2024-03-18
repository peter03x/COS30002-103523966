from random import randrange
import time

class TicTacToe(object):


    def __init__(self):
        self.board = [[' ']*3 for _ in range(3)]
        self.players = {'x': 'Super AI 2', 'o': 'Super AI 1' }
        self.winner = None
        self.current_player = 'x'
        self.col = self.row = 0
        self.render_board()
        print("Welcome to Tic Tac Toe game")


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
    
    def get_secondAi_move(self):
        for self.row in range(3):
            for self.col in range(3):
                if (self.board[self.row][self.col] == ' '):
                    return self.row, self.col
                
    def get_ai_move(self):
            self.row = randrange(3)
            self.col = randrange(3)

            if (self.board[self.row][self.col] != ' '):
                self.row = randrange(3)
                self.col = randrange(3)
            return self.row, self.col

    def process_input(self):
        if self.current_player == 'x':
            self.move = self.get_secondAi_move()
        else:
            self.move = self.get_ai_move()
    
    def update(self):
            self.board[self.row][self.col] = self.current_player
            self.winner = self.check_winner()
            if self.current_player == 'x':
                self.current_player = 'o'
            else:
                self.current_player = 'x'
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
        
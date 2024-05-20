import math

from random import randrange
from random import shuffle

class TicTacToe():
    def __init__(self, firstPlayer, secondPlayer):

        # Initialize the board game - 2D array of 3x3
        self.board = [
            [" ", " ", " "],
            [" ", " ", " "],
            [" ", " ", " "]
        ]

        self.move = None

        # Initialize the players' symbols
        self.players = {
            "X": firstPlayer,
            "O": secondPlayer
        }

        self.turnIndex = 0

        self.winner = None  

        self.currentPlayerSymbol = "X"

        self.boardsHistory = []

        print("TURN: 0. The current player is: {}".format(self.players[self.currentPlayerSymbol]))

    def checkWinner(self, board):
        # Check rows
        for row in board:
            if row[0] == row[1] == row[2] and row[0] != " ":
                return row[0]

        # Check cols
        for col in range(len(board[0])):
            if board[0][col] == board[1][col] == board[2][col] and board[0][col] != " ":
                return board[0][col]

        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] and board[0][0] != " ":
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] and board[0][2] != " ":
            return board[0][2]

        # Check if no one win
        if all(all(cell != " " for cell in row) for row in board):
            return "Tie"

        # The game is not over
        return None

    # Human: Enter manually
    def getHumanMove(self):
        print("Please enter your preferred position: \n")
        rowIndex = input("Row: ")
        colIndex = input("Col: ")

        while self.board[rowIndex][colIndex] != " ":
            print("The position is not valid, please re-enter your preferred position: \n")
            rowIndex = input("Row: ")
            colIndex = input("Col: ")

        return (int(rowIndex), int(colIndex))

    # ==================================================================================================================================================
    # First AI bot: Random totally
    def getFirstBotMove(self):
        rowIndex = randrange(3)
        colIndex = randrange(3)

        while self.board[rowIndex][colIndex] != " ":
            rowIndex = randrange(3)
            colIndex = randrange(3)

        return (rowIndex, colIndex)

    # ==================================================================================================================================================
    # Second AI bot: Make a move in the priority order: Top-to-bottom, Left-to-right
    def getSecondBotMove(self):
        for rowIndex in range(3):
            for colIndex in range(3):
                if self.board[rowIndex][colIndex] == " ":
                    return (rowIndex, colIndex)

    def getPossibleMoves(self, board):
        possibleMoves = []
        for rowIndex in range(3):
            for colIndex in range(3):
                if (board[rowIndex][colIndex] == " "):
                    possibleMoves.append((rowIndex, colIndex))
        
        return possibleMoves

    # ==================================================================================================================================================
    # Third AI bot: Make a move in the graph that has been randomly searched (Aiming to find the max value - Thirdbot's victory only)
    def getThirdBotMove(self):
        temporaryBoard = [row[:] for row in self.board]

        possibleMoves = self.getPossibleMoves(temporaryBoard)
        shuffle(possibleMoves)

        bestEvaluation = -math.inf
        bestMoveRowIndex = None
        bestMoveColIndex = None     

        for (moveRowIndex, moveColIndex) in possibleMoves:
            # Create a copy of the board in the initial state
            initialBoard = [row[:] for row in temporaryBoard]

            # Simulate a move of the ThirdBot
            temporaryBoard[moveRowIndex][moveColIndex] = self.currentPlayerSymbol

            opponentSymbol = "X" if self.currentPlayerSymbol == "O" else "O" 

            # Given that opponent will attempt a random move
            if self.checkWinner(temporaryBoard) is None:
                opponentRowIndex = randrange(3)
                opponentColIndex = randrange(3)

                while temporaryBoard[opponentRowIndex][opponentColIndex] != " ":
                    opponentRowIndex = randrange(3)
                    opponentColIndex = randrange(3)        

            evaluation = self.randomlySearch(temporaryBoard, self.currentPlayerSymbol)  

            if evaluation > bestEvaluation:
                bestEvaluation = evaluation

                bestMoveRowIndex = moveRowIndex
                bestMoveColIndex = moveColIndex          

            # Recover the board's state
            temporaryBoard = [row[:] for row in initialBoard]

        return (bestMoveRowIndex, bestMoveColIndex)

        raise ValueError("Can't find the best move for the Third AI Bot.")

    def randomlySearch(self, board, playerSymbol):
        if self.checkWinner(board) == playerSymbol:
            return 1
        elif self.checkWinner(board) == "Tie":
            return 0
        elif self.checkWinner(board) != None:
            return -1

        possibleMoves = self.getPossibleMoves(board)
        shuffle(possibleMoves)

        maxEvaluation = -math.inf

        # Simulate Thirdbot moves
        for (moveRowIndex, moveColIndex) in possibleMoves:
            # Create a copy of the board in the initial state
            initialBoard = [row[:] for row in board]

            # Simulate a move
            board[moveRowIndex][moveColIndex] = playerSymbol

            opponentSymbol = "X" if playerSymbol == "O" else "O"

            # Given that opponent will attempt a random move
            if self.checkWinner(board) is None:
                opponentRowIndex = randrange(3)
                opponentColIndex = randrange(3)

                while board[opponentRowIndex][opponentColIndex] != " ":
                    opponentRowIndex = randrange(3)
                    opponentColIndex = randrange(3)

            evaluation = self.randomlySearch(board, playerSymbol)

            # Recover the board's state
            board = [row[:] for row in initialBoard]

            maxEvaluation = max(maxEvaluation, evaluation)

        return maxEvaluation

    # ==================================================================================================================================================
    # Fourth AI Bot: Efficient search, improving ThirdBot by assuming that opponent would apply the same technique to find the min value (Opponent's victoria)
    # This is simple form of minimax (without Alpha-beta prunning)
    def getFourthBotMove(self):
        temporaryBoard = [row[:] for row in self.board]

        possibleMoves = self.getPossibleMoves(temporaryBoard)
        shuffle(possibleMoves)

        # TO BE DELETED
        # print("===================================================================")
        # print("===================================================================")
        # print("=====================FOURTH AI BOT SEARCHING=======================")

        bestEvaluation = -math.inf
        bestMoveRowIndex = None
        bestMoveColIndex = None

        for (moveRowIndex, moveColIndex) in possibleMoves:
            # Create a copy of the board in the initial state
            initialBoard = [row[:] for row in temporaryBoard]

            # Simulate a move of the FourthBot
            temporaryBoard[moveRowIndex][moveColIndex] = self.currentPlayerSymbol

            # TO BE DELETED
            # print("\n    TURN {}---------------------------------------".format(self.turnIndex))
            # print("    " + str(-1) + "-depth simulating turn: FourthBot!")
            # for rowIndex in range(3):
            #     print('        %s | %s | %s' % tuple(temporaryBoard[rowIndex][:3]))
            #     if rowIndex < 2:
            #         print('       -----------')                

            nextPlayerSymbol = "X" if self.currentPlayerSymbol == "O" else "O"

            evaluation = self.efficientSearch(temporaryBoard, 0, self.currentPlayerSymbol, nextPlayerSymbol)

            if evaluation > bestEvaluation:
                bestEvaluation = evaluation

                bestMoveRowIndex = moveRowIndex
                bestMoveColIndex = moveColIndex
        
            # Recover the board's state
            temporaryBoard = [row[:] for row in initialBoard]

            # TO BE DELETED
            # print("===================================================================")
            # print("===================================================================")

        return (bestMoveRowIndex, bestMoveColIndex)

        raise ValueError("Can't find the best move for the Fourth AI Bot.")

    def efficientSearch(self, board, depth, initialPlayerSymbol, currentPlayerSymbol):
        if self.checkWinner(board) == initialPlayerSymbol:
            return 1
        elif self.checkWinner(board) == "Tie":
            return 0
        elif self.checkWinner(board) != None:
            return -1

        possibleMoves = self.getPossibleMoves(board)
        shuffle(possibleMoves)

        # Simulate opponent move
        if currentPlayerSymbol != initialPlayerSymbol:
            minEvaluation = math.inf
            for (moveRowIndex, moveColIndex) in possibleMoves:
                # Create a copy of the board in the initial state
                initialBoard = [row[:] for row in board]

                # Simulate a random move
                board[moveRowIndex][moveColIndex] = currentPlayerSymbol

                # TO BE DELETED
                # print("\n    TURN {}---------------------------------------".format(self.turnIndex))
                # print("    " + str(depth) + "-depth simulating turn: " + self.players[currentPlayerSymbol])
                # for rowIndex in range(3):
                #     print('        %s | %s | %s' % tuple(board[rowIndex][:3]))
                #     if rowIndex < 2:
                #         print('       -----------')

                nextPlayerSymbol = "X" if currentPlayerSymbol == "O" else "O"

                evaluation = self.efficientSearch(board, depth + 1, initialPlayerSymbol, nextPlayerSymbol)
                
                # Recover the board's state
                board = [row[:] for row in initialBoard]

                minEvaluation = min(minEvaluation, evaluation)

            # TO BE DELETED
            # print("\n    -> Best value for " + self.players[currentPlayerSymbol] + " in the " + str(depth) + "-depth: " + str(minEvaluation))

            return minEvaluation

        # Simulate Fifthbot moves
        elif currentPlayerSymbol == initialPlayerSymbol:
            maxEvaluation = -math.inf
            for (moveRowIndex, moveColIndex) in possibleMoves:
                # Create a copy of the board in the initial state
                initialBoard = [row[:] for row in board]

                # Simulate a random move
                board[moveRowIndex][moveColIndex] = currentPlayerSymbol
                
                # TO BE DELETED
                # print("\n    TURN {}---------------------------------------".format(self.turnIndex))
                # print("    " + str(depth) + "-depth simulating turn: " + self.players[currentPlayerSymbol])
                # for rowIndex in range(3):
                #     print('        %s | %s | %s' % tuple(board[rowIndex][:3]))
                #     if rowIndex < 2:
                #         print('       -----------')

                nextPlayerSymbol = "X" if currentPlayerSymbol == "O" else "O"

                evaluation = self.efficientSearch(board, depth + 1, initialPlayerSymbol, nextPlayerSymbol)
                
                # Recover the board's state
                board = [row[:] for row in initialBoard]

                maxEvaluation = max(maxEvaluation, evaluation)

            # TO BE DELETED
            # print("\n    -> Best value for " + self.players[currentPlayerSymbol] + " in the " + str(depth) + "-depth: " + str(maxEvaluation))

            return maxEvaluation

    # ==================================================================================================================================================
    # Fifth AI Bot: Effective search with Minimax algorithm (with Alpha-beta prunning)
    def getFifthBotMove(self):
        temporaryBoard = [row[:] for row in self.board]

        possibleMoves = self.getPossibleMoves(temporaryBoard)
        shuffle(possibleMoves)

        # TO BE DELETED
        # print("===================================================================")
        # print("===================================================================")
        # print("=====================FIFTH AI BOT SEARCHING========================")

        bestEvaluation = -math.inf
        bestMoveRowIndex = None
        bestMoveColIndex = None

        for (moveRowIndex, moveColIndex) in possibleMoves:
            # Create a copy of the board in the initial state
            initialBoard = [row[:] for row in temporaryBoard]

            # Simulate a move of the FifthBot
            temporaryBoard[moveRowIndex][moveColIndex] = self.currentPlayerSymbol

            # TO BE DELETED
            # print("\n    TURN {}---------------------------------------".format(self.turnIndex))
            # print("    " + str(-1) + "-depth simulating turn: FifthBot!")
            # for rowIndex in range(3):
            #     print('        %s | %s | %s' % tuple(temporaryBoard[rowIndex][:3]))
            #     if rowIndex < 2:
            #         print('       -----------')                

            nextPlayerSymbol = "X" if self.currentPlayerSymbol == "O" else "O"

            evaluation = self.effectiveSearch(temporaryBoard, 0, self.currentPlayerSymbol, nextPlayerSymbol, -math.inf, math.inf)

            if evaluation > bestEvaluation:
                bestEvaluation = evaluation

                bestMoveRowIndex = moveRowIndex
                bestMoveColIndex = moveColIndex
        
            # Recover the board's state
            temporaryBoard = [row[:] for row in initialBoard]

            # TO BE DELETED
            # print("===================================================================")
            # print("===================================================================")

        return (bestMoveRowIndex, bestMoveColIndex)

        raise ValueError("Can't find the best move for the Fifth AI Bot.")

    # Minimax algorithm with Alpha-beta prunning
    def effectiveSearch(self, board, depth, initialPlayerSymbol, currentPlayerSymbol, alpha, beta):
        if self.checkWinner(board) == initialPlayerSymbol:
            return 1
        elif self.checkWinner(board) == "Tie":
            return 0
        elif self.checkWinner(board) != None:
            return -1

        possibleMoves = self.getPossibleMoves(board)
        shuffle(possibleMoves)

        # Simulate opponent move
        if currentPlayerSymbol != initialPlayerSymbol:
            minEvaluation = math.inf
            for (moveRowIndex, moveColIndex) in possibleMoves:
                # Create a copy of the board in the initial state
                initialBoard = [row[:] for row in board]

                # Simulate a random move
                board[moveRowIndex][moveColIndex] = currentPlayerSymbol

                # TO BE DELETED
                # print("\n    TURN {}---------------------------------------".format(self.turnIndex))
                # print("    " + str(depth) + "-depth simulating turn: " + self.players[currentPlayerSymbol])
                # for rowIndex in range(3):
                #     print('        %s | %s | %s' % tuple(board[rowIndex][:3]))
                #     if rowIndex < 2:
                #         print('       -----------')

                nextPlayerSymbol = "X" if currentPlayerSymbol == "O" else "O"

                evaluation = self.effectiveSearch(board, depth + 1, initialPlayerSymbol, nextPlayerSymbol, alpha, beta)
                
                # Recover the board's state
                board = [row[:] for row in initialBoard]

                minEvaluation = min(minEvaluation, evaluation)

                beta = min(beta, evaluation)
                if beta <= alpha:
                    break

            # TO BE DELETED
            # print("\n    -> Best value for " + self.players[currentPlayerSymbol] + " in the " + str(depth) + "-depth: " + str(minEvaluation))

            return minEvaluation

        # Simulate Fifthbot moves
        elif currentPlayerSymbol == initialPlayerSymbol:
            maxEvaluation = -math.inf
            for (moveRowIndex, moveColIndex) in possibleMoves:
                # Create a copy of the board in the initial state
                initialBoard = [row[:] for row in board]

                # Simulate a random move
                board[moveRowIndex][moveColIndex] = currentPlayerSymbol
                
                # TO BE DELETED
                # print("\n    TURN {}---------------------------------------".format(self.turnIndex))
                # print("    " + str(depth) + "-depth simulating turn: " + self.players[currentPlayerSymbol])
                # for rowIndex in range(3):
                #     print('        %s | %s | %s' % tuple(board[rowIndex][:3]))
                #     if rowIndex < 2:
                #         print('       -----------')
9
                nextPlayerSymbol = "X" if currentPlayerSymbol == "O" else "O"

                evaluation = self.effectiveSearch(board, depth + 1, initialPlayerSymbol, nextPlayerSymbol, alpha, beta)
                
                # Recover the board's state
                board = [row[:] for row in initialBoard]

                maxEvaluation = max(maxEvaluation, evaluation)

                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break

            # TO BE DELETED
            # print("\n    -> Best value for " + self.players[currentPlayerSymbol] + " in the " + str(depth) + "-depth: " + str(maxEvaluation))

            return maxEvaluation
            
    def getMove(self, currentPlayerName):
        switch = {
            "Human": self.getHumanMove,
            "FirstBot": self.getFirstBotMove,
            "SecondBot": self.getSecondBotMove,
            "ThirdBot": self.getThirdBotMove,
            "FourthBot": self.getFourthBotMove,
            "FifthBot": self.getFifthBotMove
        }

        return switch.get(currentPlayerName, self.getHumanMove)()

    def processInput(self):
        self.move = self.getMove(self.players[self.currentPlayerSymbol])
    
    def update(self):
        (moveRowIndex, moveColIndex) = self.move
        self.board[moveRowIndex][moveColIndex] = self.currentPlayerSymbol

        self.winner = self.checkWinner(self.board)

        self.currentPlayerSymbol = "O" if self.currentPlayerSymbol == "X" else "X"

        self.turnIndex += 1

    def render(self):
        self.displayBoard()
        
        print("=====================")
        if self.winner is None:
            print("TURN: {}. The current player is: {}".format(self.turnIndex, self.players[self.currentPlayerSymbol]))

    def displayBoard(self):
        for rowIndex in range(3):
            print('    %s | %s | %s' % tuple(self.board[rowIndex][:3]))
            if rowIndex < 2:
                print('   -----------')

    def displayResult(self):
        print("=====================")
        print("===== GAME OVER =====")
        if self.winner == 'Tie':
            print('TIE!')
        else:
            print('%s is the WINNER!!!' % self.players[self.winner])

game = TicTacToe("ThirdBot", "FifthBot")

# Standard game loop structure
while game.winner is None:
    game.processInput()
    game.update()
# responsible for sharing all the info about the current state of the game

# also responsible for determining the valid moves at the current state
# also keep a move log

class GameState():
    def __init__(self):
        # board is an 8*8 2D list
        # each element has 2 characters in its name
        # first character - color of the piece
        # second character - name of the piece
        # "--" - empty space on the board
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False  # no valid moves and the king is in check
        self.staleMate = False  # no valid moves and the king is not in check

    # takes a move as a parameter and executes it
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # to append it into the move log
        self.whiteToMove = not self.whiteToMove  # swap players
        # update the king's location if it moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

    # undo the last move
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # update the king's location
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

    def getValidMoves(self):
        # keeping in mind the valid moves with respect to the king (in case of check)
        moves = self.getAllPossibleMoves()
        for i in range(len(moves) - 1, -1, -1):
            # make all the moves
            self.makeMove(moves[i])
            # to get all opponent moves after each move made
            # check if the king is under attack
            # we need to swap turns again before calling check again
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
                # if the king is under attack, we need to remove the move from the valid moves list
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if len(moves) == 0:  # either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        return moves

    def inCheck(self):
        # determine if the current player in under check
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        # determine if the current square r, c is under attack
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # the square is under attack
                return True
        return False  # getting out of the for loop means - square is not under attack

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of columns in a given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    # get all the pawn moves for the pawn located at r, c and add them to moves (which is a list)
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # if it is white's turn to move
            if self.board[r - 1][c] == '--':  # if the square in front of the current pawn is empty
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == '--':
                    # if the square two squares ahead of the current pawn is empty
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # capture piece to the left
                if self.board[r - 1][c - 1][0] == 'b':  # black piece to be captured
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c + 1 <= 7:  # capture piece to the right
                if self.board[r - 1][c + 1][0] == 'b':  # black piece to be captured
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))

        if not self.whiteToMove:  # if it is black's turn to move
            if self.board[r + 1][c] == '--':  # if the square in front of the current pawn is empty
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][
                    c] == '--':  # if the square two squares ahead of the current pawn is empty
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # capture piece to the left
                if self.board[r + 1][c - 1][0] == 'w':  # white piece to be captured
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7:  # capture piece to the right
                if self.board[r + 1][c + 1][0] == 'w':  # white piece to be captured
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

    # get all the rook moves for the pawn located at r, c and add them to moves (which is a list)
    def getRookMoves(self, r, c, moves):
        directions = ((1, 0), (-1, 0), (0, -1), (0, 1))  # four diagonal directions
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # to make sure that the end column and the end row lie
                    # within board limits
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':  # end piece is an empty space
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:  # comes here when the piece is not on the board
                    break

    def getKnightMoves(self, r, c, moves):
        directions = ((2, -1), (2, 1), (-2, -1), (-2, 1), (1, 2), (-1, 2), (1, -2), (-1, -2))
        allyColor = 'w' if self.whiteToMove else 'b'
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # anything other than an ally piece - empty or enemy
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = ((1, 1), (1, -1), (-1, -1), (-1, 1))  # four diagonal directions
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # to make sure that the end column and the end row lie
                    # within board limits
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':  # end piece is an empty space
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:  # comes here when the piece is not on the board
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (1, 1), (1, -1), (-1, -1), (-1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        # print(self.moveID)

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    #
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

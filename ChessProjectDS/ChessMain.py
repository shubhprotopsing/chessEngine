from Chess import ChessEngine, ChessAI
import pygame
import math
pygame.init()
pygame.display.set_caption('Our own Chess Engine!')

HEIGHT = WIDTH = 672
DIMENSION = 8  # dimensions of a chess board are 8*8
SQ_SIZE = HEIGHT//DIMENSION
# print(SQ_SIZE)
MAX_FPS = 15  # will be used for animations later on
IMAGES = {}

# This is a global dictionary of images. It will be called exactly once in the main
def loadImages():
    pieces = ["wR", "wN", "wB", "wQ", "wK", "wp", "bR", "bN", "bB", "bQ", "bK", "bp"]
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load("Chess\images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        # according to this statement, images["wp"] = pygame.image.load(images/wp.png)

# Main function is the main driver of our program: it handles user input and updates the graphics
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    screenVar = True
    screen.fill(pygame.Color("white"))

    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when move is made
    animate = False  # flag variable for when animation should act
    loadImages()
    running = True
    sqSelected = ()  # to keep track of the last click of the user (tuple)
    playerClicks = []  # list of up to two elements to keep track of click history of the user (list of up to 2 tuples)
    gameOver = False  # game is over only in case of checkmate and stalemate
    playerOne = True  # playerOne refers to white, true when person is playing, false for AI
    playerTwo = False  # playerTwo refers to black, true when person is playing, false for AI

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in pygame.event.get():
            # quitting the game
            if e.type == pygame.QUIT:
                running = False
            # mouse actions
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = pygame.mouse.get_pos()  # returns a tuple for the x, y coordinates
                    col = (location[0] // SQ_SIZE)
                    row = (location[1] // SQ_SIZE)
                    if sqSelected == (row, col):  # meaning that the same square has been selected twice
                        sqSelected = ()  # unselecting it
                        playerClicks = []  # restarting the series
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # appending both the clicks

                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        if move in validMoves:
                            gs.makeMove(move)
                            moveMade = True
                            animate = True
                            sqSelected = ()  # to reset user clicks
                            playerClicks = []
                        else:
                            playerClicks = [sqSelected]
            # key handlers
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_z:
                    gs.undoMove()  # undo when z is pressed
                    moveMade = True
                    animate = False
                if e.key == pygame.K_r:  # restart the game when r is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        # AI move finder
        if not gameOver and not humanTurn:
            AIMove = ChessAI.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = ChessAI.findRandomMoves(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
                pygame.mixer.music.load("Chess\Sounds\ChessMoveSound.mp3")
                pygame.mixer.music.set_volume(0.7)
                pygame.mixer.music.play()
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate!")
            else:
                drawText(screen, "White wins by checkmate!")

        elif gs.staleMate:
            gameOver = True
            drawText(screen, "Stalemate!")

        clock.tick(MAX_FPS)
        pygame.display.flip()

# Highlighting squares
def hightlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # to make sure that sqSelected is a movable piece
            # highlight selected square
            s = pygame.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(150)
            s.fill(pygame.Color("dark green"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            # highlight valid moves from that square
            s1 = pygame.Surface((SQ_SIZE, SQ_SIZE))
            s1.set_alpha(50)
            s1.fill(pygame.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s1, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawGameState(screen, gs, validMoves, sqSelected):
    "'Responsible for all the graphics of the game'"
    drawBoard(screen)  # To draw squares on the board
    hightlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # To draw pieces on those squares

def drawBoard(screen):
    "'Drawing the squares on the board'"
    global colors
    colors = [pygame.Color(241, 240, 218), pygame.Color(130, 159, 98)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            smallSquare = pygame.Rect(SQ_SIZE * c, SQ_SIZE * r, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(screen, color, smallSquare)

def drawPieces(screen, board):
    "'Drawing the pieces on the board using gs.board'"
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], pygame.Rect(SQ_SIZE * c, SQ_SIZE * r, SQ_SIZE, SQ_SIZE))

# Animating the moves
def animateMove(move, screen, board, clock):
    global colors
    # define number of rows and columns to be traversed
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10  # frames to move in one square
    totalFrameCount = (abs(dR) + abs(dC)) * framesPerSquare  # total number of frames to move
    for frame in range(totalFrameCount + 1):
        r, c = (move.startRow + dR * frame/totalFrameCount, move.startCol + dC * frame/totalFrameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = pygame.Rect(SQ_SIZE * move.endCol, SQ_SIZE * move.endRow, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(screen, color, endSquare)

        # draw captured piece so it doesnt look disappeared while animation is going on
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        # draw the moving piece
        screen.blit(IMAGES[move.pieceMoved], pygame.Rect(SQ_SIZE * c, SQ_SIZE * r, SQ_SIZE, SQ_SIZE))
        pygame.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = pygame.font.SysFont("Helvetica", 45, True, False)
    textObject = font.render(text, 0, pygame.Color("darkgreen"), pygame.Color(241, 240, 218))
    textLocation = pygame.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)

main()
import pygame
import chess

SQUARE_SIZE = 75

def load_piece_img(path):
    return pygame.transform.scale(pygame.image.load(path), (SQUARE_SIZE, SQUARE_SIZE))


BLACK_PIECES_IMG = {
    chess.PAWN: load_piece_img('images/black-pawn.png'),
    chess.KNIGHT: load_piece_img('images/black-knight.png'),
    chess.BISHOP: load_piece_img('images/black-bishop.png'),
    chess.ROOK: load_piece_img('images/black-rook.png'),
    chess.QUEEN: load_piece_img('images/black-queen.png'),
    chess.KING: load_piece_img('images/black-king.png'),
}

WHITE_PIECES_IMG = {
    chess.PAWN: load_piece_img('images/white-pawn.png'),
    chess.KNIGHT: load_piece_img('images/white-knight.png'),
    chess.BISHOP: load_piece_img('images/white-bishop.png'),
    chess.ROOK: load_piece_img('images/white-rook.png'),
    chess.QUEEN: load_piece_img('images/white-queen.png'),
    chess.KING: load_piece_img('images/white-king.png'),
}

class Draw:
    def __init__(self, screen: pygame.display, board: chess.Board):
        self.screen = screen
        self.board = board
        self.square_selected = None

    def select_square(self):
        pos = pygame.mouse.get_pos()
        file = pos[0] // SQUARE_SIZE
        rank = pos[1] // SQUARE_SIZE
        square = chess.square(file, rank)
        self.square_selected = square

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.draw_board()

    def draw_board(self):
        for square in chess.SQUARES:
            file = chess.square_file(square)
            rank = chess.square_rank(square)
            square_color = self.get_square_color(square)
            square_rect = (file * SQUARE_SIZE, rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(self.screen, square_color, square_rect)

            piece_type = self.board.piece_type_at(square)
            if self.board.color_at(square) == chess.WHITE:
                self.screen.blit(WHITE_PIECES_IMG[piece_type], square_rect)
            elif self.board.color_at(square) == chess.BLACK:
                self.screen.blit(BLACK_PIECES_IMG[piece_type], square_rect)

    def get_square_color(self, square: chess.Square):
        if square == self.square_selected:
            return 130, 151, 105
        elif (chess.square_file(square) + chess.square_rank(square)) % 2 == 0:
            return 240, 217, 181
        else:
            return 181, 136, 99
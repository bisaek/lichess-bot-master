import pygame
import chess
from multiprocessing import Process, Queue
from bot.searcher import Searcher
from bot.transposition_table import TranspositionTable
from engine import get_bot_searcher_after_search

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


def get_bot_move(board, transposition_table, return_queue: Queue):
    transposition_table.board = board
    searcher = Searcher(board, transposition_table, 5)
    return_queue.put(searcher.start_search())


class BoardUI:
    def __init__(self, screen: pygame.display, color_viewer: chess.Color):
        self.searcher_queue = None
        self.bot_move_process = None
        self.screen = screen
        self.board = chess.Board()
        self.square_selected = None
        self.legal_moves_squares = []
        self.color_viewer = color_viewer
        self.transposition_table = TranspositionTable()
        self.players = {
            chess.WHITE: "player",
            chess.BLACK: "player",
        }
        self.bot_searching = False

    def mouse_button_down(self):
        pos = pygame.mouse.get_pos()
        file = pos[0] // SQUARE_SIZE
        rank = pos[1] // SQUARE_SIZE
        square = chess.square(file, rank) if self.color_viewer == chess.BLACK else chess.square(7 - file, 7 - rank)

        if self.board.piece_at(square) is not None and self.board.piece_at(square).color == self.board.turn:
            self.square_selected = square
            self.legal_moves_squares = []
            for move in list(self.board.legal_moves):
                if move.from_square == square:
                    self.legal_moves_squares.append(move.to_square)
        elif self.players[self.board.turn] == "player" and square in self.legal_moves_squares:
            self.make_move(chess.Move(self.square_selected, square))

    def make_move(self, move):
        self.board.push(move)
        self.legal_moves_squares = []
        self.square_selected = None

    def bot_move(self):
        if not self.bot_searching:
            self.bot_searching = True
            print("gegsdsdsssssssssssf")
            self.searcher_queue = Queue()
            self.bot_move_process = Process(target=get_bot_searcher_after_search, args=(self.board, self.transposition_table, self.searcher_queue))
            self.bot_move_process.start()
        if not self.bot_move_process.is_alive():
            print("gegesdf")
            searcher = self.searcher_queue.get()
            print(searcher)
            self.make_move(searcher)
            self.bot_searching = False

    def is_bots_turn(self):
        return "bot" == self.players[self.board.turn]

    def draw_board(self):
        for square in chess.SQUARES:
            file = chess.square_file(square)
            rank = chess.square_rank(square)
            square_color = self.get_square_color(square)

            square_rect = (file * SQUARE_SIZE, rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            if self.color_viewer == chess.WHITE:
                square_rect = ((7 - file) * SQUARE_SIZE, (7 - rank) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(self.screen, square_color, square_rect)

            piece_type = self.board.piece_type_at(square)
            if self.board.color_at(square) == chess.WHITE:
                self.screen.blit(WHITE_PIECES_IMG[piece_type], square_rect)
            elif self.board.color_at(square) == chess.BLACK:
                self.screen.blit(BLACK_PIECES_IMG[piece_type], square_rect)

    def get_square_color(self, square: chess.Square):
        if square == self.square_selected:
            return 130, 151, 105
        elif square in self.legal_moves_squares:
            return 235, 64, 52
        elif (chess.square_file(square) + chess.square_rank(square)) % 2 == 0:
            return 240, 217, 181
        else:
            return 181, 136, 99

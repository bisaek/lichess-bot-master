import chess

from bot.searcher import Searcher
from bot.transposition_table import TranspositionTable


class Bot:
    def __init__(self):
        self.transposition_table = TranspositionTable()

    def best_move(self, board: chess.Board):
        self.transposition_table.board = board
        searcher = Searcher(board, self.transposition_table, 0.2)
        return searcher.start_search()

import chess

from bot2.searcher import Searcher
from bot2.transposition_table import TranspositionTable


class Bot:
    def __init__(self):
        pass
        #self.transposition_table = TranspositionTable()

    def best_move(self, board: chess.Board):
        #self.transposition_table.board = board
        searcher = Searcher(board, 0.2)
        return searcher.start_search()

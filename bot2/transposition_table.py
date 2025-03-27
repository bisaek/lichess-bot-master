from dataclasses import dataclass
import chess
import chess.polyglot

EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2

class TranspositionTable:
    def __init__(self, board: chess.Board = None):
        self.board = board
        self.count = 1000000
        self.entries = [Transposition()] * self.count

    def store_evaluation(self, depth, evaluation, move: chess.Move, flag: EXACT | LOWERBOUND | UPPERBOUND):
        self.entries[self.get_index()] = Transposition(chess.polyglot.zobrist_hash(self.board), evaluation, move, depth, flag)

    def get_evaluation(self, depth, alpha, beta):
        entry = self.entries[self.get_index()]

        if entry.key == chess.polyglot.zobrist_hash(self.board) and entry.depth >= depth:
            if entry.flag == EXACT:
                return entry.value
            elif entry.flag == LOWERBOUND:
                alpha = max(alpha, entry.value)
            elif entry.flag == UPPERBOUND:
                beta = min(beta, entry.value)

            if alpha >= beta:
                return entry.value, alpha, beta
        return None, alpha, beta

    def get_move(self):
        return self.entries[self.get_index()].move

    def get_index(self):
        return chess.polyglot.zobrist_hash(self.board) % self.count


@dataclass
class Transposition:
    key: int = None
    value: int = None
    move: chess.Move = None
    depth: int = None
    flag: EXACT | LOWERBOUND | UPPERBOUND = None

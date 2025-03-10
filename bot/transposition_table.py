from dataclasses import dataclass
import chess
import chess.polyglot

class TranspositionTable:
    def __init__(self, board: chess.Board):
        self.board = board
        self.count = 1000000
        self.entries = [Transposition()] * self.count

    def store_evaluation(self, depth, evaluation, move: chess.Move):
        self.entries[self.get_index()] = Transposition(chess.polyglot.zobrist_hash(self.board), evaluation, move, depth)

    def get_evaluation(self, depth):
        entry = self.entries[self.get_index()]

        if entry.key == chess.polyglot.zobrist_hash(self.board) and entry.depth >= depth:
            return entry.value

    def get_index(self):
        return chess.polyglot.zobrist_hash(self.board) % self.count


@dataclass
class Transposition:
    key: int | None = None
    value: int | None = None
    move: chess.Move | None = None
    depth: int | None = None

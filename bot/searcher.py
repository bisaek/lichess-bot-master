import chess
import logging
from bot.evaluation import eval, get_piece_value

logger = logging.getLogger(__name__)


class Searcher:
    def __init__(self, board: chess.Board, depth=4):
        self.depth = depth
        self.extensions_length = 0
        self.board = board

        self.counter = 0
        self.quiesce_counter = 0

        self.color = board.turn

    def start_search(self):
        logger.info(self.get_ordered_legal_moves())
        return self.alpha_beta(1, float("-inf"), float("inf"), True)

    def alpha_beta(self, depth, alpha, beta, log=False):
        self.counter += 1
        if depth >= self.depth or self.board.legal_moves.count() == 0:
            # if depth >= 10 or board.legal_moves.count() >= 10 or board.legal_moves.count() == 0:
            return self.quiesce(alpha, beta)
            # logger.info(depth)
        best_move_eval = float("-inf")
        best_move = None
        i = 0
        legal_moves_count = self.board.legal_moves.count()
        legal_moves = list(self.board.legal_moves)
        if depth == 1:
            legal_moves = self.get_ordered_legal_moves()
        for legal_move in legal_moves:
            i += 1

            self.board.push(legal_move)
            move_eval = -self.alpha_beta(depth + 1, -beta, -alpha)
            if log:
                logger.info(f"depth: {depth}")
                logger.info(f"move: {legal_move.uci()}")
                logger.info(f"eval: {move_eval}")
                logger.info(f"legal moves count: {i}/{legal_moves_count}")
                logger.info(f"called: {self.counter}")
                logger.info(f"quiesce called: {self.quiesce_counter}")
                logger.info(self.board.fen())
                # logger.info(board)

            self.board.pop()
            if move_eval > best_move_eval:

                # self.minimax(board, depth + 1, True)
                best_move_eval = move_eval
                best_move = legal_move
                if move_eval > alpha:
                    alpha = move_eval

            if move_eval >= beta:
                # if depth == 1:
                #    return best_move
                # else:
                return best_move_eval

        if depth == 1:
            if log:
                logger.info("best move")
                logger.info(f"move: {best_move.uci()}")
                logger.info(f"eval: {best_move_eval}")
                logger.info(f"called: {self.counter}")
                logger.info(self.board.fen())
                logger.info(self.board)
            return best_move
        else:
            return best_move_eval

    def quiesce(self, alpha, beta):
        self.quiesce_counter += 1
        stand_pad = eval(self.board, self.board.turn) - eval(self.board, not self.board.turn)
        best_value = stand_pad
        if stand_pad >= beta:
            return stand_pad
        if alpha < stand_pad:
            alpha = stand_pad

        for move in list(self.board.generate_legal_captures()):
            self.board.push(move)
            score = -self.quiesce(-beta, -alpha)
            self.board.pop()

            if score >= beta:
                return score
            if score > best_value:
                best_value = score
            if score > alpha:
                alpha = score
        return best_value

    def get_ordered_legal_moves(self):
        moves = list(self.board.legal_moves)
        moves.sort(key=self.move_ordering, reverse=True)
        return moves

    def move_ordering(self, move: chess.Move):
        score = 0
        if self.board.is_capture(move):
            score = 10 * get_piece_value(self.board.piece_at(move.to_square).piece_type) - get_piece_value(self.board.piece_at(move.from_square).piece_type)
        return score

    def determine_extension(self):
        return 0

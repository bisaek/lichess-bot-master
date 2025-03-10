import chess
import logging
import time
from bot.evaluation import eval, get_piece_value
from bot.transposition_table import TranspositionTable

logger = logging.getLogger(__name__)


class Searcher:
    def __init__(self, board: chess.Board, seach_time=60):
        #self.depth = depth
        self.seach_time = seach_time
        self.extensions_length = 0
        self.board = board

        self.counter = 0
        self.quiesce_counter = 0

        self.color = board.turn

        self.start_time = 0

        self.cancelled = False

        self.best_move = None
        #self.best_move_eval = float("-inf")
        self.best_move_this_iteration = None
        #self.best_move_this_iteration_eval = float("-inf")

        self.transpositionTable = TranspositionTable(board)

    def start_search(self):
        self.cancelled = False
        self.start_time = time.time()
        for depth in range(1, 20):
            # logger.info(self.get_ordered_legal_moves())
            #logger.info(self.transpositionTable.entries)
            self.alpha_beta(depth, float("-inf"), float("inf"), 0, True)
            logger.info(f'Depth: {depth}')
            logger.info(f'Time: {time.time() - self.start_time}')
            logger.info("best move")
            logger.info(f"move: {self.best_move_this_iteration.uci()}")
            # logger.info(f"eval: {best_move_eval}")
            logger.info(f"called: {self.counter}")
            logger.info(self.board.fen())
            logger.info(self.board)
            if not self.cancelled:
                self.best_move = self.best_move_this_iteration
            else:
                break

        return self.best_move

    def alpha_beta(self, depth, alpha, beta, extensions_length, first=False):
        self.counter += 1
        if depth == 0 or self.board.legal_moves.count() == 0:
            # if depth >= 10 or board.legal_moves.count() >= 10 or board.legal_moves.count() == 0:
            return self.quiesce(alpha, beta)
            # logger.info(depth)

        #tt_eval = self.transpositionTable.get_evaluation(depth)
        #if tt_eval is not None:
        #    return tt_eval
        best_move_eval = float("-inf")
        best_move = None
        i = 0
        legal_moves_count = self.board.legal_moves.count()
        legal_moves = list(self.board.legal_moves)
        if first:
            legal_moves = self.get_ordered_legal_moves()
        for legal_move in legal_moves:
            i += 1
            if time.time() - self.start_time >= self.seach_time:
                self.cancelled = True
                return 0
            self.board.push(legal_move)
            ext = self.determine_extension(extensions_length)
            #if ext != 0:
            #    logger.info(ext)
            move_eval = -self.alpha_beta(depth + ext - 1, -beta, -alpha, extensions_length + ext)
            #if first:
            #    logger.info(f"depth: {depth}")
            #    logger.info(f"move: {legal_move.uci()}")
            #    logger.info(f"eval: {move_eval}")
            #    logger.info(f"legal moves count: {i}/{legal_moves_count}")
            #    logger.info(f"called: {self.counter}")
            #    logger.info(f"quiesce called: {self.quiesce_counter}")
            #    logger.info(self.board.fen())
                # logger.info(board)

            self.board.pop()
            if move_eval > best_move_eval:

                # self.minimax(board, depth + 1, True)
                best_move_eval = move_eval
                best_move = legal_move
                if first:
                    self.best_move_this_iteration = legal_move
                    #self.best_move_this_iteration_eval = move_eval
                if move_eval > alpha:
                    alpha = move_eval

            if move_eval >= beta:
                return best_move_eval

        #self.transpositionTable.store_evaluation(depth, best_move_eval, best_move)
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
        if move == self.best_move:
            logger.info("same move")
            return 9999999
        score = 0
        if self.board.is_capture(move):
            score = 10 * get_piece_value(self.board.piece_at(move.to_square).piece_type) - get_piece_value(self.board.piece_at(move.from_square).piece_type)
        return score

    def determine_extension(self, extensions_length):
        if extensions_length > 2:
            return 0
        extension = 0
        if self.board.is_check():
            extension = 1
            #logger.info(extensions_length)

        if extension == 1:
            self.extensions_length += 1
        return extension


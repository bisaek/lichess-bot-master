"""
Some example classes for people who want to create a homemade bot.

With these classes, bot makers will not have to implement the UCI or XBoard interfaces themselves.
"""
from operator import index

import chess
from chess.engine import PlayResult, Limit
import random
from lib.engine_wrapper import MinimalEngine
from lib.lichess_types import MOVE, HOMEMADE_ARGS_TYPE
import logging


# Use this logger variable to print messages to the console or log files.
# logger.info("message") will always print "message" to the console or log file.
# logger.debug("message") will only print "message" if verbose logging is enabled.
logger = logging.getLogger(__name__)

class Bot(MinimalEngine):

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        #logger.info(self.minimax(board, 1).uci())
        self.counter = 0

        logger.info(self.eval(board, board.turn, True))

        #return PlayResult(self.minimax(board, 1, True), None)
        return PlayResult(self.alpha_beta(board, 1, float("-inf"), float("inf"), True), None)


    def minimax(self, board: chess.Board, depth, log=False):
        self.counter += 1
        if depth == 5 or board.legal_moves.count() == 0:
            return self.eval(board, board.turn) - self.eval(board, not board.turn)
        best_move_eval = float("-inf")
        best_move = None
        i = 0
        legal_moves_count = board.legal_moves.count()
        for legal_move in list(board.legal_moves):
            i += 1

            board.push(legal_move)
            move_eval = -self.minimax(board, depth + 1)
            if log:
                logger.info(f"depth: {depth}")
                logger.info(f"move: {legal_move.uci()}")
                logger.info(f"eval: {move_eval}")
                logger.info(f"legal moves count: {i}/{legal_moves_count}")
                logger.info(f"called: {self.counter}")
                logger.info(board.fen())
                #logger.info(board)
            if move_eval > best_move_eval:

                    #self.minimax(board, depth + 1, True)
                best_move_eval = move_eval
                best_move = legal_move
            board.pop()
    

        if depth == 1:
            if log:
                logger.info("best move")
                logger.info(f"move: {best_move.uci()}")
                logger.info(f"eval: {best_move_eval}")
                logger.info(f"called: {self.counter}")
                logger.info(board.fen())
                logger.info(board)
            return best_move
        else:
            return best_move_eval

    def alpha_beta(self, board: chess.Board, depth, alpha, beta, log=False):
        self.counter += 1
        if depth >= 6 or board.legal_moves.count() == 0:
            if depth >= 10 or board.legal_moves.count() >= 10 or board.legal_moves.count() == 0:
                return self.eval(board, board.turn) - self.eval(board, not board.turn)
            #logger.info(depth)
        best_move_eval = float("-inf")
        best_move = None
        i = 0
        legal_moves_count = board.legal_moves.count()
        for legal_move in list(board.legal_moves):
            i += 1

            board.push(legal_move)
            move_eval = -self.alpha_beta(board, depth + 1, -beta, -alpha)
            if log:
                logger.info(f"depth: {depth}")
                logger.info(f"move: {legal_move.uci()}")
                logger.info(f"eval: {move_eval}")
                logger.info(f"legal moves count: {i}/{legal_moves_count}")
                logger.info(f"called: {self.counter}")
                logger.info(board.fen())
                #logger.info(board)
            if move_eval > best_move_eval:

                    #self.minimax(board, depth + 1, True)
                best_move_eval = move_eval
                best_move = legal_move
                if move_eval > alpha:
                    alpha = move_eval
            
            board.pop()
            if move_eval >= beta:
                #if depth == 1:
                #    return best_move
                #else:
                return best_move_eval
            
    

        if depth == 1:
            if log:
                logger.info("best move")
                logger.info(f"move: {best_move.uci()}")
                logger.info(f"eval: {best_move_eval}")
                logger.info(f"called: {self.counter}")
                logger.info(board.fen())
                logger.info(board)
            return best_move
        else:
            return best_move_eval

    def eval(self, board: chess.Board, color: chess.Color, log=False):
        if board.outcome() != None:
            if board.outcome().winner == color:
                return 999
            elif board.outcome().winner == None:
                return 0
        
        eval = 0
        eval += len(board.pieces(chess.PAWN, color))
        eval += len(board.pieces(chess.KNIGHT, color)) * 3
        eval += len(board.pieces(chess.BISHOP, color)) * 3
        eval += len(board.pieces(chess.ROOK, color)) * 5
        eval += len(board.pieces(chess.QUEEN, color)) * 9

        if board.fullmove_number < 25:
            eval += 1/30 * board.legal_moves.count()
            eval += len(board.attackers(color, chess.D4)) * 0.1
            eval += len(board.attackers(color, chess.D5)) * 0.1
            eval += len(board.attackers(color, chess.E4)) * 0.1
            eval += len(board.attackers(color, chess.E5)) * 0.1

            #bishops and knight are defended
            for piece in list(board.pieces(chess.BISHOP, color)) + list(board.pieces(chess.KNIGHT, color)):
                if self.is_defended(board, piece, color):
                    eval -= 0.3
                    if log:
                        logger.info(chess.square_name(piece))

            # rocks are defended
            for piece in list(board.pieces(chess.ROOK, color)):
                if self.is_defended(board, piece, color):
                    eval -= 0.5
                    if log:
                        logger.info(chess.square_name(piece))

            # queen are defended
            for piece in list(board.pieces(chess.QUEEN, color)):
                if self.is_defended(board, piece, color):
                    eval -= 0.9
                    if log:
                        logger.info(chess.square_name(piece))

        return eval

    def is_defended(self, board: chess.Board, square, color) -> bool:
        if color == chess.WHITE:
            return not board.is_attacked_by(color, square) and chess.square_rank(square) > 3
        else:
            return not board.is_attacked_by(color, square) and chess.square_rank(square) < 4

class ExampleEngine(MinimalEngine):
    """An example engine that all homemade engines inherit."""


# Bot names and ideas from tom7's excellent eloWorld video

class RandomMove(ExampleEngine):
    """Get a random move."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:  # noqa: ARG002
        """Choose a random move."""
        return PlayResult(random.choice(list(board.legal_moves)), None)


class Alphabetical(ExampleEngine):
    """Get the first move when sorted by san representation."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:  # noqa: ARG002
        """Choose the first move alphabetically."""
        moves = list(board.legal_moves)
        moves.sort(key=board.san)
        return PlayResult(moves[0], None)


class FirstMove(ExampleEngine):
    """Get the first move when sorted by uci representation."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:  # noqa: ARG002
        """Choose the first move alphabetically in uci representation."""
        moves = list(board.legal_moves)
        moves.sort(key=str)
        return PlayResult(moves[0], None)


class ComboEngine(ExampleEngine):
    """
    Get a move using multiple different methods.

    This engine demonstrates how one can use `time_limit`, `draw_offered`, and `root_moves`.
    """

    def search(self,
               board: chess.Board,
               time_limit: Limit,
               ponder: bool,  # noqa: ARG002
               draw_offered: bool,
               root_moves: MOVE) -> PlayResult:
        """
        Choose a move using multiple different methods.

        :param board: The current position.
        :param time_limit: Conditions for how long the engine can search (e.g. we have 10 seconds and search up to depth 10).
        :param ponder: Whether the engine can ponder after playing a move.
        :param draw_offered: Whether the bot was offered a draw.
        :param root_moves: If it is a list, the engine should only play a move that is in `root_moves`.
        :return: The move to play.  
        """
        if isinstance(time_limit.time, int):
            my_time = time_limit.time
            my_inc = 0
        elif board.turn == chess.WHITE:
            my_time = time_limit.white_clock if isinstance(time_limit.white_clock, int) else 0
            my_inc = time_limit.white_inc if isinstance(time_limit.white_inc, int) else 0
        else:
            my_time = time_limit.black_clock if isinstance(time_limit.black_clock, int) else 0
            my_inc = time_limit.black_inc if isinstance(time_limit.black_inc, int) else 0

        possible_moves = root_moves if isinstance(root_moves, list) else list(board.legal_moves)

        if my_time / 60 + my_inc > 10:
            # Choose a random move.
            move = random.choice(possible_moves)
        else:
            # Choose the first move alphabetically in uci representation.
            possible_moves.sort(key=str)
            move = possible_moves[0]
        return PlayResult(move, None, draw_offered=draw_offered)

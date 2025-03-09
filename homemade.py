"""
Some example classes for people who want to create a homemade bot.

With these classes, bot makers will not have to implement the UCI or XBoard interfaces themselves.
"""
from operator import index

import chess
import chess.polyglot
from chess.engine import PlayResult, Limit
import random
from lib.engine_wrapper import MinimalEngine
from lib.lichess_types import MOVE, HOMEMADE_ARGS_TYPE
import logging
from functools import lru_cache 

# Use this logger variable to print messages to the console or log files.
# logger.info("message") will always print "message" to the console or log file.
# logger.debug("message") will only print "message" if verbose logging is enabled.
logger = logging.getLogger(__name__)

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.BISHOP: 320,
    chess.KNIGHT: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900
}

PAWN_PIECE_SQUARE_TABLE = [0,  0,  0,  0,  0,  0,  0,  0,
                           50, 50, 50, 50, 50, 50, 50, 50,
                           10, 10, 20, 30, 30, 20, 10, 10,
                           5,  5,  10, 25, 25, 10, 5,  5,
                           0,  0,  0,  20, 20, 0,  0,  0,
                           5, -5, -10, 0,  0, -10,-5,  5,
                           5,  10, 10,-20,-20, 10, 10, 5,
                           0,  0,  0,  0,  0,  0,  0,  0]

KNIGHT_PIECE_SQUARE_TABLE = [-50,-40,-30,-30,-30,-30,-40,-50,
                             -40,-20,  0,  0,  0,  0,-20,-40,
                             -30,  0, 10, 15, 15, 10,  0,-30,
                             -30,  5, 15, 20, 20, 15,  5,-30,
                             -30,  0, 15, 20, 20, 15,  0,-30,
                             -30,  5, 10, 15, 15, 10,  5,-30,
                             -40,-20,  0,  5,  5,  0,-20,-40,
                             -50,-40,-30,-30,-30,-30,-40,-50,]

BISHOP_PIECE_SQUARE_TABLE = [-20,-10,-10,-10,-10,-10,-10,-20,
                             -10,  0,  0,  0,  0,  0,  0,-10,
                             -10,  0,  5, 10, 10,  5,  0,-10,
                             -10,  5,  5, 10, 10,  5,  5,-10,
                             -10,  0, 10, 10, 10, 10,  0,-10,
                             -10, 10, 10, 10, 10, 10, 10,-10,
                             -10,  5,  0,  0,  0,  0,  5,-10,
                             -20,-10,-10,-10,-10,-10,-10,-20,]

ROOK_PIECE_SQUARE_TABLE = [  0,  0,  0,  0,  0,  0,  0,  0,
                             5, 10, 10, 10, 10, 10, 10,  5,
                            -5,  0,  0,  0,  0,  0,  0, -5,
                            -5,  0,  0,  0,  0,  0,  0, -5,
                            -5,  0,  0,  0,  0,  0,  0, -5,
                            -5,  0,  0,  0,  0,  0,  0, -5,
                            -5,  0,  0,  0,  0,  0,  0, -5,
                             0,  0,  0,  5,  5,  0,  0,  0]

QUEEN_PIECE_SQUARE_TABLE = [-20,-10,-10, -5, -5,-10,-10,-20,
                            -10,  0,  0,  0,  0,  0,  0,-10,
                            -10,  0,  5,  5,  5,  5,  0,-10,
                            -5,  0,  5,  5,  5,  5,  0, -5,
                             0,  0,  5,  5,  5,  5,  0, -5,
                            -10,  5,  5,  5,  5,  5,  0,-10,
                            -10,  0,  5,  0,  0,  0,  0,-10,
                            -20,-10,-10, -5, -5,-10,-10,-20]

KING_MIDDLE_GAME_PIECE_SQUARE_TABLE = [-30,-40,-40,-50,-50,-40,-40,-30,
                                      -30,-40,-40,-50,-50,-40,-40,-30,
                                      -30,-40,-40,-50,-50,-40,-40,-30,
                                      -30,-40,-40,-50,-50,-40,-40,-30,
                                      -20,-30,-30,-40,-40,-30,-30,-20,
                                      -10,-20,-20,-20,-20,-20,-20,-10,
                                       20, 20,  0,  0,  0,  0, 20, 20,
                                       20, 30, 10,  0,  0, 10, 30, 20]

KING_END_GAME_PIECE_SQUARE_TABLE = [-50,-40,-30,-20,-20,-30,-40,-50,
                                    -30,-20,-10,  0,  0,-10,-20,-30,
                                    -30,-10, 20, 30, 30, 20,-10,-30,
                                    -30,-10, 30, 40, 40, 30,-10,-30,
                                    -30,-10, 30, 40, 40, 30,-10,-30,
                                    -30,-10, 20, 30, 30, 20,-10,-30,
                                    -30,-30,  0,  0,  0,  0,-30,-30,
                                    -50,-30,-30,-30,-30,-30,-30,-50]

class Bot(MinimalEngine):

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        #logger.info(self.minimax(board, 1).uci())
        self.counter = 0
        self.quiesce_counter = 0


        moves = list(board.legal_moves)
        moves.sort(key=lambda move : self.move_ordering(move, board), reverse=True)
        logger.info(moves)

        chess.Board.__hash__ = chess.polyglot.zobrist_hash
        return PlayResult(self.alpha_beta(board, 1, float("-inf"), float("inf"), True), None)



    def alpha_beta(self, board: chess.Board, depth, alpha, beta, log=False):
        self.counter += 1
        if depth >= 5 or board.legal_moves.count() == 0:
            #if depth >= 10 or board.legal_moves.count() >= 10 or board.legal_moves.count() == 0:
            return self.quiesce(board, alpha, beta)
            #logger.info(depth)
        best_move_eval = float("-inf")
        best_move = None
        i = 0
        legal_moves_count = board.legal_moves.count()
        legal_moves = list(board.legal_moves)
        if depth == 1:
            legal_moves.sort(key=lambda move : self.move_ordering(move, board), reverse=True)
        for legal_move in legal_moves:
            i += 1

            board.push(legal_move)
            move_eval = -self.alpha_beta(board, depth + 1, -beta, -alpha)
            if log:
                logger.info(f"depth: {depth}")
                logger.info(f"move: {legal_move.uci()}")
                logger.info(f"eval: {move_eval}")
                logger.info(f"legal moves count: {i}/{legal_moves_count}")
                logger.info(f"called: {self.counter}")
                logger.info(f"quiesce called: {self.quiesce_counter}")
                logger.info(board.fen())
                #logger.info(board)

            board.pop()
            if move_eval > best_move_eval:

                    #self.minimax(board, depth + 1, True)
                best_move_eval = move_eval
                best_move = legal_move
                if move_eval > alpha:
                    alpha = move_eval
            
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
        
    def quiesce(self, board: chess.Board, alpha, beta):
        self.quiesce_counter += 1
        stand_pad = self.eval(board, board.turn) - self.eval(board, not board.turn)
        best_value = stand_pad
        if stand_pad >= beta:
            return stand_pad
        if alpha < stand_pad:
            alpha = stand_pad
        
        for move in list(board.generate_legal_captures()):
            board.push(move)
            score = -self.quiesce(board, -beta, -alpha)
            board.pop()

            if score >= beta:
                return score
            if score > best_value:
                best_value = score
            if score > alpha:
                alpha = score
        return best_value
            

    def move_ordering(self, move: chess.Move, board: chess.Board):
        # board.push(move)
        # score = self.eval(board, not board.turn)
        # board.pop()


        score = 0
        if board.is_capture(move):
           score = 10 * self.get_piece_value(board.piece_at(move.to_square).piece_type) - self.get_piece_value(board.piece_at(move.from_square).piece_type)
        return score

    def eval(self, board: chess.Board, color: chess.Color, log=False):
        if board.outcome() != None:
            if board.outcome().winner == color:
                return 9999999
            elif board.outcome().winner == None:
                return 0
        if log:
            logger.info(self.is_end_game(board))
        eval = 0
        eval += len(board.pieces(chess.PAWN, color)) * self.get_piece_value(chess.PAWN)
        eval += len(board.pieces(chess.KNIGHT, color)) * self.get_piece_value(chess.KNIGHT)
        eval += len(board.pieces(chess.BISHOP, color)) * self.get_piece_value(chess.BISHOP)
        eval += len(board.pieces(chess.ROOK, color)) * self.get_piece_value(chess.ROOK)
        eval += len(board.pieces(chess.QUEEN, color)) * self.get_piece_value(chess.QUEEN)

        for pawn in list(board.pieces(chess.PAWN, color)):
            if color == chess.WHITE:
                eval += PAWN_PIECE_SQUARE_TABLE[63 - pawn]
            else:
                eval += PAWN_PIECE_SQUARE_TABLE[pawn]

        for knight in list(board.pieces(chess.KNIGHT, color)):
            if color == chess.WHITE:
                eval += KNIGHT_PIECE_SQUARE_TABLE[63 - knight]
            else:
                eval += KNIGHT_PIECE_SQUARE_TABLE[knight]

        for bishop in list(board.pieces(chess.BISHOP, color)):
            if color == chess.WHITE:
                eval += BISHOP_PIECE_SQUARE_TABLE[63 - bishop]
            else:
                eval += BISHOP_PIECE_SQUARE_TABLE[bishop]

        for rook in list(board.pieces(chess.ROOK, color)):
            if color == chess.WHITE:
                eval += ROOK_PIECE_SQUARE_TABLE[63 - rook]
            else:
                eval += ROOK_PIECE_SQUARE_TABLE[rook]

        for queen in list(board.pieces(chess.QUEEN, color)):
            if color == chess.WHITE:
                eval += QUEEN_PIECE_SQUARE_TABLE[63 - queen]
            else:
                eval += QUEEN_PIECE_SQUARE_TABLE[queen]

        for king in list(board.pieces(chess.KING, color)):
            if self.is_end_game(board):
                if color == chess.WHITE:
                    eval += KING_END_GAME_PIECE_SQUARE_TABLE[63 - king]
                else:
                    eval += KING_END_GAME_PIECE_SQUARE_TABLE[king]
            else:
                if color == chess.WHITE:
                    eval += KING_MIDDLE_GAME_PIECE_SQUARE_TABLE[63 - king]
                else:
                    eval += KING_MIDDLE_GAME_PIECE_SQUARE_TABLE[king]


        return eval

    def is_defended(self, board: chess.Board, square, color) -> bool:
        if color == chess.WHITE:
            return not board.is_attacked_by(color, square) and chess.square_rank(square) > 3
        else:
            return not board.is_attacked_by(color, square) and chess.square_rank(square) < 4
        
    def get_piece_value(self, piece_type: chess.PieceType):
        return PIECE_VALUES[piece_type]
    
    def is_end_game(self, board: chess.Board):
        zero_queens = len(board.pieces(chess.QUEEN, chess.WHITE)) == 0 and len(board.pieces(chess.QUEEN, chess.BLACK)) == 0
        zero_rooks = len(board.pieces(chess.ROOK, chess.WHITE)) == 0 and len(board.pieces(chess.ROOK, chess.BLACK)) == 0
        white_minorpieces = len(board.pieces(chess.BISHOP, chess.WHITE)) + len(board.pieces(chess.KNIGHT, chess.WHITE))
        black_minorpieces = len(board.pieces(chess.BISHOP, chess.BLACK)) + len(board.pieces(chess.KNIGHT, chess.BLACK))
        return zero_queens or (zero_rooks and white_minorpieces <= 1 and black_minorpieces <= 1)

        
        

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

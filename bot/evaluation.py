import chess
import logging

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


def is_end_game(board: chess.Board):
    zero_queens = len(board.pieces(chess.QUEEN, chess.WHITE)) == 0 and len(board.pieces(chess.QUEEN, chess.BLACK)) == 0
    zero_rooks = len(board.pieces(chess.ROOK, chess.WHITE)) == 0 and len(board.pieces(chess.ROOK, chess.BLACK)) == 0
    white_minorpieces = len(board.pieces(chess.BISHOP, chess.WHITE)) + len(board.pieces(chess.KNIGHT, chess.WHITE))
    black_minorpieces = len(board.pieces(chess.BISHOP, chess.BLACK)) + len(board.pieces(chess.KNIGHT, chess.BLACK))
    return zero_queens or (zero_rooks and white_minorpieces <= 1 and black_minorpieces <= 1)


def get_piece_value(piece_type: chess.PieceType):
    return PIECE_VALUES[piece_type]


def is_defended(board: chess.Board, square, color) -> bool:
    if color == chess.WHITE:
        return not board.is_attacked_by(color, square) and chess.square_rank(square) > 3
    else:
        return not board.is_attacked_by(color, square) and chess.square_rank(square) < 4


def eval(board: chess.Board, color: chess.Color, log=False):
    if board.outcome() != None:
        if board.outcome().winner == color:
            return 9999999
        elif board.outcome().winner == None:
            return 0
    if log:
        logger.info(is_end_game(board))
    eval = 0
    eval += len(board.pieces(chess.PAWN, color)) * get_piece_value(chess.PAWN)
    eval += len(board.pieces(chess.KNIGHT, color)) * get_piece_value(chess.KNIGHT)
    eval += len(board.pieces(chess.BISHOP, color)) * get_piece_value(chess.BISHOP)
    eval += len(board.pieces(chess.ROOK, color)) * get_piece_value(chess.ROOK)
    eval += len(board.pieces(chess.QUEEN, color)) * get_piece_value(chess.QUEEN)

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
        if is_end_game(board):
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

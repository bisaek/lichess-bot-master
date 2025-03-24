import pygame
import chess
from multiprocessing import Process, Queue
from board import BoardUI, SQUARE_SIZE
from bot.searcher import Searcher
from test.versus.versus import Versus
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True
    logger.info("test")
    board = BoardUI(screen, chess.WHITE)
    versus = Versus(1, 1, board)
    versus.start_games()

    is_engine_searching = False
    while running:
        #if board.is_bots_turn():
        #    board.bot_move()


            #engine(board, transposition_table)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                board.mouse_button_down()
        board.draw_board()
        pygame.display.flip()

    pygame.quit()


def engine(board, transposition_table, return_queue):
    transposition_table.board = board
    searcher = Searcher(board, transposition_table, 5)
    return_queue.put(searcher.start_search())




if __name__ == '__main__':
    main()

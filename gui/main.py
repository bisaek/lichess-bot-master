import pygame
import chess
from multiprocessing import Process, Queue
from board import Board, SQUARE_SIZE
from bot.searcher import Searcher
from bot.transposition_table import TranspositionTable


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True

    board = Board(screen, chess.WHITE)

    transposition_table = TranspositionTable()
    is_engine_searching = False
    while running:
        if board.board.turn == chess.BLACK:
            if not is_engine_searching:
                is_engine_searching = True
                return_queue = Queue()
                engine_process = Process(target=engine, args=(board.board, transposition_table, return_queue))
                engine_process.start()
            elif not engine_process.is_alive():
                move = return_queue.get()
                board.board.push(move)
                is_engine_searching = False
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

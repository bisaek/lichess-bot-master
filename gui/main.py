import pygame
import chess
from multiprocessing import Process, Queue
from draw import Draw, SQUARE_SIZE
from bot.searcher import Searcher
from bot.transposition_table import TranspositionTable


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True

    board = chess.Board()
    draw = Draw(screen, board, chess.WHITE)

    transposition_table = TranspositionTable()
    is_engine_searching = False
    while running:
        if board.turn == chess.BLACK:
            if not is_engine_searching:
                is_engine_searching = True
                return_queue = Queue()
                engine_process = Process(target=engine, args=(board, transposition_table, return_queue))
                engine_process.start()
            elif not engine_process.is_alive():
                move = return_queue.get()
                board.push(move)
            #engine(board, transposition_table)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                draw.select_square()
        draw.draw()
        pygame.display.flip()

    pygame.quit()


def engine(board, transposition_table, return_queue):
    transposition_table.board = board
    searcher = Searcher(board, transposition_table, 5)
    return_queue.put(searcher.start_search())




if __name__ == '__main__':
    main()

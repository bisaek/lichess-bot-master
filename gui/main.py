import pygame
import chess
from draw import Draw, SQUARE_SIZE


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True

    board = chess.Board()
    draw = Draw(screen, board, chess.WHITE)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                draw.select_square()

        draw.draw()
        pygame.display.flip()

    pygame.quit()







if __name__ == '__main__':
    main()

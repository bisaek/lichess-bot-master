from multiprocessing import Process, Value

import chess
import pygame
import socket

from bot.searcher import Searcher
from bot.transposition_table import TranspositionTable
from gui.board import BoardUI

class Versus:
    def __init__(self):
        self.player1_wins = 0
        self.player2_wins = 0
        self.draws = 0

        self.socket_player_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_player_1.bind(('', 5555))
        self.socket_player_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_player_2.bind(('', 5556))



    def start_games(self):

        with open('fens.txt', 'r') as f:
            boards = [chess.Board(line) for line in f]
        for board in boards:
            self.boardUI.board = board
            self.boardUI.draw_board()
            pygame.display.flip()
            while not board.is_game_over():
                transposition_table = TranspositionTable()
                transposition_table.board = board
                searcher = Searcher(board, transposition_table, 1)
                board.push(searcher.start_search())
                self.boardUI.board = board
                self.boardUI.draw_board()
                pygame.display.flip()
                print(board)
            if board.outcome().winner == chess.WHITE:
                self.player1_wins += 1
            elif board.outcome().winner == chess.BLACK:
                self.player2_wins += 1
            else:
                self.draws += 1

            print(f"{self.player1_wins=}, {self.player2_wins=}, {self.draws=}")

#versus = Versus(1, 1)
#versus.start_games()
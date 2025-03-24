from multiprocessing import Process, Value

import chess
import pygame
import socket
from threading import Thread

from bot.searcher import Searcher
from bot.transposition_table import TranspositionTable


class Versus:
    def __init__(self):
        self.player1_wins = 0
        self.player2_wins = 0
        self.draws = 0
        self.board = chess.Board()

        self.socket_player_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_player_1.bind(('', 5555))
        self.socket_player_1.listen()
        self.socket_player_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_player_2.bind(('', 5556))
        self.socket_player_2.listen()

        client_socket_player_1, adress_player_1 = self.socket_player_1.accept()
        client_socket_player_2, adress_player_2 = self.socket_player_2.accept()

        self.talk_to_client(client_socket_player_1)

    def talk_to_client(self, client_socket):
        Thread(target=self.receive_message, args=(client_socket)).start()
        self.send_message(client_socket)

    def send_message(self, client_socket):
        while True:
            server_message = input()
            client_socket.send(bytes(server_message.encode()))

    def receive_message(self, client_socket):
        while True:
            client_message = client_socket.recv(1024).decode()
            print(client_message)

    def start_games(self):

        with open('fens.txt', 'r') as f:
            boards = [chess.Board(line) for line in f]
        for board in boards:
            #self.boardUI.board = board
            #self.boardUI.draw_board()
            self.board = board
            pygame.display.flip()
            while not board.is_game_over():
                transposition_table = TranspositionTable()
                transposition_table.board = self.board
                searcher = Searcher(self.board, transposition_table, 1)
                self.board.push(searcher.start_search())
                #self.boardUI.board = board
                #self.boardUI.draw_board()
                #pygame.display.flip()
                print(board)
            if self.board.outcome().winner == chess.WHITE:
                self.player1_wins += 1
            elif self.board.outcome().winner == chess.BLACK:
                self.player2_wins += 1
            else:
                self.draws += 1

            print(f"{self.player1_wins=}, {self.player2_wins=}, {self.draws=}")


versus = Versus()
#versus.start_games()

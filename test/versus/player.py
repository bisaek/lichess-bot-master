import socket
from threading import Thread

class Player:
    def __init__(self, player1 = True):
        self.player1 = player1

        self.socket = socket.socket()
        self.socket.connect(('', 5555))

        self.talk_to_client()

    def talk_to_client(self):
        Thread(target=self.receive_message).start()
        self.send_message()

    def send_message(self):
        while True:
            server_message = input()
            self.socket.send(bytes(server_message.encode()))

    def receive_message(self):
        while True:
            client_message = self.socket.recv(1024).decode()
            print(client_message)

Player()
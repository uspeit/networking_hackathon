import random
import threading
import time
from _thread import start_new_thread
from socket import *

SERVER_PORT = 2845
SERVER_IP = gethostbyname(gethostname())
BROADCAST_PORT = 13147


class Server:
    def __init__(self):
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.teams = []
        self.start_game = False
        self.score = [0, 0]

    def start_server(self):
        self.udp_socket.bind((SERVER_IP, SERVER_PORT))
        self.tcp_socket.bind((SERVER_IP, SERVER_PORT))
        thread = threading.Thread(target=self.start_tcp_server)
        thread.start()

    def start_tcp_server(self):
        print("Server started, listening on IP address " + str(SERVER_IP))

        threading.Thread(target=self.broadcast_details).start()
        self.tcp_socket.listen()
        while True:
            # Accept client
            c, addr = self.tcp_socket.accept()
            lock = threading.Lock()
            lock.acquire()
            if len(self.teams) == 1:
                random.shuffle(self.teams)
            lock.release()

            # Start handler on new thread
            start_new_thread(self.client_handler, (c,))

    def client_handler(self, s):
        team_name = str(s.recv(1024), 'utf-8')
        self.teams += [team_name]

        if len(self.teams) > 1:
            self.start_game = True

        while not self.start_game:
            time.sleep(0.5)

        # Save team names
        team1 = ''.join(self.teams[:int(len(self.teams) / 2)])
        team2 = ''.join(self.teams[int(len(self.teams) / 2):])

        # Send start message
        s.send(bytes(
            f"Welcome to the online typing game.\n"
            f"Team '{team1}' playing against Team '{team2}'\n"
            f"Type your fastest for the next 10 seconds.",
            encoding='utf8'))

        index = self.teams.index(team_name) // 2

        # Listen for packets for 10 seconds
        start_time = time.time()
        while time.time() - start_time < 10:
            data = s.recv(1024)
            if not data:
                continue
            print(f"{team_name} sent: {str(data, 'utf-8')}")
            self.score[index] += 1

        winner_index = 0
        if self.score[0] < self.score[1]:
            winner_index = 1
        winner_team_name = team1
        if self.score[0] < self.score[1]:
            winner_team_name = team2
        # Game Over Message
        message = f"===\nGame over!\n===\n" \
                  f"Team '{self.teams[0]}' typed {self.score[0]} characters.\n" \
                  f"Team '{self.teams[1]}' typed {self.score[1]} characters.\n" \
                  f"Group {winner_index + 1} wins! \n\n" \
                  f"Congratulations to {winner_team_name} for winning the game."
        s.send(bytes(message, encoding='utf8'))
        self.start_game = False
        s.close()

    def broadcast_details(self):
        while True:
            if not self.start_game:
                start_time = time.time()
                server = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
                server.settimeout(0.2)
                server.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                server.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
                magic_cookie = "feedbeef"
                message_type = "02"
                x = bytes.fromhex(magic_cookie)
                y = bytes.fromhex(message_type)
                z = SERVER_PORT.to_bytes(2, byteorder='big')
                message = x + y + z

                while time.time() - start_time < 10:
                    server.sendto(message, ('<broadcast>', BROADCAST_PORT))
                    time.sleep(1)


def start_server():
    server = Server()
    server.start_server()


if __name__ == '__main__':
    start_server()

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
        self.players = []
        self.scores = [0, 0, 0, 0]
        self.game_started = False

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
            if len(self.players) > 1:
                random.shuffle(self.players)
            lock.release()

            # Start handler on new thread
            start_new_thread(self.client_handler, (c,))

    def client_handler(self, s):
        team_name = str(s.recv(1024), 'utf-8')
        self.players += [team_name]

        if len(self.players) > 1:
            self.game_started = True

        while not self.game_started:
            time.sleep(0.5)

        # Send start message
        s.send(bytes(
            "Welcome to Keyboard Spamming Battle Royale.\n"
            "Group 1:\n==\n"
            f"{self.players[0]}\n{self.players[1]}\n"
            "Group 2:\n==\n"
            f"{self.players[2]}\n{self.players[3]}\n"
            "Start pressing keys on your keyboard as fast as you can!!\n",
            encoding='utf8'))

        player_index = self.players.index(team_name)

        # Listen for packets for 10 seconds
        start_time = time.time()
        while time.time() - start_time < 10:
            data = s.recv(1024)
            if not data:
                continue
            print(f"{team_name} sent: {str(data, 'utf-8')}")
            self.scores[player_index] += 1

        team_scores = [
            self.scores[0] + self.scores[1],
            self.scores[2] + self.scores[3]
        ]

        winner_team_index = 0
        team_names = ["Group 1", "Group 2"]
        if team_scores[0] < team_scores[1]:
            winner_team_index = 1
        # Game Over Message
        message = "Game over!\n" \
                  f"Group 1 typed in {team_scores[0]} characters. Group 2 typed in {team_scores[1]} characters.\n" \
                  f"{team_names[winner_team_index]} wins!\n==\n" \
                  f"Congratulations to the winners:\n==\n" \
                  f"{self.players[0 + winner_team_index * 2]}\n{self.players[1 + winner_team_index * 2]}\n"
        s.send(bytes(message, encoding='utf8'))

        self.game_started = False
        s.close()

    def broadcast_details(self):
        while True:
            if not self.game_started:
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

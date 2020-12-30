import enum
import threading
import time
from _thread import start_new_thread
import random
from socket import *
from threading import *
import struct

SERVER_PORT = 2845
SERVER_IP = gethostbyname(gethostname())
dest_port=13147


class Server:
    def __init__(self):
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.connections = {}
        self.game_treads = {}
        self.group1 = {}
        self.group2 = {}
        self.teams=[]
        self.start_game=False
        self.numOfPlayer=0
        self.scores=[0,0,0,0]

    def startServer(self):
        self.udp_socket.bind((SERVER_IP,SERVER_PORT))
        self.tcp_socket.bind((SERVER_IP,SERVER_PORT))
        thread = threading.Thread(target=self.startTCP)
        thread.start()

    def startTCP(self):
        print("Server started, listening on IP address "+str(SERVER_IP))

        self.Broadcast()
        self.tcp_socket.listen()
        while True:
            # establish connection with client
            c, addr = self.tcp_socket.accept()
            lock=threading.Lock()
            lock.acquire()
            self.numOfPlayer += 1
            if self.numOfPlayer == 1:
                random.shuffle(self.teams)
            lock.release()

            # Start a new thread and return its identifier
            start_new_thread(self.clientHandler, (c,))
        self.tcp_socket.close()

    def clientHandler(self, c):
        TeamName = str(c.recv(1024), 'utf-8')
        self.teams += [TeamName]
        while not self.start_game:
            time.sleep(0.5)

        # setting team names in a variable
        team1 = ''.join(self.teams[:int(len(self.teams) / 2)])
        team2 = ''.join(self.teams[int(len(self.teams) / 2):])

        # S Sending start message
        c.send(bytes(
            f"Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n{team1}Group 2:\n==\n{team2}\nStart pressing keys on your keyboard as fast as you can!!",
            encoding='utf8'))

        index = self.teams.index(TeamName) // 2

        # While not past 10 seconds - listen to key presses.
        start_time = time.time()
        while time.time() - start_time < 10:
            # data received from client
            data = c.recv(1024)
            if not data:
                continue
            print(f"RECEIVED: {data}")
            self.scores[index] += 1


        winner = 0
        if (self.scores[0] > self.scores[1]):
            pass
        else :
            winner=1
        winner_team = team1
        if (self.scores[0] < self.scores[1]):
            winner_team= team2
        # Game Over Message
        message = f"\nGame over!\nGroup 1 typed in {self.scores[0]} characters. Group 2 typed in {self.scores[1]} characters.\nGroup {winner + 1} wins! \n\nCongratulations to the winners:\n==\n{winner_team}"
        c.send(bytes(message, encoding='utf8'))
        self.start_game = False
        # connection closed
        c.close()


    def Broadcast(self):
        # Starts Broadcasting via a thread.
        thread = threading.Thread(target=self.startBroadcast)
        thread.start()

    def startBroadcast(self):
        while True:
            if not self.start_game:
                start_time = time.time()
                server = socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
                # Enable port reusage
                # server.setsockopt(SOL_SOCKET,SO_REUSEPORT, 1)
                # Enable broadcasting mode
                server.setsockopt(SOL_SOCKET,SO_BROADCAST, 1)

                # Set a timeout so the socket does not block
                # indefinitely when trying to receive data.
                server.settimeout(0.2)
                magic_cookie = "feedbeef"
                message_type = "02"
                x = bytes.fromhex(magic_cookie)
                y = bytes.fromhex(message_type)
                z = SERVER_PORT.to_bytes(2, byteorder='big')
                message = x + y + z

                while time.time() - start_time < 10:
                    server.sendto( message, ('<broadcast>',dest_port))
                    time.sleep(1)
                self.start_game = True


def startServer():
    server = Server()
    server.startServer()


if __name__ == '__main__':
    startServer()

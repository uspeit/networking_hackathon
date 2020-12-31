import socket
import sys
import threading
from socket import *
import getch

CLIENT_IP = gethostbyname(gethostname())
BROADCAST_PORT = 13147


class Client():
    def __init__(self, team_name):
        self.team_name = team_name
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)

    def start(self):
        # Creates a thread to start listening for broadcasts.
        thread = threading.Thread(target=self.listen)
        thread.start()

    def listen(self):
        print("Client started - listening for broadcasts...")

        try:
            self.udp_socket.bind(('', BROADCAST_PORT))
        except:
            self.listen()

        # Receive Packet
        message = self.udp_socket.recvfrom(1024)

        self.udp_socket.close()
        # Teardown Packet
        # magic_cookie = message[:4]
        # message_type = message[4]
        port_tcp = message[0][5:]
        tmp = int.from_bytes(port_tcp, byteorder='big', signed=False)
        m = message[1][0]
        self.connect_to_tcp_server(tmp, m)

    def connect_to_tcp_server(self, port_tcp, m):
        s = socket(AF_INET, SOCK_STREAM)
        print(f"Client connecting to server port: {port_tcp}")
        s.connect((CLIENT_IP, port_tcp))
        # Send team name
        s.send(bytes(self.team_name, encoding='utf8'))

        # Receive start message
        data = str(s.recv(1024), 'utf-8')
        print(data)

        s.settimeout(0.0)
        running = True
        while running:
            try:
                data = s.recv(1024)
                message = str(data, 'utf-8')
                print(message)
                running = False
            except:
                try:
                    c = getch.getch()
                    try:
                        s.send(bytes(c, encoding='utf8'))
                    except:
                        data = s.recv(1024)
                        message = str(data, 'utf-8')
                        print(message)
                        running = False
                except:
                    continue

        s.close()


def start_client():
    client = Client(sys.argv[1])
    client.start()


if __name__ == '__main__':
    start_client()

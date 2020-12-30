import socket
import threading
import sys
import os
import time
import random
from socket import *
import curses 
import struct

SERVER_PORT = 2845
client_IP = gethostbyname(gethostname())
sorce_port=13147

class Client():
    def __init__(self,team_name,stdscr):
        self.teamName = team_name
        self.stdscr = stdscr
        self.receievedData = False
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)

    def listenToBroadcast(self):
        # Creates a thread to start listening for broadcasts.
        thread = threading.Thread(target=self.listen)
        thread.start()

    def listen(self):
        #s = socket(AF_INET,SOCK_DGRAM)
        print( "Client started, listening for offer requests...")

        # Binds client to listen on port self.port. (will be 13117)
        try:
            self.udp_socket.bind(('', sorce_port))
        except:
            self.listen()
        # Receives Message
        message= self.udp_socket.recvfrom(1024)

        # Message Teardown.
        # magic_cookie = message[:4]
        # message_type = message[4]
        port_tcp = message[0][5:]
        tmp=int.from_bytes(port_tcp, byteorder='big', signed=False)
        m=message[1][0]
        self.connectTCPServer(tmp,m)


    def connectTCPServer(self,port_tcp,m):
        s = socket(AF_INET,SOCK_STREAM)
        # connect to tcp server
        print(port_tcp)
        s.connect(('192.168.0.198', port_tcp))
        # Sending team name
        s.send(bytes(self.teamName, encoding='utf8'))

        # Receive data from Server
        data = str(s.recv(1024), 'utf-8')
        # Enable Curses
        curses.noecho() # prevents user input from being echoed
        curses.curs_set(0)
        curses.cbreak()
        self.stdscr.addstr(0, 0, data)

        # Setting blocking to false, Data to none and removing key presses representation
        data = None
        s.settimeout(0.0)
        #capture characters without press enter?
        # os.system("stty raw -echo")
        while True:
            # if data is recieved it will stop and print, else it will send every key press to the server.
            try:
                data = s.recv(1024)
                message = str(data, 'utf-8')
                #self.receievedData = True
                print(message)
            except:
                c = self.stdscr.getch()
                self.stdscr.move(7, 0)
                if c > 0:
                    s.send(struct.pack('b', c))
        s.close()
        # Disable Curses
        self.stdscr.clear()
        self.stdscr.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()


def startClient(stdscr):
    stdscr.nodelay(1)
    client=Client("dor_eitan",stdscr)
    client.listenToBroadcast()
        
if __name__ == '__main__':
    curses.wrapper(startClient)
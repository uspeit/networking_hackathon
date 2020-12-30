from Client import startClient
from Server import startServer
import curses 


def main(stdscr):
    startServer()
    startClient(stdscr)


if __name__ == '__main__':
    curses.wrapper(main)
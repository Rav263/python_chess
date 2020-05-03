#! /usr/bin/python3

import ui
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

from board import Board
from gamelogic import Logic
from io_functions import Data


def main():
    # Here we need to init Field and Game logic
    data = Data("data.dat")
    board = Board(data)
    logic = Logic(data)
    # Then we need start game

    qss_file = open('styles.qss').read()
    # logic.start(board, data)
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()
    print('Size: %d x %d' % (size.width(), size.height()))
    
    app.setStyleSheet(qss_file);
    main_window = ui.Main_Window()
    sys.exit(app.exec_())
    
    # Maybe if it will be in web, we must start game server
    # Or we can create some server with a few people, who play PVP


if __name__ == "__main__":
    print("Hello, this is python chess game")
    main()

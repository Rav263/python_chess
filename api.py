from board import Board
from gamelogic import Logic
from io_functions import Data


class Api:
    def __init__(self):
        # Here we need to init Field and Game logic
        self.data = Data("data.dat")
        self.board = Board(self.data)
        self.logic = Logic(self.data)
        # Then we need start game

    def start_cmd(self):
        self.logic.start(self.board, self.data)

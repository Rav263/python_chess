#! /usr/bin/python3

from board import Board
from gamelogic import Logic
from io_functions import Data


def main():
    # Here we need to init Field and Game logic
    data = Data("data.dat")
    board = Board(data)
    logic = Logic()
    # Then we need start game

    logic.start(board, data)

    # Maybe if it will be in web, we must start game server
    # Or we can create some server with a few people, who play PVP


if __name__ == "__main__":
    print("Hello, this is python chess game")
    main()

from board import Board
from gamelogic import Logic
from io_functions import Data


from collections import defaultdict


class Api:
    def __init__(self):
        # Here we need to init Field and Game logic
        self.data = Data("data.dat")
        self.board = Board(self.data)
        self.logic = Logic(self.data)
        # Then we need start game

    def start_cmd(self):
        self.logic.start(self.board, self.data)

    def get_possible_turns(self, color):
        possible_turns = self.logic.generate_all_possible_turns(self.board, color)

        turns = defaultdict(list)

        for end_pos in possible_turns:
            for start_pos in possible_turns[end_pos]:
                turns[start_pos].append(end_pos)

        return turns

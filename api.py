from board import Board
from gamelogic import Logic
from gamelogic import Turn
from io_functions import Data


from collections import defaultdict


class Api:
    def __init__(self, difficulty, threads):
        # Here we need to init Field and Game logic
        self.data = Data("data.dat")
        self.board = Board(self.data)
        self.logic = Logic(self.data, threads)
        difficulty = 2
        self.difficulty = difficulty
        print("difficulty:", difficulty)
        print("threads:   ", threads)
        # Then we need start game

    def start_cmd(self):
        self.logic.start(self.board, self.data, self.difficulty)

    def get_possible_turns(self, color):
        possible_turns = self.logic.generate_all_possible_turns(self.board, color)

        turns = defaultdict(list)

        for end_pos in possible_turns:
            for start_pos in possible_turns[end_pos]:
                turns[start_pos].append(end_pos)

        return turns

    def get_field(self, pos):
        if self.board.check_pos(pos):
            return self.board.get_map(pos)

        return -1

    def set_field(self, pos, value):
        if self.board.check_pos(pos):
            return self.board.set_map(pos, value)

        return -1

    def do_turn(self, start, end):
        return self.board.do_turn(Turn(start, end, self.board.get_color_map(start)))

    def ai_turn(self, color, turn=True):
        now_turn = self.logic.root_ai_turn(self.board, color, self.difficulty)[0]

        if turn:
            self.board.do_turn(now_turn)

        return now_turn

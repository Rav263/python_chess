import io_functions
import check_turn as check
import math_functions as mf
import generate_turns as gt

from collections import defaultdict
from itertools import product


class Turn:
    def __init__(self, start_pos, end_pos, color):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color

    def print(self):
        print("start pos: ({0}, {1})".format(*self.start_pos))
        print("start pos: ({0}, {1})".format(*self.end_pos))


class Logic:
    def __init__(self):
        print("Init game logic class")

    def start(self, plate, data):
        color = 1

        while True:
            io_functions.print_field(plate.field, data)
            now_turn = io_functions.get_turn(self, color, plate)

            plate.do_turn(now_turn)

            color = 3 - color

            possible_turns = self.generate_all_possible_turns(plate, color)
            for now in possible_turns:
                print("{0}:".format(now), *possible_turns[now])
                now_turn = Turn(possible_turns[now][0], now, color)

            plate.do_turn(now_turn)

            color = 3 - color

    def check_turn(self, turn, plate):
        if (not plate.check_pos(turn.start_pos) or not plate.check_pos(turn.end_pos)):
            return False

        if (plate.get_color_map(turn.start_pos) != turn.color or
                plate.get_type_map(turn.start_pos) == plate.empty_map or
                plate.get_color_map(turn.end_pos) == turn.color):
            return False

        now_figure = plate.get_map(turn.start_pos)
        figure_type = plate.get_type_figure(now_figure)

        # pown
        if figure_type == plate.pown:
            return check.check_pown(turn, plate)

        coord_diff = mf.difference(turn.start_pos, turn.end_pos)

        # knight
        if figure_type == plate.knight:
            return check.check_knight(*coord_diff)

        # bishop
        if figure_type == plate.bishop:
            return check.check_bishop(turn, *coord_diff, plate)

        # rook
        if figure_type == plate.rook:
            return check.check_rook(turn, *coord_diff, plate)

        # king
        if figure_type == plate.king:
            if ((coord_diff[0] == 1 or coord_diff[0] == 0) and
                    (coord_diff[1] == 1 or coord_diff[1] == 0)):
                return True

        # queen
        if figure_type == plate.queen:
            return (check.check_bishop(turn, *coord_diff, plate) or
                    check.check_rook(turn, *coord_diff, plate))

        return False

    def generate_all_possible_turns(self, plate, color):
        possible_turns = defaultdict(list)
        # dict key = position of possible turn
        # dict value = list of positions where from this turn can be done

        for pos in product(range(plate.field_size), repeat=2):
            if plate.get_color_map(pos) == color:
                if plate.get_type_map(pos) == plate.pown:
                    gt.generate_turns_pown(pos, plate, possible_turns)

                if plate.get_type_map(pos) == plate.knight:
                    gt.generate_turns_knight(pos, plate, possible_turns, color)

        return possible_turns

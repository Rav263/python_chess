"""Module with functions to generate turns"""
from itertools import permutations
from itertools import islice
from itertools import count
from itertools import product


import math_functions as mf


def generate_turns_pawn(pos, board, possible_turns):
    """generate_turns_pawn(pos, board, possible_turns) -> None

    pos   -- figure position
    board -- class Board object
    possible_turns -- dict with key - end turn pos, value - list of start turn pos

    Adds all turns for pawn in dict
    """

    if board.get_color_map(pos) == board.white:
        if (pos[0] == board.white_pawn_start and
                board.get_type_map((pos[0] - 2, pos[1])) == board.empty_map):

            possible_turns[(pos[0] - 2, pos[1])].append(pos)

        if board.get_type_map((pos[0] - 1, pos[1])) == board.empty_map:
            possible_turns[(pos[0] - 1, pos[1])].append(pos)

        if (board.get_type_map((pos[0] - 1, pos[1] - 1)) > board.empty_map and
                board.get_color_map((pos[0] - 1, pos[1] - 1)) != board.white):
            possible_turns[(pos[0] - 1, pos[1] - 1)].append(pos)

        if (board.get_type_map((pos[0] - 1, pos[1] + 1)) > board.empty_map and
                board.get_color_map((pos[0] - 1, pos[1] + 1)) != board.white):
            possible_turns[(pos[0] - 1, pos[1] + 1)].append(pos)

    else:
        if (pos[0] == board.black_pawn_start and
                board.get_type_map((pos[0] + 2, pos[1])) == board.empty_map):

            possible_turns[(pos[0] + 2, pos[1])].append(pos)

        if board.get_type_map((pos[0] + 1, pos[1])) == board.empty_map:
            possible_turns[(pos[0] + 1, pos[1])].append(pos)

        if (board.get_type_map((pos[0] + 1, pos[1] - 1)) > board.empty_map and
                board.get_color_map((pos[0] + 1, pos[1] - 1)) != board.black):
            possible_turns[(pos[0] + 1, pos[1] - 1)].append(pos)

        if (board.get_type_map((pos[0] + 1, pos[1] + 1)) > board.empty_map and
                board.get_color_map((pos[0] + 1, pos[1] + 1)) != board.black):
            possible_turns[(pos[0] + 1, pos[1] + 1)].append(pos)


def generate_turns_knight(pos, board, possible_turns, color):
    """generate_turns_knight(pos, board, possible_turns, color) -> None

    pos             -- figure position
    board           -- class Board object
    possible_turns  -- dict with key - end turn pos, value - list of start turn pos
    color           -- figure color

    Adds all turns for pawn in dict
    """

    possible_diffs = [(x, y) for x, y in permutations([1, 2, -1, -2], 2) if abs(x) != abs(y)]

    for diff in possible_diffs:
        turn_end = mf.tuple_sum(pos, diff)
        if board.check_pos(turn_end) and board.get_color_map(turn_end) != color:
            possible_turns[turn_end].append(pos)


def generate_turns_rook(pos, board, possible_turns, color):
    """generate_turns_rook(pos, board, possible_turns, color) -> None

    pos             -- figure position
    board           -- class Board object
    possible_turns  -- dict with key - end turn pos, value - list of start turn pos
    color           -- figure color

    Adds all turns for pawn in dict
    """

    possible_diffs = [-1, 1]

    for diff in possible_diffs:
        for x_coord in islice(count(pos[0] + diff, diff), board.board_size):
            if not board.check_pos((x_coord, pos[1])):
                break
            if board.get_type_map((x_coord, pos[1])) != board.empty_map:
                if board.get_color_map((x_coord, pos[1])) != color:
                    possible_turns[(x_coord, pos[1])].append(pos)
                break
            possible_turns[(x_coord, pos[1])].append(pos)

        for y_coord in islice(count(pos[1] + diff, diff), board.board_size):
            if not board.check_pos((pos[0], y_coord)):
                break
            if board.get_type_map((pos[0], y_coord)) != board.empty_map:
                if board.get_color_map((pos[0], y_coord)) != color:
                    possible_turns[(pos[0], y_coord)].append(pos)
                break
            possible_turns[(pos[0], y_coord)].append(pos)


def generate_turns_bishop(pos, board, possible_turns, color):
    """generate_turns_bishop(pos, board, possible_turns, color) -> None

    pos             -- figure position
    board           -- class Board object
    possible_turns  -- dict with key - end turn pos, value - list of start turn pos
    color           -- figure color

    Adds all turns for pawn in dict
    """
    possible_diffs = product([-1, 1], repeat=2)

    for diff_x, diff_y in possible_diffs:
        for i in range(1, board.board_size):
            turn_end = mf.tuple_sum(pos, (diff_x * i, diff_y * i))

            if not board.check_pos(turn_end):
                break

            if board.get_type_map(turn_end) != board.empty_map:
                if board.get_color_map(turn_end) != color:
                    possible_turns[turn_end].append(pos)
                break

            possible_turns[turn_end].append(pos)


def generate_turns_queen(pos, board, possible_turns, color):
    """generate_turns_queen(pos, board, possible_turns, color) -> None

    pos             -- figure position
    board           -- class Board object
    possible_turns  -- dict with key - end turn pos, value - list of start turn pos
    color           -- figure color

    Adds all turns for pawn in dict
    """
    generate_turns_rook(pos, board, possible_turns, color)
    generate_turns_bishop(pos, board, possible_turns, color)


def generate_turns_king(pos, board, possible_turns, color):
    """generate_turns_king(pos, board, possible_turns, color) -> None

    pos             -- figure position
    board           -- class Board object
    possible_turns  -- dict with key - end turn pos, value - list of start turn pos
    color           -- figure color

    Adds all turns for pawn in dict
    """
    possible_diffs = product([1, -1, 0], repeat=2)

    for diff in possible_diffs:
        turn_end = mf.tuple_sum(pos, diff)

        if board.check_pos(turn_end) and board.get_color_map(turn_end) != color:
            possible_turns[turn_end].append(pos)

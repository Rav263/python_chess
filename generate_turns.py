import math_functions as mf

from itertools import permutations
from itertools import islice
from itertools import count
from itertools import product


def generate_turns_pown(pos, board, possible_turns):
    if board.get_color_map(pos) == board.white:
        if pos[0] == 6 and board.get_type_map((pos[0] - 2, pos[1])) == board.empty_map:
            possible_turns[(pos[0] - 2, pos[1])].append(pos)

        if board.get_type_map((pos[0] - 1, pos[1])) == board.empty_map:
            possible_turns[(pos[0] - 1, pos[1])].append(pos)
    else:
        if pos[0] == 1 and board.get_type_map((pos[0] + 2, pos[1])) == board.empty_map:
            possible_turns[(pos[0] + 2, pos[1])].append(pos)

        if board.get_type_map((pos[0] + 1, pos[1])) == board.empty_map:
            possible_turns[(pos[0] + 1, pos[1])].append(pos)


def generate_turns_knight(pos, board, possible_turns, color):
    possible_diffs = [(x, y) for x, y in permutations([1, 2, -1, -2], 2) if abs(x) != abs(y)]

    for diff in possible_diffs:
        turn_end = mf.sum(pos, diff)
        if board.check_pos(turn_end) and board.get_color_map(turn_end) != color:
            possible_turns[turn_end].append(pos)


def generate_turns_rook(pos, board, possible_turns, color):
    possible_diffs = [-1, 1]

    for diff in possible_diffs:
        for x in islice(count(pos[0] + diff, diff), board.board_size):
            if not board.check_pos((x, pos[1])):
                break
            if board.get_type_map((x, pos[1])) != board.empty_map:
                if board.get_color_map((x, pos[1])) != color:
                    possible_turns[(x, pos[1])].append(pos)
                break
            possible_turns[(x, pos[1])].append(pos)

        for y in islice(count(pos[1] + diff, diff), board.board_size):
            if not board.check_pos((pos[0], y)):
                break
            if board.get_type_map((pos[0], y)) != board.empty_map:
                if board.get_color_map((pos[0], y)) != color:
                    possible_turns[(pos[0], y)].append(pos)
                break
            possible_turns[(pos[0], y)].append(pos)


def generate_turns_bishop(pos, board, possible_turns, color):
    possible_diffs = product([-1, 1], repeat=2)

    for diff_x, diff_y in possible_diffs:
        for i in range(1, board.board_size):
            turn_end = mf.sum(pos, (diff_x * i, diff_y * i))

            if not board.check_pos(turn_end):
                break

            if board.get_type_map(turn_end) != board.empty_map:
                if board.get_color_map(turn_end) != color:
                    possible_turns[turn_end].append(pos)
                break

            possible_turns[turn_end].append(pos)


def generate_turns_queen(pos, board, possible_turns, color):
    generate_turns_rook(pos, board, possible_turns, color)
    generate_turns_bishop(pos, board, possible_turns, color)


def generate_turns_king(pos, board, possible_turns, color):
    possible_diffs = product([1, -1, 0], repeat=2)

    for diff in possible_diffs:
        turn_end = mf.sum(pos, diff)

        if board.check_pos(turn_end) and board.get_color_map(turn_end) != color:
            possible_turns[turn_end].append(pos)

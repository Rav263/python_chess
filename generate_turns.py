import math_functions as mf

from itertools import permutations


def generate_turns_pown(pos, plate, possible_turns):
    if plate.get_color_map(pos) == plate.white:
        if pos[0] == 6 and plate.get_type_map((pos[0] - 2, pos[1])) == plate.empty_map:
            possible_turns[(pos[0] - 2, pos[1])].append(pos)

        if plate.get_type_map((pos[0] - 1, pos[1])) == plate.empty_map:
            possible_turns[(pos[0] - 1, pos[1])].append(pos)
    else:
        if pos[0] == 1 and plate.get_type_map((pos[0] + 2, pos[1])) == plate.empty_map:
            possible_turns[(pos[0] + 2, pos[1])].append(pos)

        if plate.get_type_map((pos[0] + 1, pos[1])) == plate.empty_map:
            possible_turns[(pos[0] + 1, pos[1])].append(pos)


def generate_turns_knight(pos, plate, possible_turns, color):
    possible_diffs = [(x, y) for x, y in permutations([1, 2, -1, -2], 2) if abs(x) != abs(y)]

    for diff in possible_diffs:
        turn_end = mf.sum(pos, diff)
        if plate.check_pos(turn_end) and plate.get_color_map(turn_end) != color:
            possible_turns[turn_end].append(pos)

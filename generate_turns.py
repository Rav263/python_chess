"""Module with functions to generate turns"""
# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches

from itertools import permutations
from itertools import islice
from itertools import count
from itertools import product
from collections import defaultdict


import math_functions as mf


def transform_turns_dict(possible_turns):
    """transform_turns_dict(possible_turns) -> defaultdict"""
    turns = defaultdict(list)

    for end_pos in possible_turns:
        for start_pos in possible_turns[end_pos]:
            turns[start_pos].append(end_pos)

    return turns


def remove_not_important_turns(turns, important_start_positions):
    """remove_not_important_turns(turns, important_start_positions) -> defaultdict"""
    important_turns = defaultdict(list)

    for start_position in important_start_positions:
        important_turns[start_position] = turns[start_position]

    return important_turns


def normalize_tuple(tuple_1):
    """normalize_tuple(tuple_1) -> tuple

    returns normalized tuple
    """
    if tuple_1[0] != 0:
        return ((tuple_1[0] // abs(tuple_1[0]), tuple_1[1] // abs(tuple_1[0])), abs(tuple_1[0]))
    return ((tuple_1[0] // abs(tuple_1[1]), tuple_1[1] // abs(tuple_1[1])), abs(tuple_1[1]))


def remove_not_possible_turns(board, king_pos, turns, opponent_turns):
    """remove_not_possible_turns(board, king_pos, turns, opponent_turns) -> defaultdict(list)"""
    if king_pos not in opponent_turns:
        return turns

    start_positions = opponent_turns[king_pos]
    opponent_start_turns = transform_turns_dict(opponent_turns)
    start_turns = transform_turns_dict(turns)

    important_turns = remove_not_important_turns(opponent_start_turns, start_positions)

    possible_turns = defaultdict(list)

    for end_turn in start_turns[king_pos]:
        if end_turn not in opponent_turns:
            possible_turns[end_turn].append(king_pos)

    if len(important_turns) == 1:
        positions_for_block = positions_for_turns_block(board, [*important_turns], king_pos)

        for pos_for_block in positions_for_block:
            if pos_for_block in turns:
                for start_pos in turns[pos_for_block]:
                    if start_pos not in opponent_turns:
                        possible_turns[pos_for_block].append(start_pos)
                    else:
                        for opp_start_pos in opponent_start_turns[start_pos]:
                            if check_king_on_fire(board, opp_start_pos, king_pos, start_pos):
                                possible_turns[pos_for_block].append(start_pos)

    return possible_turns


def check_diff(board, diff, start_map_type):
    """check_diff(board, diff, start_map_type) -> bool

    returns True if diff is possible for this figure type
    """
    if start_map_type == board.queen:
        return abs(diff[0]) == abs(diff[1]) or 0 in diff

    if start_map_type == board.bishop:
        return abs(diff[0]) == abs(diff[1])

    if start_map_type == board.rook:
        return 0 in diff

    return False


def check_king_on_fire(board, start_pos, king_pos, now_figure_pos):
    """check_king_on_fire(board, start_pos, king_pos) -> bool

    returns True if king on fire
    """
    start_map_type = board.get_type_map(start_pos)

    if start_map_type in (board.queen, board.rook, board.bishop):
        diff = mf.difference(king_pos, start_pos)

        if not check_diff(board, diff, start_map_type):
            return False

        norm_diff, rang = normalize_tuple(diff)

        for i in range(rang):
            now_pos = mf.tuple_sum(start_pos, mf.mul(norm_diff, i))
            if now_pos == now_figure_pos:
                continue
            if board.get_type_map(now_pos) != board.empty_map:
                return False
        return True
    return False


def positions_for_turns_block(board, list_of_start_pos, king_pos):
    """positions_for_turns_block(board, list_of_start_pos, king_pos) -> list

    returns list of turns for blocking
    """
    start_pos = list_of_start_pos[0]

    positions_for_block = list()

    start_map_type = board.get_type_map(start_pos)

    if start_map_type in (board.queen, board.rook, board.bishop):
        diff = mf.difference(king_pos, start_pos)
        norm_diff, rang = normalize_tuple(diff)

        for i in range(rang):
            positions_for_block.append(mf.tuple_sum(start_pos, mf.mul(norm_diff, i)))

    elif start_map_type in (board.pawn, board.knight):
        positions_for_block.append(start_pos)

    return positions_for_block


def generate_turns_pawn(pos, board, possible_turns, turns_for_king):
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

        if board.get_type_map((pos[0] - 1, pos[1] - 1)) > board.empty_map:
            if board.get_color_map((pos[0] - 1, pos[1] - 1)) != board.white:
                possible_turns[(pos[0] - 1, pos[1] - 1)].append(pos)
            else:
                turns_for_king[(pos[0] - 1, pos[1] - 1)].append(pos)

        if board.get_type_map((pos[0] - 1, pos[1] + 1)) > board.empty_map:
            if board.get_color_map((pos[0] - 1, pos[1] + 1)) != board.white:
                possible_turns[(pos[0] - 1, pos[1] + 1)].append(pos)
            else:
                turns_for_king[(pos[0] - 1, pos[1] + 1)].append(pos)

    else:
        if (pos[0] == board.black_pawn_start and
                board.get_type_map((pos[0] + 2, pos[1])) == board.empty_map):

            possible_turns[(pos[0] + 2, pos[1])].append(pos)

        if board.get_type_map((pos[0] + 1, pos[1])) == board.empty_map:
            possible_turns[(pos[0] + 1, pos[1])].append(pos)

        if board.get_type_map((pos[0] + 1, pos[1] - 1)) > board.empty_map:
            if board.get_color_map((pos[0] + 1, pos[1] - 1)) != board.black:
                possible_turns[(pos[0] + 1, pos[1] - 1)].append(pos)
            else:
                turns_for_king[(pos[0] + 1, pos[1] - 1)].append(pos)

        if board.get_type_map((pos[0] + 1, pos[1] + 1)) > board.empty_map:
            if board.get_color_map((pos[0] + 1, pos[1] + 1)) != board.black:
                possible_turns[(pos[0] + 1, pos[1] + 1)].append(pos)
            else:
                turns_for_king[(pos[0] + 1, pos[1] + 1)].append(pos)


def generate_turns_knight(pos, board, possible_turns, color, turns_for_king):
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
        if board.check_pos(turn_end):
            if board.get_color_map(turn_end) != color:
                possible_turns[turn_end].append(pos)
            else:
                turns_for_king[turn_end].append(pos)


def generate_turns_rook(pos, board, possible_turns, color, turns_for_king):
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
                else:
                    turns_for_king[(x_coord, pos[1])].append(pos)
                break
            possible_turns[(x_coord, pos[1])].append(pos)

        for y_coord in islice(count(pos[1] + diff, diff), board.board_size):
            if not board.check_pos((pos[0], y_coord)):
                break
            if board.get_type_map((pos[0], y_coord)) != board.empty_map:
                if board.get_color_map((pos[0], y_coord)) != color:
                    possible_turns[(pos[0], y_coord)].append(pos)
                else:
                    turns_for_king[(pos[0], y_coord)].append(pos)
                break
            possible_turns[(pos[0], y_coord)].append(pos)


def generate_turns_bishop(pos, board, possible_turns, color, turns_for_king):
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
                else:
                    turns_for_king[turn_end].append(pos)
                break

            possible_turns[turn_end].append(pos)


def generate_turns_queen(pos, board, possible_turns, color, turns_for_king):
    """generate_turns_queen(pos, board, possible_turns, color) -> None

    pos             -- figure position
    board           -- class Board object
    possible_turns  -- dict with key - end turn pos, value - list of start turn pos
    color           -- figure color

    Adds all turns for pawn in dict
    """
    generate_turns_rook(pos, board, possible_turns, color, turns_for_king)
    generate_turns_bishop(pos, board, possible_turns, color, turns_for_king)


def generate_turns_king(pos, board, possible_turns, color, opponent_turns, opponent_turns_for_king):
    """generate_turns_king(pos, board, possible_turns, color) -> None

    pos             -- figure position
    board           -- class Board object
    possible_turns  -- dict with key - end turn pos, value - list of start turn pos
    color           -- figure color
    opponent_turns  -- opponent possible turns

    Adds all turns for pawn in dict
    """
    start_opponent_turns = transform_turns_dict(opponent_turns_for_king)

    possible_diffs = product([1, -1, 0], repeat=2)

    for diff in possible_diffs:
        turn_end = mf.tuple_sum(pos, diff)

        if (board.check_pos(turn_end) and board.get_color_map(turn_end) != color and
                turn_end not in opponent_turns and turn_end not in start_opponent_turns):
            possible_turns[turn_end].append(pos)

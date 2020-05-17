"""Module with functions to generate turns"""
# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
# pylint: disable=too-many-locals

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


def process_pos(board, turn_end, color, fig_pos, tmp_list, possible_turns,
                bad_figs, good_figs, beating_figures):
    """process_pos(...) -> (bool, fig_pos)"""
    if not board.check_pos(turn_end):
        return (True, fig_pos)

    if board.get_type_map(turn_end) != board.empty_map:
        if board.get_color_map(turn_end) != color and fig_pos == (-1, -1):
            return (True, fig_pos)
        if board.get_color_map(turn_end) != color and fig_pos != (-1, -1):
            tmp_list.append(turn_end)
            if board.get_type_map(turn_end) in good_figs:
                beating_figures.append(turn_end)
                if board.get_type_map(fig_pos) in good_figs:
                    possible_turns[fig_pos].extend(tmp_list)
                else:
                    bad_figs.append(fig_pos)
            return (True, fig_pos)
        if fig_pos == (-1, -1):
            fig_pos = turn_end
        else:
            return (True, fig_pos)
    else:
        tmp_list.append(turn_end)

    return (False, fig_pos)


def check_king_protected(board, king_pos, color, turns):
    """checks"""

    possible_turns = defaultdict(list)
    bad_figures = list()
    beating_figures = list()

    # check for roook and queen
    possible_diffs = [-1, 1]

    for diff in possible_diffs:
        tmp_list = list()
        fig_pos = (-1, -1)
        for x_coord in islice(count(king_pos[0] + diff, diff), board.board_size):
            turn_end = (x_coord, king_pos[1])
            flag, fig_pos = process_pos(board, turn_end, color, fig_pos, tmp_list, possible_turns,
                                        bad_figures, (board.rook, board.queen), beating_figures)
            if flag:
                break

        tmp_list = list()
        fig_pos = (-1, -1)

        for y_coord in islice(count(king_pos[1] + diff, diff), board.board_size):
            turn_end = (king_pos[0], y_coord)
            flag, fig_pos = process_pos(board, turn_end, color, fig_pos, tmp_list, possible_turns,
                                        bad_figures, (board.rook, board.queen), beating_figures)
            if flag:
                break
    # check foor bishop and queen
    possible_diffs = product([-1, 1], repeat=2)

    for diff_x, diff_y in possible_diffs:
        tmp_list = list()
        fig_pos = (-1, -1)
        for i in range(1, board.board_size):
            turn_end = mf.tuple_sum(king_pos, (diff_x * i, diff_y * i))
            flag, fig_pos = process_pos(board, turn_end, color, fig_pos, tmp_list, possible_turns,
                                        bad_figures, (board.bishop, board.queen), beating_figures)
            if flag:
                break

    # check for pawn
    for start_pos in bad_figures:
        if board.get_type_map(start_pos) == board.pawn:
            counter = 0
            for end_pos in turns[start_pos]:
                if end_pos in beating_figures:
                    if counter == 1:
                        bad_figures.append(start_pos)
                        possible_turns.pop(start_pos)
                        break
                    counter += 1
                    bad_figures.remove(start_pos)
                    possible_turns[start_pos].append(end_pos)

    return (possible_turns, bad_figures)


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


def remove_not_possible_turns(board, king_pos, color, turns, opponent_turns):
    """remove_not_possible_turns(board, king_pos, turns, opponent_turns) -> defaultdict(list)"""
    start_turns = transform_turns_dict(turns)
    good_turns, bad_figures = check_king_protected(board, king_pos, color, start_turns)

    for start_turn in good_turns:
        start_turns[start_turn] = good_turns[start_turn]

    for start_turn in bad_figures:
        start_turns.pop(start_turn)

    turns = transform_turns_dict(start_turns)
    if king_pos not in opponent_turns:
        return turns

    start_positions = opponent_turns[king_pos]
    opponent_start_turns = transform_turns_dict(opponent_turns)

    important_turns = remove_not_important_turns(opponent_start_turns, start_positions)

    possible_turns = defaultdict(list)

    for end_turn in start_turns[king_pos]:
        if end_turn not in opponent_turns:
            possible_turns[end_turn].append(king_pos)

    positions_for_block = positions_for_turns_block(board, [*important_turns], king_pos)

    for pos_for_block in positions_for_block:
        if pos_for_block in turns:
            for start_pos in turns[pos_for_block]:
                if start_pos not in opponent_turns or pos_for_block in opponent_turns[start_pos]:
                    possible_turns[pos_for_block].append(start_pos)
                else:
                    for opp_start_pos in opponent_start_turns[start_pos]:
                        if check_king_on_fire(board, opp_start_pos, king_pos, start_pos):
                            print("WTF")
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


def add_pawn_transformation(start_pos, end_pos, possible_turns, color):
    possible_turns[end_pos].append((start_pos[0], start_pos[1], color * 10 + 2))
    possible_turns[end_pos].append((start_pos[0], start_pos[1], color * 10 + 3))
    possible_turns[end_pos].append((start_pos[0], start_pos[1], color * 10 + 4))
    possible_turns[end_pos].append((start_pos[0], start_pos[1], color * 10 + 6))


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
            if not pos[0] - 1:
                add_pawn_transformation(pos, (pos[0] - 1, pos[1]), possible_turns, board.white)
            else:
                possible_turns[(pos[0] - 1, pos[1])].append(pos)

        if board.get_type_map((pos[0] - 1, pos[1] - 1)) > board.empty_map:
            if board.get_color_map((pos[0] - 1, pos[1] - 1)) != board.white:
                if not pos[0] - 1:
                    add_pawn_transformation(pos, (pos[0] - 1, pos[1] - 1),
                                            possible_turns, board.white)
                else:
                    possible_turns[(pos[0] - 1, pos[1] - 1)].append(pos)
            else:
                turns_for_king[(pos[0] - 1, pos[1] - 1)].append(pos)

        if board.get_type_map((pos[0] - 1, pos[1] + 1)) > board.empty_map:
            if board.get_color_map((pos[0] - 1, pos[1] + 1)) != board.white:
                if not pos[0] - 1:
                    add_pawn_transformation(pos, (pos[0] - 1, pos[1] + 1),
                                            possible_turns, board.white)
                else:
                    possible_turns[(pos[0] - 1, pos[1] + 1)].append(pos)
            else:
                turns_for_king[(pos[0] - 1, pos[1] + 1)].append(pos)

    else:
        if (pos[0] == board.black_pawn_start and
                board.get_type_map((pos[0] + 2, pos[1])) == board.empty_map):

            possible_turns[(pos[0] + 2, pos[1])].append(pos)

        if board.get_type_map((pos[0] + 1, pos[1])) == board.empty_map:
            if pos[0] + 1 == board.board_size - 1:
                add_pawn_transformation(pos, (pos[0] + 1, pos[1]), possible_turns, board.black)
            else:
                possible_turns[(pos[0] + 1, pos[1])].append(pos)

        if board.get_type_map((pos[0] + 1, pos[1] - 1)) > board.empty_map:
            if board.get_color_map((pos[0] + 1, pos[1] - 1)) != board.black:
                if pos[0] + 1 == board.board_size - 1:
                    add_pawn_transformation(pos, (pos[0] + 1, pos[1] - 1),
                                            possible_turns, board.black)
                else:
                    possible_turns[(pos[0] + 1, pos[1] - 1)].append(pos)
            else:
                turns_for_king[(pos[0] + 1, pos[1] - 1)].append(pos)

        if board.get_type_map((pos[0] + 1, pos[1] + 1)) > board.empty_map:
            if board.get_color_map((pos[0] + 1, pos[1] + 1)) != board.black:
                if pos[0] + 1 == board.board_size - 1:
                    add_pawn_transformation(pos, (pos[0] + 1, pos[1] + 1),
                                            possible_turns, board.black)
                else:
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
                turn_end not in opponent_turns):
            if turn_end in start_opponent_turns:
                for now_pos in start_opponent_turns[turn_end]:
                    if now_pos in opponent_turns:
                        break
                else:
                    possible_turns[turn_end].append(pos)
            else:
                possible_turns[turn_end].append(pos)

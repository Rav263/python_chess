"""Module with functions to generate turns"""
# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
# pylint: disable=too-many-locals
# pylint: disable=unused-argument
# pylint: disable=inconsistent-return-statements

from itertools import permutations
from itertools import islice
from itertools import count
from itertools import product
from collections import defaultdict


import PythonChess.math_functions as mf


def transform_turns_dict(possible_turns):
    """Make possible turns dictionary

    :param possible_turns: possible turns
    :type possible_turns:
    :return: possible turns dictionary
    :rtype: dict()
    """
    turns = defaultdict(list)

    for end_pos in possible_turns:
        for start_pos in possible_turns[end_pos]:
            turns[start_pos].append(end_pos)

    return turns


def process_pos(board, turn_end, color, fig_pos, tmp_list, possible_turns,
                bad_figs, good_figs, beating_figures, figs):
    """
    Process positions from king

    :param board: game board
    :type board: class Board
    :param turn_end: position to process
    :type turn_end: (int, int)
    :param color: color
    :type color: int
    :param fig_pos: figure position
    :type fig_pos: (int, int)
    :param tmp_list: list of positions
    :type tmp_list: list((int, int))
    :param possible_turns: possible turns
    :type possible_turns: dict(tuple: {dict(tuple: {list()})})
    :param bad_figs: bad figures, that can't block check
    :type bad_figs: list
    :param good_figs: good figures for check
    :type good_figs: list
    :param beating_figures: beating figures
    :type beating_figures: list
    :param figs: figures
    :type figs: list
    :return: break flag + figure position
    :rtype: (bool, (int, int))
    """
    if not board.check_pos(turn_end):
        return (True, fig_pos)

    if board.get_type_map(turn_end) != board.empty_map:
        if board.get_color_map(turn_end) != color and board.get_type_map(turn_end) in good_figs:
            figs.append(turn_end)
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
    """Checks if king can be beaten

    :param board: board object
    :type board: class board object
    :param king_pos: king position
    :type king_pos: (int, int)
    :param color: color
    :type color: int
    :param turns: possible turns
    :type turns: dict(tuple: {dict(tuple: {list()})})
    :return: possible turns, bad figures, figures in check
    :rtype: tuple
    """

    possible_turns = defaultdict(list)
    bad_figures = list()
    beating_figures = list()
    figs = list()

    # check for roook and queen
    possible_diffs = [-1, 1]

    for diff in possible_diffs:
        tmp_list = list()
        fig_pos = (-1, -1)
        for x_coord in islice(count(king_pos[0] + diff, diff), board.board_size):
            turn_end = (x_coord, king_pos[1])
            flag, fig_pos = process_pos(board, turn_end, color, fig_pos,
                                        tmp_list, possible_turns,
                                        bad_figures, (board.rook, board.queen),
                                        beating_figures, figs)
            if flag:
                break
        tmp_list = list()
        fig_pos = (-1, -1)

        for y_coord in islice(count(king_pos[1] + diff, diff), board.board_size):
            turn_end = (king_pos[0], y_coord)
            flag, fig_pos = process_pos(board, turn_end, color, fig_pos,
                                        tmp_list, possible_turns,
                                        bad_figures, (board.rook, board.queen),
                                        beating_figures, figs)
            if flag:
                break
    # check foor bishop and queen
    possible_diffs = product([-1, 1], repeat=2)

    for diff_x, diff_y in possible_diffs:
        tmp_list = list()
        fig_pos = (-1, -1)
        for i in range(1, board.board_size):
            turn_end = mf.tuple_sum(king_pos, (diff_x * i, diff_y * i))
            flag, fig_pos = process_pos(board, turn_end, color, fig_pos,
                                        tmp_list, possible_turns,
                                        bad_figures, (board.bishop, board.queen),
                                        beating_figures, figs)
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

    return (possible_turns, bad_figures, figs)


def remove_not_important_turns(turns, important_start_positions):
    """Leaves only important start position in possible turns

    :param turns: possible turns
    :type turns: list(class Turn object)
    :param important_start_positions: positions that are to be left
    :type important_start_positions: list((int, int))
    :return: important start position
    :rtype: dict(tuple: {dict(tuple: {list()})})
    """
    important_turns = defaultdict(list)

    for start_position in important_start_positions:
        important_turns[start_position] = turns[start_position]

    return important_turns


def normalize_tuple(tuple_1):
    """Normalizes tuple

    :param tuple_1: tuple to normalize
    :type tuple_1: (int, int)
    :return: normalized tuple
    :rtype: (int, int)
    """
    if tuple_1[0] != 0:
        return ((tuple_1[0] // abs(tuple_1[0]), tuple_1[1] // abs(tuple_1[0])), abs(tuple_1[0]))
    return ((tuple_1[0] // abs(tuple_1[1]), tuple_1[1] // abs(tuple_1[1])), abs(tuple_1[1]))


def remove_not_possible_turns(board, king_pos, color, turns, opponent_turns, turns_for_king):
    """Removes impossinle turns

    :param board: board object
    :type board: class board object
    :param king_pos: king position
    :type king_pos: (int, int)
    :param color: color
    :type color: int
    :param turns: [description]
    :type turns: [type]
    :param opponent_turns: [description]
    :type opponent_turns: [type]
    :return: possible turns
    :rtype: list(class Turn object)
    """
    start_turns = transform_turns_dict(turns)
    good_turns, bad_figures, figs = check_king_protected(board, king_pos, color, start_turns)

    bad_positions = list()
    for now_fig in figs:
        if board.get_type_map(now_fig) in (board.rook, board.queen):
            if now_fig[0] == king_pos[0]:
                if (king_pos[0], king_pos[1] + 1) != now_fig:
                    bad_positions.append((king_pos[0], king_pos[1] + 1))
                if (king_pos[0], king_pos[1] - 1) != now_fig:
                    bad_positions.append((king_pos[0], king_pos[1] - 1))
            elif now_fig[1] == king_pos[1]:
                if (king_pos[0] + 1, king_pos[1]) != now_fig:
                    bad_positions.append((king_pos[0] + 1, king_pos[1]))
                if (king_pos[0] - 1, king_pos[1]) != now_fig:
                    bad_positions.append((king_pos[0] - 1, king_pos[1]))
        if board.get_type_map(now_fig) in (board.bishop, board.queen):
            now = normalize_tuple(mf.difference(king_pos, now_fig))[0]
            bad_positions.append(mf.tuple_sum(king_pos, now))
    for start_turn in good_turns:
        start_turns[start_turn] = good_turns[start_turn]

    for start_turn in bad_figures:
        if start_turn in start_turns:
            start_turns.pop(start_turn)

    start_positions = opponent_turns[king_pos]
    opponent_start_turns = transform_turns_dict(opponent_turns)

    important_turns = remove_not_important_turns(opponent_start_turns, start_positions)

    possible_turns = defaultdict(list)
    for end_turn in start_turns[king_pos]:
        if end_turn not in bad_positions:
            if end_turn not in opponent_turns:
                possible_turns[end_turn].append(king_pos)
            elif end_turn not in turns_for_king:
                for start_pos in opponent_turns:
                    if board.get_type_map(start_pos) != board.pawn:
                        break
                else:
                    possible_turns[end_turn].append(king_pos)

    if king_pos not in opponent_turns or len(opponent_turns[king_pos]) == 0:
        pos_start_turns = transform_turns_dict(possible_turns)
        start_turns[king_pos] = pos_start_turns[king_pos]
        turns = transform_turns_dict(start_turns)
        return turns

    positions_for_block = positions_for_turns_block(board, [*important_turns], king_pos)
    for pos_for_block in positions_for_block:
        if pos_for_block in turns:
            for start_pos in turns[pos_for_block]:
                if board.get_type_map(start_pos) != board.king:
                    possible_turns[pos_for_block].append(start_pos)

    return possible_turns


def check_diff(board, diff, start_map_type):
    """check_diff(board, diff, start_map_type) -> bool

    :param board: board object
    :type board: class board object
    :param diff: [description]
    :type diff: [type]
    :param start_map_type: [description]
    :type start_map_type: [type]
    :return: True if diff is possible for this figure type
    :rtype: bool
    """
    if start_map_type == board.queen:
        return abs(diff[0]) == abs(diff[1]) or 0 in diff

    if start_map_type == board.bishop:
        return abs(diff[0]) == abs(diff[1])

    if start_map_type == board.rook:
        return 0 in diff

    return False


def check_king_on_fire(board, start_pos, king_pos, now_figure_pos):
    """Checks if king is under attack

    :param board: board object
    :type board: class board object
    :param start_pos: [description]
    :type start_pos: (int, int)
    :param king_pos: king position
    :type king_pos: (int, int)
    :param now_figure_pos: [description]
    :type now_figure_pos: (int, int)
    :return: if king is on fire
    :rtype: bool
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
    """Get positions of blocking figures

    :param board: board object
    :type board: class board object
    :param list_of_start_pos: list of starting positions
    :type list_of_start_pos: list((int, int))
    :param king_pos: king position
    :type king_pos: (int, int)
    :return: list of turns for blocking
    :rtype: list((int, int))
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
    """Pawn transformation

    :param start_pos: pawn start position
    :type start_pos: (int, int)
    :param end_pos: pawn end position
    :type end_pos: (int, int)
    :param possible_turns: possible turns
    :type possible_turns: [type]
    :param color: pawn color
    :type color: int
    """
    possible_turns[end_pos].append((start_pos[0], start_pos[1], color * 10 + 2))
    possible_turns[end_pos].append((start_pos[0], start_pos[1], color * 10 + 3))
    possible_turns[end_pos].append((start_pos[0], start_pos[1], color * 10 + 4))
    possible_turns[end_pos].append((start_pos[0], start_pos[1], color * 10 + 6))


def check_de_passant(board, possible_turns, last_turn, color):
    """Check if pawn can take another en passant

    :param board: board object
    :type board: class board object
    :param possible_turns: possible turns
    :type possible_turns: [type]
    :param last_turn: previous turn
    :type last_turn: (int, int)
    :param color: pawn color
    :type color: int
    :return: none if en passent is impossible
    :rtype: none
    """
    if board.get_type_map(last_turn.end_pos) != board.pawn:
        return None

    if abs(last_turn.start_pos[0] - last_turn.end_pos[0]) != 2:
        return None

    pos_1 = (last_turn.end_pos[0], last_turn.end_pos[1] - 1)
    pos_2 = (last_turn.end_pos[0], last_turn.end_pos[1] + 1)

    color_diff = -1 if (color == 1 and not board.flipped) else 1

    if board.get_type_map(pos_1) == board.pawn and board.get_color_map(pos_1) == color:
        possible_turns[(pos_1[0] + color_diff, pos_1[1] + 1, True)].append(pos_1)

    if board.get_type_map(pos_2) == board.pawn and board.get_color_map(pos_2) == color:
        possible_turns[(pos_2[0] + color_diff, pos_2[1] - 1, True)].append(pos_2)
    return None


def generate_turns_pawn(pos, board, possible_turns, color, turns_for_king):
    """ Adds all turns for pawn in dict

    :param pos: figure position
    :type pos: (int, int)
    :param board: board object
    :type board: class board object
    :param possible_turns: pawn possible turns, dict with key - end turn pos,
    value - list of start turn pos
    :type possible_turns: dict(...)
    :param color: pawn color
    :type color: int
    :param turns_for_king: kings possible turns
    :type turns_for_king: dict(...)
    """
    diff = -1
    if (color == 2 and not board.flipped) or (color == 1 and board.flipped):
        diff = 1
    if (pos[0] == board.pawn_start[diff] and
            board.get_type_map((pos[0] + 2 * diff, pos[1])) == board.empty_map and
            board.get_type_map((pos[0] + diff, pos[1])) == board.empty_map):

        # turns_for_king[(pos[0] + 2 * diff, pos[1])].append(pos)
        possible_turns[(pos[0] + 2 * diff, pos[1])].append(pos)

    if board.get_type_map((pos[0] + diff, pos[1])) == board.empty_map:
        if pos[0] + diff in (board.board_size - 1, 0):
            add_pawn_transformation(pos, (pos[0] + diff, pos[1]), possible_turns, color)
        else:
            possible_turns[(pos[0] + diff, pos[1])].append(pos)
        # turns_for_king[(pos[0] + diff, pos[1])].append(pos)
    diffs = [-1, 1]
    for x_diff in diffs:
        if board.get_type_map((pos[0] + diff, pos[1] + x_diff)) > board.empty_map:
            if board.get_color_map((pos[0] + diff, pos[1] + x_diff)) != color:
                if pos[0] + diff in (board.board_size - 1, 0):
                    add_pawn_transformation(pos, (pos[0] + diff, pos[1] + x_diff),
                                            possible_turns, color)
                else:
                    possible_turns[(pos[0] + diff, pos[1] + x_diff)].append(pos)
            else:
                turns_for_king[(pos[0] + diff, pos[1] + x_diff)].append(pos)
        else:
            turns_for_king[(pos[0] + diff, pos[1] + x_diff)].append(pos)


def generate_turns_knight(pos, board, possible_turns, color, turns_for_king):
    """ Adds all turns for knight in dict

    :param pos: figure position
    :type pos: (int, int)
    :param board: board object
    :type board: class board object
    :param possible_turns: kinght possible turns, dict with key - end turn pos,
    value - list of start turn pos
    :type possible_turns: dict(...)
    :param color: knight color
    :type color: int
    :param turns_for_king: kings possible turns
    :type turns_for_king: dict(...)
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
    """ Adds all turns for rook in dict


    :param pos: figure position
    :type pos: (int, int)
    :param board: board object
    :type board: class board object
    :param possible_turns: rook possible turns, dict with key - end turn pos,
    value - list of start turn pos
    :type possible_turns: dict(...)
    :param color: rook color
    :type color: int
    :param turns_for_king: kings possible turns
    :type turns_for_king: dict(...)
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
    """ Adds all turns for bishop in dict

    :param pos: figure position
    :type pos: (int, int)
    :param board: board object
    :type board: class board object
    :param possible_turns: bishop possible turns, dict with key - end turn pos,
    value - list of start turn pos
    :type possible_turns: dict(...)
    :param color: bishop color
    :type color: int
    :param turns_for_king: kings possible turns
    :type turns_for_king: dict(...)
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
    """ Adds all turns for queen in dict


    :param pos: figure position
    :type pos: (int, int)
    :param board: board object
    :type board: class board object
    :param possible_turns: queen possible turns, dict with key - end turn pos,
    value - list of start turn pos
    :type possible_turns: dict(...)
    :param color: queen color
    :type color: int
    :param turns_for_king: kings possible turns
    :type turns_for_king: dict(...)
    """
    generate_turns_rook(pos, board, possible_turns, color, turns_for_king)
    generate_turns_bishop(pos, board, possible_turns, color, turns_for_king)


def generate_turns_king(pos, board, possible_turns, color, opponent_turns, opponent_turns_for_king):
    """ Adds all turns for king in dict

    :param pos: figure position
    :type pos: (int, int)
    :param board: board object
    :type board: class board object
    :param possible_turns: queen possible turns, dict with key - end turn pos,
    value - list of start turn pos
    :type possible_turns: dict(...)
    :param color: queen color
    :type color: int
    :param turns_for_king: kings possible turns
    :type turns_for_king: dict(...)
    """

    possible_diffs = product([1, -1, 0], repeat=2)

    for diff in possible_diffs:
        turn_end = mf.tuple_sum(pos, diff)
        if (board.check_pos(turn_end) and board.get_color_map(turn_end) != color):
            if turn_end not in opponent_turns_for_king:
                possible_turns[turn_end].append(pos)

    # check castling

    diff = 7
    if color == board.white and board.flipped:
        diff = 0
    if color == board.black and not board.flipped:
        diff = 0

    if (pos[0] != diff and color == board.white) or (pos[0] != diff and color == board.black):
        return None

    if board.castling[color]:
        return None
    if pos in opponent_turns:
        return None

    left_rook, right_rook = (pos[0], 0), (pos[0], 7)

    positions = [1, 2, 3]
    if board.flipped:
        positions = [1, 2]

    if not board.king_movement[color] and not board.rook_movement[color][0]:
        if (board.get_type_map(left_rook) == board.rook and
                board.get_color_map(left_rook) == color):
            for x_coord in positions:
                if board.get_type_map((pos[0], x_coord)) != board.empty_map:
                    break
                if (pos[0], x_coord) in opponent_turns:
                    break
            else:
                if board.flipped:
                    possible_turns[(pos[0], 1)].append((*pos, (pos[0], 0), (pos[0], 2)))
                else:
                    possible_turns[(pos[0], 2)].append((*pos, (pos[0], 0), (pos[0], 3)))

    positions = [5, 6]
    if board.flipped:
        positions = [4, 5, 6]

    if not board.king_movement[color] and not board.rook_movement[color][1]:
        if (board.get_type_map(right_rook) == board.rook and
                board.get_color_map(right_rook) == color):

            for x_coord in positions:
                if board.get_type_map((pos[0], x_coord)) != board.empty_map:
                    break
                if (pos[0], x_coord) in opponent_turns:
                    break
            else:
                if board.flipped:
                    possible_turns[(pos[0], 5)].append((*pos, (pos[0], 7), (pos[0], 4)))
                else:
                    possible_turns[(pos[0], 6)].append((*pos, (pos[0], 7), (pos[0], 5)))

    return None

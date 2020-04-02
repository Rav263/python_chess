import math_functions as mf


def check_pown(turn, plate):
    if turn.color == 1:
        if turn.end_pos[1] == turn.start_pos[1] and plate.get_map(turn.end_pos) == 0:
            tmp = turn.start_pos[0] - turn.end_pos[0]
            if tmp == 1 or (tmp == 2 and turn.start_pos[0] == 6):
                if plate.get_type_map(turn.end_pos) == plate.empty_map:
                    return True
    else:
        if turn.end_pos[1] == turn.start_pos[1]:
            tmp = turn.end_pos[0] - turn.start_pos[0]
            if tmp == 1 or (tmp == 2 and turn.start_pos[0] == 1):
                if plate.get_type_map(turn.end_pos) == plate.empty_map:
                    return True

    return False


def check_knight(coord_diff_x, coord_diff_y):
    if abs(coord_diff_x) == 1 and abs(coord_diff_y) == 2:
        return True

    if abs(coord_diff_x) == 2 and abs(coord_diff_y) == 1:
        return True

    return False


def check_bishop(turn, coord_diff_x, coord_diff_y, plate):
    if abs(coord_diff_x) == abs(coord_diff_y):
        sign_x = -1 if coord_diff_x < 0 else 1
        sign_y = -sign_x if coord_diff_x == -coord_diff_y else sign_x

        for i in range(sign_x, coord_diff_x, sign_x):
            if (plate.get_type_map(mf.sum(turn.end_pos, (i, i * sign_x * sign_y))) !=
                    plate.empty_map):
                return False
        return True

    return False


def check_rook(turn, coord_diff_x, coord_diff_y, plate):
    if (coord_diff_x == 0 and coord_diff_y != 0) or (coord_diff_x != 0 and coord_diff_y == 0):
        sign_x = -1 if coord_diff_x < 0 else 1 if coord_diff_x != 0 else 0
        sign_y = -1 if coord_diff_y < 0 else 1 if coord_diff_y != 0 else 0

        for i in range(1, coord_diff_x + coord_diff_y):
            if (plate.get_type_map(mf.sum(turn.end_pos, (i * sign_x, i * sign_y))) !=
                    plate.empty_map):
                return False

        return True

    return False

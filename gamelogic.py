import io_functions


def difference(tuple_1, tuple_2):
    return (tuple_1[0] - tuple_2[0], tuple_1[1] - tuple_2[1])


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
            return self.check_pown(turn, plate)

        coord_diff = difference(turn.start_pos, turn.end_pos)

        # knight
        if figure_type == plate.knight:
            return self.check_knight(*coord_diff)

        # bishop
        if figure_type == plate.bishop:
            return self.check_bishop(turn, *coord_diff, plate)

        # rook
        if figure_type == plate.rook:
            return self.check_rook(turn, *coord_diff, plate)

        # king
        if figure_type == plate.king:
            if ((coord_diff[0] == 1 or coord_diff[0] == 0) and
                    (coord_diff[1] == 1 or coord_diff[1] == 0)):
                return True

        # queen
        if figure_type == plate.queen:
            return (self.check_bishop(turn, *coord_diff, plate) or
                    self.check_rook(turn, *coord_diff, plate))

        return False

    def check_pown(self, turn, plate):
        if turn.color == 1:
            if turn.end_pos[1] == turn.start_pos[1] and plate.get_map(turn.end_pos) == 0:
                tmp = turn.start_pos[0] - turn.end_pos[0]
                if tmp == 1 or (tmp == 2 and turn.start_pos[0] == 6):
                    return True
        else:
            if turn.end_pos[1] == turn.start_pos[1]:
                tmp = turn.end_pos[0] - turn.start_pos[0]
                if tmp == 1 or (tmp == 2 and turn.start_pos[0] == 1):
                    return True
        return False

    def check_knigth(self, coord_diff_x, coord_diff_y):
        if abs(coord_diff_x) == 1 and abs(coord_diff_y) == 2:
            return True

        if abs(coord_diff_x) == 2 and abs(coord_diff_y) == 1:
            return True

        return False

    def check_bishop(self, turn, coord_diff_x, coord_diff_y, plate):
        if abs(coord_diff_x) == abs(coord_diff_y):
            sign_x = -1 if coord_diff_x < 0 else 1
            sign_y = -sign_x if coord_diff_x == -coord_diff_y else sign_x

            for i in range(sign_x, coord_diff_x, sign_x):
                if plate.get_type_map(turn.end_pos + (i, i * sign_x * sign_y)) != plate.empty_map:
                    return False
            return True

        return False

    def check_rook(self, turn, coord_diff_x, coord_diff_y, plate):
        if (coord_diff_x == 0 and coord_diff_y != 0) or (coord_diff_x != 0 and coord_diff_y == 0):
            sign_x = -1 if coord_diff_x < 0 else 1 if coord_diff_x != 0 else 0
            sign_y = -1 if coord_diff_y < 0 else 1 if coord_diff_y != 0 else 0

            for i in range(1, coord_diff_x + coord_diff_y):
                if plate.get_type_map(turn.end_pos + (i * sign_x, i * sign_y)) != plate.empty_map:
                    return False

            return True

        return False

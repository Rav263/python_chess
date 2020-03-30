import io_functions


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

        mod_1 = turn.start_pos[0] - turn.end_pos[0]
        mod_2 = turn.start_pos[1] - turn.end_pos[1]

        # knight
        if figure_type == plate.knight:
            return self.check_knight(mod_1, mod_2)

        # bishop
        if figure_type == plate.bishop:
            print("BISHOP")
            return self.check_bishop(turn, mod_1, mod_2, plate)

        # rook
        if figure_type == plate.rook:
            return self.check_rook(turn, mod_1, mod_2, plate)

        # king
        if figure_type == plate.king:
            if (mod_1 == 1 or mod_1 == 0) and (mod_2 == 1 or mod_2 == 0):
                return True

        # queen
        if figure_type == plate.queen:
            return (self.check_bishop(turn, mod_1, mod_2, plate) or
                    self.check_rook(turn, mod_1, mod_2, plate))

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

    def check_knigth(self, mod_1, mod_2):
        if abs(mod_1) == 1 and abs(mod_2) == 2:
            return True

        if abs(mod_1) == 2 and abs(mod_2) == 1:
            return True

        return False

    def check_bishop(self, turn, mod_1, mod_2, plate):
        if abs(mod_1) == abs(mod_2):
            sign_1 = -1 if mod_1 < 0 else 1
            sign_2 = -sign_1 if mod_1 == -mod_2 else sign_1

            for i in range(sign_1, mod_1, sign_1):
                if plate.get_type_map(turn.end_pos + (i, i * sign_1 * sign_2)) != plate.empty_map:
                    return False
            return True

        return False

    def check_rook(self, turn, mod_1, mod_2, plate):
        if (mod_1 == 0 and mod_2 != 0) or (mod_1 != 0 and mod_2 == 0):
            sign_1 = -1 if mod_1 < 0 else 1 if mod_1 != 0 else 0
            sign_2 = -1 if mod_2 < 0 else 1 if mod_2 != 0 else 0

            for i in range(1, mod_1 + mod_2):
                if plate.get_type_map(turn.end_pos + (i * sign_1, i * sign_2)) != plate.empty_map:
                    return False

            return True

        return False

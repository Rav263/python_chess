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
        if (turn.start_pos[0] > 7 or turn.start_pos[0] < 0 or
                turn.start_pos[1] > 7 or turn.start_pos[1] < 0 or
                turn.end_pos[0] > 7 or turn.end_pos[0] < 0 or
                turn.end_pos[1] > 7 or turn.end_pos[1] < 0):
            return False

        if (plate.get_map(turn.start_pos) // 10 != turn.color or
                plate.get_map(turn.start_pos) == 0 or
                plate.get_map(turn.end_pos) // 10 == turn.color):
            return False

        now_figure = plate.get_map(turn.start_pos)

        # pown
        if now_figure == 10 or now_figure == 20:
            return self.check_pown(turn, plate)

        mod_1 = turn.start_pos[0] - turn.end_pos[0]
        mod_2 = turn.start_pos[1] - turn.end_pos[1]

        # hourse
        if now_figure == 11 or now_figure == 21:
            return self.check_knight(mod_1, mod_2)

        # elephant
        if now_figure == 12 or now_figure == 22:
            return self.check_bishop(turn, mod_1, mod_2, plate)

        # rook
        if now_figure == 13 or now_figure == 23:
            return self.check_rook(turn, mod_1, mod_2, plate)

        # king
        if now_figure == 14 or now_figure == 24:
            if (mod_1 == 1 or mod_1 == 0) and (mod_2 == 1 or mod_2 == 0):
                return True

        # queen
        if now_figure == 15 or now_figure == 25:
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
                if plate.get_map((turn.end_pos[0] + i, turn.end_pos[1] + i * sign_1 * sign_2)) != 0:
                    return False
            return True

        return False

    def check_rook(self, turn, mod_1, mod_2, plate):
        if (mod_1 == 0 and mod_2 != 0) or (mod_1 != 0 and mod_2 == 0):
            sign_1 = -1 if mod_1 < 0 else 1 if mod_1 != 0 else 0
            sign_2 = -1 if mod_2 < 0 else 1 if mod_2 != 0 else 0

            for i in range(1, mod_1 + mod_2):
                if plate.get_map((turn.end_pos[0] + i * sign_1, turn.end_pos[1] + i * sign_2)) != 0:
                    return False

            return True

        return False

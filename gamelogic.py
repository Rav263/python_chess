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

    def check_turn(self, turn, plane):
        if (turn.start_pos > 7 or turn.start_pos < 0 or
                turn.end_pos > 7 or turn.end_pos < 0):
            return False

        if (plane.get_map(turn.start_pos) // 10 != turn.color or
                plane.get_map(turn.start_pos) == 0):
            return False

        now_figure = plane.get_map(turn.start_pos)

        # white pawn
        if now_figure == 10:
            if turn.end_pos[1] == turn.start_pos[1]:
                tmp = turn.start_pos[0] - turn.end_pos[0]
                if tmp == 1 or (tmp == 2 and turn.start_pos[0] == 6):
                    return True

        # black pawn
        if now_figure == 20:
            if turn.end_pos[1] == turn.start_pos[1]:
                tmp = turn.end_pos[0] - turn.start_pos[0]
                if tmp == 1 or (tmp == 2 and turn.start_pos[0] == 1):
                    return True

        mod_1 = abs(turn.start_pos[0] - turn.end_pos[0])
        mod_2 = abs(turn.start_pos[1] - turn.end_pos[1])

        # hourse
        if now_figure == 11 or now_figure == 21:
            if mod_1 == 1 and mod_2 == 2:
                return True

            if mod_1 == 2 and mod_2 == 1:
                return True

        # elephant
        if now_figure == 12 or now_figure == 22:
            if mod_1 == mod_2:
                return True

        # rook
        if now_figure == 13 or now_figure == 23:
            if mod_1 == 0 and mod_2 != 0:
                return True
            if mod_1 != 0 and mod_2 == 0:
                return True

        # king
        if now_figure == 14 or now_figure == 24:
            if (mod_1 == 1 or mod_1 == 0) and (mod_2 == 1 or mod_2 == 0):
                return True

        # queen
        if now_figure == 15 or now_figure == 25:
            if mod_1 == mod_2 or (mod_1 == 0 and mod_2 != 0) or (mod_1 != 0 and mod_2 == 0):
                return True

        return False

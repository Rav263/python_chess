class Turn:
    def __init__(self, start_pos, end_pos, color):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color


class Logic:
    def __init__(self):
        print("Init game logic class")

    def check_turn(self, turn, plane):
        if (plane.get_map(turn.start_pos) // 10 != turn.color or
                plane.get_map(turn.start_pos) == 0):
            return False
        if plane.get_map(turn.start_pos) == 10:
            return True
        return True

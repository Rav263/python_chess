class Field:
    empty_map = 0
    pown = 1
    knight = 2
    bishop = 3
    rook = 4
    king = 5
    queen = 6

    def __init__(self, data):
        print("Init field class")
        self.load_field(data)
        self.field_size = data.field_size

    def do_turn(self, turn):
        print("Doing turn from {0} to {1}".format(turn.start_pos, turn.end_pos))

        # move figure
        self.set_map(turn.end_pos, self.get_map(turn.start_pos))
        self.set_map(turn.start_pos, 0)

    def load_field(self, data):
        self.field = data.data["FIELD"]

    def get_map(self, pos):
        return self.field[pos[0]][pos[1]]

    def get_color_figure(self, figure):
        return figure // 10

    def get_type_figure(self, figure):
        return figure % 10

    def get_type_map(self, pos):
        return self.get_map(pos) % 10

    def get_color_map(self, pos):
        return self.get_map(pos) // 10

    def check_pos(self, pos):
        if pos[0] >= self.field_size or pos[0] < 0:
            return False

        if pos[1] >= self.field_size or pos[1] < 0:
            return False

        return True

    def set_map(self, pos, value):
        self.field[pos[0]][pos[1]] = value

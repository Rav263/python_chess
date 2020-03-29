class Field:
    def __init__(self, data):
        print("Init field class")
        self.load_field(data)

    def do_turn(self, turn):
        print("Doing turn from {0} to {1}".format(turn.start_pos, turn.end_pos))

        # move figure
        self.set_map(turn.end_pos, self.get_map(turn.start_pos))
        self.set_map(turn.start_pos, 0)

    def load_field(self, data):
        self.field = data.data["FIELD"]

    def get_map(self, pos):
        return self.field[pos[0]][pos[1]]

    def set_map(self, pos, value):
        self.field[pos[0]][pos[1]] = value

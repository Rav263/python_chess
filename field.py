import io_functions

class Field:
    def __init__(self, data):
        print("Init field class")
        self.load_field(data)

    def do_turn(self, start_pos, end_pos):
        print("Doing turn from {0} to {1}".format(start_pos, end_pos))

        # move figure
        self.field[end_pos[0]][end_pos[1]] = self.field[start_pos[0]][start_pos[1]] 
        self.field[start_pos[0]][start_pos[1]] = 0 
    
    def load_field(self, data):
        self.field = data.data["FIELD"]  

"""Board class file"""
from itertools import product


class Board:
    """Board class for chess game"""
    empty_map = 0
    pawn = 1
    knight = 2
    bishop = 3
    rook = 4
    king = 5
    queen = 6
    white = 1
    black = 2
    white_pawn_start = 6
    black_pawn_start = 1

    def __init__(self, data, copy=None):
        if copy is None:
            print("Init board class")
            self.load_board(data)
            self.board_size = data.board_size
            self.data = data
        else:
            self.board = [line.copy() for line in copy.board]
            self.board_size = copy.board_size
            self.data = copy.data

    def do_turn(self, turn, fig=0):
        """do_turn(self, turn, fig) -> figure

        self -- class Board object
        turn -- class Turn object
        fig  -- figure to set on start pos

        returns figure from turn end position
        """
        # print("Doing turn from {0} to {1}".format(turn.start_pos, turn.end_pos))
        # move figure

        tmp = self.set_map(turn.end_pos, self.get_map(turn.start_pos))
        self.set_map(turn.start_pos, fig)
        return tmp

    def copy(self):
        """copy(self) -> copyed Board object"""
        return Board(None, self)

    def load_board(self, data):
        """load_board(self, data) -> set self.board object from data file"""
        self.board = data.data["BOARD"]

    def get_map(self, pos):
        """get_map(self, pos) -> figure

        self -- class Board object
        pos  -- position

        returns figure on position
        """
        return self.board[pos[0]][pos[1]]

    def get_type_map(self, pos):
        """get_type_map(self, pos) -> Int(type of figure on this position

        self -- class Board object
        pos  -- position


        returns figure type on this position or -1 if position not on board
        """

        if not self.check_pos(pos):
            return -1
        return self.get_map(pos) % 10

    def get_color_map(self, pos):
        """get_color_map(self, pos) -> Int(figure color)

        self -- class Board object
        pos  -- position

        returns figure color on this position or -1 if position not on board
        """

        if not self.check_pos(pos):
            return -1
        return self.get_map(pos) // 10

    def check_pos(self, pos):
        """chech_pos(self, pos) -> bool"""
        if pos[0] >= self.board_size or pos[0] < 0:
            return False

        if pos[1] >= self.board_size or pos[1] < 0:
            return False

        return True

    def set_map(self, pos, value):
        """set_map(self, pos, value) -> Int(figure on position)"""
        tmp = self.board[pos[0]][pos[1]]
        self.board[pos[0]][pos[1]] = value
        return tmp

    def calculate_board_cost(self, figures_cost):
        """calculate_board_cost(self, color, figures_cost) - Int(sum of figures)"""
        summ = 0  # figures_cost["sum"]
        for pos in product(range(self.board_size), repeat=2):
            summ += figures_cost[self.get_map(pos)]

        return summ

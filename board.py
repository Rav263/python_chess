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

    king_movement = ["костыль", False, False]
    rook_movement = ["костыль", [False, False], [False, False]]
    castling = ["костыль", False, False]

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

    def __str__(self):
        return (f"king flags: {self.king_movement}\n" +
                f"rook flags: {self.rook_movement}\n" +
                f"castling flags: {self.castling}")

    def rotate_board(self):
        self.white_pawn_start = 7 - self.white_pawn_start
        self.black_pawn_start = 7 - self.black_pawn_start
        for now in range(4):
            self.board[7 - now], self.board[now] = self.board[now], self.board[7 - now]

    def get_king_pos(self, color):
        """get_king_pos(self, color) -> tuple

        Returns king position with the same color
        """

        for pos in product(range(self.board_size), repeat=2):
            if self.get_type_map(pos) == self.king and self.get_color_map(pos) == color:
                return pos
        return (-1, -1)

    def set_movement_flags(self, start_pos):
        color = self.get_color_map(start_pos)
        fig_type = self.get_type_map(start_pos)

        flags = dict()

        if fig_type == self.king and not self.king_movement[color]:
            self.king_movement[color] = True
            flags["king"] = color
        if fig_type == self.rook:
            if start_pos[1] == 0 and not self.rook_movement[color][0]:
                self.rook_movement[color][0] = True
                flags["left rook"] = color
            if start_pos[1] == self.board_size - 1 and not self.rook_movement[color][1]:
                self.rook_movement[color][1] = True
                flags["right rook"] = color

        return flags

    def un_set_movement_flags(self, flags):
        for flag in flags:
            if flag == "king":
                self.king_movement[flags[flag]] = False
            if flag == "left rook":
                self.rook_movement[flags[flag]][0] = False
            if flag == "right rook":
                self.rook_movement[flags[flag]][1] = False

    def do_turn(self, turn, fig=0):
        """do_turn(self, turn, fig) -> figure

        self -- class Board object
        turn -- class Turn object
        fig  -- figure to set on start pos

        returns figure from turn end position
        """
        # print("Doing turn from {0} to {1}".format(turn.start_pos, turn.end_pos))
        # move figure
        if turn.castling:
            self.castling[turn.color] = True
            tmp = self.set_map(turn.end_pos, self.get_map(turn.start_pos[:2]))
            self.set_map((turn.start_pos[0], turn.start_pos[1]), fig)
            self.set_map(turn.start_pos[3], self.get_map(turn.start_pos[2]))
            self.set_map(turn.start_pos[2], 0)
            flags = dict()
        elif turn.passant:
            diff = turn.end_pos[1] - turn.start_pos[1]
            tmp = self.set_map((turn.start_pos[0], turn.start_pos[1] + diff), 0)
            flags = self.set_movement_flags(turn.start_pos)
            self.set_map(turn.end_pos, self.get_map(turn.start_pos), pawn=turn.pawn)
            self.set_map(turn.start_pos, 0)
        else:
            flags = self.set_movement_flags(turn.start_pos)
            tmp = self.set_map(turn.end_pos, self.get_map(turn.start_pos), pawn=turn.pawn)
            self.set_map(turn.start_pos, fig)
        return (tmp, flags)

    def un_do_turn(self, turn, fig, flags):
        if turn.castling:
            self.castling[turn.color] = False
            self.set_map(turn.start_pos[:2], self.get_map(turn.end_pos))
            self.set_map(turn.end_pos, 0)
            self.set_map(turn.start_pos[2], self.get_map(turn.start_pos[3]))
            self.set_map(turn.start_pos[3], 0)
        elif turn.passant:
            self.un_set_movement_flags(flags)
            diff = turn.end_pos[1] - turn.start_pos[1]
            self.set_map((turn.start_pos[0], turn.start_pos[1] + diff), fig)
            self.set_map(turn.start_pos, self.get_map(turn.end_pos))
            self.set_map(turn.end_pos, 0)
        else:
            self.un_set_movement_flags(flags)
            self.set_map(turn.start_pos, self.get_map(turn.end_pos))
            if turn.pawn:
                self.set_map(turn.start_pos, self.pawn + 10*turn.color)
            self.set_map(turn.end_pos, fig)

    def copy(self):
        """copy(self) -> copyed Board object"""
        return Board(None, self)

    def load_board(self, data):
        """load_board(self, data) -> set self.board object from data file"""
        self.board = []
        for line in data.data["BOARD"]:
            new_line = [x for x in line]
            self.board.append(new_line)

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

    def set_map(self, pos, value, pawn=0):
        """set_map(self, pos, value) -> Int(figure on position)"""
        tmp = self.board[pos[0]][pos[1]]
        self.board[pos[0]][pos[1]] = pawn if pawn else value
        return tmp

    def generate_fen(self, fen_dict):
        fen = ""
        for index, now_line in enumerate(self.board):
            counter = 0
            for now_fig in now_line:
                if now_fig == 0:
                    counter += 1
                    continue
                if counter:
                    fen += str(counter)
                    counter = 0
                fen += fen_dict[now_fig]
            if counter:
                fen += str(counter)
            if index != self.board_size - 1:
                fen += "/"
        return fen

    def calculate_board_cost(self, figures_cost):
        """calculate_board_cost(self, color, figures_cost) - Int(sum of figures)"""
        summ = 0  # figures_cost["sum"]
        for pos in product(range(self.board_size), repeat=2):
            summ += figures_cost[self.get_map(pos)]

        return summ

        """
        fen = self.generate_fen(self.data.data["FEN"])

        return -float(subprocess.getoutput("./stockfish " + fen + " eval").split()[-3])
        """

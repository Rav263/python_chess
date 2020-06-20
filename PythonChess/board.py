"""Board class file"""
# pylint: disable=undefined-variable
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

    flipped = False

    pawn_start = ["костыль", 1, 6]

    king_movement = ["костыль", False, False]
    rook_movement = ["костыль", [False, False], [False, False]]
    castling = ["костыль", False, False]

    def __init__(self, data, copy=None):
        if copy is None:
            print(_("Init board class"))
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
        """Rotates board
        """
        self.flipped = not self.flipped
        tmp = list([0 for x in range(8)] for y in range(8))

        for pos in product(range(self.board_size), repeat=2):
            tmp[7 - pos[0]][7 - pos[1]] = self.get_map(pos)

        self.board = tmp

    def get_figures(self, flag=True):
        """return figures

        :param flag: flag to return tuple or dict, defaults to True
        :type flag: bool, optional
        :return: figures
        :rtype: tuple or dict
        """
        figures = ("костыль", {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}, {1: 0, 2: 0, 3: 0, 4: 0, 5: 0})

        for pos in product(range(self.board_size), repeat=2):
            now_type = self.get_type_map(pos)
            if now_type == self.queen:
                figures[self.get_color_map(pos)][5] += 1
                continue
            if now_type == self.empty_map:
                continue
            figures[self.get_color_map(pos)][now_type] += 1
        black_figs = list()
        white_figs = list()

        for now in figures[2]:
            black_figs.append((now, figures[2][now]))
        for now in figures[1]:
            white_figs.append((now, figures[1][now]))
        if flag:
            return ((*white_figs), (*black_figs))
        return figures

    def get_king_pos(self, color):
        """Returns king's position with the same color

        :param color: color
        :type color: int
        :return: king's position
        :rtype: (int, int)
        """

        for pos in product(range(self.board_size), repeat=2):
            if self.get_type_map(pos) == self.king and self.get_color_map(pos) == color:
                return pos
        return (-1, -1)

    def set_movement_flags(self, start_pos):
        """set castling flags depending start porition

        :param start_pos: start position
        :type start_pos: tuple
        :return: movement flags
        :rtype: dict
        """
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
        """set previous flags

        :param flags: previous flags
        :type flags: dict
        """
        for flag in flags:
            if flag == "king":
                self.king_movement[flags[flag]] = False
            if flag == "left rook":
                self.rook_movement[flags[flag]][0] = False
            if flag == "right rook":
                self.rook_movement[flags[flag]][1] = False

    def do_turn(self, turn, fig=0):
        """Returns figure from turn end position

        :param turn: current turn
        :type turn: class Turn
        :param fig: figure to set, defaults to 0
        :type fig: int, optional
        :return: figure + flags
        :rtype: (int, dict)
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
        """Undoes a turn

        :param turn: turn to undo
        :type turn: class Truen
        :param fig: figure type
        :type fig: int
        :param flags: flags
        :type flags: dict
        """
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
        """Copies a board

        :return: copyed Board
        :rtype: class Board object
        """
        return Board(None, self)

    def load_board(self, data):
        """Load positions from data file

        :param data: data file
        :type data: class Data object
        """
        self.board = []
        for line in data.data["BOARD"]:
            new_line = [*line]
            self.board.append(new_line)

    def get_map(self, pos):
        """Gets figure on position

        :param pos: coordinates
        :type pos: (int, int)
        :return: figure
        :rtype: int
        """
        return self.board[pos[0]][pos[1]]

    def get_type_map(self, pos):
        """Gets figure type on position

        :param pos: coordinates
        :type pos: (int, int)
        :return: figure type on this position or -1 if position not on board
        :rtype: int
        """
        if not self.check_pos(pos):
            return -1
        return self.get_map(pos) % 10

    def get_color_map(self, pos):
        """Gets figure color on position

        :param pos: coordinates
        :type pos: (int, int)
        :return: figure color on this position or -1 if position not on board
        :rtype: int
        """

        if not self.check_pos(pos):
            return -1
        return self.get_map(pos) // 10

    def check_pos(self, pos):
        """Checks if position is on board

        :param pos: position
        :type pos: (int, int)
        :return: False if pos is out of board True otherwise
        :rtype: bool
        """
        if pos[0] >= self.board_size or pos[0] < 0:
            return False

        if pos[1] >= self.board_size or pos[1] < 0:
            return False

        return True

    def set_map(self, pos, value, pawn=0):
        """set board cell

        :param pos: position
        :type pos: (int, int)
        :param value: figure
        :type value: int
        :param pawn: pawn promotion, defaults to 0
        :type pawn: int, optional
        :return: new value
        :rtype: int
        """

        tmp = self.board[pos[0]][pos[1]]
        self.board[pos[0]][pos[1]] = pawn if pawn else value
        return tmp

    def generate_fen(self, fen_dict):
        """generate fen board view

        :param fen_dict: dict of figures
        :type fen_dict: dict
        :return: fen board view
        :rtype: str
        """
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
        """Returns sum of figures on the board

        :param figures_cost: cost array
        :type figures_cost: dict
        :return: sum of figures
        :rtype: int
        """
        summ = 0  # figures_cost["sum"]
        for pos in product(range(self.board_size), repeat=2):
            summ += figures_cost[self.get_map(pos)]

        return summ

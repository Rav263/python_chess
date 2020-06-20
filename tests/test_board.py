from PythonChess.board import Board
from PythonChess.api import Api
from PythonChess.turns import Turn
import os
import sys
import gettext

gettext.install("locale", os.path.abspath(sys.argv[0]), names=("ngettext",))


class Test_Board:
    def setup(self):
        self.api = Api(2, 2, False, True)
        self.board = Board(self.api.data)

    def test_rotate_board(self):
        self.board.rotate_board()

        test_board = [
                [14, 12, 13, 15, 16, 13, 12, 14],
                [11, 11, 11, 11, 11, 11, 11, 11],
                [00, 00, 00, 00, 00, 00, 00, 00],
                [00, 00, 00, 00, 00, 00, 00, 00],
                [00, 00, 00, 00, 00, 00, 00, 00],
                [00, 00, 00, 00, 00, 00, 00, 00],
                [21, 21, 21, 21, 21, 21, 21, 21],
                [24, 22, 23, 25, 26, 23, 22, 24]]

        assert self.board.board == test_board
        self.board.rotate_board()

    def test_get_figures(self):
        first = ((1, 8), (2, 2), (3, 2), (4, 2), (5, 2), (1, 8), (2, 2), (3, 2), (4, 2), (5, 2)) 
        second = ({1: 8, 2: 2, 3: 2, 4: 2, 5: 2}, {1: 8, 2: 2, 3: 2, 4: 2, 5: 2})
        assert self.board.get_figures() == first
        assert self.board.get_figures(False)[1:] == second

    def test_get_king_pos(self):
        res = ((7, 4), (0, 4))
        assert self.board.get_king_pos(1) == res[0]
        assert self.board.get_king_pos(2) == res[1]

    def test_check_pos(self):
        assert not self.board.check_pos((-1, -1))
        assert not self.board.check_pos((8, 0))
        assert not self.board.check_pos((0, 8))
        assert self.board.check_pos((0, 0))

    def test_turn(self):
        turn = Turn((6, 4), (4, 4), 1)
        tmp, flags = self.board.do_turn(turn)
        assert tmp == 0
        assert flags == {}
        assert self.board.board == [[24, 22, 23, 26, 25, 23, 22, 24],
                                    [21, 21, 21, 21, 21, 21, 21, 21],
                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 11, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                    [11, 11, 11, 11, 0, 11, 11, 11],
                                    [14, 12, 13, 16, 15, 13, 12, 14]]
        self.board.un_do_turn(turn, tmp, flags)
        assert self.board.board == [[24, 22, 23, 26, 25, 23, 22, 24],
                                    [21, 21, 21, 21, 21, 21, 21, 21],
                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                    [11, 11, 11, 11, 11, 11, 11, 11],
                                    [14, 12, 13, 16, 15, 13, 12, 14]]

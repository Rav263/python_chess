from PythonChess.api import Api
import os
import sys
import gettext

gettext.install("locale", os.path.dirname(sys.argv[0]), names=("ngettext",))


class Test_Data:
    def setup(self):
        self.api = Api(2, 2, False, True)
        self.data = self.api.data

    def test_readed_figures(self):
        test_figs = {0: '..', 11: 'Pw', 12: 'Nw', 13: 'Bw',
                     14: 'Rw', 15: 'Kw', 16: 'Qw', 21: 'Pb',
                     22: 'Nb', 23: 'Bb', 24: 'Rb', 25: 'Kb', 26: 'Qb'}

        assert self.data.data["FIGURES"] == test_figs

    def test_readed_board(self):
        test_board = [[24, 22, 23, 26, 25, 23, 22, 24],
                      [21, 21, 21, 21, 21, 21, 21, 21],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [11, 11, 11, 11, 11, 11, 11, 11],
                      [14, 12, 13, 16, 15, 13, 12, 14]]

        assert self.data.data["BOARD"] == test_board

    def test_readed_figures_cost(self):
        test_costs = {0: 0.0, 11: -1.0, 12: -3.0, 13: -3.0,
                      14: -5.0, 15: -900.0, 16: -9.0, 21: 1.0,
                      22: 3.0, 23: 3.0, 24: 5.0, 25: 900.0, 26: 9.0, 'sum': 0.0}

        assert self.data.data["FIGURES_COST"] == test_costs

    def test_readed_board_size(self):
        board_size = 8

        assert self.data.board_size == board_size

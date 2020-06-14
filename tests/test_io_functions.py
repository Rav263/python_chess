import PythonChess.io_functions as io


class Test_Data:
    def setup(self):
        self.data = io.Data("./data.dat")

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
        test_costs = {0: 0.0, 11: -10.0, 12: -30.0, 13: -30.0,
                      14: -50.0, 15: -900.0, 16: -90.0, 21: 10.0,
                      22: 30.0, 23: 30.0, 24: 50.0, 25: 900.0, 26: 90.0, 'sum': 0.0}

        assert self.data.data["FIGURES_COST"] == test_costs

    def test_readed_board_size(self):
        board_size = 8

        assert self.data.board_size == board_size

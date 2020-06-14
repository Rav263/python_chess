from collections import defaultdict
from PythonChess.api import Api


class Test_Api:
    def setup(self):
        self.api = Api(2, 2, False)

    def test_get_possible_turn(self):
        start_white_turns = defaultdict(list, {(6, 0): [(4, 0), (5, 0)], (7, 1): [(5, 0), (5, 2)],
                                        (6, 2): [(5, 2), (4, 2)], (6, 1): [(4, 1), (5, 1)],
                                        (6, 3): [(4, 3), (5, 3)], (6, 4): [(4, 4), (5, 4)],
                                        (6, 5): [(4, 5), (5, 5)], (7, 6): [(5, 5), (5, 7)],
                                        (6, 7): [(5, 7), (4, 7)], (6, 6): [(4, 6), (5, 6)]})

        start_black_turns = defaultdict(list, {(0, 1): [(2, 2), (2, 0)], (1, 2): [(2, 2), (3, 2)],
                                        (1, 0): [(2, 0), (3, 0)], (0, 6): [(2, 7), (2, 5)],
                                        (1, 7): [(2, 7), (3, 7)], (1, 5): [(2, 5), (3, 5)],
                                        (1, 1): [(3, 1), (2, 1)], (1, 3): [(3, 3), (2, 3)],
                                        (1, 4): [(3, 4), (2, 4)], (1, 6): [(3, 6), (2, 6)]})

        assert (self.api.get_possible_turns(1) == start_white_turns and
                self.api.get_possible_turns(2) == start_black_turns)

    def test_get_field(self):
        figures = [14, 12, 13, 16, 15, 13, 12, 14,
                   24, 22, 23, 26, 25, 23, 22, 24,
                   00, 00, 00, 00, 00, 00, 00, 00,
                   -1, -1]
        maps = list()
        maps.extend([(7, x) for x in range(8)])
        maps.extend([(0, x) for x in range(8)])
        maps.extend([(4, x) for x in range(8)])
        maps.extend([(8, 7), (-1, 2)])

        now = True
        for index, mp in enumerate(maps):
            now = now and self.api.get_field(mp) == figures[index]

        assert now

    def test_set_field(self):
        mp = (0, 0)
        now = self.api.set_field(mp, 0) == 24
        now = now and self.api.set_field(mp, 14) == 0
        now = now and self.api.set_field((-1, -1), 0) == -1

        assert now

    def test_do_turn(self):
        start = (6, 4)
        end = (4, 4)

        flg = self.api.do_turn(start, end)
        now = self.api.get_field((4, 4)) == 11
        self.api.previous_turn()
        assert (not flg) and now

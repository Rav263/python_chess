from PythonChess import math_functions as mf


def test_difference():
    test = [((1, 1), (1, 1), (0, 0)),
            ((2, 2), (0, 0), (2, 2)),
            ((1, 5), (5, 1), (-4, 4))]
    for fir, sec, res in test:
        assert mf.difference(fir, sec) == res


def test_tuple_sum():
    test = [((1, 1), (1, 1), (2, 2)),
            ((2, 2), (0, 5), (2, 7)),
            ((1, 5), (5, 1), (6, 6))]
    for fir, sec, res in test:
        assert mf.tuple_sum(fir, sec) == res


def test_mul():
    test = [((1, 1), 2, (2, 2)),
            ((2, 2), -2, (-4, -4)),
            ((-1, 1), -3, (3, -3))]

    for fir, sec, res in test:
        assert mf.mul(fir, sec) == res

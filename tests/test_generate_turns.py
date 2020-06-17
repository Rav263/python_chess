import PythonChess.generate_turns as gt


def test_transform_turns_dict():
    start = {(1, 2): [(2, 3), (4, 2)], (4, 2): [(2, 3), (4, 5)]}
    end = {(4, 2): [(1, 2)], (2, 3): [(1, 2), (4, 2)], (4, 5): [(4, 2)]}

    assert gt.transform_turns_dict(start) == end

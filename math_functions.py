"""Math functions for tuple"""


def difference(tuple_1, tuple_2):
    """difference(tuple_1, tuple_2) -> tuple

    returns tuple difference
    """

    return (tuple_1[0] - tuple_2[0], tuple_1[1] - tuple_2[1])


def tuple_sum(tuple_1, tuple_2):
    """tuple_sum(tuple_1, tuple_2) -> tuple

    returns tuple sum
    """

    return (tuple_1[0] + tuple_2[0], tuple_1[1] + tuple_2[1])


def mul(tuple_1, num):
    """mul(tuple_1, num) -> tuple

    returns tuple mull with num
    """

    return (tuple_1[0] * num, tuple_1[1] * num)

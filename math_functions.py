"""Math functions for tuple"""


def difference(tuple_1, tuple_2):
    """Calculates tuple difference

    :param tuple_1: first tuple
    :type tuple_1: (int, int)
    :param tuple_2: second tuple
    :type tuple_2: (int, int)
    :return: tuple_1 - tuple_2
    :rtype: (int, int)
    """
    difference(tuple_1, tuple_2) -> tuple

    returns tuple difference
    

    return (tuple_1[0] - tuple_2[0], tuple_1[1] - tuple_2[1])


def tuple_sum(tuple_1, tuple_2):
    """Calculates tuple sum

    :param tuple_1: first tuple
    :type tuple_1: (int, int)
    :param tuple_2: second tuple
    :type tuple_2: (int, int)
    :return: tuple_1 + tuple_2
    :rtype: (int, int)
    """

    return (tuple_1[0] + tuple_2[0], tuple_1[1] + tuple_2[1])


def mul(tuple_1, num):
    """Calculates tuple multiplication

    :param tuple_1: first tuple
    :type tuple_1: (int, int)
    :param tuple_2: second tuple
    :type tuple_2: (int, int)
    :return: tuple_1 x tuple_2
    :rtype: (int, int)
    """

    return (tuple_1[0] * num, tuple_1[1] * num)

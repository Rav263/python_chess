"""Modeue for IO functions"""
# pylint: disable=undefined-variable
# pylint: disable=too-many-branches
import sys
import os
# pylint: disable=undefined-variable
# pylint: disable=unused-variable
# pylint: disable=no-else-break
# pylint: disable=too-many-branches
class Data:
    """Class Data for load config file and get info from it"""
    data = dict()

    def __init__(self, file_name):
        self.board_size = 8

        try:
            file = open(file_name, "r")
        except FileNotFoundError:
            print(os.path.abspath(os.getcwd()))
            print(_("ERROR:: data file not found"))
            sys.exit(1)

        for i in file:
            if len(i.strip()) == 0 or i.strip()[0] == '#':
                continue

            if i.strip() == "BOARD":
                tmp = []
                for j in range(self.board_size):
                    tmp_str = file.readline()
                    tmp.append([int(i) for i in tmp_str.strip().split()])
                self.data["BOARD"] = tmp

            if i.strip() == "BOARD_DEBUG":
                tmp = []
                for j in range(self.board_size):
                    tmp_str = file.readline()
                    tmp.append([self.data["FIGURES_DEBUG"][i] for i in tmp_str.strip().split()])
                self.data["BOARD"] = tmp

            if i.strip() == "FIGURES":
                tmp = dict()
                debug_tmp = dict()
                for j in range(13):
                    tmp_str = file.readline().split()
                    tmp[int(tmp_str[0])] = tmp_str[1]
                    debug_tmp[tmp_str[1]] = int(tmp_str[0])
                self.data["FIGURES"] = tmp
                self.data["FIGURES_DEBUG"] = debug_tmp
            if i.strip() == "FEN":
                tmp = dict()
                for j in range(13):
                    tmp_str = file.readline().split()
                    tmp[int(tmp_str[0])] = tmp_str[1]
                    debug_tmp[tmp_str[1]] = int(tmp_str[0])
                self.data["FEN"] = tmp
            if i.strip() == "BOARD_SIZE":
                self.board_size = int(file.readline().strip())

            if i.strip() == "FIGURES_COST":
                tmp = dict()
                summ = 0

                for j in range(13):
                    tmp_str = file.readline().split()
                    tmp[int(tmp_str[0])] = float(tmp_str[1])
                    summ += float(tmp_str[1])

                tmp["sum"] = summ / 2
                self.data["FIGURES_COST"] = tmp
        file.close()

    def get_figures_costs(self):
        """Geta figures cost

        :return: figures costs
        :rtype: dict()
        """
        return self.data["FIGURES_COST"]

    def get_board_size(self):
        """Gets board size

        :return: board size
        :rtype: int
        """
        return self.data["BOARD_SIZE"]


def print_board(board, data):
    """ Prints boards in console

    :param board: board object
    :type board: class board object
    :param data: data file
    :type data: class Data object
    """
    print()
    for i in range(data.board_size):
        print(data.board_size - i, end=" |")

        for now_fig in board[i]:
            print(data.data["FIGURES"][now_fig], end=" ")
        print()

    print("  ", end="")
    for i in range(data.board_size):
        print("---", end="")
    print()
    print("   ", end="")
    print(*[(chr(ord("a") + i) + " ") for i in range(data.board_size)])
    print()


def get_color():
    """Gets color

    :return: color
    :rtype: 1 for white 2 for black
    """
    while True:
        color = input(_("Please enter your color (white\\black): ")).strip().lower()
        if color in ("white", "black"):
            break
    return 1 if color == "white" else 2


def new_game():
    """Accept new game

    :return: y/n depending on whether a user wants a new game
    :rtype: bool
    """
    while True:
        game = input(_("Do you whant another game (y\\n):")).strip().lower()
        if game in ("y", "n"):
            break
        print("Please, try again")
    return game == "y"


def get_difficulty():
    """Gets game difficulty

    :return: difficulty
    :rtype: int
    """
    while True:
        diff = input(_("Please enter difficulty (2-4): "))
        if not diff.isnumeric():
            print(_("This is not num"))
            continue
        if int(diff) < 2 or int(diff) > 4:
            print(_("This is wrong difficulty"))
            continue
        break
    return int(diff)


def get_turn(color, api):
    """ Get turn from user

    :param color: color
    :type color: int
    :param api: API module
    :type api: class Api object
    :return: requested turn (start pos, end pos, figure)
    :rtype: ((int, int), (int, int), int)
    """
    possible_turns = api.get_possible_turns(color)

    if len(possible_turns) == 0:
        return ((-1, -1), (-1, -1), -1)

    while True:
        line = input(_("Please enter your turn: (e2e4)")).strip()
        if len(line) not in (4, 5):
            print(_("Wrong format"))
            continue
        if ord(line[0]) < ord("a") or ord(line[0]) > ord("h"):
            print(_("Wrong format"))
            continue
        if ord(line[2]) < ord("a") or ord(line[2]) > ord("h"):
            print(_("Wrong format"))
            continue
        if ord(line[1]) < ord("1") or ord(line[1]) > ord("8"):
            print(_("Wrong format"))
            continue
        if ord(line[3]) < ord("1") or ord(line[3]) > ord("8"):
            print(_("Wrong format"))
            continue

        start_pos = (api.board.board_size - int(line[1]), abs(ord(line[0]) - ord("a")))
        end_pos = (api.board.board_size - int(line[3]), abs(ord(line[2]) - ord("a")))

        fig_num = 0
        if len(line) == 5:
            figure = line[4]
            if figure == "Q":
                fig_num = api.board.queen
            elif figure == "K":
                fig_num = api.board.knight
            elif figure == "R":
                fig_num = api.board.rook
            elif figure == "B":
                fig_num = api.board.bishop
            else:
                print(_("Undefined promotion figure"))
                continue
        if start_pos in possible_turns:
            if end_pos in possible_turns[start_pos]:
                break
            print(_("Not possible turn"))
        else:
            print(_("Not possible turn"))
    return (start_pos, end_pos, fig_num)

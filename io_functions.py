"""Modeue for IO functions"""
import sys


import gamelogic


class Data:
    """Class Data for load config file and get info from it"""
    data = dict()

    def __init__(self, file_name):
        self.board_size = 8

        try:
            file = open(file_name, "r")
        except FileNotFoundError:
            print("ERROR:: data file not found")
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

            if i.strip() == "FIGURES":
                tmp = dict()
                for j in range(13):
                    tmp_str = file.readline().split()
                    tmp[int(tmp_str[0])] = tmp_str[1]
                self.data["FIGURES"] = tmp

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
        """get_figures_costs(self) -> dict"""
        return self.data["FIGURES_COST"]

    def get_board_size(self):
        """get_board_size(self) -> Int"""
        return self.data["BOARD_SIZE"]


def print_board(board, data):
    """print_board(board, data) -> None

    prints boards in console
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


def get_turn(logic, color, board):
    """get_turn(logic, color, board) -> Turn

    Get turn from user
    """
    possible_turns = logic.generate_all_possible_turns(board, color)

    while True:
        line = input("Please enter your turn: ").strip()
        if len(line) != 5:
            print("Wrong format")
            return get_turn(logic, color, board)

        start_pos = (board.board_size - int(line[1]), abs(ord(line[0]) - ord("a")))
        end_pos = (board.board_size - int(line[4]), abs(ord(line[3]) - ord("a")))

        now_turn = gamelogic.Turn(start_pos, end_pos, color)

        if end_pos in possible_turns and start_pos in possible_turns[end_pos]:
            break

        print("Wrong Turn, try again")

    return now_turn

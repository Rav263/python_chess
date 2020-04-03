import gamelogic


class Data:
    data = dict()

    def __init__(self, file_name):
        self.field_size = 8

        try:
            file = open(file_name, "r")
        except FileNotFoundError:
            print("ERROR:: data file not found")
            exit(1)

        for i in file:
            if len(i.strip()) == 0 or i.strip()[0] == '#':
                continue

            if i.strip() == "FIELD":
                tmp = []
                for j in range(self.field_size):
                    tmp_str = file.readline()
                    tmp.append([int(i) for i in tmp_str.strip().split()])
                self.data["FIELD"] = tmp

            if i.strip() == "FIGURES":
                tmp = dict()
                for j in range(13):
                    tmp_str = file.readline().split()
                    tmp[int(tmp_str[0])] = tmp_str[1]
                self.data["FIGURES"] = tmp

            if i.strip() == "FIELD_SIZE":
                self.field_size = int(file.readline().strip())

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
        return self.data["FIGURES_COST"]


def print_field(field, data):
    print()
    for i in range(data.field_size):
        print(data.field_size - i, end=" |")

        for now_fig in field[i]:
            print(data.data["FIGURES"][now_fig], end=" ")
        print()

    print("  ", end="")
    for i in range(data.field_size):
        print("---", end="")
    print()
    print("   ", end="")
    print(*[(chr(ord("a") + i) + " ") for i in range(data.field_size)])
    print()


def get_turn(logic, color, plane):
    line = input("Please enter your turn: ").strip()
    if len(line) != 5:
        print("Wrong format")
        return get_turn(logic, color, plane)

    start_pos = (plane.field_size - int(line[1]), abs(ord(line[0]) - ord("a")))
    end_pos = (plane.field_size - int(line[4]), abs(ord(line[3]) - ord("a")))

    now_turn = gamelogic.Turn(start_pos, end_pos, color)

    if not logic.check_turn(now_turn, plane):
        print("Wrong turn")
        return get_turn(logic, color, plane)

    return now_turn

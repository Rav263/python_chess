class Turn:
    """Turn class for store chess turn"""
    def __init__(self, start_pos, end_pos, color, pawn=0, castling=False, passant=False):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.pawn = pawn
        self.castling = castling
        self.passant = passant

    def print(self):
        """print(self) -> None: prints Turn information"""
        print("start pos: ({0}, {1})".format(*self.start_pos))
        print("end pos:   ({0}, {1})".format(*self.end_pos))

    def __str__(self):
        start_pos = chr(self.start_pos[1] + ord('a')) + str(8 - self.start_pos[0])
        end_pos = chr(self.end_pos[1] + ord('a')) + str(8 - self.end_pos[0])

        if self.pawn % 10 == 2:
            end_pos += "n"
        elif self.pawn % 10 == 3:
            end_pos += "b"
        elif self.pawn % 10 == 4:
            end_pos += "r"
        elif self.pawn % 10 == 6:
            end_pos += "q"

        return start_pos + end_pos
        """
        return ("start pos: ({0}, {1})\n".format(*self.start_pos) +
                "end pos:   ({0}, {1})\n".format(*self.end_pos) +
                f"color:      {self.color}")
        """
    def __eq__(self, second):
        return (self.start_pos == self.start_pos and self.end_pos == second.end_pos and
                self.color == second.color and self.pawn == second.pawn and
                self.castling == second.castling)

    def __repr__(self):
        start_pos = chr(self.start_pos[1] + ord('a')) + str(8 - self.start_pos[0])
        end_pos = chr(self.end_pos[1] + ord('a')) + str(8 - self.end_pos[0])

        if self.pawn % 10 == 2:
            end_pos += "n"
        elif self.pawn % 10 == 3:
            end_pos += "b"
        elif self.pawn % 10 == 4:
            end_pos += "r"
        elif self.pawn % 10 == 6:
            end_pos += "q"

        return start_pos + end_pos

    def __hash__(self):
        return hash((self.start_pos, self.end_pos, self.color, self.pawn, self.castling, self.passant))

class Node:
    def __init__(self):
        self.turn = None
        self.next_turns = dict()
        self.sorted_turns = list()
        self.win_rate = None

    def add_turn(self, turn, cost, node=None):
        self.next_turns[turn] = node
        self.sorted_turns.append((turn, cost))

    def sort_turns(self):
        if self.turn is None or self.turn.color == 2:
            self.sorted_turns = sorted(self.sorted_turns, key=lambda x: -sum(x[1][:2])/x[1][2])
        else:
            self.sorted_turns = sorted(self.sorted_turns, key=lambda x: -(x[1][2] - x[1][0])/x[1][2])

    def get_max_turn(self):
        return self.sorted_turns[0][0]


def build_tree(nodes, now_index, node, depth):
    turn, indexes, win_rate = nodes[now_index]

    if turn is not None:
        node.turn = Turn(turn[0], turn[1], depth % 2 + 1)

    node.win_rate = win_rate
    
    for index in indexes:
        now_node = Node()
        build_tree(nodes, index, now_node, depth + 1)
        node.add_turn(now_node.turn, now_node.win_rate, now_node)
    node.sort_turns()


def read_nodes():
    file_deb = open("./debuts.dat")
    nodes = eval(file_deb.readline())
    file_deb.close()

    root = Node()
    build_tree(nodes, 0, root, -1)

    return root

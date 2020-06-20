# pylint: disable=undefined-variable
# pylint: disable=line-too-long
# pylint: disable=eval-used
# pylint: disable=too-many-arguments
# pylint: disable=unnecessary-comprehension
# pylint: disable=import-error
from tqdm import tqdm
class Turn:
    """Turn class for store chess turn"""
    flipped = False

    def __init__(self, start_pos, end_pos, color, pawn=0, castling=False, passant=False):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.pawn = pawn
        self.castling = castling
        self.passant = passant

    def print(self):
        """Prints self"""
        print("start pos: ({0}, {1})".format(*self.start_pos))
        print("end pos:   ({0}, {1})".format(*self.end_pos))

    def __str__(self):
        """Turn self to str

        :return: string representation
        :rtype: str
        """
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

    def __eq__(self, second):
        """Checks turns for equalitu

        :param second: second turn
        :type second: class Turn object
        :return: True if equal
        :rtype: bool
        """
        return (self.start_pos == self.start_pos and self.end_pos == second.end_pos and
                self.color == second.color and self.pawn == second.pawn and
                self.castling == second.castling)

    def __repr__(self):
        """Returns str representation

        :return: str representation
        :rtype: str
        """
        return str(self)

    def __hash__(self):
        return hash((self.start_pos, self.end_pos,
                     self.color, self.pawn, self.castling, self.passant))

    def rotate(self):
        """Rotate turn on the board
        """
        self.flipped = not self.flipped
        self.start_pos = (7 - self.start_pos[0], 7 - self.start_pos[1])
        self.end_pos = (7 - self.end_pos[0], 7 - self.end_pos[1])


class Node:
    """Class node
    """
    def __init__(self):
        self.turn = None
        self.next_turns = dict()
        self.sorted_turns = list()
        self.win_rate = None

    def add_turn(self, turn, cost, node=None):
        """Add turn to Node

        :param turn: turn
        :type turn: class Turn object
        :param cost: turns cost
        :type cost: int
        :param node: new node, defaults to None
        :type node: class Node, optional
        """
        self.next_turns[turn] = node
        self.sorted_turns.append((turn, cost))

    def sort_turns(self):
        """Sorts turns
        """
        if self.turn is None or self.turn.color == 2:
            self.sorted_turns = sorted(self.sorted_turns, key=lambda x: -sum(x[1][:2])/x[1][2])
        else:
            self.sorted_turns = sorted(self.sorted_turns, key=lambda x: -(x[1][2] - x[1][0])/x[1][2])

    def get_max_turn(self):
        """Gets best turn

        :return: best turn
        :rtype: class Turn object
        """
        return self.sorted_turns[0][0]


def build_tree(nodes, now_index, node, depth):
    """Build tree for turn keping

    :param nodes: list of tree nodes
    :type nodes: list
    :param now_index: now node index
    :type now_index: int
    :param node: now node
    :type node: class Node
    :param depth: recursion depth
    :type depth: int
    """
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
    """Read debuts

    :return: list of nodes
    :rtype: list
    """
    print(_("Reading debuts, please wait (It can take from 15 sec to 1 min, depends your comuter):"))
    fil = open("./debuts.dat", "r")
    lines = [line for line in fil]
    fil.close()
    nodes = list()
    for line in tqdm(lines):
        nodes.extend(eval(line))

    root = Node()
    build_tree(nodes, 0, root, -1)

    return root

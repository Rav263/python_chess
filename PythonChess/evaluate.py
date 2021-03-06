"""Board position evaluation module"""
from itertools import product
# pylint: disable=eval-used
# pylint: disable=unused-variable
# pylint: disable=invalid-name
# pylint: disable=no-self-use

class Evaluate:
    """Evaluate class"""
    def __init__(self, data_file_name):
        data_file = open(data_file_name, "r")
        self.hash_table = dict()
        for line in data_file:
            if line.strip() == "FIGURE_PRICE_MG":
                self.figure_price_mg = eval(data_file.readline())

            if line.strip() == "PSQT_BONUS_MG":
                psqt_line = ""
                for i in range(5):
                    psqt_line += data_file.readline()
                self.psqt_price_mg = eval(psqt_line)

            if line.strip() == "PPSQT_BONUS_MG":
                psqt_line = ""
                for i in range(2):
                    psqt_line += data_file.readline()
                self.ppsqt_price_mg = eval(psqt_line)

            if line.strip() == "IMB_QO":
                self.imb_qo = eval(data_file.readline())

            if line.strip() == "IMB_QT":
                self.imb_qt = eval(data_file.readline())

            if line.strip() == "IMB_DICT":
                self.imb_dict = eval(data_file.readline())
        data_file.close()

    def hash_board(self, board):
        """Hash game board

        :param board: Board to hash
        :type board: class Board
        :return: board hash
        :rtype: int
        """
        hsh = 0
        for line in board.board:
            for now_fig in line:
                hsh <<= 5
                hsh += now_fig
        return hsh

    def evaluate_board_mg(self, board, color):
        """Board evaluation

        :param board: board object
        :type board: class board object
        :param color: color
        :type color: int
        :return: board evaluation
        :rtype: int
        """
        hsh = self.hash_board(board)
        imb_val = 0
        bishops = [0, 0, 0]
        value = 0

        if hsh in self.hash_table:
            value = self.hash_table[hsh]
            return value[0] if color == value[1] else -value[0]
        for pos in product(range(board.board_size), repeat=2):
            if board.get_type_map(pos) == board.empty_map:
                continue
            if board.get_type_map(pos) == board.bishop:
                bishops[board.get_color_map(pos)] += 1
            value += (self.piece_value_mg(board, color, pos) -
                      self.piece_value_mg(board, 3 - color, pos))

            value += (self.psqt_mg(board, color, pos) -
                      self.psqt_mg(board, 3 - color, pos))

            imb_val += (self.imbalance_mg(board, color, pos) -
                        self.imbalance_mg(board, 3 - color, pos))

        imb_val += ((bishops[color] // 2) - (bishops[3 - color] // 2)) * 1438

        value += (imb_val // 16)

        self.hash_table[hsh] = [value, color]

        return value

    def piece_value_mg(self, board, color, pos):
        """Piece coofs evaluation

        :param board: board object
        :type board: class board object
        :param color: color
        :type color: int
        :param pos: position
        :type pos: (int, int)
        :return: eval for now position
        :rtype: int
        """
        if board.get_color_map(pos) == color:
            return self.figure_price_mg[board.get_type_map(pos)]
        return 0

    def psqt_mg(self, board, color, pos):
        """psqt coofs evaluation

        :param board: board object
        :type board: class board object
        :param color: color
        :type color: int
        :param pos: position
        :type pos: (int, int)
        :return: eval for now position
        :rtype: int
        """
        if board.get_color_map(pos) == color:
            map_type = board.get_type_map(pos)

            if map_type == board.pawn:
                return self.ppsqt_price_mg[7 - pos[0]][pos[1]]
            return self.psqt_price_mg[map_type - 2][7 - pos[0]][min(pos[1], 7 - pos[1])]
        return 0

    def imbalance_mg(self, board, color, pos):
        """imbalance board evaluation

        :param board: board object
        :type board: class board object
        :param color: color
        :type color: int
        :param pos: position
        :type pos: (int, int)
        :return: imbalance board evaluation for now pos
        :rtype: int
        """
        value = 0
        if board.get_color_map(pos) == color:
            map_type = board.get_type_map(pos)
            if map_type == board.king:
                return 0
            if map_type == board.queen:
                map_type = 5
            bishop = [0, 0, 0]
            for now_pos in product(range(board.board_size), repeat=2):
                now_map_type = board.get_type_map(now_pos)
                if now_map_type in (board.empty_map, board.king):
                    continue
                if now_map_type == board.queen:
                    now_map_type = 5
                if now_map_type == board.bishop:
                    bishop[board.get_color_map(now_pos)] += 1

                if now_map_type > map_type:
                    continue

                if board.get_color_map(now_pos) == color:
                    value += self.imb_qo[map_type][now_map_type]
                else:
                    value += self.imb_qt[map_type][now_map_type]

            if bishop[1] > 1:
                value += self.imb_qt[map_type][0]
            if bishop[2] > 1:
                value += self.imb_qo[map_type][0]
        return value

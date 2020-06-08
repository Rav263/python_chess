from itertools import product
from turns import Node

# pylint: disable=eval-used


class Evaluate:
    def __init__(self, data_file_name):
        data_file = open(data_file_name, "r")
        self.hash_hit = 0
        self.hash_miss = 0
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

        data_file.close()

    def rank_moves(self, board, moves, turn, color):
        ranked_moves = list()
        for now_move in moves:
            tmp, flags = board.do_turn(now_move)
            now_cost = self.evaluate_board_mg(board, color, turn)
            board.un_do_turn(now_move, tmp, flags)
            ranked_moves.append(Node(now_move, 0))

        return sorted(ranked_moves, key=lambda x: -x.cost)

    def hash_board(self, board):
        hsh = 0
        for a in board.board:
            for sq in a:
                hsh <<= 5
                hsh += sq
        return hsh

    def clear_hash_table(self, turn_num):
        tmp_keys = [*self.hash_table.keys()]
        for key in tmp_keys:
            if self.hash_table[key][2] < turn_num:
                del(self.hash_table[key])

    def evaluate_board_mg(self, board, color, turn):
        value = 0
        imb_val = 0
        bishops = [0, 0, 0]
        hsh = self.hash_board(board)

        if hsh in self.hash_table:
            self.hash_hit += 1
            value = self.hash_table[hsh]
            return value[0] if color == value[1] else -value[0]

        for pos in product(range(board.board_size), repeat=2):
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
        self.hash_table[hsh] = [value, color, turn]
        self.hash_miss += 1
        return value

    def piece_value_mg(self, board, color, pos):
        if board.get_color_map(pos) == color:
            return self.figure_price_mg[board.get_type_map(pos)]
        return 0

    def psqt_mg(self, board, color, pos):
        if board.get_color_map(pos) == color:
            map_type = board.get_type_map(pos)

            if map_type == board.pawn:
                return self.ppsqt_price_mg[7 - pos[0]][pos[1]]
            return self.psqt_price_mg[map_type - 2][7 - pos[0]][min(pos[1], 7 - pos[1])]
        return 0

    def imbalance_mg(self, board, color, pos):
        value = 0
        if board.get_color_map(pos) == color:
            map_type = board.get_type_map(pos)
            if map_type == board.king:
                return 0
            if map_type == 6:
                map_type = 5
            bishop = [0, 0, 0]
            for now_pos in product(range(board.board_size), repeat=2):
                now_map_type = board.get_type_map(now_pos)
                if now_map_type in (board.empty_map, board.king):
                    continue
                if now_map_type == 6:
                    now_map_type = 5
                if now_map_type == board.bishop:
                    bishop[board.get_color_map(now_pos)] += 1

                if now_map_type > map_type:
                    continue

                if board.get_color_map(now_pos) == color:
                    value += self.imb_qo[map_type][now_map_type]
                else:
                    value += self.imb_qt[map_type][now_map_type]

            if (bishop[1] > 1):
                value += self.imb_qt[map_type][0]
            if (bishop[2] > 1):
                value += self.imb_qo[map_type][0]
        return value

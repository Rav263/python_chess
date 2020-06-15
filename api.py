"""module to connect backend ang gui"""

from collections import defaultdict
from itertools import product
from board import Board
from gamelogic import Logic
from io_functions import Data
from evaluate import Evaluate
from turns import read_nodes, Node


class Api:
    """backend api class to ui"""

    def __init__(self, difficulty, threads, deb):
        # Here we need to init Field and Game logic
        self.data = Data("data.dat")
        self.board = Board(self.data)
        self.evaluate = Evaluate("eval_coofs.dat")
        if deb:
            self.debuts = read_nodes()
        else:
            self.debuts = Node()
        self.logic = Logic(self.data, threads, self.evaluate, self.debuts)
        self.difficulty = difficulty
        self.turn_index = 0

        print(self.evaluate.evaluate_board_mg(self.board, 1))
        print("difficulty:", difficulty)
        print("threads:   ", threads)

        # Then we need start game

    def start_cmd(self):
        """start command line UI"""
        self.logic.start(self.board, self.data, self.difficulty)

    def get_possible_turns(self, color):
        """returns possible turns from backend"""
        if self.turn_index != 0:
            last_turn = self.logic.turn_history[self.turn_index - 1][0]
        else:
            last_turn = self.logic.NULL_TURN
        possible_turns = self.logic.generate_all_possible_turns(self.board, color, last_turn)

        turns = defaultdict(list)

        for end_pos in possible_turns:
            for start_pos in possible_turns[end_pos]:
                turns[start_pos[:2]].append(end_pos[:2])

        return turns

    def flip_board(self):
        self.board.rotate_board()

    def get_field(self, pos):
        """returns cell value on board"""
        if self.board.check_pos(pos):
            return self.board.get_map(pos)

        return -1

    def set_field(self, pos, value):
        """set cell value on board"""
        if self.board.check_pos(pos):
            return self.board.set_map(pos, value)

        return -1

    def check_check(self, color):
        if self.turn_index != 0:
            last_turn = self.logic.turn_history[self.turn_index - 1][0]
        else:
            last_turn = self.logic.NULL_TURN
        possible_turns = self.logic.generate_all_possible_turns(self.board, 3 - color, last_turn)
        
        king_pos = self.board.get_king_pos(color)

        return king_pos in possible_turns

    def get_taken_figures(self):
        white_figs = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        black_figs = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        
        for pos in product(range(self.board.board_size), repeat=2):
            if self.board.get_color_map(pos) == self.board.white:
                white_figs[self.board.get_type_map(pos)] += 1
            if self.board.get_color_map(pos) == self.board.black:
                black_figs[self.board.get_type_map(pos)] += 1
        
        all_figs = dict()

        for now in white_figs:
            all_figs[now] = white_figs[now] - black_figs[now]
        
        black_figs = list()
        white_figs = list()
        black_score = 0
        white_score = 0

        for now in all_figs:
            if all_figs[now] < 0:
                black_figs.append((now, abs(all_figs[now])))
                black_score += self.data.data["FIGURES_COST"][10 + now] * all_figs[now] 
            elif all_figs[now] > 0:
                white_figs.append((now, abs(all_figs[now])))
                white_score -= self.data.data["FIGURES_COST"][10 + now] * all_figs[now] 
        return (white_figs, black_figs, white_score, black_score)

    def do_turn(self, start, end, pawn=0):
        """doing User turn
        start    -- start position
        end      -- end position
        pawn     -- figure type if pawn get transformation
        """

        color = self.board.get_color_map(start)

        if self.turn_index != len(self.logic.turn_history):
            self.logic.turn_history = self.logic.turn_history[:self.turn_index]

        last_turn = self.logic.NULL_TURN
        if self.turn_index != 0:
            last_turn = self.logic.turn_history[self.turn_index - 1][0]
        
        all_turns = self.logic.generate_turns(self.board, color, last_turn)

        for tmp_turn in all_turns:
            if tmp_turn.start_pos[:2] == start and tmp_turn.end_pos[:2] == end:
                now_turn = tmp_turn
                break

        if pawn != 0:
            now_turn.pawn = 10 * color + pawn

        tmp, flags = self.board.do_turn(now_turn)

        self.logic.add_turn_to_history((now_turn, tmp, flags))
        self.turn_index += 1
        return now_turn.passant or now_turn.castling or now_turn.pawn != 0

    def ai_turn(self, color):
        """ai do turn with color"""
        
        if self.turn_index != 0:
            last_turn = self.logic.turn_history[self.turn_index - 1][0]
        else:
            last_turn = self.logic.NULL_TURN

        now_turn = self.logic.root_ai_turn(self.board, color, self.difficulty, last_turn)[0]
        tmp, flags = self.board.do_turn(now_turn)

        self.logic.add_turn_to_history((now_turn, tmp, flags))

        self.turn_index += 1
        return (now_turn, now_turn.passant or now_turn.castling or now_turn.pawn != 0)

    def start_new_game(self, difficulty):
        self.board = Board(self.data)
        self.logic.debuts = self.debuts
        self.logic.flag = True
        self.difficulty = difficulty
 
    def get_board_eval(self):
        return self.evaluate.evaluate_board_mg(self.board, self.board.white) / 1000

    def previous_turn(self):
        """returns previous turn and un do it on board"""
        if self.turn_index == 0:
            return None

        self.turn_index -= 1

        turn = self.logic.get_turn_from_history(self.turn_index)

        self.board.un_do_turn(*turn)
        return turn[:2]

    def next_turn(self):
        """do next turn from history"""
        if self.turn_index >= len(self.logic.turn_history):
            return None

        turn = self.logic.get_turn_from_history(self.turn_index)

        self.board.do_turn(turn[0])
        self.turn_index += 1

        return turn[0]

"""module to connect backend ang gui"""

from collections import defaultdict
from board import Board
from gamelogic import Logic
from io_functions import Data
from evaluate import Evaluate
from turns import read_nodes

class Api:
    """backend api class to ui"""

    def __init__(self, difficulty, threads):
        # Here we need to init Field and Game logic
        self.data = Data("data.dat")
        self.board = Board(self.data)
        self.evaluate = Evaluate("eval_coofs.dat")
        self.debuts = read_nodes()
        self.logic = Logic(self.data, threads, self.evaluate, self.debuts)
        self.difficulty = difficulty
        self.turn_index = 0
        print(self.evaluate.evaluate_board_mg(self.board, 1))
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

    def get_map(self, pos):
        """returns cell value on board"""
        if self.board.check_pos(pos):
            return self.board.get_map(pos)

        return -1

    def set_map(self, pos, value):
        """set cell value on board"""
        if self.board.check_pos(pos):
            return self.board.set_map(pos, value)

        return -1

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
            now_turn.pawn = pawn

        tmp, flags = self.board.do_turn(now_turn)

        self.logic.add_turn_to_history((now_turn, tmp, flags))
        self.turn_index += 1

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
        return now_turn

    def start_new_game(self):
        self.board = Board(self.data)
        print("WTF")
        self.logic.debuts = self.debuts
        self.logic.flag = True

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

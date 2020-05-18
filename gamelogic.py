"""Class Logic and class Turn module"""
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=arguments-out-of-order

from collections import defaultdict
from itertools import product
from multiprocessing import Process
from multiprocessing import Manager


import io_functions
import generate_turns as gt
from board import Board


class Turn:
    """Turn class for store chess turn"""
    def __init__(self, start_pos, end_pos, color, pawn=0, castling=False):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.pawn = pawn
        self.castling = castling

    def print(self):
        """print(self) -> None: prints Turn information"""
        print("start pos: ({0}, {1})".format(*self.start_pos))
        print("end pos:   ({0}, {1})".format(*self.end_pos))

    def __str__(self):
        return ("start pos: ({0}, {1})\n".format(*self.start_pos) +
                "end pos:   ({0}, {1})\n".format(*self.end_pos) +
                f"color:      {self.color}")

    def __eq__(self, second):
        return (self.start_pos == self.start_pos and self.end_pos == second.end_pos and
                self.color == second.color and self.pawn == second.pawn and
                self.castling == second.castling)


class Logic:
    """main Logic class for game logic realisation"""
    MAX_COST = 9999
    MIN_COST = -9999
    NULL_TURN = Turn((-1, -1), (-1, -1), 0)
    turn_history = list()

    def __init__(self, data, num_threads):
        print("Init game logic class")
        self.figures_cost = data.data["FIGURES_COST"]
        self.av_threads = num_threads

    def start(self, board, data, difficulty):
        """start(self, board, data, difficulty) -> None

        Main game cycle in text mode
        """

        color = 1

        while True:
            io_functions.print_board(board.board, data)
            now_turn = io_functions.get_turn(self, color, board)

            if now_turn == self.NULL_TURN:
                print("CHECK MATE! YOU LOSE!")
                break

            board.do_turn(now_turn)

            color = 3 - color

            print(board.calculate_board_cost(self.figures_cost))

            now_turn = self.root_ai_turn(board, color, difficulty)[0]

            if now_turn == self.NULL_TURN:
                print("CHECK MATE! YOU WIN!")
                break

            board.do_turn(now_turn)

            color = 3 - color

    def add_turn_to_history(self, now_turn):
        """adds turn for history"""
        self.turn_history.append(now_turn)

    def get_turn_from_history(self, index):
        """returns turn from history"""
        return self.turn_history[index]

    def generate_all_possible_turns(self, board, color, check_check=True):
        """generate_all_possible_turns(self, board, color) -> dict

        self  -- class Logic object
        board -- class Board object
        color -- color of figures

        returns all possible turns in dict
        dict key   - end turn position
        dict value - list of start turn positions
        """

        if check_check:
            opponent_turns, opponent_turns_for_king = (
                self.generate_all_possible_turns(board, 3 - color, check_check=False))

        possible_turns = defaultdict(list)
        turns_for_king = defaultdict(list)
        # dict key = position of possible turn
        # dict value = list of positions where from this turn can be done

        for pos in product(range(board.board_size), repeat=2):
            if board.get_color_map(pos) == color:
                if board.get_type_map(pos) == board.pawn:
                    gt.generate_turns_pawn(pos, board, possible_turns, turns_for_king)

                if board.get_type_map(pos) == board.knight:
                    gt.generate_turns_knight(pos, board, possible_turns, color, turns_for_king)

                if board.get_type_map(pos) == board.rook:
                    gt.generate_turns_rook(pos, board, possible_turns, color, turns_for_king)

                if board.get_type_map(pos) == board.bishop:
                    gt.generate_turns_bishop(pos, board, possible_turns, color, turns_for_king)

                if board.get_type_map(pos) == board.queen:
                    gt.generate_turns_queen(pos, board, possible_turns, color, turns_for_king)

                if board.get_type_map(pos) == board.king:
                    if check_check:
                        gt.generate_turns_king(pos, board, possible_turns, color,
                                               opponent_turns, opponent_turns_for_king)
                    else:
                        gt.generate_turns_king(pos, board, possible_turns, color,
                                               defaultdict(list), defaultdict(list))

        if check_check:
            king_pos = board.get_king_pos(color)
            possible_turns = gt.remove_not_possible_turns(board, king_pos, color,
                                                          possible_turns, opponent_turns)
            return possible_turns

        return (possible_turns, turns_for_king)

    def thread_generate(self, board, color, depth, turns, index, return_dict):
        """thread_generate(self, board, color, depth, turns, index, return_dict) -> tuple

        self        -- class Logic object
        board       -- class Board object
        color       -- figure color for turn
        depth       -- recursion depth
        turns       -- list of turns for this process
        index       -- process index
        return_dict -- dict for return value

        returns tuple of best_turn and it cost
        """
        best_cost = self.MIN_COST if color == board.black else self.MAX_COST
        best_turn = self.NULL_TURN

        for turn in turns:
            if len(turn[0]) == 3:
                now_turn = Turn((turn[0][0], turn[0][1]), turn[1], color, pawn=turn[0][2])
            elif len(turn[0]) == 4:
                now_turn = Turn(turn[0], turn[1], color, castling=True)
            else:
                now_turn = Turn(turn[0], turn[1], color)

            tmp, flags = board.do_turn(now_turn)

            now_cost = self.ai_turn(board, 3 - color, depth - 1)[1]

            board.un_do_turn(now_turn, tmp, flags)
            if color == board.black:
                if now_cost >= best_cost:
                    best_cost = now_cost
                    best_turn = now_turn
            else:
                if now_cost <= best_cost:
                    best_cost = now_cost
                    best_turn = now_turn

        return_dict[index] = (best_turn, best_cost)

    def root_ai_turn(self, board, color, depth):
        """root_ai_turn(self, board, color, depth) -> tuple

        self  -- class Logic object
        board -- class Board object
        color -- color of turn
        depth -- recursion depth

        return tuple of best_turn and it cost
        """

        manager = Manager()
        return_dict = manager.dict()

        possible_turns = self.generate_all_possible_turns(board, color)

        turns = []
        threads = []

        for end_pos in possible_turns:
            for start_pos in possible_turns[end_pos]:
                turns.append((start_pos, end_pos))

        num_of_turns = len(turns) // self.av_threads + 1
        num_of_threads = len(turns) // num_of_turns + 1

        if len(turns) < self.av_threads:
            num_of_threads = 1

        for i in range(num_of_threads):
            now_board = Board(None, board)
            start = i * num_of_turns

            end = (i + 1) * num_of_turns
            end = end if end < len(turns) else len(turns) - 1

            threads.append(Process(target=self.thread_generate, name=len(threads),
                                   args=(now_board, color, depth,
                                         turns[start:end + 1], i, return_dict)))

            threads[len(threads) - 1].start()

        for thread in threads:
            thread.join()
        if color == board.black:
            return max(return_dict.values(), key=lambda x: x[1])
        return min(return_dict.values(), key=lambda x: x[1])

    def ai_turn(self, board, color, depth, alpha=MIN_COST, beta=MAX_COST):
        """root_ai_turn(self, board, color, depth) -> tuple

        self  -- class Logic object
        board -- class Board object
        color -- color of turn
        depth -- recursion depth
        alpha -- optimization varaible
        beta  -- the same as alpha

        return tuple of best_turn and it cost
        """

        possible_turns = self.generate_all_possible_turns(board, color)

        best_cost = self.MIN_COST if color == board.black else self.MAX_COST
        best_turn = self.NULL_TURN

        for end_pos in possible_turns:
            for start_pos in possible_turns[end_pos]:
                if len(start_pos) == 3:
                    now_turn = Turn((start_pos[0], start_pos[1]), end_pos, color, start_pos[2])
                elif len(start_pos) == 4:
                    now_turn = Turn(start_pos, end_pos, color, castling=True)
                else:
                    now_turn = Turn(start_pos, end_pos, color)

                tmp, flags = board.do_turn(now_turn)

                if depth == 1:
                    now_cost = board.calculate_board_cost(self.figures_cost)
                else:
                    now_cost = self.ai_turn(board, 3 - color, depth - 1, alpha, beta)[1]

                board.un_do_turn(now_turn, tmp, flags)

                if color == board.black:
                    if now_cost >= best_cost:
                        best_cost = now_cost
                        best_turn = now_turn
                    alpha = max(alpha, best_cost)
                else:
                    if now_cost <= best_cost:
                        best_cost = now_cost
                        best_turn = now_turn
                    beta = min(beta, best_cost)

                if beta <= alpha:
                    return (best_turn, best_cost)

        return (best_turn, best_cost)

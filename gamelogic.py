"""Class Logic and class Turn module"""
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=arguments-out-of-order

from threads import MainThread
from moves import Moves, Turn

import io_functions


class Logic:
    """main Logic class for game logic realisation"""
    MAX_COST = 9999
    MIN_COST = -9999
    NULL_TURN = Turn((-1, -1), (-1, -1), 0)
    turn_history = list()
    hash_table = dict()

    def __init__(self, data, num_threads, evaluation, difficulty, color):
        print("Init game logic class")
        self.figures_cost = data.data["FIGURES_COST"]
        self.av_threads = num_threads
        self.evaluation = evaluation
        self.difficulty = difficulty
        self.main_thread = MainThread(evaluation, num_threads, difficulty, color)
        self.turn = 0
        self.color = color

    def start(self, board, data):
        """start(self, board, data, difficulty) -> None

        Main game cycle in text mode
        """

        color = 1
        last_turn = self.NULL_TURN
        print(board.generate_fen(data.data["FEN"]))
        print(self.evaluation.evaluate_board_mg(board, 1, self.turn))
        print(self.evaluation.evaluate_board_mg(board, 2, self.turn))
        moves = Moves(self.NULL_TURN)
        print([str(x) for x in moves.generate_turns(board, color, last_turn)])
        while True:
            io_functions.print_board(board.board, data)
            now_turn = io_functions.get_turn(moves, color, board, last_turn)
            print(now_turn)
            if now_turn == self.NULL_TURN:
                print("CHECK MATE! YOU LOSE!")
                break

            board.do_turn(now_turn)
            self.turn += 1
            last_turn = now_turn

            color = 3 - color
            now_turn = self.main_thread.start_thinking(board, last_turn, self.difficulty)
            print("BEST COST: ", now_turn.cost)
            now_turn = now_turn.turn

            self.evaluation.clear_hash_table(self.turn)
            if now_turn == self.NULL_TURN:
                print("CHECK MATE! YOU WIN!")
                break

            board.do_turn(now_turn)
            last_turn = now_turn
            print(self.evaluation.evaluate_board_mg(board, 2, self.turn))
            self.turn += 1
            color = 3 - color

    def add_turn_to_history(self, now_turn):
        """adds turn for history"""
        self.turn_history.append(now_turn)

    def get_turn_from_history(self, index):
        """returns turn from history"""
        return self.turn_history[index]

    def ai_turn(self, board, last_turn):
        return self.main_thread.start_thinking(board, last_turn, self.difficulty).turn

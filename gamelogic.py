import io_functions
import generate_turns as gt
from board import Board


from collections import defaultdict
from itertools import product
from multiprocessing import Process
from multiprocessing import Manager
# from tqdm import tqdm


class Turn:
    def __init__(self, start_pos, end_pos, color):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color

    def print(self):
        print("start pos: ({0}, {1})".format(*self.start_pos))
        print("start pos: ({0}, {1})".format(*self.end_pos))


class Logic:
    MAX_COST = 9999
    MIN_COST = -9999
    NULL_TURN = Turn((-1, -1), (-1, -1), 0)

    def __init__(self, data, num_threads):
        print("Init game logic class")
        self.figures_cost = data.data["FIGURES_COST"]
        self.av_threads = num_threads

    def start(self, board, data, difficulty):
        color = 1

        while True:
            io_functions.print_board(board.board, data)
            now_turn = io_functions.get_turn(self, color, board)

            board.do_turn(now_turn)

            color = 3 - color

            print(board.calculate_board_cost(color, self.figures_cost))

            now_turn = self.root_ai_turn(board, color, difficulty)[0]
            board.do_turn(now_turn)

            color = 3 - color

    def generate_all_possible_turns(self, board, color):
        possible_turns = defaultdict(list)
        # dict key = position of possible turn
        # dict value = list of positions where from this turn can be done

        for pos in product(range(board.board_size), repeat=2):
            if board.get_color_map(pos) == color:
                if board.get_type_map(pos) == board.pawn:
                    gt.generate_turns_pawn(pos, board, possible_turns)

                if board.get_type_map(pos) == board.knight:
                    gt.generate_turns_knight(pos, board, possible_turns, color)

                if board.get_type_map(pos) == board.rook:
                    gt.generate_turns_rook(pos, board, possible_turns, color)

                if board.get_type_map(pos) == board.bishop:
                    gt.generate_turns_bishop(pos, board, possible_turns, color)

                if board.get_type_map(pos) == board.queen:
                    gt.generate_turns_queen(pos, board, possible_turns, color)

                if board.get_type_map(pos) == board.king:
                    gt.generate_turns_king(pos, board, possible_turns, color)

        return possible_turns

    def thread_generate(self, board, color, depth, turns, index, return_dict):
        best_cost = self.MIN_COST if color == board.black else self.MAX_COST
        best_turn = self.NULL_TURN

        for turn in turns:
            tmp = board.do_turn(Turn(turn[0], turn[1], color))
            now_cost = self.ai_turn(board, 3 - color, depth - 1)[1]

            board.do_turn(Turn(turn[1], turn[0], color), fig=tmp)

            if now_cost >= best_cost:
                best_cost = now_cost
                best_turn = Turn(turn[0], turn[1], color)

        return_dict[index] = (best_turn, best_cost)

    def root_ai_turn(self, board, color, depth):
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

        return max(return_dict.values(), key=lambda x: x[1])

    def ai_turn(self, board, color, depth, alpha=MIN_COST, beta=MAX_COST):
        possible_turns = self.generate_all_possible_turns(board, color)

        best_cost = self.MIN_COST if color == board.black else self.MAX_COST
        best_turn = self.NULL_TURN

        for end_pos in possible_turns:
            for start_pos in possible_turns[end_pos]:
                tmp = board.do_turn(Turn(start_pos, end_pos, color))

                if depth == 1:
                    now_cost = board.calculate_board_cost(color, self.figures_cost)
                else:
                    now_cost = self.ai_turn(board, 3 - color, depth - 1, alpha, beta)[1]

                board.do_turn(Turn(end_pos, start_pos, color), fig=tmp)

                if color == board.black:
                    if now_cost >= best_cost:
                        best_cost = now_cost
                        best_turn = Turn(start_pos, end_pos, color)
                    alpha = max(alpha, best_cost)
                else:
                    if now_cost <= best_cost:
                        best_cost = now_cost
                        best_turn = Turn(start_pos, end_pos, color)
                    beta = min(beta, best_cost)

                if beta <= alpha:
                    return (best_turn, best_cost)

        return (best_turn, best_cost)

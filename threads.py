from multiprocessing import Process, Manager
from moves import Moves, Turn
from tqdm import tqdm
from turns import Node


class MainThread:
    NULL_TURN = Turn((-1, -1), (-1, -1), -1)

    def __init__(self, evaluation, num_threads, difficulty, color):
        self.evaluation = evaluation
        self.moves = Moves(self.NULL_TURN)
        self.threads = [Thread(self.evaluation, self.moves, index) for index in range(num_threads)]
        self.color = color
        self.difficulty = difficulty

    def start_thinking(self, board, last_turn, turn_num):
        procs = list()
        manager = Manager()
        return_dict = manager.dict()

        root_moves = self.moves.generate_turns(board, self.color, last_turn)
        root_moves = self.evaluation.rank_moves(board, root_moves, turn_num, self.color)

        for index, now_thread in enumerate(self.threads):
            now_thread.root_moves = list()
            for now_move in root_moves[index::len(self.threads)]:
                now_thread.root_moves.append(now_move)

        for index, now_thread in enumerate(self.threads):
            now_thread.board = board.copy()
            now_thread.depth = self.difficulty
            now_thread.turn = turn_num
            procs.append(Process(target=now_thread.start_thinking, args=(self.color, return_dict)))
            procs[-1].start()

        for now_proc in procs:
            now_proc.join()

        return max([root_moves[0] for root_moves in return_dict.values()], key=lambda x: x.cost)


def make_iter(some, thread_index):
    if thread_index == 0:
        for now in tqdm(some):
            yield now
    else:
        for now in some:
            yield now


def print_list(lst):
    print([now.cost for now in lst])


class Thread:
    MIN_COST = -9999
    MAX_COST = 9999
    NULL_TURN = Turn((-1, -1), (-1, -1), -1)
    multi_pv = 1

    def __init__(self, evaluation, moves, index):
        self.evaluation = evaluation
        self.moves = moves
        self.index = index

    def start_thinking(self, color, return_dict):
        alpha = self.MIN_COST
        beta = self.MAX_COST
        delta = self.MIN_COST
        self.color = color

        if len(self.root_moves) == 0:
            self.root_moves.append(Node(self.NULL_TURN, self.MIN_COST))
            return None

        for depth in make_iter(range(1, self.depth), self.index):

            for turn_index, now_turn in enumerate(self.root_moves):
                if turn_index == self.multi_pv:
                    break
                if depth >= 4:
                    delta = int(21 + abs(now_turn.prev_cost) / 256)
                    alpha = max(now_turn.prev_cost - delta, self.MIN_COST)
                    beta = min(now_turn.prev_cost + delta, self.MAX_COST)
                    
                    tmp, flags = self.board.do_turn(now_turn.turn)
                    print(alpha, beta, delta)
                    now_cost = -self.search(3 - color, depth, now_turn.turn, -beta, -alpha)[1]
                    self.board.un_do_turn(now_turn.turn, tmp, flags)

                    self.root_moves[turn_index].update_cost(now_cost)

            self.root_moves = sorted(self.root_moves, key=lambda x: -x.cost)

        return_dict[self.index] = self.root_moves

    def search(self, color, depth, now_turn, alpha, beta):
        possible_turns = self.moves.generate_turns(self.board, color, now_turn)
        best_cost = self.MIN_COST
        best_turn = self.NULL_TURN
        
        for now_turn in possible_turns:
            tmp, flags = self.board.do_turn(now_turn)

            if depth == 1:
                now_cost = self.evaluation.evaluate_board_mg(self.board, color, self.turn + self.depth - 1)
            else:
                now_cost = -self.search(3 - color, depth - 1, now_turn, -beta, -alpha)[1]
            self.board.un_do_turn(now_turn, tmp, flags)
            
            if now_cost >= best_cost:
                best_cost = now_cost
                best_turn = now_turn
            if color == self.color:
                alpha = max(alpha, best_cost)
            else:
                beta = min(beta, best_cost)
            if alpha > beta:
                return (best_turn, best_cost)
        return (best_turn, best_cost)

from multiprocessing import Process, Manager
from moves import Moves, Turn
from turns import Node


class MainThread:
    NULL_TURN = Turn((-1, -1), (-1, -1), -1)

    def __init__(self, evaluation, num_threads, difficulty, color):
        self.evaluation = evaluation
        self.moves = Moves(self.NULL_TURN)
        self.threads = [Thread(self.evaluation, self.moves, index) for index in range(1)]
        self.color = color
        self.difficulty = difficulty

    def start_thinking(self, board, last_turn, turn_num):
        root_moves = self.moves.generate_turns(board, self.color, last_turn)
        root_moves = self.evaluation.rank_moves(board, root_moves, turn_num, self.color)

        self.threads[0].root_moves = root_moves
        self.threads[0].board = board.copy()
        self.threads[0].depth = self.difficulty
        self.threads[0].turn = turn_num

        return_dict = dict()
        self.threads[0].start_thinking(self.color, return_dict)
        return max([root_moves[0] for root_moves in return_dict.values()], key=lambda x: x.cost)

    def start_thinking_old(self, board, last_turn, turn_num):
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


def print_list(lst):
    print([now.cost for now in lst])


class Thread:
    MIN_COST = -9999
    MAX_COST = 9999
    NULL_TURN = Turn((-1, -1), (-1, -1), -1)
    multi_pv = 1
    depth = 1
    root_moves = list()

    def __init__(self, evaluation, moves, index):
        self.evaluation = evaluation
        self.moves = moves
        self.index = index

    def print_root_moves(self, moves=None):
        if moves is None:
            moves = self.root_moves
        for now_move in moves:
            print(f"({now_move.turn}, {now_move.cost}, {now_move.best_move_count})", end=" ")
        print()

    def start_thinking(self, color, return_dict):
        alpha = self.MIN_COST
        beta = self.MAX_COST
        delta = self.MIN_COST
        self.color = color

        if len(self.root_moves) == 0:
            self.root_moves.append(Node(self.NULL_TURN, self.MIN_COST))
            return None

        for depth in range(1, self.depth):
            if len(self.root_moves) <= 1:
                break
            self.print_root_moves()
            for now in self.root_moves:
                now.prev_cost = now.cost
            
            now_turn = self.root_moves[0]
            if depth >= 3:
                delta = int(21 + abs(now_turn.prev_cost) / 256)
                if delta <= 0:
                    print("WTH")
                    input()

                alpha = max(now_turn.prev_cost - delta, self.MIN_COST)
                beta = min(now_turn.prev_cost + delta, self.MAX_COST)

            for turn_index in range(min(len(self.root_moves), self.multi_pv)):
                while True:
                    now_turn = self.root_moves[turn_index]
                    self.print_root_moves()
                    print(f"depth: {depth}, turn:\n{now_turn.turn}\ncost: {now_turn.cost}")
                    print(f"alpha {alpha}, beta: {beta}, delta: {delta}")
                    tmp, flags = self.board.do_turn(now_turn.turn)
                    now_cost = -self.search(3 - color, depth, now_turn.turn, -beta, -alpha, True)[1]
                    self.board.un_do_turn(now_turn.turn, tmp, flags)
                    print(f"now cost: {now_cost}")
                    print()

                    self.root_moves[turn_index].update_cost(now_cost)
                    # self.root_moves[turn_index].update_cost(self.MIN_COST)

                    self.root_moves = sorted(self.root_moves, key=lambda x: -x.cost)

                    if now_cost <= alpha:
                        print("cost < alpha")
                        if delta < 0:
                            break
                        print(f"BETA WAS: {beta}", end=", ")
                        beta = (alpha + beta) // 2
                        print(f"BETA IS: {beta}")
                        alpha = max(now_cost - delta, self.MIN_COST)
                    elif now_cost >= beta:
                        beta = min(now_cost + delta, self.MAX_COST)
                    else:
                        self.root_moves[turn_index].best_move_count += 1
                        break
                    if delta > 0:
                        delta += delta // 4 + 5

        self.root_moves = sorted(self.root_moves, key=lambda x: -x.cost)
        self.print_root_moves()

        return_dict[self.index] = self.root_moves

    def search(self, color, depth, now_turn, alpha, beta, root_turn=False):
        possible_turns = self.moves.generate_turns(self.board, color, now_turn)
        best_cost = self.MIN_COST
        best_turn = self.NULL_TURN

        for turn_index, now_turn in enumerate(possible_turns):
            tmp, flags = self.board.do_turn(now_turn)

            if depth == 1:
                now_cost = self.evaluation.evaluate_board_mg(self.board, color,
                                                             self.turn + self.depth - 1)
            else:
                now_cost = -self.search(3 - color, depth - 1, now_turn, -beta, -alpha)[1]
            self.board.un_do_turn(now_turn, tmp, flags)

            if now_cost >= best_cost:
                best_cost = now_cost
                best_turn = now_turn

                alpha = max(alpha, best_cost)
            
            if not root_turn and alpha > beta:
                return (best_turn, best_cost)
        return (best_turn, best_cost)

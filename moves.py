from collections import defaultdict
from itertools import product

import generate_turns as gt


class Turn:
    """Turn class for store chess turn"""
    def __init__(self, start_pos, end_pos, color, pawn=0, castling=False, passant=False):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.pawn = pawn
        self.castling = castling
        self.passant = passant

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


class Moves:
    def __init__(self, null_turn):
        self.NULL_TURN = null_turn

    def generate_all_possible_turns(self, board, color, last_turn, check_check=True):
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
                self.generate_all_possible_turns(board, 3 - color, self.NULL_TURN,
                                                 check_check=False))

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
        gt.check_de_passant(board, possible_turns, last_turn, color)

        if check_check:
            king_pos = board.get_king_pos(color)
            possible_turns = gt.remove_not_possible_turns(board, king_pos, color,
                                                          possible_turns, opponent_turns)
            return possible_turns

        return (possible_turns, turns_for_king)

    def generate_turns(self, board, color, last_turn):
        possible_turns = self.generate_all_possible_turns(board, color, last_turn)
        turns = list()

        for end_pos in possible_turns:
            for start_pos in possible_turns[end_pos]:
                if len(start_pos) == 3:
                    now_turn = Turn((start_pos[0], start_pos[1]), end_pos, color, start_pos[2])
                elif len(start_pos) == 4:
                    now_turn = Turn(start_pos, end_pos, color, castling=True)
                elif len(end_pos) == 3:
                    now_turn = Turn(start_pos, end_pos[:2], color, passant=True)
                else:
                    now_turn = Turn(start_pos, end_pos, color)

                turns.append(now_turn)

        return turns

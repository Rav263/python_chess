"""turn tree module for fast turn computing"""
from collections import defaultdict


class TurnTree:
    """Turn tree class to store possible good turns"""
    def __init__(self):
        self.root_turn = None

    def add_turn(self, turn, turn_history):
        pass


class TurnNode:
    turns_dict = dict()

    def __init__(self, turn, cost):
        self.turn = turn
        self.cost = cost

    def add_turn(self, turn, cost):
        """function too add turn to node"""
        self.turns_dict[(cost, *turn.start_pos)]
        pass


class Node:
    MIN_COST = -9999

    def __init__(self, turn, cost):
        self.turn = turn
        self.cost = cost
        self.prev_cost = self.MIN_COST

    def update_cost(self, new_cost):
        self.prev_cost = self.cost
        self.cost = new_cost

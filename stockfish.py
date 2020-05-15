"""Stockfish vs ai play"""
from other_engines_io import Stockfish
import io_functions


def main(api, num_threads):
    """main loop"""
    stockfish = Stockfish(num_threads)

    io_functions.print_board(api.board.board, api.data)

    color = 1

    while True:
        stockfish.do_command("go")
        turn = stockfish.get_turn(api.board.board_size, color)

        api.do_turn(turn.start_pos, turn.end_pos)
        stockfish.do_turn(turn, api.board.board_size)

        io_functions.print_board(api.board.board, api.data)

        color = 3 - color

        turn = api.ai_turn(color)

        stockfish.do_turn(turn, api.board.board_size)

        io_functions.print_board(api.board.board, api.data)
        color = 3 - color

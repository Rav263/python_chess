"""Stockfish vs ai play"""
from other_engines_io import Stockfish
import io_functions


def main(api, num_threads):
    """main loop"""
    difficulty = int(input("Enter stockfish level: "))
    stockfish = Stockfish(num_threads, difficulty)

    io_functions.print_board(api.board.board, api.data)

    color = 1

    while True:
        stockfish.do_command("go")
        turn = stockfish.get_turn(api.board, color)
        if turn == api.logic.NULL_TURN:
            print("STOCKFISH LOSE")
            stockfish.do_command("quit")
            stockfish.end_game()
            break

        print("stockfish turn:")
        print(turn)
        api.board.do_turn(turn)
        stockfish.do_turn(turn, api.board.board_size)

        io_functions.print_board(api.board.board, api.data)

        color = 3 - color

        turn = api.ai_turn(color)

        if turn == api.logic.NULL_TURN:
            print("CHECK MATE! AI LOSE!")
            stockfish.do_command("quit")
            stockfish.end_game()
            break

        print("AI turn:")
        print(turn)
        stockfish.do_turn(turn, api.board.board_size)

        io_functions.print_board(api.board.board, api.data)
        color = 3 - color

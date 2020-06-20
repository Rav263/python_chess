"""Module for UCI engines io"""
# pylint: disable=line-too-long
# pylint: disable=too-many-branches
# pylint: disable=no-self-use
import threading
import subprocess
from queue import Queue

from .turns import Turn


class Stockfish:
    """Class to use stockfish"""
    def __init__(self, threads_num, difficulty):
        self.process = subprocess.Popen(["./stockfish"], shell=False, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=None)

        self.process_queu = Queue()

        self.stockfish_thread = threading.Thread(target=self.read_output)

        self.stockfish_thread.deamon = True
        self.stockfish_thread.start()

        self.process.stdin.flush()
        self.history = []
        self.do_command("setoption name threads value " + str(threads_num))
        self.do_command("setoption name Skill Level value " + str(difficulty))

    def read_output(self):
        """Reads output from external process"""
        while True:
            now_line = self.process.stdout.readline()
            decoded_line = now_line.decode("utf-8")
            if "evaluation" in decoded_line:
                print(decoded_line)
                try:
                    self.process_queu.put(decoded_line.split()[2])
                except NameError:
                    break
            if "bestmove" in decoded_line:
                print(decoded_line)
                try:
                    self.process_queu.put(decoded_line.split()[1])
                except NameError:
                    break

    def end_game(self):
        """Ends game
        """
        del self.process_queu
        self.stockfish_thread.join()

    def do_turn(self, turn, board_size):
        """Does turn on a board

        :param turn: turn
        :type turn: class Turn object
        :param board_size: board size
        :type board_size: int
        """
        start_pos = chr(turn.start_pos[1] + ord('a')) + str(board_size - turn.start_pos[0])
        end_pos = chr(turn.end_pos[1] + ord('a')) + str(board_size - turn.end_pos[0])

        if turn.pawn % 10 == 2:
            end_pos += "n"
        elif turn.pawn % 10 == 3:
            end_pos += "b"
        elif turn.pawn % 10 == 4:
            end_pos += "r"
        elif turn.pawn % 10 == 6:
            end_pos += "q"

        self.history.append(start_pos + end_pos)

        self.do_command("position startpos moves " + " ".join(self.history))

    def check_diff(self, start_pos, end_pos):
        """Checks position differences

        :param start_pos: start pos
        :type start_pos: (int, int)
        :param end_pos: end pos
        :type end_pos: (int, int)
        :return: difference
        :rtype: int
        """
        return abs(start_pos[1] - end_pos[1]) > 1

    def get_eval(self):
        """Gets position evaluation

        :return: evaluation
        :rtype: int
        """
        self.do_command("eval")
        while self.process_queu.empty():
            pass
        return self.process_queu.get()

    def get_turn(self, board, color):
        """Gets turn

        :param board: board object
        :type board: class board object
        :param color: color
        :type color: int
        :return: turn
        :rtype: class Turn object
        """
        while self.process_queu.empty():
            pass

        board_size = board.board_size

        line = self.process_queu.get()
        if line == "(none)":
            return Turn((-1, -1), (-1, -1), 0)

        start_pos = (board_size - int(line[1]), abs(ord(line[0]) - ord("a")))
        end_pos = (board_size - int(line[3]), abs(ord(line[2]) - ord("a")))

        if len(line) == 5:
            figure = line[4]
            fig_num = 0
            if figure == "q":
                fig_num = board.queen
            elif figure == "n":
                fig_num = board.knight
            elif figure == "r":
                fig_num = board.rook
            elif figure == "b":
                fig_num = board.bishop
            else:
                print('BAD TURN')
            now_turn = Turn(start_pos, end_pos, color, pawn=(color*10+fig_num))

        else:
            if board.get_king_pos(color) == start_pos and self.check_diff(start_pos, end_pos):
                print(start_pos, end_pos)
                if start_pos[1] > end_pos[1]:
                    start_pos = (*start_pos, (start_pos[0], 0), (start_pos[0], 3))
                else:
                    start_pos = (*start_pos, (start_pos[0], 7), (start_pos[0], 5))

                now_turn = Turn(start_pos, end_pos, color, castling=True)
            elif board.get_type_map(start_pos) == board.pawn and board.get_type_map(end_pos) == board.empty_map and abs(start_pos[1] - end_pos[1]) == 1:
                now_turn = Turn(start_pos, end_pos, color, passant=True)
            else:
                now_turn = Turn(start_pos, end_pos, color)

        return now_turn

    def do_command(self, command):
        """Does a specific command

        :param command: command
        :type command: int
        """
        self.process.stdin.write(command.strip().encode("utf-8"))
        self.process.stdin.write("\r\n".encode("utf-8"))
        self.process.stdin.flush()

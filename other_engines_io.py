"""Module for UCI engines io"""

import threading
import subprocess
from queue import Queue

from gamelogic import Turn


class Stockfish:
    """Class to use stockfish"""
    def __init__(self, threads_num):
        self.process = subprocess.Popen(["./stockfish"], shell=False, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=None)

        self.process_queu = Queue()

        self.stockfish_thread = threading.Thread(target=self.read_output)

        self.stockfish_thread.deamon = True
        self.stockfish_thread.start()

        self.process.stdin.flush()
        self.history = []
        self.do_command("setoption name threads value " + str(threads_num))

    def read_output(self):
        """reading output from external process"""
        while True:
            now_line = self.process.stdout.readline()
            decoded_line = now_line.decode("utf-8")
            if "bestmove" in decoded_line:
                self.process_queu.put(decoded_line.split()[1])

    def do_turn(self, turn, board_size):
        """do_turn(self, turn, board_size) -> None"""
        start_pos = chr(turn.start_pos[1] + ord('a')) + str(board_size - turn.start_pos[0])
        end_pos = chr(turn.end_pos[1] + ord('a')) + str(board_size - turn.end_pos[0])

        self.history.append(start_pos + end_pos)

        self.do_command("position startpos moves " + " ".join(self.history))

    def get_turn(self, board_size, color):
        """get_turn(self, board, color) -> Turn"""
        while self.process_queu.empty():
            pass

        now_turn = self.process_queu.get()

        start_pos = (board_size - int(now_turn[1]), abs(ord(now_turn[0]) - ord("a")))
        end_pos = (board_size - int(now_turn[3]), abs(ord(now_turn[2]) - ord("a")))

        return Turn(start_pos, end_pos, color)

    def do_command(self, command):
        """do_command(self, command) -> None"""
        self.process.stdin.write(command.strip().encode("utf-8"))
        self.process.stdin.write("\r\n".encode("utf-8"))
        self.process.stdin.flush()

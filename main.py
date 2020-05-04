#! /usr/bin/python3

import ui
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore


from api import Api


from multiprocessing import cpu_count
import sys


def parse_args():
    parsed_args = dict()

    for index, arg in enumerate(sys.argv):
        if arg == "--mode":
            parsed_args["MODE"] = sys.argv[index + 1]
        if arg == "--help":
            parsed_args["HELP"] = True
        if arg == "--difficulty":
            parsed_args["DIFFICULTY"] = int(sys.argv[index + 1])
        if arg == "--threads":
            parsed_args["THREADS"] = int(sys.argv[index + 1])

    return parsed_args


def print_help():
    print("------ HELP MESSAGE ------")
    print(" --mode (GUI, CMD)        GUI default, to run in GUI. CMD - to run in text mode")
    print(" --difficulty (2 - 5)     Set AI difficulty. default 5")
    print(" --threads (num)          Set num of threads. default max")
    print(" --help                   Print this message")


def main():
    parsed_args = parse_args()

    if "HELP" in parsed_args:
        print_help()
        return None

    difficulty = 5
    if "DIFFICULTY" in parsed_args:
        difficulty = parsed_args["DIFFICULTY"]

    threads = cpu_count()
    if "THREADS" in parsed_args:
        threads = parsed_args["THREADS"]

    api = Api(difficulty, threads)

    if "MODE" in parsed_args and parsed_args["MODE"] == "CMD":
        api.start_cmd()
    else:
        print("Starting GUI")
        # GUI START CODE HERE
        qss_file = open('styles.qss').read()
        app = QApplication(sys.argv)
        screen = app.primaryScreen()
        size = screen.size()
    
        app.setStyleSheet(qss_file);
        main_window = ui.Main_Window(api)
        sys.exit(app.exec_())


if __name__ == "__main__":
    print("Hello, this is python chess game")
    main()

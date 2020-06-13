#! /usr/bin/python3
"""Main python_chess module file"""
# pylint: disable=missing-function-docstring

import sys
import os

from api import Api
from cmd_ui import CmdUi
import stockfish


def get_num_threads():
    return (int)(os.popen('grep -c cores /proc/cpuinfo').read())


def parse_args():
    parsed_args = dict()
    parsed_args["DEBUTS"] = True
    parsed_args["DIFFICULTY"] = 4
    parsed_args["THREADS"] = get_num_threads()
    parsed_args["HELP"] = False
    for index, arg in enumerate(sys.argv):
        if arg == "--mode":
            parsed_args["MODE"] = sys.argv[index + 1]
        if arg == "--help":
            parsed_args["HELP"] = True
        if arg == "--no_debuts":
            parsed_args["DEBUTS"] = False
        if arg == "--difficulty":
            parsed_args["DIFFICULTY"] = int(sys.argv[index + 1])
        if arg == "--threads":
            parsed_args["THREADS"] = int(sys.argv[index + 1])

    return parsed_args


def print_help():
    print("------ HELP MESSAGE ------")
    print(" --mode (GUI, CMD)        GUI default, to run in GUI. CMD - to run in text mode")
    print(" --difficulty (2 - 5)     Set AI difficulty. default 4")
    print(" --threads (num)          Set num of threads. default max")
    print(" --no_debuts              Do not load debuts")
    print(" --help                   Print this message")


def main():
    parsed_args = parse_args()

    if parsed_args["HELP"]:
        print_help()
        return None

    api = Api(parsed_args["DIFFICULTY"], parsed_args["THREADS"], parsed_args["DEBUTS"])

    if "MODE" in parsed_args:
        if parsed_args["MODE"] == "CMD":
            ui = CmdUi(api)
            ui.start()
        elif parsed_args["MODE"] == "AI":
            stockfish.main(api, parsed_args["THREADS"])
        else:
            print("Starting GUI")
            # GUI START CODE HERE
    else:
        print("Starting GUI")
        # GUI START CODE HERE

    return None


if __name__ == "__main__":
    print("Hello, this is python chess game")
    main()

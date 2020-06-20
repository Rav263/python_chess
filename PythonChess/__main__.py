#! /usr/bin/python3
"""Main python_chess module file"""
# pylint: disable=missing-function-docstring
# pylint: disable=undefined-variable
# pylint: disable=invalid-name
from multiprocessing import cpu_count
import sys
import gettext
import os

from PythonChess.api import Api
from PythonChess.cmd_ui import CmdUi
from PythonChess.ui import Gui
import PythonChess.stockfish


def parse_args():
    """Parses comand line arguments

    :return: args list
    :rtype: dict(int)
    """
    parsed_args = dict()
    parsed_args["DEBUTS"] = True
    parsed_args["DIFFICULTY"] = 4
    parsed_args["THREADS"] = cpu_count()
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
    """Prints help message
    """
    print(_("------ HELP MESSAGE ------"))
    print(_(" --mode (GUI, CMD)        GUI default, to run in GUI. CMD - to run in text mode"))
    print(_(" --difficulty (2 - 5)     Set AI difficulty. default 4"))
    print(_(" --threads (num)          Set num of threads. default max"))
    print(_(" --no_debuts              Do not load debuts"))
    print(_(" --help                   Print this message"))


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
            PythonChess.stockfish.main(api, parsed_args["THREADS"])
        else:
            print(_("Starting GUI"))
            # GUI START CODE HERE
            gui = Gui(api)
            gui.start()
    else:
        print(_("Starting GUI"))
        # GUI START CODE HERE
        gui = Gui(api)
        gui.start()

    return None


if __name__ == "__main__":
    gettext.install("locale", os.path.dirname(sys.argv[0]), names=("ngettext",))
    print(_("Hello, this is python chess game"))
    main()

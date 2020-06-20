"""CMD User Interface"""
# pylint: disable=undefined-variable
# pylint: disable=too-few-public-methods
from .io_functions import print_board, get_turn, get_color, new_game
from .io_functions import get_difficulty


class CmdUi:
    """Main cycle cmd user interface class"""
    def __init__(self, api):
        self.api = api
        self.color = get_color()

    def start(self):
        """
        Main game cycle in text mode
        """
        if self.color == 2:
            self.api.flip_board()
        while True:
            color = 1
            while True:
                if color == self.color:
                    print_board(self.api.board.board, self.api.data)
                    now_turn = get_turn(color, self.api)
                    if now_turn[0][0] == -1:
                        print(_("CHECK MATE! YOU LOSE!"))
                        break

                    self.api.do_turn(*now_turn)

                    color = 3 - color
                else:
                    print_board(self.api.board.board, self.api.data)
                    print(color)
                    now_turn = self.api.ai_turn(color)[0]

                    if now_turn == self.api.logic.NULL_TURN:
                        print(_("CHECK MATE! YOU WIN!"))
                        break
                    print(now_turn)

                    color = 3 - color
            if not new_game():
                break
            difficulty = get_difficulty()
            self.api.new_game(difficulty)
            self.color = get_color()

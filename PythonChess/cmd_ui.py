from .io_functions import print_board, get_turn, get_color, new_game
from .io_functions import get_difficulty


class CmdUi:
    def __init__(self, api):
        self.api = api
        self.color = get_color()
    
    def start(self):
        """start(self, board, data, difficulty) -> None

        Main game cycle in text mode
        """
        while True:
            color = 1 
            while True:
                if color == self.color:
                    print_board(self.api.board.board, self.api.data)
                    now_turn = get_turn(color, self.api)
                    if now_turn[0][0] == -1:
                        print("CHECK MATE! YOU LOSE!")
                        break

                    self.api.do_turn(*now_turn)
            
                    color = 3 - color
                else:
                    now_turn = self.api.ai_turn(color)[0]

                    if now_turn == self.api.logic.NULL_TURN:
                        print("CHECK MATE! YOU WIN!")
                        break
                    print(now_turn)

                    color = 3 - color
            if not new_game():
                break
            difficulty = get_difficulty()
            self.api.new_game(difficulty)
            self.color = get_color()

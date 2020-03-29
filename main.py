#! /usr/bin/python3

import field
import gamelogic
import io_functions


def main():
    # Here we need to init Field and Game logic
    data = io_functions.Data("data.dat")
    plate = field.Field(data)
    logic = gamelogic.Logic()
    # Then we need start game

    color = 1

    while True:
        io_functions.print_field(plate.field, data)
        now_turn = io_functions.get_turn(logic, color, plate)

        plate.do_turn(now_turn)

        color = 3 - color
    # Maybe if it will be in web, we must start game server
    # Or we can create some server with a few people, who play PVP


if __name__ == "__main__":
    print("Hello, this is python chess game")
    main()

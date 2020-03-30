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

    logic.start(plate, data)

    # Maybe if it will be in web, we must start game server
    # Or we can create some server with a few people, who play PVP


if __name__ == "__main__":
    print("Hello, this is python chess game")
    main()

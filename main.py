#! /usr/bin/python3

import field
import gamelogic
import io_functions


def main():
    data  = io_functions.Data("data.dat")
    plate = field.Field(data) 

    io_functions.print_field(plate.field, data)
    plate.do_turn((0,0), (2, 2))
    io_functions.print_field(plate.field, data)
    # Here we need to init Field and Game logic
    logic = gamelogic.Logic()
    # Then we need start game 
    # Maybe if it will be in web, we must start game server
    # Or we can create some server with a few people, who play PVP
    print("Hello, this is python chess game")


if __name__ == "__main__":
    main()

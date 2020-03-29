#! /usr/bin/python3

import field
import gamelogic

def main():
    plate = field.Field() 
    # Here we need to init Field and Game logic
    logic = gamelogic.Logic()
    # Then we need start game 
    # Maybe if it will be in web, we must start game server
    # Or we can create some server with a few people, who play PVP
    print("Hello, this is python chess game")


if __name__ == "__main__":
    main()

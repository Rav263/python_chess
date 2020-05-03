#! /usr/bin/python3

from api import Api


def main():
    api = Api()
    api.start_cmd()
    # Maybe if it will be in web, we must start game server
    # Or we can create some server with a few people, who play PVP


if __name__ == "__main__":
    print("Hello, this is python chess game")
    main()

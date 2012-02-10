#!/usr/bin/env python2
from getpass import getpass
from gog import Gog

def main():
    username = raw_input("username: ")
    password = getpass("password: ")

    gog = Gog()
    logged_in = gog.login(username, password)
    if not logged_in:
        print("Failed to log in.")
        return

    gog.get_games()

    gog.download_extras()

if __name__ == "__main__":
    main()

# vim: set ts=4 sw=4 et:

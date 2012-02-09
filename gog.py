#!/usr/bin/env python2
"""
Back up all games with extra content from GOG.com.
"""

import BeautifulSoup
import requests

from collections import namedtuple
from zipfile import ZipFile


class Gog(object):
    """
    Class encapsulating getting a list of all games with game and extras
    downloads and the possibility to download these files.
    """

    Download = namedtuple("Download", "name url size")

    class Game(object):
        """
        Container class representing a Game with name and associated downloads.
        """

        name = ""
        code = ""
        game_downloads = []
        extras_downloads = []

        @staticmethod
        def __get_total_size(download_list):
            """Get total size of all downloads in a list of Downloads."""
            total_size = 0
            for download in download_list:
                total_size += download.size
            return total_size

        def game_size(self):
            """Get size of game downloads."""
            return self.__get_total_size(self.game_downloads)

        def extras_size(self):
            """Get size of extras for game."""
            return self.__get_total_size(self.extras_downloads)

    def __init__(self):
        self._session = requests.session()
        self.games = []

    def login(self, user, password):
        """
        Authenticate with GOG using user name (email) and password.

        Returns a boolean to indicate authentication success. Must be called
        and succeed before method "get_games".
        """
        url = "https://www.gog.com/en/login"
        payload = {"log_email": user, "log_password": password}
        rep = self._session.post(url, data=payload)

        if rep.status_code == 500:
            print "Error logging in"
            return False

        if rep.headers.get("location") != "http://www.gog.com/en/login/":
            print "Invalid user name or password"
            return False

        return True

    def get_games(self):
        """"
        Download list of all games for a user.

        Requires successful authentication with login. After executing this
        method you can access the games using the attribute "games".
        """
        myaccount = self._session.get("https://www.gog.com/en/myaccount")
        soup = BeautifulSoup.BeautifulSoup(myaccount.text)
        listcontainer = soup.find("div", id="listContainer")

        games = listcontainer.findAll("div", {"class": "tab_1_row"})
        for game_top in games:
            game = self.Game()
            game_element = game_top.find("div", {"class": "tab_1_title"})
            game_link_element = game_element.find("a")
            game.name = game_link_element.text
            game.code = game_link_element.get("href").split("/")[-1]
            categories = game_top.findAll("div", {"class": "sh_o_item"})
            game.game_downloads = self.__get_downloads(categories[0])
            if len(categories) > 1:
                game.extras_downloads = self.__get_downloads(categories[1])
            self.games.append(game)

    def __get_downloads(self, category_element):
        """Extract and return all downloads for a category. (game or extras)"""
        current_downloads = []
        downloads = category_element.findAll("div", {"class": "sh_o_i_row"})
        for download in downloads:
            name_el = download.find("div", {"class": "sh_o_i_text"})
            name = name_el.text.replace("\t", " ", 1).replace("\t", "")
            size_el = download.find("div", {"class": "sh_o_i_size_1"})
            number, unit = size_el.text.split()
            multi = 1024 if unit == "GB" else 1
            size = float(number) * multi
            if download.find("a"):
                url = download.find("a").get("href")
            else:
                # Slice is to remove window.top.location='' around url
                url = download.get("onclick")[21:-1]
            current_download = self.Download(name, url, size)
            current_downloads.append(current_download)
        return current_downloads

    def __verify_zip(filename):
        """Verify existence and integrity of a zip file."""
        is_ok = False
        try:
            with ZipFile(filename, "r") as zip_file:
                is_ok = zip_file.testzip() == None
        except IOError as e:
            pass
        return is_ok

# vim: set ts=4 sw=4 et:

"""
Back up all games with extra content from GOG.com.
"""
from __future__ import print_function

import BeautifulSoup
import requests
import time
import sys

from collections import namedtuple
from os import path, mkdir
from zipfile import ZipFile


class Gog(object):
    """
    Class encapsulating getting a list of all games with game and extras
    downloads and the possibility to download these files.
    """

    Download = namedtuple("Download", "name url size")
    Download_status = namedtuple(
        "Download_status",
        "success bytes_downloaded time_for_download"
    )

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
            print("Error logging in")
            return False

        if rep.headers.get("location") != "http://www.gog.com/en/login/":
            print("Invalid user name or password")
            return False

        return True

    def get_games(self):
        """"
        Download list of all games for a user.

        Requires successful authentication with login. After executing this
        method you can access the games using the attribute "games".
        """
        print("Getting games...", end="")
        sys.stdout.flush()

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
        print("ok")

    def download_games(self):
        for game in self.games:
            print("### %s ###" % game.name)
            try:
                mkdir(game.code)
            except OSError:
                pass
            game_folder = path.abspath(game.code)
            for game_download in game.game_downloads:
                number, unit = self.__format_bytes(game_download.size)
                print("Downloading %s (%.1f %s)..." % (
                    game_download.name,
                    number,
                    unit
                ), end="")
                sys.stdout.flush()

                download_status = self.__download(
                    game_download.url,
                    game_folder
                )
                if download_status.success:
                    print("success (%s)" % (self.__calculate_speed(
                        download_status.bytes_downloaded,
                        download_status.time_for_download
                    )))
                else:
                    print("failed")

    def download_extras(self):
        for game in self.games:
            print("### %s ###" % game.name)
            try:
                mkdir(game.code)
            except OSError:
                pass
            game_folder = path.abspath(game.code)
            for extra in game.extras_downloads:
                number, unit = self.__format_bytes(extra.size)
                print("Downloading %s (%.1f %s)..." % (
                    extra.name,
                    number,
                    unit
                ), end="")
                sys.stdout.flush()

                download_status = self.__download(extra.url, game_folder)
                if download_status.success:
                    print("success (%s)" % (self.__calculate_speed(
                        download_status.bytes_downloaded,
                        download_status.time_for_download
                    )))
                else:
                    print("failed")

    def __get_downloads(self, category_element):
        """Extract and return all downloads for a category. (game or extras)"""
        current_downloads = []
        downloads = category_element.findAll("div", {"class": "sh_o_i_row"})
        for download in downloads:
            name_el = download.find("div", {"class": "sh_o_i_text"})
            name = name_el.text.replace("\t", " ", 1).replace("\t", "")
            size_el = download.find("div", {"class": "sh_o_i_size_1"})
            number, unit = size_el.text.split()
            multi = 2 ** 30 if unit == "GB" else 2 ** 20
            size = float(number) * multi
            if download.find("a"):
                url = download.find("a").get("href")
            else:
                # Slice is to remove window.top.location='' around url
                url = download.get("onclick")[21:-1]
            current_download = self.Download(name, url, size)
            current_downloads.append(current_download)
        return current_downloads

    @staticmethod
    def __verify_zip(filename):
        """Verify existence and integrity of a zip file."""
        is_ok = False
        try:
            with ZipFile(filename, "r") as zip_file:
                is_ok = zip_file.testzip() is None
        except IOError:
            pass
        return is_ok

    @staticmethod
    def __extract_file_name(url):
        # Extract file name between last '/' and optional '?'.
        # E.g. http://host/path/file.zip?code -> file.zip
        return url.rpartition("/")[2].partition("?")[0]

    @staticmethod
    def __format_bytes(number):
        """
        Format a number of bytes to the correct value for a unit.

        Returns a tuple with the number for a unit and the unit.
        Example: 1536 Byte would return (1.5, "KB")
        """
        if number >= 2 ** 30:
            return number / 2 ** 30, "GB"
        if number >= 2 ** 20:
            return number / 2 ** 20, "MB"
        if number >= 2 ** 10:
            return number / 2 ** 10, "KB"
        return number, "B"

    def __calculate_speed(self, bytes_downloaded, time_for_download):
        """
        Format the downloaded number of bytes in a time for a unit.

        Returns a string with the number to one decimal place and the unit.
        Example: 1536 Byte in 1 sec would return "1.5 KB/s"

        If the number of bytes downloaded is zero, returns the string "found"
        to indicate that the file was already found on disk.
        """
        if bytes_downloaded == 0:
            return "found"

        bytes_per_second = bytes_downloaded / time_for_download
        return "%.1f %s/s" % self.__format_bytes(bytes_per_second)

    def __download(self, url, target_folder):
        """
        Download the file specified by url to the target folder.

        Returns a tuple with the download success as first element parameter,
        the bytes read as second element and time passed as third element.
        """
        rep = self._session.get(url)
        if rep.status_code != 200:
            return self.Download_status(False, 0, 0)

        filename = self.__extract_file_name(rep.url)
        target_file = path.join(target_folder, filename)

        if path.exists(target_file):
            if filename.endswith("zip"):
                is_valid = self.__verify_zip(target_file)
                if is_valid:
                    return self.Download_status(True, 0, 1)

        bytes_read = 0
        start = time.clock()
        try:
            with open(target_file, "wb") as output:
                for chunk in rep.iter_content():
                    bytes_read += len(chunk)
                    output.write(chunk)
        except IOError:
            # TODO: Print error information
            return self.Download_status(False, 0, 0)

        time_passed = time.clock() - start
        # Download was faster than timer, avoid null division.
        if not time_passed:
            time_passed = 1

        if filename.endswith("zip"):
            is_valid = self.__verify_zip(target_file)
            if not is_valid:
                return self.Download_status(False, 0, 0)
        return self.Download_status(True, bytes_read, time_passed)

# vim: set ts=4 sw=4 et:

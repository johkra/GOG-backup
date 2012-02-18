GOG-Backup
==========

GOG-Backup is a simple program to backup all your games and extras from
GOG.com.

You can download its executable from the `github Download page`_.

.. _github Download page: https://github.com/johkra/GOG-backup/downloads

How to use
----------

Drop the cli.exe file inside the directory where you want to store the
downloads. The program will create folders for each game using the same
naming scheme as the official downloader. If you put it into your GOG
downloader directory, it will not download any game files you've already
downloaded using the official downloader.

You can double-click on the exe file or open a command prompt window,
navigate to the directory where you stored the cli.exe file and type "cli" to
start the program. Opening a command line prompt is recommended as you will be
able to view program output even after the program has finished running.

When the program has started, enter your GOG.com login data and wait for the
downloads to finish. There's no progress indicator during a download, but you
will be shown the download speed once a download has finished.

You can stop the program and it will not re-download files you have already
downloaded when you start it again. Be aware, however, that the program can
not resume partially completed downloads. Please delete such files before
starting the program.

How to use when you have Python installed (also for Linux and Mac)
------------------------------------------------------------------

The program has been tested with Python 2.7. Other versions might work, but
have not been tested.

You can get the Python code either by cloning this project or downloading a
zip_ or tar_ file with the code.

.. _zip: https://github.com/johkra/GOG-backup/zipball/master
.. _tar: https://github.com/johkra/GOG-backup/tarball/master

In order to run the program, you need to have BeautifulSoup and requests
installed. The easiest way is to install them with pip_::

    pip install -r requirements.txt

.. _pip: http.//pypi.python.org/pypi/pip

Afterwards just execute the cli.py script with Python and use the program as
described above.

How to create an exe from the code
----------------------------------

When you use Windows, you can create an exe file so you can execute the program
without having to install Python and the required libraries. Note that exe
files are provided for download on github, see the first section of this
README.

You need to have Python and the requirements installed as described in the
previous section. To build an exe, please also install setuptools_ and py2exe_.

.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _py2exe: http://www.py2exe.org

Then execute the following in the source directory to build the exe file::

    python setup.py py2exe

This will build an exe file containing the Python runtime and all required
libraries in the dist directory.
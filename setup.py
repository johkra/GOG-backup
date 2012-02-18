from distutils.core import setup
import zipfile
import certifi
import os
import py2exe
import shutil

shutil.copyfile("py2exe_certifi.py", "certifi.py")

py2exe_options = {"includes": ["certifi"], "bundle_files": 1,
                  "dll_excludes": ["w9xpopen.exe"],
                  "optimize": 2, "compressed": True}

setup(
    console=['cli.py'],
    zipfile=None,
    options={"py2exe": py2exe_options}
)

os.remove("certifi.py")

with zipfile.ZipFile(os.path.join("dist", "cli.exe"), "a") as library:
    library.write(certifi.where(), "cacerts.pem", zipfile.ZIP_DEFLATED)
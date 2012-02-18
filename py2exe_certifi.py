import atexit
import os
import sys
import tempfile
import zipfile

def where():
    target = tempfile.mkdtemp()

    def delete_on_exit():
        os.remove(os.path.join(target, "cacerts.pem"))
        os.rmdir(target)

    atexit.register(delete_on_exit)

    with zipfile.ZipFile(sys.executable) as library:
        library.extract("cacerts.pem", target)

    return os.path.join(target, "cacerts.pem")

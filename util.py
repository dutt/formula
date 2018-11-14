import os, sys

class Size:
    def __init__(self, width, height):
        self.width  = width
        self.height = height

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<size w={}, h={}>".format(self.width, self.height)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

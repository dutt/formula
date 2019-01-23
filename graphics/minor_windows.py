#from graphics.story_window import StoryWindow
from graphics.window import TextWindow
from util import resource_path


#class WelcomeWindow(TextWindow):
#    PATH = resource_path("data/help/welcome.txt")

#    def __init__(self, constants, visible=False):
#        super().__init__(constants, visible, path=WelcomeWindow.PATH, next_window=StoryWindow)


class GeneralHelpWindow(TextWindow):
    PATH = resource_path("data/help/general.txt")

    def __init__(self, constants, visible=False):
        super().__init__(constants, visible, path=GeneralHelpWindow.PATH, next_window=None)

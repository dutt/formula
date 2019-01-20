import os

import util


class StoryData:
    def __init__(self, loader):
        self.loader = loader
        self.current_story_idx = 0
        self.current_page_idx = 0
        self.section = None
        self.load_current()

    def load_current(self):
        self.section = self.loader.sections[self.current_story_idx]

    def next_story(self):
        self.current_story_idx += 1
        self.load_current()

    @property
    def current_content(self):
        return self.section.content

class StorySection:
    def __init__(self, floor, content):
        self.floor = floor
        self.content = content


class StoryLoader:
    def __init__(self):
        self.sections = []
        path = util.resource_path("data/story")
        self.load(path)

    def load(self, path):
        def get_key(val):
            return int(val[len("floor."):-4])

        files = sorted(os.listdir(path), key=get_key)
        for file in files:
            filepath = os.path.join(path, file)
            section = self.load_section(filepath)
            self.sections.append(section)

    def load_section(self, filepath):
        with open(filepath, 'r') as reader:
            content = reader.read()
        base = os.path.basename(filepath)
        base = os.path.splitext(base)[0]
        return StorySection(base, content)

    def get(self, floor):
        return self.sections[floor]

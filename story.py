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

    @property
    def current_page(self):
        return self.section.pages[self.current_page_idx]

    @property
    def page_count(self):
        return len(self.section.pages)

    @property
    def page_num(self):
        return self.current_page_idx+1

    @property
    def is_last_page(self):
        return self.current_page_idx+1 >= len(self.section.pages)

    def next_story(self):
        self.current_page_idx = 0
        self.current_story_idx += 1
        self.load_current()

    def next_page(self):
        self.current_page_idx += 1


class StorySection:
    def __init__(self, floor, pages):
        self.floor = floor
        self.pages = pages


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
        num = int(base.split(".")[1])
        pages = content.split("----")
        pages = [page.strip() for page in pages]
        return StorySection(base, pages)

    def get(self, floor):
        return self.sections[floor]

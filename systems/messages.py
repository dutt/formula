import textwrap

import tcod


class Message:
    def __init__(self, text, color=tcod.white):
        self.text = text
        self.color = color
        self.id = -1

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<msg: {}>".format(self.text)


class MessageLog:
    def __init__(self, width):
        self.messages = []
        self.width = width
        self.offset = 0
        self.last_id = 0

    def add_message(self, msg):
        msg.id = self.last_id
        self.last_id += 1
        lines = textwrap.wrap(msg.text, self.width)
        print("LOG: {} {}".format(msg.id, msg.text))
        for line in lines:
            self.messages.append(Message("{}: {}".format(msg.id, line), msg.color))

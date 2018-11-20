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
    def __init__(self, x, size):
        self.messages = []
        self.x = x
        self.size = size
        self.last_id = 0

    def add_message(self, msg):
        msg.id = self.last_id
        self.last_id += 1
        lines = textwrap.wrap(msg.text, self.size.width)

        for line in lines:
            if len(self.messages) == self.size.height:
                del self.messages[0]
            self.messages.append(Message(line, msg.color))

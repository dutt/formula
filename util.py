
class Size:
    def __init__(self, width, height):
        self.width  = width
        self.height = height

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<size w={}, h={}>".format(self.width, self.height)

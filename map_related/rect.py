class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        cx = int((self.x1 + self.x2) / 2)
        cy = int((self.y1 + self.y2) / 2)
        return cx, cy

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    def contains(self, x, y):
        return x >= self.x1 and x <= self.x2 and y >= self.y1 and y <= self.y2

    def __str__(self):
        return "<rect x1={} x2={} y1={} y2={}".format(self.x1, self.x2, self.y1, self.y2)

    def __repr__(self):
        return str(self)

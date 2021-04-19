class Cursor:
    x = 0
    y = 0
    def __init__(self, y_, x_):
        self.x = x_
        self.y = y_

    def __lt__(self, other):
        return [self.y, self.x] < [other.y, other.x]

    def __le__(self, other):
        return [self.y, self.x] <= [other.y, other.x]

    def __ge__(self, other):
        return [self.y, self.x] >= [other.y, other.x]

    def __gt__(self, other):
        return [self.y, self.x] > [other.y, other.x]

    def __eq__(self, other):
        return [self.y, self.x] == [other.y, other.x]

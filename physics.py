from math import sin, cos, sqrt, atan2

PI = 3.141592
DEG2RAD = PI / 180
RAD2DEG = 180 / PI

def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    return 0

def vec2point(vec):
    return Point(cos(vec.dir) * vec.size, sin(vec.dir) * vec.size)

def point2vec(point):
    return Vec(point.size(), atan2(point.y, point.x))

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def size(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    def __iadd__(self, other):
        if isinstance(other, Point):
            self.x += other.x
            self.y += other.y

            return self
        elif isinstance(other, Vec):
            self += vec2point(other)

            return self
        else:
            raise TypeError

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        else:
            raise TypeError

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Point(self.x * other, self.y * other)
        else:
            raise TypeError

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Point(self.x / other, self.y / other)
        else:
            raise TypeError

    def __iter__(self):
        yield from [self.x, self.y]

    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            raise IndexError

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError

    def __str__(self):
        return "Point({}, {})".format(self.x, self.y)


class Vec:
    def __init__(self, size=1, dir=0):
        self.size = size
        self.dir = dir

    def __mul__(self, other):
        return Vec(self.size * other, self.dir)

class Size(Point):
    @property
    def width(self):
        return self.x

    @property
    def height(self):
        return self.y

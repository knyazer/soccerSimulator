from math import sin, cos, sqrt, atan2

PI = 3.141592
DEG2RAD = PI / 180
RAD2DEG = 180 / PI

def angleCheck(x):
    while x >= 2 * PI:
        x -= 2 * PI

    while x < 0:
        x += 2 * PI

    return x

def adduction(x):
    while x > PI:
        x -= 2 * PI

    while x < -PI:
        x += 2 * PI

    return x

def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    return 0

def avgAngle(x):
    return atan2(sum([sin(el) for el in x]), sum(cos(el) for el in x))

def angleDelta(a, b):
    a = angleCheck(a)
    b = angleCheck(b)

    if abs(a - b) < PI:
        return abs(a - b)

    return 2 * PI - abs(a - b)

def getProj(vec, angle):
    sz = cos(angle - vec.dir) * abs(vec.size)

    if sz < 0:
        angle += PI
    return Vec(abs(sz), angleCheck(angle))

def getMirrorProj(vec, angle):
    return Vec(vec.size, angleCheck(angle + (angle - vec.dir)))

def vec2point(vec):
    return Point(cos(vec.dir), sin(vec.dir)) * vec.size

def point2vec(point):
    return Vec(point.size(), atan2(point.y, point.x))

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def fSize(self):
        return self.x ** 2 + self.y ** 2

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
        elif isinstance(other, (int, float)):
            return Point(self.x + other, self.y + other)
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

    def __lt__(self, other):
        if isinstance(other, (Point, Size)):
            return [self.x < other.x, self.y < other.y]
        elif isinstance(other, (int, float)):
            return [self.x < other, self.y < other]
        else:
            raise TypeError

    def __gt__(self, other):
        if isinstance(other, (Point, Size)):
            return [self.x > other.x, self.y > other.y]
        elif isinstance(other, (int, float)):
            return [self.x > other, self.y > other]
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
        return f"Point({self.x}, {self.y})"

class Vec:
    def __init__(self, size=1, dir=0):
        self.size = size
        self.dir = dir

    def __mul__(self, other):
        return Vec(self.size * other, self.dir)

    def __sub__(self, other):
        return point2vec(vec2point(self) - vec2point(other))

    def __add__(self, other):
        return point2vec(vec2point(self) + vec2point(other))

    def __str__(self):
        return f"Vector({self.size}, {self.dir})"

class Size(Point):
    @property
    def width(self):
        return self.x

    @property
    def height(self):
        return self.y

class AABB:
    def __init__(self, min=Point(), max=Point()):
        self.min = min
        self.max = max

    def collide(self, other):
        if self.max.x < other.min.x or self.min.x > other.max.x or self.max.y < other.min.y or self.min.y > other.max.y:
            return False

        return True

    def update(self, min=None, max=None):
        if min != None:
            self.min = min

        if max != None:
            self.max = max

class Object:
    def __init__(self, mass=0, pos=0, vel=0):
        self.setMass(mass)

        self.pos = pos
        self.vel = vel

        self.AABB = AABB()

    def update(self, *args):
        pass

    def setMass(self, mass):
        self.mass = mass

        ### Calculate inverted mass, 0 means infinity
        if self.mass == 0:
            self.iMass = 0
        else:
            self.iMass = 1 / mass

    def collide(self, other):
        return False

class Circle(Object):
    def __init__(self, r=1, *args, **kwargs):
        super(Object, self).__init__(*args, **kwargs)

        self.r = r
        self.AABB.update(self.pos - r, self.pos + r)

    def consist(self, point):
        return (point - pos).fSize() < (self.r ** 2)

    def collide(self, other):
        if isinstance(other, Rectangle):
            pass#return any(self.consist(other.vertexes()))
        else:
            pass

def Rectangle(Object):
    def __init__(self, size=Size(), *args, **kwargs):
        super(Object, self).__init__(*args, **kwargs)

        self.AABB.update(self.pos - size / 2, self.pos + size / 2)

    def consist(self, point):
        min = self.pos - self.size / 2
        max = self.pos + self.size / 2

        if point.x < min.x or point.y < min.y or point.x > max.x or point.y > max.y:
            return False

        return True

    def collide(self, other, checkAABB=True):
        ### Check bounding boxes colliding
        if checkAABB and not self.AABB.collide(other.AABB):
            return False

        if isinstance(other, Rectangle):
            return True

        elif isinstance(other, Circle):
            return other.collide(self, checkAABB=False)

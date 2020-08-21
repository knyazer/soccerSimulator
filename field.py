from physics import *

class FieldSingleton:
    def __init__(self):
        self.size = Size(2.4, 1.8)

    def touch(self, obj):
        intersectionsList = (obj.pos + obj.r > self.size / 2) + (obj.pos - obj.r < -self.size / 2)
        angles = [0, PI / 2, PI, PI * 3 / 2]
        if any(intersectionsList):
            res = []
            for i in range(4):
                if intersectionsList[i]:
                    res.append(angles[i])
            return True, res
        else:
            return False, None

Field = FieldSingleton()

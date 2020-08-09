from physics import *

dt = 0.03

class Robot:
    def __init__(self):
        self.pos = Point(0, 0)
        self.angle = 0
        self.r = 0.11
        self.wheelsR = 0.08

        self.vel = Vec(0, 0)

        self.wheels = [Wheel(45 * DEG2RAD), Wheel(135 * DEG2RAD), Wheel(225 * DEG2RAD), Wheel(310 * DEG2RAD)]
        self.wheels[0].vel = 0.1
        #self.wheels[2].vel = -0.1

        self.maxAbsVel = 3

    def calcRotation(self):
        omega = 0

        for wheel in self.wheels:
            omega += wheel.vel * self.wheelsR

        return omega

    def calcVel(self):
        wholeVel = Point(0, 0)
        for wheel in self.wheels:
            wholeVel += Point(cos(wheel.angle) * wheel.vel, sin(wheel.angle) * wheel.vel)

        velWithoutFriction = point2vec(wholeVel)

        return velWithoutFriction

    def update(self):
        self.angle += self.calcRotation()

        self.vel = self.calcVel()
        self.vel.dir += self.angle

        self.pos += self.vel * dt

class Wheel:
    def __init__(self, angle=0):
        self.vel = 0
        self.acc = 0

        self.nFriction = 0.01
        self.friction = 0.5

        self.angle = angle

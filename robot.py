from physics import *

MAX_VEL = 3
FRICTION = 0.05

class Ball:
    def __init__(self):
        self.pos = Point(0, 0)
        self.vel = Vec(0, 0)

        self.r = 0.035
        self.bounceFactor = 0.4
        self.friction = 0.03

    def update(self, dt):
        self.pos += vec2point(self.vel) * dt
        self.vel.size -= self.friction

        if self.vel.size < 0:
            self.vel.size = 0

class Robot:
    def __init__(self):
        self.pos = Point(0, 0)
        self.angle = 0

        self.r = 0.11
        self.wheelsR = 0.08
        self.m = 2.2

        self.vel = Vec(0, 0)

        self.wheels = [Wheel(45 * DEG2RAD), Wheel(135 * DEG2RAD), Wheel(225 * DEG2RAD), Wheel(315 * DEG2RAD)]
        self.wheels[0].target = 0.5
        self.wheels[2].target = -0.5;

    def calcOmega(self):
        vels = [x.vel for x in self.wheels]
        omega = sum(vels) / len(self.wheels)

        dOmega = 0
        delta = [0] * 4
        for i, wheel in enumerate(self.wheels):
            delta[i] = wheel.vel - omega
            if abs(delta[i]) > FRICTION:
                delta[i] = sign(delta[i]) * FRICTION
            dOmega += delta[i]

        if sign(dOmega + omega) != sign(omega):
            omega = 0
        else:
            omega = omega + dOmega

        return omega / self.wheelsR

    def calcVel(self):
        wholeVel = Point(0, 0)
        for wheel in self.wheels:
            wholeVel += Point(cos(wheel.angle), sin(wheel.angle)) * wheel.vel

        velNF = point2vec(wholeVel)

        deltaVel = Point()
        for i, wheel in enumerate(self.wheels):
            dV = cos(velNF.dir - wheel.angle) * velNF.size - wheel.vel
            deltaVel += Point(cos(wheel.angle), sin(wheel.angle)) * dV

        deltaVelVec = point2vec(deltaVel)
        if deltaVelVec.size > FRICTION * 4:
            deltaVelVec.size = FRICTION * 4

        return point2vec(wholeVel - vec2point(deltaVelVec))

class Wheel:
    def __init__(self, angle=0):
        self.vel = 0
        self.target = 0
        self.acc = 15
        self.angle = angle

    def update(self, dt=0.001):
        if abs(abs(self.vel) - abs(self.target)) > self.acc * dt:
            self.vel += self.acc * dt * sign(self.target - self.vel)
        else:
            self.vel = self.target

        if self.vel > MAX_VEL:
            self.vel = MAX_VEL

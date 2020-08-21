from physics import *

MAX_VEL = 3
FRICTION = 0.05

class Ball:
    def __init__(self):
        self.pos = Point(0, 0)
        self.vel = Vec(1.5, PI / 4)

        self.r = 0.035
        self.bounceFactor = 0.7
        self.friction = 0.1

    def update(self, dt):
        self.pos += vec2point(self.vel) * dt
        self.vel.size -= self.friction * dt

        if self.vel.size < 0:
            self.vel.size = 0

class Robot:
    def __init__(self):
        self.pos = Point(0.5, 0)
        self.angle = 0

        self.r = 0.11
        self.wheelsR = 0.08
        self.m = 2.2

        self.vel = Vec(0, 0)

        self.wheels = [Wheel(45 * DEG2RAD), Wheel(135 * DEG2RAD), Wheel(225 * DEG2RAD), Wheel(315 * DEG2RAD)]

    def touch(self, obj):
        delta = point2vec(obj.pos - self.pos)
        if delta.size <= self.r + obj.r:
            return True, [delta.dir]
        else:
            return False, None

    def setMotors(self, vel):
        [wheel.set(vel[i]) for i, wheel in enumerate(self.wheels)]

    def move(self, vel, dir, heading):
        if abs(vel) > 2:
            vel = 2 * sign(vel)

        dir += PI

        _dir = abs(dir);
        while (_dir > PI / 2):
            _dir -= PI / 2
        _dir = min(_dir, PI / 2 - _dir)

        vel *= 1.0 / cos(_dir)

        err = heading - self.angle
        err = adduction(err)
        u = err * 5

        if abs(u) > 0.3:
            u = sign(u) * 0.3

        v = [(vel * sin(wheel.angle + dir - self.angle)) for wheel in self.wheels]
        k = abs(vel) / max([abs(x) for x in v])
        v = [(vm * k + u) for vm in v]

        self.setMotors(v)

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
        self.acc = 25
        self.angle = angle

    def update(self, dt=0.001):
        if abs(abs(self.vel) - abs(self.target)) > self.acc * dt:
            self.vel += self.acc * dt * sign(self.target - self.vel)
        else:
            self.vel = self.target

        if self.vel > MAX_VEL:
            self.vel = MAX_VEL

    def set(self, value):
        self.target = value

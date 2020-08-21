from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPainter, QPen, QBrush
from PyQt5.QtCore import QTimer, Qt
from palette import *
from physics import *
from robot import *
from field import *
from time import time

class PhysEngine:
    def __init__(self, simulationTime=0.001, simulationSpeed=1):
        self.robots = [Robot()]
        self.ball = Ball()
        self.iterationsPerSecond = 1000 # Default value, will be autobalanced
        self.targetSimulationTime = simulationTime / simulationSpeed
        self.simulationSpeed = simulationSpeed

        self.dir = 0
        self.vel = 0.2

    def updateSimulationParams(self, simulationTime, simulationSpeed):
        self.targetSimulationTime = simulationTime / simulationSpeed
        self.simulationSpeed = simulationSpeed

    def update(self):
        ts = time()

        ### Calculate current time delta per iteration
        dt = self.simulationSpeed / self.iterationsPerSecond
        its = round(self.iterationsPerSecond * self.targetSimulationTime)

        for i in range(its):
            for robot in self.robots:
                ### Apply orientation changes
                robot.angle += robot.calcOmega() * dt

                ### Calculate velocity
                robot.vel = robot.calcVel()
                robot.vel.dir += robot.angle

                ### Detect and process touches
                complete, normal = Field.touch(robot)
                if complete:
                    for nrm in normal:
                        if angleDelta(robot.vel.dir, nrm) < PI / 2:
                            robot.vel = getProj(robot.vel, nrm + PI / 2)

                complete, normal = robot.touch(self.ball)
                if complete:
                    for nrm in normal:
                        ### Go to robot local coordinate system
                        lVel = self.ball.vel - robot.vel
                        if angleDelta(lVel.dir, nrm) > PI / 2:
                            print(self.ball.vel.size, self.robots[0].vel.size, lVel.size)
                            self.ball.vel = getMirrorProj(lVel, nrm + PI / 2) * self.ball.bounceFactor + getProj(robot.vel, nrm)
                            print(self.ball.vel.size)

                ### Apply velocity
                robot.pos += robot.vel * dt

                ### Apply acceleration
                for wheel in robot.wheels:
                    wheel.update(dt)

            ### Process touches
            complete, normal = Field.touch(self.ball)
            if complete:
                for nrm in normal:
                    if angleDelta(self.ball.vel.dir, nrm) < PI / 2:
                        self.ball.vel = getMirrorProj(self.ball.vel, nrm + PI / 2) * self.ball.bounceFactor

            ### Apply physics
            self.ball.update(dt)

        self.robots[0].move(self.vel, self.dir, 0)

        ### CPU load balancing
        if time() - ts > self.targetSimulationTime:
            self.iterationsPerSecond /= 1.04
        else:
            self.iterationsPerSecond *= 1.04

        if self.iterationsPerSecond <= (1 / self.targetSimulationTime):
            self.iterationsPerSecond = (1 / self.targetSimulationTime)

    def setRobotTarget(self, point):
        delta = self.robots[0].pos - point
        self.dir = atan2(delta.x, delta.y)
        self.vel = delta.size()

class GraphEngine:
    def __init__(self, painter, engine, canvas):
        self.painter = painter
        self.engine = engine
        self.canvas = canvas
        self.size = Size(0, 0)

    def draw(self):
        self.painter.begin(self.canvas)
        self.painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        noPen = QPen()
        noPen.setStyle(Qt.NoPen)

        ### Draw Background
        backgroundPen = QPen(Palette(Grey))

        backgroundBrush = QBrush(Palette(LightGrey))
        backgroundBrush.setStyle(Qt.BDiagPattern)

        self.painter.setPen(backgroundPen)
        self.painter.setBrush(backgroundBrush)

        self.painter.drawRect(0, 0, self.size.width, self.size.height)

        ### Draw field
        fieldBoundPen = QPen(QColor(5, 5, 5))
        fieldBoundPen.setWidth(3)
        fieldBoundPen.setJoinStyle(Qt.RoundJoin)

        self.painter.setPen(fieldBoundPen)
        self.painter.setBrush(Palette(Green))

        fieldBoundX, fieldBoundY = self.transform(-Field.size / 2)
        self.painter.drawRect(fieldBoundX, fieldBoundY, Field.size.width * self.scaleFactor, Field.size.height * self.scaleFactor)


        ### Draw robots
        for robot in self.engine.robots:
            ### Apply radius (scale) transformation
            r = robot.r * self.scaleFactor

            ### Apply coordinates transformation
            posX, posY = self.transform(robot.pos)

            self.painter.save()

            self.painter.translate(posX, posY)

            self.painter.rotate(robot.angle * RAD2DEG)

            ### Set dark and transparent color for border of robots
            self.painter.setPen(QPen(QColor(64, 64, 64, 64)))
            self.painter.setBrush(Palette(Grey))

            self.painter.drawEllipse(-r, -r, r * 2, r * 2)

            pen = QPen(Palette(DarkGrey))
            pen.setWidth(1)

            self.painter.setPen(pen)
            self.painter.setBrush(Palette(DarkGrey))

            self.painter.drawLine(0, 0, r * 0.7, 0)

            self.painter.restore()

        ### Draw ball
        self.painter.setPen(noPen)
        self.painter.setBrush(Palette(Red))

        r = self.engine.ball.r * self.scaleFactor
        x, y = self.transform(self.engine.ball.pos)
        self.painter.drawEllipse(x - r, y - r, r * 2, r * 2)

        self.painter.end()

    def resizeEvent(self, e):
        self.size = Size(e.size().width(), e.size().height())

        self.scaleFactor = (self.size.width - 10) / Field.size.width

    def transform(self, point):
        return (self.size / 2) + point * self.scaleFactor

    def reverseTransform(self, point):
        return (point - self.size / 2) / self.scaleFactor


class CanvasArea(QtWidgets.QWidget):
    def __init__(self, *args):
        super(QtWidgets.QWidget, self).__init__(*args)

        TIME_PER_FRAME_MS = 16
        QUALITY_PERFORMANCE = 10

        self.pEngine = PhysEngine(TIME_PER_FRAME_MS / (1000 * 2), QUALITY_PERFORMANCE)

        self.gEngine = GraphEngine(QPainter(), self.pEngine, self)

        self.mainTimer = QTimer(self, timeout=self.systemUpdate, interval=TIME_PER_FRAME_MS)
        self.mainTimer.start()

        self.setMouseTracking(True)

    def systemUpdate(self, *args):
        self.pEngine.update()
        self.update()

    def paintEvent(self, event):
        self.gEngine.draw()

    def resizeEvent(self, event):
        self.gEngine.resizeEvent(event)

    def mousePressEvent(self, event):
        print(event.x(), event.y())

        self.pEngine.setRobotTarget(self.gEngine.reverseTransform(Point(event.x(), event.y())))


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(884, 663)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter_2 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.splitter = QtWidgets.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.textArea = QtWidgets.QTextEdit(self.splitter)
        self.textArea.setObjectName("textArea")

        self.canvasArea = CanvasArea(self.splitter)

        self.canvasArea.setObjectName("canvasArea")
        self.infoArea = QtWidgets.QScrollArea(self.splitter_2)
        self.infoArea.setWidgetResizable(True)
        self.infoArea.setObjectName("infoArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 864, 174))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.infoArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.splitter_2, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 884, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

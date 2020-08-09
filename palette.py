import csv
from PyQt5.QtGui import QColor

White = 0
Pink = 1
Grey = 2
Green = 3
LightGrey = 4
DarkGrey = 5

class SingletonPalette:
    def __init__(self):
        self.load()

    def clear(self):
        self.data = []

    def add(self, value):
        self.data.append(QColor(0, 0, 0))
        self.data[-1].setNamedColor(value)

    def load(self):
        ### Trying to read configuration file
        try:
            with open("palette.txt") as file:
                self.clear()
                for row in csv.reader(file):
                    self.add(row)

        except Exception as e:
            print("%s while processing palette file\nFalling back to default palette" % e)

            self.clear()
            for val in ['#f0f0f0', '#ffd4d4', '#a0a0a0', '#23ac50', '#bbb', '#555']:
                self.add(val)

    def __call__(self, color):
        return self.data[color]

Palette = SingletonPalette()

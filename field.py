from physics import *

class FieldSingleton:
    def __init__(self):
        self.size = Size(2.4, 1.8)

Field = FieldSingleton()

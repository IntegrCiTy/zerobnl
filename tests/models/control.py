class Model:
    def __init__(self):
        self.flow = 0.0
        self.SoC = 0.0
        self.io = 0.0

    def step(self, _):
        if self.SoC > 0.75 and self.io == 1.0:
            self.io = 0.0
        if self.SoC < 0.25 and self.io == 0.0:
            self.io = 1.0

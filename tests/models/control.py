class Model:
    def __init__(self):
        self.SoC = 0.0
        self.io = 0.0

    def step(self, value):
        if self.SoC > 0.95 and self.io == 1.0:
            self.io = 0.0
        if self.SoC < 0.05 and self.io == 0.0:
            self.io = 1.0

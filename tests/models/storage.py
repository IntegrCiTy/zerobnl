class Model:
    def __init__(self):
        self.capacity = 0.0

        self.i_flow = 0.0

        self.SoC = 0.0

    def step(self, value):
        self.SoC += (self.i_flow - 75) / self.capacity
        self.SoC = max(0, min(self.SoC, 1))

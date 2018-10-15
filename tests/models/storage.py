import numpy as np


class Model:
    def __init__(self):
        self.capacity = 0.0

        self.i_flow = 0.0

        self.SoC = 0.0

    def step(self, value):
        self.SoC -= value * np.random.normal(200, 10) / 60
        self.SoC += value * self.i_flow

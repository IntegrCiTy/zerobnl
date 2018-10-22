class Model:
    def __init__(self):
        self.p_nom = 0.0

        self.io = 0.0

        self.conso = 0.0
        self.o_flow = 0.0

    def step(self, value):
        self.conso = self.io * self.p_nom
        self.o_flow = self.io * self.p_nom

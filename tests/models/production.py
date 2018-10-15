class Model:
    def __init__(self):
        self.p_nom = 0.0

        self.io = 0.0

        self.conso = 0.0
        self.o_flow = 0.0

    def step(self, _):
        self.conso = self.io * self.p_nom
        self.o_flow = 0.9*self.o_flow

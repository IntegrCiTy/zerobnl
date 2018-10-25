class Model:
    def __init__(self):
        self.consoA = 0.0
        self.consoB = 0.0

        self.total = 0.0

    def step(self, value):
        self.total = self.consoA + self.consoB

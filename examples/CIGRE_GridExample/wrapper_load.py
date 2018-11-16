import numpy as np

from zerobnl.kernel import Node


class Load(Node):
    def __init__(self):
        super().__init__()

        self.loc = 0
        self.scale = 1.0

        self.pf = 0.1

        self.p_kw = 0
        self.q_kvar = 0

    def set_attribute(self, attr, value):
        super().set_attribute(attr, value)
        setattr(self, attr, value)

    def get_attribute(self, attr):
        super().get_attribute(attr)
        return getattr(self, attr)

    def step(self, value):
        super().step(value)
        self.p_kw = round(np.random.normal(self.loc, self.scale), 2)
        self.q_kvar = round(max(0.0, self.p_kw * self.pf), 2)


if __name__ == "__main__":
    node = Load()
    node.run()

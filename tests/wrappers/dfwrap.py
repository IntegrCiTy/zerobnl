from zerobnl.kernel import Node

import numpy as np
import pandas as pd


class MyNode(Node):
    def __init__(self):
        super().__init__()
        self.a = 0
        self.b = 0

        self.y = None

        self.c = None

        self.df = pd.DataFrame(np.random.uniform(size=(5, 10)))

    def set_attribute(self, attr, value):
        """This method is called to set an attribute of the model to a given value, you need to adapt it to your model."""
        super().set_attribute(attr, value)  # Keep this line, it triggers the parent class method.
        setattr(self, attr, value)

    def get_attribute(self, attr):
        """This method is called to get the value of an attribute, you need to adapt it to your model."""
        super().get_attribute(attr)  # Keep this line, it triggers the parent class method.
        return getattr(self, attr)

    def step(self, value):
        """This method is called to make a step, you need to adapt it to your model."""
        super().step(value)  # Keep this line, it triggers the parent class method.
        self.y = np.random.choice([-1, 0, 1])
        self.b = self.a + self.y * self.c
        self.df = pd.DataFrame(np.random.uniform(size=(5, 10)))
        self.save_attribute("y")
        self.save_attribute("df")


if __name__ == "__main__":
    node = MyNode()
    node.run()

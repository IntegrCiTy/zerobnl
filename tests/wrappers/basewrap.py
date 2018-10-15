from zerobnl.kernel import Node


class MyNode(Node):
    def __init__(self):
        super().__init__()
        model = getattr(__import__(self.parameters["model"], fromlist=["Model"]), "Model")
        self.model = model()

    def get_attribute(self, attr):
        super().get_attribute(attr)
        getattr(self.model, attr)

    def set_attribute(self, attr, value):
        super().set_attribute(attr, value)
        setattr(self.model, attr, value)

    def step(self, value):
        super().step(value)
        self.model.step(value)


if __name__ == "__main__":
    node = MyNode()
    node.run()

import json

from docopt import docopt
from zerobnl.core import Node


class MyNode(Node):
    """docstring for Model"""

    def __init__(self, name, group, inputs_map, outputs, init_values):
        super(MyNode, self).__init__(name, group, inputs_map, outputs, init_values)

        self.a = 0
        self.b = 0

        self.c = None

    def set_attribute(self, attr, value):
        super(MyNode, self).set_attribute(attr, value)
        setattr(self, attr, value)

    def get_attribute(self, attr):
        super(MyNode, self).get_attribute(attr)
        getattr(self, attr)

    def step(self, value, unit):
        super(MyNode, self).step(value, unit)
        self.b = self.a + self.c


if __name__ == "__main__":
    args = docopt(Node.DOC, version="0.0.1")

    with open(Node.ATTRIBUTE_FILE) as json_data:
        attrs = json.load(json_data)

    with open(Node.INIT_VALUES_FILE) as json_data:
        init_val = json.load(json_data)

    i_map = attrs["to_set"]
    o_list = attrs["to_get"]

    node = MyNode(name=args["<name>"], group=args["<group>"], inputs_map=i_map, outputs=o_list, init_values=init_val)

    node.run()

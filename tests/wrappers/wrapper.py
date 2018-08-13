import os
import json

from docopt import docopt
from zerobnl.core import Node


class Model(Node):
    """docstring for Model"""
    def __init__(self, name, group, zmq_sub, zmq_push, inputs_map, outputs):
        super(Model, self).__init__(name, group, zmq_sub, zmq_push, inputs_map, outputs)
        

if __name__ == '__main__':
    args = docopt(Node.DOC, version="0.0.1")

    with open('node_attributes.json') as f:
        attrs = json.load(f)

    i_map = attrs["to_set"]
    o_list = attrs["to_get"]

    node = Node(
        name=args["<name>"],
        group=args["<group>"],
        zmq_sub=os.environ["ZMQ_SUB_ADDRESS"],
        zmq_push=os.environ["ZMQ_PUSH_ADDRESS"],
        inputs_map=i_map,
        outputs=o_list
    )

    node.run()

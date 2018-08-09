import os
import ast
import zmq

from docopt import docopt

from zerobnl import __version__
from zerobnl.logs import logger

# This doc is used to make the wrapper callable by command line and gather easily all the given parameters
doc = """>>> ZEROBNL node wrapper command <<<
Usage:
    node.py (<name> <group> <zmq-sub> <zmq-push>) [<inputs-map> <outputs>]
    node.py -h | --help
    node.py --version

Options
    <name>          name of the node
    <group>         simulation group of the node
    <zmq-sub>       tcp address and port used to subscribe to orchestrator's messages
    <zmq-push>      tcp address and port used to push messages to orchestrator
    
    <inputs-map>    dictionary mapping other nodes attributes to node's attributes to set
    <outputs>       list of output attributes (used by other nodes)
     
    -h --help       show this
    --version       show version
"""


class Node:
    """docstring for Node"""

    CONTEXT = zmq.Context()
    DOC = doc

    def __init__(self, name, group, zmq_sub, zmq_push, inputs_map, outputs):

        self._name = name
        self._group = group
        self._inputs_map = inputs_map
        self._outputs = outputs

        logger.debug("Node {} created in group {}".format(name, group))

        self._sub = self.CONTEXT.socket(zmq.SUB)
        self._sub.connect(zmq_sub)
        self._sub.setsockopt_string(zmq.SUBSCRIBE, self._group)
        self._sub.setsockopt_string(zmq.SUBSCRIBE, "ALL")

        logger.debug("{} -> SUB to {}".format(self._name, zmq_sub))

        self._sender = self.CONTEXT.socket(zmq.PUSH)
        self._sender.connect(zmq_push)

        logger.debug("{} -> PUSH to {}".format(self._name, zmq_push))

    def set_attribute(self, attr, value):
        """[TO OVERRIDE] The set_attribute() method is called to set an attribute of the model to a given value."""
        logger.debug("{} -> attribute {} set to value {}".format(self._name, attr, value))

    def get_attribute(self, attr):
        """[TO OVERRIDE] The get_attribute() method is called to get the value of an attribute of the model."""
        logger.debug("{} -> get attribute {}".format(self._name, attr))

    def step(self, value, unit):
        """[TO OVERRIDE] The step() method is called to make a step with the model with a given step size and unit."""
        logger.debug("{} -> STEP {} {}".format(self._name, value, unit))

    def exit(self):
        """[TO OVERRIDE (if an exit action is needed)] The exit() method is called to properly close the model"""
        logger.info("{} -> EXIT".format(self._name))

    def update_inputs(self, state):
        logger.debug("{} -> UPDATE inputs".format(self._name))
        for attr_to_set, (from_node, from_attr) in self._inputs_map:
            self.set_attribute(attr_to_set, state[from_node][from_attr])

    def run(self):
        self._sender.send_string('{}'.format(self._name))
        logger.debug("{} -> RUNNING ...".format(self._name))

        while True:
            string = self._sub.recv_string()
            logger.debug("{} received {}".format(self._name, string))
            grp, act, value = string.split(" | ")

            if act == 'UPDATE':
                self.update_inputs(ast.literal_eval(value))
                self._sender.send_string('{} | Update | Done'.format(self._name))

            elif act == 'STEP':
                step, unit = value.split(":")
                self.step(step, unit)

                self._sender.send_string('{} | {} | {}'.format(self._name, "STATE", self.internal_state))
                logger.info("{} is waiting ...".format(self._name))

            elif act == 'END':
                self.exit()
                break

    @property
    def internal_state(self):
        return {attr: self.get_attribute(attr) for attr in self._outputs}


if __name__ == '__main__':
    args = docopt(Node.DOC, version=__version__)

    if not args["<inputs-map>"]:
        args["<inputs-map>"] = {}

    if not args["<outputs>"]:
        args["<outputs>"] = []

    node = Node(
        name=args["<name>"], 
        group=args["<group>"],
        zmq_sub=args["<zmq-sub>"],
        zmq_push=args["<zmq-push>"],
        inputs_map=args["<inputs-map>"],
        outputs=args["<outputs>"]
        )
    # Uncomment the following line to launch the node
    # node.run()

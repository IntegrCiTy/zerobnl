import os
import ast
import zmq
import redis
import pandas as pd
from docopt import docopt

from zerobnl.logs import logger
from zerobnl.config import *

# TODO: Create ZerOBNL-Kernel sub-module https://blog.github.com/2016-02-01-working-with-submodules/
# This doc is used to make the wrapper callable by command line and gather easily all the given parameters
doc = """>>> ZEROBNL node wrapper command <<<
Usage:
    node.py (<name> <group>)
    node.py -h | --help
    node.py --version

Options
    <name>          name of the node
    <group>         simulation group of the node

    -h --help       show this
    --version       show version
"""


class Node:
    """docstring for Node"""

    CONTEXT = zmq.Context()
    DOC = doc
    ATTRIBUTE_FILE = ATTRIBUTE_FILE
    INIT_VALUES_FILE = INIT_VALUES_FILE
    UNIT = UNIT

    def __init__(self, name, group, inputs_map, outputs, init_values, start=START):

        self._name = name
        self._group = group
        self._inputs_map = inputs_map
        self._outputs = outputs

        self._init_values = init_values

        self._time = pd.to_datetime(start)
        self._relative_simulation_time = 0.0

        # TODO: it will not work if node is local
        self._redis = redis.StrictRedis(host=REDIS_HOST_NAME, port=REDIS_PORT, db=0)

        logger.debug("Node {} just created in group {}".format(name, group))

        self._sub = self.CONTEXT.socket(zmq.SUB)

        try:
            self._sub.connect(os.environ["ZMQ_SUB_ADDRESS"])
            logger.debug("{} -> SUB to {}".format(self._name, os.environ["ZMQ_SUB_ADDRESS"]))
        except KeyError:
            self._sub.connect("tcp://{}:{}".format("localhost", port_pub_sub))
            logger.debug("{} -> SUB to {}".format(self._name, "tcp://{}:{}".format("localhost", port_pub_sub)))

        self._sub.setsockopt_string(zmq.SUBSCRIBE, self._group)
        self._sub.setsockopt_string(zmq.SUBSCRIBE, "ALL")

        self._sender = self.CONTEXT.socket(zmq.PUSH)

        try:
            self._sender.connect(os.environ["ZMQ_PUSH_ADDRESS"])
            logger.debug("{} -> PUSH to {}".format(self._name, os.environ["ZMQ_PUSH_ADDRESS"]))
        except KeyError:
            self._sender.connect("tcp://{}:{}".format("localhost", port_push_pull))
            logger.debug("{} -> PUSH to {}".format(self._name, "tcp://{}:{}".format("localhost", port_push_pull)))

    def set_attribute(self, attr, value):
        """[TO OVERRIDE] The set_attribute() method is called to set an attribute of the model to a given value."""
        logger.debug("{} -> attribute {} set to value {}".format(self._name, attr, value))

    def get_attribute(self, attr):
        """[TO OVERRIDE] The get_attribute() method is called to get the value of an attribute of the model."""
        logger.debug("{} -> get attribute {}".format(self._name, attr))

    def step(self, value, unit):
        """[TO OVERRIDE] The step() method is called to make a step with the model with a given step size and unit."""
        self._time += pd.DateOffset(**{unit: value})
        self._relative_simulation_time += value * self.UNIT[unit]
        logger.info("{} -> STEP {} {}".format(self._name, value, unit))

    def get_relative_time(self):
        """Return relative simulation time [s] (updated in the step() method)"""
        return self._relative_simulation_time

    def get_real_time(self):
        """Return real simulation time (updated in the step() method)"""
        return self._time

    def exit(self):
        """[TO OVERRIDE (if an exit action is needed)] The exit() method is called to properly close the model"""
        logger.info("{} -> EXIT".format(self._name))

    def save_attribute(self, attr):
        """The save_attribute() method can be called to properly store an internal state variable to the results DB"""
        self._send_attribute_value_to_results_db(attr, opt="X")

    def _send_attribute_value_to_results_db(self, attr, opt):
        """"""
        logger.debug("trying to save {} -> {} to RedisDB".format(self._name, attr))
        value = self.get_attribute(attr)
        logger.debug("{} -> {} = {} retrieved from model".format(self._name, attr, value))
        time = self.get_real_time()
        key = "{}||{}||{}".format(opt, self._name, attr)
        logger.debug("Ready to store {}".format(key))
        self._redis.rpush(key, value)
        self._redis.rpush(key + "||time", time)
        logger.debug("{} -> {} = {} saved to RedisDB".format(self._name, attr, value))

    def _update_inputs(self, state):
        """The update_inputs() method is called to update the input of the node with values from other nodes"""
        logger.debug("{} -> UPDATE inputs".format(self._name))
        for attr_to_set, (from_node, from_attr) in self._inputs_map.items():
            self.set_attribute(attr_to_set, state[from_node][from_attr])
            self._send_attribute_value_to_results_db(attr_to_set, opt="IN")

    def run(self):
        """The run() method is the main method of the node, it triggers the other methods
        and sorts the messages from the orchestrator"""

        logger.debug("init_values: {}".format(self._init_values))
        for attr, value in self._init_values.items():
            self.set_attribute(attr, value)

        self._sender.send_string("{}".format(self._name))
        logger.debug("{} -> RUNNING ...".format(self._name))

        while True:
            string = self._sub.recv_string()
            logger.debug("{} received {}".format(self._name, string))
            grp, act, value = string.split(" | ")

            if act == "UPDATE":
                self._update_inputs(ast.literal_eval(value))
                self._sender.send_string("{} | Update | Done".format(self._name))

            elif act == "STEP":
                step, unit = value.split(":")
                self.step(int(step), unit)

                for attr in self._outputs:
                    self._send_attribute_value_to_results_db(attr, opt="OUT")

                self._sender.send_string("{} | {} | {}".format(self._name, "STATE", self.internal_state))
                logger.debug("{} is waiting ...".format(self._name))

            elif act == "END":
                self.exit()
                break

    @property
    def internal_state(self):
        return {attr: self.get_attribute(attr) for attr in self._outputs}


if __name__ == "__main__":
    args = docopt(Node.DOC, version="0.0.1")

    node = Node(name=args["<name>"], group=args["<group>"], inputs_map={}, outputs=[], init_values={})

    node.run()

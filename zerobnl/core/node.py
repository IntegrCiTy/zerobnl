import os
import ast
import zmq
import redis
import pandas as pd

from zerobnl.logs import logger
from zerobnl.config import *


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

        self._redis = redis.StrictRedis.from_url(os.environ["REDIS_URL"])

        logger.debug("Node {} created in group {}".format(name, group))

        self._sub = self.CONTEXT.socket(zmq.SUB)
        self._sub.connect(os.environ["ZMQ_SUB_ADDRESS"])
        self._sub.setsockopt_string(zmq.SUBSCRIBE, self._group)
        self._sub.setsockopt_string(zmq.SUBSCRIBE, "ALL")

        logger.debug("{} -> SUB to {}".format(self._name, os.environ["ZMQ_SUB_ADDRESS"]))

        self._sender = self.CONTEXT.socket(zmq.PUSH)
        self._sender.connect(os.environ["ZMQ_PUSH_ADDRESS"])

        logger.debug("{} -> PUSH to {}".format(self._name, os.environ["ZMQ_PUSH_ADDRESS"]))

    def set_attribute(self, attr, value):
        """[TO OVERRIDE] The set_attribute() method is called to set an attribute of the model to a given value."""
        logger.debug("{} -> attribute {} set to value {}".format(self._name, attr, value))

    def get_attribute(self, attr):
        """[TO OVERRIDE] The get_attribute() method is called to get the value of an attribute of the model."""
        logger.debug("{} -> get attribute {}".format(self._name, attr))

    def step(self, value, unit):
        """[TO OVERRIDE] The step() method is called to make a step with the model with a given step size and unit."""
        logger.debug("TYPE offset {}".format(type(**{unit: value})))
        self._time += pd.DateOffset(**{unit: value})
        logger.info("{} -> STEP {} {}".format(self._name, value, unit))

    def exit(self):
        """[TO OVERRIDE (if an exit action is needed)] The exit() method is called to properly close the model"""
        logger.info("{} -> EXIT".format(self._name))

    def save_attribute(self, attr):
        """"""
        self._send_attribute_value_to_results_db(attr, opt="X")

    def _send_attribute_value_to_results_db(self, attr, opt):
        """"""
        value = self.get_attribute(attr)
        time = self._time
        key = "{}||{}||{}".format(opt, self._name, attr)
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
                self.step(step, unit)

                for attr in self._outputs:
                    self._send_attribute_value_to_results_db(attr, opt="OUT")

                self._sender.send_string("{} | {} | {}".format(self._name, "STATE", self.internal_state))
                logger.info("{} is waiting ...".format(self._name))

            elif act == "END":
                self.exit()
                break

    @property
    def internal_state(self):
        return {attr: self.get_attribute(attr) for attr in self._outputs}

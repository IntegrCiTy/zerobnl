import ast
import zmq
import json
import redis
import pandas as pd

from zerobnl.config import *
from zerobnl.logs import logger


class Node:
    """

    """

    def __init__(self):
        with open(NODE_CONFIG_FILE) as fp:
            config = json.load(fp)
            logger.debug("LOAD CONFIG NODE")

        self.name = config["NAME"]
        self.group = config["GROUP"]
        self.local = config["LOCAL"]

        self.input_map = ast.literal_eval(config["INPUT_MAP"])
        self.outputs = config["OUTPUTS"]
        self.init_values = config["INIT_VALUES"]
        self.parameters = config["PARAMETERS"]

        self.real_time = pd.to_datetime(config["START"])
        self.time_unit = config["TIME_UNIT"]
        self.simu_time = 0.0

        redis_host = {True: "localhost", False: REDIS_HOST_NAME}[self.local]
        self.redis = redis.StrictRedis(host=redis_host, port=REDIS_PORT, db=0)
        logger.debug("CONNECT REDIS")

        self.sub = zmq.Context().socket(zmq.SUB)
        self.sender = zmq.Context().socket(zmq.PUSH)
        logger.debug("CREATE SUB/SEND")

        zero_host = {True: "localhost", False: ORCH_HOST_NAME}[self.local]
        self.sub.connect("tcp://{}:{}".format(zero_host, PORT_PUB_SUB))
        self.sender.connect("tcp://{}:{}".format(zero_host, PORT_PUSH_PULL))
        logger.debug("CONNECT TO SUB/SEND")

        self.sub.setsockopt_string(zmq.SUBSCRIBE, self.group)
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "ALL")
        logger.debug("SUBSCRIBED TO GRP/ALL")

        logger.debug("INIT DONE")

    def set_attribute(self, attr, value):
        """[TO OVERRIDE] The set_attribute() method is called to set an attribute of the model to a given value."""
        logger.debug("SET ATTRIBUTE {} to {}".format(attr, value))

    def get_attribute(self, attr):
        """[TO OVERRIDE] The get_attribute() method is called to get the value of an attribute of the model."""
        logger.debug("GET ATTRIBUTE {}".format(attr))

    def step(self, value):
        """[TO OVERRIDE] The step() method is called to make a step with the model with a given step size and unit."""
        self.real_time += pd.DateOffset(**{self.time_unit: value})
        self.simu_time += value
        logger.debug("NEW TIME")

    def exit(self):
        """[TO OVERRIDE (if an exit action is needed)] The exit() method is called to properly close the model"""
        logger.debug("EXIT")

    def save_attribute(self, attr):
        """The save_attribute() method can be called to properly store an internal state variable to the results DB"""
        self._send_attribute_value_to_results_db(attr, opt="X")

    def _send_attribute_value_to_results_db(self, attr, value=None, opt="IN"):
        """

        :param attr:
        :param opt:
        """
        if not value:
            value = self.get_attribute(attr)
        key = "{}||{}||{}".format(opt, self.name, attr)
        self.redis.rpush(key, float(value))
        self.redis.rpush(key + "||time", str(self.real_time))

    def _update_inputs(self, state):
        """

        :param state:
        """
        logger.debug("INPUTS {}".format(state))
        for key, value in state.items():
            if key in self.input_map:
                self.set_attribute(self.input_map[key], value)
                self._send_attribute_value_to_results_db(self.input_map[key], value, opt="IN")

    def run(self):
        """

        """
        for attr, value in self.init_values.items():
            self.set_attribute(attr, value)

        self.sender.send_string("{}".format(self.name))
        logger.debug("INIT VALUES DONE")

        while True:
            string = self.sub.recv_string()
            grp, act, value = string.split(" | ")

            if act == "UPDATE":
                logger.debug("UPDATE")
                self._update_inputs(ast.literal_eval(value))
                self.sender.send_string("{} | Update | Done".format(self.name))
                logger.debug("UPDATE DONE")

            elif act == "STEP":
                logger.debug("STEP")
                self.step(float(value))
                state = {o: self.get_attribute(o) for o in self.outputs}
                for attr, value in state.items():
                    self._send_attribute_value_to_results_db(attr, value, opt="OUT")
                logger.debug("STATE {}".format(state))
                self.sender.send_string("{} | {} | {}".format(self.name, "STATE", state))
                logger.debug("STEP DONE")

            elif act == "END":
                self.exit()
                break

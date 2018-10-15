import ast
import zmq
import json

from zerobnl.config import *
from zerobnl.logs import logger


class Master:
    """

    """

    def __init__(self):
        with open(ORCH_CONFIG_FILE) as fp:
            config = json.load(fp)

        self.sequence = config["SEQUENCE"]
        self.steps = config["STEPS"]
        self.current_state = {}

        self.pub = zmq.Context().socket(zmq.PUB)
        self.pub.bind("tcp://*:{}".format(PORT_PUB_SUB))

        self.receiver = zmq.Context().socket(zmq.PULL)
        self.receiver.bind("tcp://*:{}".format(PORT_PUSH_PULL))

    def wait_for_nodes(self, n):
        ack = 0
        answer = []
        while ack < n:
            answer.append(self.receiver.recv_string())
            ack += 1
        return answer

    def send_current_state_for_update(self):
        self.pub.send_string("{} | {} | {}".format("ALL", "UPDATE", self.current_state))
        self.wait_for_nodes(sum(self.sequence))

    def make_step(self, idx_group, step):
        self.pub.send_string("GRP{} | {} | {}".format(idx_group, "STEP", step))
        for answer in self.wait_for_nodes(self.sequence[idx_group]):
            node, _, values = answer.split(" | ")
            values = ast.literal_eval(values)
            for key, value in values.items():
                self.current_state[(node, key)] = value

    def run(self):
        self.wait_for_nodes(sum(self.sequence))
        for idx, step in enumerate(self.steps):
            logger.debug("STEP {}/{}".format(idx, len(self.steps)))
            for idx_group in range(len(self.sequence)):
                self.send_current_state_for_update()
                self.make_step(idx_group, step)

        self.pub.send_string("{} | {} | {}".format("ALL", "END", 0))

import json
import zmq
import ast

from zerobnl.logs import logger
from zerobnl.config import port_pub_sub, port_push_pull, SEQUENCE_FILE, STEPS_FILE

from docopt import docopt

# This doc is used to make the orchestrator callable by command line and gather easily all the given parameters
doc = """>>> ZEROBNL orchestrator command <<<
Usage:
    orch.py [--port-pub=<pub> --port-pull=<pull>]
    orch.py -h | --help
    orch.py --version
Options
    --port-pub=<pub>    TCP port used to publish messages to nodes [default: {}]
    --port-pull=<pull>  TCP port used to pull messages from nodes [default: {}]

    -h --help           show this
    --version           show version
""".format(
    port_pub_sub, port_push_pull
)


class Orch:
    """docstring for Orch"""

    CONTEXT = zmq.Context()
    DOC = doc
    SEQUENCE_FILE = SEQUENCE_FILE
    STEPS_FILE = STEPS_FILE

    def __init__(self, sequence, steps, port_pub, port_pull):

        self._sequence = sequence  # [["GRP1", 2], ["GRP2", 1]]
        self._steps = steps  # [60, 60, 60, 60] (in sec)
        self._state = {}

        logger.debug("ORCH -> created")

        self._pub = self.CONTEXT.socket(zmq.PUB)
        self._pub.bind("tcp://*:{}".format(port_pub))

        logger.debug("ORCH -> PUB to {}".format(port_pub))

        self._receiver = self.CONTEXT.socket(zmq.PULL)
        self._receiver.bind("tcp://*:{}".format(port_pull))

        logger.debug("ORCH -> PULL to {}".format(port_pull))

    def wait_all_nodes_to_connect(self):
        """The wait_all_nodes_to_connect() method is called at the beginning of the simulation in order to wait
        for all the nodes to be connected and ready before launching the simulation steps."""
        logger.info("ORCH is waiting for all nodes to connect...")

        ack = 0
        val = sum([nbr[1] for nbr in self._sequence])
        while ack < val:
            self._receiver.recv()
            ack += 1
            logger.info("Nodes connected: {}/{}".format(ack, val))

    def update_attributes(self, step, grp, nbr):
        """The update_attributes() method is used to send to nodes the last state of the complete system
        in order for the nodes to update theri inputs."""
        logger.debug("ORCH -> GRP {}, UPDATE {}".format(grp, step))
        self._pub.send_string("{} | {} | {}".format(grp, "UPDATE", self._state))

        ack = 0
        while ack < nbr:
            self._receiver.recv_string()
            ack += 1

    def make_step(self, step, unit, grp, nbr):
        """The make_step() method allow to make a simulation step for a group,
        and used at each step for each group defined in the simulation sequence."""
        logger.debug("ORCH -> GRP {}, STEP {}".format(grp, step))
        self._pub.send_string("{} | {} | {}:{}".format(grp, "STEP", step, unit))

        ack = 0
        while ack < nbr:
            string = self._receiver.recv_string()
            node, _, value = string.split(" | ")

            node_state = ast.literal_eval(value)

            if node not in self._state.keys():
                self._state[node] = {}

            for attr, value in node_state.items():
                self._state[node][attr] = value

            ack += 1
            logger.debug("ORCH -> STEP {} {}/{}".format(step, ack, nbr))

        logger.debug("STATE: {}".format(self._state))

    def run(self):
        """The run() method is the main method of the orchestrator, it triggers the other methods."""
        self.wait_all_nodes_to_connect()

        for idx_step, step in enumerate(self._steps):
            logger.info("ORCH -> STEP {}/{}: {} {}".format(idx_step, len(self._steps), step, "seconds"))

            for j, grp in enumerate(self._sequence):
                if idx_step != 0:
                    self.update_attributes(step, grp[0], grp[1])
                self.make_step(step, "seconds", grp[0], grp[1])

        logger.info("ORCH -> Work done, sending EXIT to all nodes")
        self._pub.send_string("{} | {} | {}".format("ALL", "END", 0))


if __name__ == "__main__":
    args = docopt(Orch.DOC, version="0.0.1")

    with open(Orch.SEQUENCE_FILE) as json_data:
        seq = json.load(json_data)

    with open(Orch.STEPS_FILE) as json_data:
        ste = json.load(json_data)

    orch = Orch(sequence=seq, steps=ste, port_pub=args["--port-pub"], port_pull=args["--port-pull"])

    orch.run()

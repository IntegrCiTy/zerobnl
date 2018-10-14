import ast
import json


class Master:
    """

    """

    CONFIG_FILE = "config_master.json"

    def __init__(self):
        with open(self.CONFIG_FILE) as fp:
            config = json.load(fp)

        self.sequence = config["SEQUENCE"]
        self.steps = config["STEPS"]
        self.current_state = {}

        # TODO: proper zeromq connections
        self.pub = None
        self.receiver = None

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
            for key, value in values:
                self.current_state[(node, key)] = value

    def run(self):
        self.wait_for_nodes(sum(self.sequence))
        for step in self.steps:
            for idx_group in range(len(self.sequence)):
                self.send_current_state_for_update()
                self.make_step(idx_group, step)

        self.pub.send_string("{} | {} | {}".format("ALL", "END", 0))


if __name__ == "__main__":
    orch = Master()
    orch.run()

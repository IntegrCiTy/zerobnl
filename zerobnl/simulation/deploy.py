import os
import json
import shutil
import docker
from zerobnl.config import *

from zerobnl.simulation import CoSimCreator


def generate_and_add_master_file_to_orchestrator_folder(folder):
    fname = "main.py"
    with open(os.path.join(folder, fname), "w") as f:
        f.write(ORCH_STR_FILE)


class CoSimDeploy(CoSimCreator):
    def __init__(self):
        super().__init__()

        self.docker_client = docker.from_env()
        self.simulation_docker_network = None

    def create_and_fill_folders_to_mount_into_nodes(self):
        if os.path.exists(TEMP_FOLDER) and os.path.isdir(TEMP_FOLDER):
            shutil.rmtree(TEMP_FOLDER)

        # TODO: put everything in a single json file
        for node, values in self.nodes.iterrows():
            node_folder = os.path.join(TEMP_FOLDER, node.lower())
            os.makedirs(node_folder)

            shutil.copy(values["Wrapper"], node_folder)
            shutil.copy(values["Dockerfile"], node_folder)

            for file in values["Files"]:
                shutil.copy(file, os.path.join(TEMP_FOLDER, node.lower()))

            input_map = self.get_input_map(node)

            config = {
                "NAME": node,
                "GROUP": "GRP{}".format(self.get_node_group(node)),
                "LOCAL": values["Dockerfile"],
                "INPUT_MAP": {str(key): val for key, val in input_map.items()},
                "OUTPUTS": [a[0] for a in values["ToGet"]],
                "INIT_VALUES": values["InitVal"],
                "PARAMETERS": values["Parameters"],
                "START": self.start,
                "TIME_UNIT": self.time_unit,
            }

            with open(os.path.join(node_folder, NODE_CONFIG_FILE), "w") as fp:
                json.dump(config, fp)

    def create_and_fill_orchestrator_folder(self):
        orch_folder = os.path.join(TEMP_FOLDER, ORCH_FOLDER)
        os.makedirs(orch_folder)

        generate_and_add_master_file_to_orchestrator_folder(orch_folder)

        config = {"SEQUENCE": [len(group) for group in self.sequence], "STEPS": self.steps}
        with open(os.path.join(orch_folder, ORCH_CONFIG_FILE), "w") as fp:
            json.dump(config, fp)

    def launch_redis_and_docker_network(self):
        self.simulation_docker_network = self.docker_client.networks.create_network(SIM_NET, driver="bridge")

        redis = self.docker_client.containers.run(
            "redis:4-alpine",
            hostname=REDIS_HOST_NAME,
            network=self.simulation_docker_network.name,
            ports={"{}/tcp".format(REDIS_PORT): REDIS_PORT},
            detach=True,
        )

        while redis.status != "running":
            redis = self.docker_client.containers.get(redis.name)

    def run_orchestrator_and_nodes(self):
        pass

import os
import json
import shutil
import docker
from zerobnl.config import *

from zerobnl.simulation import CoSimCreator


class CoSimDeploy(CoSimCreator):
    def __init__(self):
        super().__init__()

        self.docker_client = docker.from_env()

    def create_and_fill_folders_to_mount_into_nodes(self):
        if os.path.exists(TEMP_FOLDER) and os.path.isdir(TEMP_FOLDER):
            shutil.rmtree(TEMP_FOLDER)

        # TODO: put everything in a single json file
        for node, values in self.nodes.iterrows():
            node_folder = os.path.join(TEMP_FOLDER, node.lower())
            os.makedirs(node_folder)

            shutil.copy(values["Wrapper"], node_folder)

            with open(os.path.join(node_folder, INIT_VALUES_FILE), "w") as fp:
                json.dump(values["InitVal"], fp)

            input_map = self.get_input_map(node)
            with open(os.path.join(node_folder, INPUT_MAP_FILE), "w") as fp:
                json.dump({str(key): val for key, val in input_map.items()}, fp)

            for file in values["Files"]:
                shutil.copy(file, os.path.join(TEMP_FOLDER, node.lower()))

    def create_and_fill_orchestrator_folder(self):
        orch_folder = os.path.join(TEMP_FOLDER, ORCH_FOLDER)
        os.makedirs(orch_folder)

        # TODO: put everything in a single json file
        config = {"sequence": [len(group) for group in self.sequence], "steps": self.steps}
        with open(os.path.join(orch_folder, ORCH_CONFIG_FILE), "w") as fp:
            json.dump(config, fp)

    def launch_redis_and_docker_network(self):
        pass

    def run_orchestrator_and_nodes(self):
        pass

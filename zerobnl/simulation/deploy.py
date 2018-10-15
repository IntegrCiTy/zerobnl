import os
import json
import shutil
import docker
import subprocess
import urllib.request

from zerobnl.config import *

from zerobnl.simulation import CoSimCreator
from zerobnl.simulation.compose import create_full_yaml


def generate_and_add_master_file_to_orchestrator_folder(folder):
    with open(os.path.join(folder, ORCH_MAIN_FILE), "w") as f:
        f.write(ORCH_STR_FILE)


class CoSimDeploy(CoSimCreator):
    def __init__(self):
        super().__init__()

        self.docker_client = docker.from_env()
        self.simulation_docker_network = None

    def create_and_fill_folders_to_mount_into_nodes(self):
        if os.path.exists(TEMP_FOLDER) and os.path.isdir(TEMP_FOLDER):
            shutil.rmtree(TEMP_FOLDER)

        for node, values in self.nodes.iterrows():
            node_folder = os.path.join(TEMP_FOLDER, node.lower())
            os.makedirs(node_folder)

            shutil.copy(values["Wrapper"], os.path.join(node_folder, NODE_WRAP_FILE))
            shutil.copy(values["Dockerfile"], os.path.join(node_folder, NODE_DOCKERFILE))

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

        filename, headers = urllib.request.urlretrieve(ORCH_DOCKERFILE_URL, filename=os.path.join(orch_folder, "Dockerfile"))

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

    @staticmethod
    def docker_compose_up():
        cmd = [
            "docker-compose",
            "-f",
            os.path.join(TEMP_FOLDER, DOCKER_COMPOSE_FILE),
            "up",
            "--build",
            "--no-color",
            "--abort-on-container-exit",
        ]
        with open("nodes.log", "w") as outfile:
            subprocess.call(cmd, stdout=outfile)

    def run_orchestrator_and_nodes(self):
        self.create_and_fill_folders_to_mount_into_nodes()
        self.create_and_fill_orchestrator_folder()
        self.launch_redis_and_docker_network()
        create_full_yaml(self.nodes.index)
        self.docker_compose_up()

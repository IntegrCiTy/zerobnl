import os
import json
import redis
import shutil
import docker
import subprocess
import urllib.request

from zerobnl.config import *
from zerobnl.logs import logger

from zerobnl.simulation import CoSimCreator
from zerobnl.simulation.compose import create_full_yaml


def generate_and_add_master_file_to_orchestrator_folder(folder):
    with open(os.path.join(folder, ORCH_MAIN_FILE), "w") as f:
        f.write(ORCH_STR_FILE)


class CoSimDeploy(CoSimCreator):
    def __init__(self):
        super().__init__()

        self.docker_client = docker.from_env()

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
                "LOCAL": values["Local"],
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
        if SIM_NET not in [net.name for net in self.docker_client.networks.list()]:
            self.docker_client.networks.create(SIM_NET, driver="bridge", attachable=True)

        if REDIS_HOST_NAME in [cont.name for cont in self.docker_client.containers.list()]:
            # TODO: allow for multiple database
            redis_db = redis.StrictRedis(host="localhost", port=REDIS_PORT, db=0)
            redis_db.flushall()
        else:
            redis_db = self.docker_client.containers.run(
                "redis:4-alpine",
                name=REDIS_HOST_NAME,
                hostname=REDIS_HOST_NAME,
                network=SIM_NET,
                ports={"{}/tcp".format(REDIS_PORT): REDIS_PORT},
                auto_remove=True,
                detach=True,
            )

            while redis_db.status != "running":
                redis_db = self.docker_client.containers.get(redis_db.name)

    @staticmethod
    def docker_compose_up():
        cmd = [
            "docker-compose",
            "-f",
            os.path.join(TEMP_FOLDER, DOCKER_COMPOSE_FILE),
            "up",
            "--build",
            "--no-color",
            # "--abort-on-container-exit",
        ]
        with open("nodes.log", "w") as outfile:
            subprocess.call(cmd, stdout=outfile)

    def run(self):
        self.create_and_fill_folders_to_mount_into_nodes()
        logger.debug("CREATE NODES")
        self.create_and_fill_orchestrator_folder()
        logger.debug("CREATE ORCH")
        self.launch_redis_and_docker_network()
        logger.debug("LAUNCH NETWORK+REDIS")
        create_full_yaml(self.nodes.index)
        logger.debug("DUMP YAML")
        self.docker_compose_up()
        logger.debug("FINISHED PROCESS")

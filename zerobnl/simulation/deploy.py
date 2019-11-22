import os
import json
import redis
import shutil
import docker
import subprocess
import urllib.request

from time import time

from zerobnl.config import *
from zerobnl.logs import logger

from zerobnl.simulation import CoSimCreator
from zerobnl.simulation.compose import create_full_yaml

here = os.path.dirname(os.path.realpath(__file__))

def _generate_and_add_master_file_to_orchestrator_folder(folder):
    """Write main file to orchestrator folder

    :param folder: The path to the orchestrator folder
    """
    with open(os.path.join(folder, ORCH_MAIN_FILE), "w") as f:
        f.write(ORCH_STR_FILE)


class CoSimDeploy(CoSimCreator):
    """

    """
    def __init__(self):
        super().__init__()

        self.docker_client = docker.from_env()

    def _create_and_fill_folders_to_mount_into_nodes(self):
        """

        """
        if os.path.exists(TEMP_FOLDER) and os.path.isdir(TEMP_FOLDER):
            shutil.rmtree(TEMP_FOLDER)

        for node, values in self.nodes.iterrows():
            node_folder = os.path.join(TEMP_FOLDER, node.lower())
            os.makedirs(node_folder)

            shutil.copy(values["Wrapper"], os.path.join(node_folder, NODE_WRAP_FILE))
            shutil.copy(values["Dockerfile"], os.path.join(node_folder, NODE_DOCKERFILE))

            for file in values["Files"]:
                shutil.copy(file, os.path.join(TEMP_FOLDER, node.lower()))

            config = {
                "NAME": node,
                "GROUP": "GRP{}".format(self._get_node_group(node)),
                "LOCAL": values["Local"],
                "INPUT_MAP": str(self._get_input_map(node)),
                "OUTPUTS": [a[0] for a in values["ToGet"]],
                "INIT_VALUES": values["InitVal"],
                "PARAMETERS": values["Parameters"],
                "START": self.start,
                "TIME_UNIT": self.time_unit,
            }

            with open(os.path.join(node_folder, NODE_CONFIG_FILE), "w") as fp:
                json.dump(config, fp)

    def _create_and_fill_orchestrator_folder(self):
        """

        """
        orch_folder = os.path.join(TEMP_FOLDER, ORCH_FOLDER)
        os.makedirs(orch_folder)

        _generate_and_add_master_file_to_orchestrator_folder(orch_folder)

        dockerfile = os.path.join(here, "..", "..", "Dockerfiles", "Dockerfile")
        shutil.copy(dockerfile, os.path.join(orch_folder, "Dockerfile"))

        config = {"SEQUENCE": [len(group) for group in self.sequence], "STEPS": self.steps}
        with open(os.path.join(orch_folder, ORCH_CONFIG_FILE), "w") as fp:
            json.dump(config, fp)

    def _launch_redis_and_docker_network(self):
        """Create and launch a simulation docker network and a Redis container (for the results database)

        This method re-use the docker network or the Redis container if it's already existing.
        It also flushes all data if the Redis container is already existing.
        """
        if SIM_NET not in [net.name for net in self.docker_client.networks.list()]:
            self.docker_client.networks.create(SIM_NET, driver="bridge", attachable=True)

        if REDIS_HOST_NAME in [cont.name for cont in self.docker_client.containers.list()]:
            # TODO: allow for multiple database
            redis_db = redis.StrictRedis(host="localhost", port=REDIS_PORT, db=0)
            redis_db.flushall()
        else:
            redis_db = self.docker_client.containers.run(
                "redis:5-alpine",
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
    def _docker_compose_up():
        """Run the created docker-compose.yml file

        """
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

    def run(self):
        """Run the co-simulation

        This method deploys and run the co-simulation and waits for manual nodes to bun launched.

        >>> from zerobnl import CoSim
        >>> sim = CoSim()
        --> Create complete co-simulation graph (meta-models, environments, nodes and links) with simulation sequence
        >>> sim.run()
        """
        self._create_and_fill_folders_to_mount_into_nodes()
        logger.debug("CREATE NODES")
        self._create_and_fill_orchestrator_folder()
        logger.debug("CREATE ORCH")
        self._launch_redis_and_docker_network()
        logger.debug("LAUNCH NETWORK+REDIS")
        nodes_to_run = self.nodes.loc[self.nodes["Local"] == False].index
        create_full_yaml(nodes_to_run)
        logger.debug("DUMP YAML")
        local_nodes = self.nodes.loc[self.nodes["Local"] == True]

        for node in local_nodes.index:
            logger.warning(
                "Local node to run in [{}] > python {}".format(os.path.join(TEMP_FOLDER, node.lower()), NODE_WRAP_FILE)
            )

        if len(local_nodes) > 0:
            logger.info("Waiting for local nodes to run...")

        start = time()
        self._docker_compose_up()
        stop = time() - start

        logger.info("Simulation finished in {} min and {} sec".format(int(stop // 60), int(round(stop % 60, 0))))
        logger.debug("FINISHED PROCESS")


    def add_container_to_simulation(self, container_name):

        if SIM_NET not in [net.name for net in self.docker_client.networks.list()]:
            sim_net = self.docker_client.networks.create(SIM_NET, driver="bridge", attachable=True)
            sim_net.connect(container_name)
        else:
            sim_net = self.docker_client.networks.get(SIM_NET)
            if container_name not in [c.name for c in sim_net.containers]:
                sim_net.connect(container_name)

import os
import yaml
from zerobnl.config import *

# docker-compose.yml skeleton to fill out using "service" entries.
BASE = {"version": "3", "services": {}, "networks": {"default": {"external": {"name": SIM_NET}}}}


def create_yaml_node_entry(node):
    entry = {
        "container_name": node.lower(),
        "command": NODE_WRAP_FILE,
        "depends_on": [ORCH_HOST_NAME],
        "build": {"context": node.lower(), "dockerfile": NODE_DOCKERFILE, "args": {"BRANCH": BRANCH}},
        "volumes": ["{}:/code".format(os.path.join(os.getcwd(), TEMP_FOLDER, node.lower()))],
    }
    return entry


def create_yaml_orch_entry():
    entry = {
        "container_name": ORCH_HOST_NAME,
        "command": ORCH_MAIN_FILE,
        "ports": ["{0}:{0}".format(PORT_PUB_SUB), "{0}:{0}".format(PORT_PUSH_PULL)],
        "build": {"context": ORCH_FOLDER, "dockerfile": "Dockerfile", "args": {"BRANCH": BRANCH}},
        "volumes": ["{}:/code".format(os.path.join(os.getcwd(), TEMP_FOLDER, ORCH_FOLDER))],
    }
    return entry


def create_full_yaml(nodes):
    to_dump = dict(BASE)
    to_dump["services"][ORCH_HOST_NAME] = create_yaml_orch_entry()
    for node in nodes:
        to_dump["services"][node.lower()] = create_yaml_node_entry(node.lower())
    with open(os.path.join(TEMP_FOLDER, DOCKER_COMPOSE_FILE), "w") as yaml_file:
        yaml.dump(to_dump, yaml_file, default_flow_style=False, indent=2)

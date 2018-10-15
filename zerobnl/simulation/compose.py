import os
from zerobnl.config import *

# docker-compose.yml skeleton to fill out using "service" entries.
BASE = {
    "version": "3",
    "services": {},
    "networks": {
        "external": {
            "default": {
                "name": SIM_NET
            }
        }
    }
}


def create_yaml_node_entry(node, wrapper, dockerfile):
    entry = {
        "container_name": node.lower(),
        "command": wrapper,
        "depends_on": [ORCH_HOST_NAME],
        "build": {"context": node.lower(), "dockerfile": dockerfile},
        "volumes": ["{}:/code".format(os.path.join(".", node.lower()))]
    }
    return entry


def create_yaml_orch_entry():
    entry = {
        "container_name": ORCH_HOST_NAME,
        "command": ORCH_MAIN_FILE,
        "ports": ["{0}/tcp:{0}".format(PORT_PUB_SUB), "{0}/tcp:{0}".format(PORT_PUSH_PULL)],
        "build": {"context": ORCH_FOLDER, "dockerfile": "Dockerfile"},
        "volumes": ["{}:/code".format(os.path.join(".", ORCH_FOLDER))]
    }
    return entry

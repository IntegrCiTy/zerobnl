import os
import yaml
import json
import shutil
import subprocess

from zerobnl.logs import logger
from zerobnl.config import *

# docker-compose.yml skeleton to fill out using "service" entries.
BASE_YML = {
    "version": '3',
    "services": {
    },
    "networks": {
        SIM_NET: {
            "driver": "bridge"
        }
    }
}

REDIS_YML = {
    "version": '3',
    "services": {
        "redis": {
            "image": "redis:alpine",
            "hostname": REDIS_HOST_NAME,
            "ports": ["{0}:{0}".format(REDIS_PORT)],
            "networks": [SIM_NET]
        }
    },
    "networks": {
        SIM_NET: {
            "driver": "bridge"
        }
    }
}


def dump_dict_to_json_in_folder(folder, data, filename):
    data_json = os.path.join(folder, filename)
    with open(data_json, "w") as outfile:
        json.dump(data, outfile)
        logger.debug("Data dumped in {}".format(outfile.name))


def create_sub_folder_in_temporary_folder(sub_folder_name):
    """

    :param sub_folder_name:
    :return:
    """
    sub_folder = os.path.join(TEMP_FOLDER, sub_folder_name.lower())
    os.makedirs(sub_folder)
    logger.debug("Folder {} created for {}".format(sub_folder, sub_folder_name))
    return sub_folder


def copy_files_to_folder(folder, *files):
    """

    :param folder:
    :param files:
    :return:
    """
    for file in files:
        shutil.copyfile(file, os.path.join(folder, os.path.basename(file)))
        logger.debug("File {} added in folder {}".format(file, folder))


def clean_temp_folder():
    """

    :return:
    """
    if os.path.isdir(TEMP_FOLDER):
        shutil.rmtree(TEMP_FOLDER)
        logger.debug("Deleted {}".format(TEMP_FOLDER))
    else:
        logger.debug("{} does not exist".format(TEMP_FOLDER))


def create_yaml_orch_entry():
    """

    :return:
    """
    entry = {
        "build": {"context": ORCH_FOLDER, "dockerfile": "Dockerfile"},
        "container_name": ORCH_FOLDER,
        "command": "orch.py",
        "ports": ["{0}:{0}".format(port_pub_sub), "{0}:{0}".format(port_push_pull)],
        "networks": [SIM_NET],
        "depends_on": [REDIS_HOST_NAME],
        "volumes": ["{}:/code".format(os.path.join(".", ORCH_FOLDER))],
    }

    logger.debug("Created yaml orchestrator entry")
    return entry


def create_yaml_node_entry(node, group, wrapper, dockerfile=None):
    """

    :param node:
    :param group:
    :param wrapper:
    :param dockerfile:
    :return:
    """
    entry = {
        "container_name": node.lower(),
        "environment": {
            "ZMQ_PUSH_ADDRESS": "tcp://orch:{}".format(port_push_pull),
            "ZMQ_SUB_ADDRESS": "tcp://orch:{}".format(port_pub_sub),
        },
        "command": "{} {} {}".format(wrapper, node, group),
        "depends_on": [ORCH_FOLDER],
        "networks": [SIM_NET],
    }

    if not dockerfile:
        dockerfile = "Dockerfile"

    entry["build"] = {"context": node.lower(), "dockerfile": dockerfile}

    entry["volumes"] = ["{}:/code".format(os.path.join(".", node.lower()))]

    logger.debug("Created yaml node entry for {}".format(node))
    return entry


def create_yaml_docker_compose(groups):
    """

    :param groups: of the form:
    {"GRP1": [("node0", "node0_wrapper.py", "Dockerfile"), ("node1", "node1_wrapper.py", "Dockerfile")]}
    :return: nothing
    """
    to_dump = dict(BASE_YML)
    to_dump["services"][ORCH_FOLDER] = create_yaml_orch_entry()

    for group, nodes in groups.items():
        for (node, wrapper, dockerfile) in nodes:
            to_dump["services"][node.lower()] = create_yaml_node_entry(node, group, wrapper, dockerfile=dockerfile)

    with open(os.path.join(TEMP_FOLDER, DOCKER_COMPOSE_FILE), "w") as yaml_file:
        yaml.dump(to_dump, yaml_file, default_flow_style=False, indent=2)
        logger.debug("Created complete docker-compose file in {}".format(DOCKER_COMPOSE_FILE))


def create_redis_yaml_docker_compose():
    to_dump = dict(REDIS_YML)
    with open(os.path.join(TEMP_FOLDER, "redis-{}".format(DOCKER_COMPOSE_FILE)), "w") as yaml_file:
        yaml.dump(to_dump, yaml_file, default_flow_style=False, indent=2)
        logger.debug("Created redis docker-compose file in redis-{}".format(DOCKER_COMPOSE_FILE))


# TODO: run redis separately
def docker_compose_up_redis():
    """

    :return:
    """
    cmd = [
        "docker-compose",
        "-f",
        os.path.join(TEMP_FOLDER, "redis-{}".format(DOCKER_COMPOSE_FILE)),
        "up",
        "redis",
        "--no-color",
        "--detach"
    ]

    subprocess.Popen(cmd)


def docker_compose_up_simulation():
    """

    :return:
    """
    cmd = [
        "docker-compose",
        "-f",
        os.path.join(TEMP_FOLDER, DOCKER_COMPOSE_FILE),
        "up",
        "--build",
        "--no-color",
    ]
    with open("nodes.log", "w") as outfile:
        subprocess.run(cmd, stdout=outfile)

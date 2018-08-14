import os
import yaml
import json
import shutil
import subprocess

from zerobnl.logs import logger
from zerobnl.config import *

# docker-compose.yml skeleton to fill out using "service" entries.
BASE = {"services": {"redis": {"image": "redis:alpine", "container_name": "redis"}}, "version": "3"}


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
        "build": {
            "context": ORCH_FOLDER,
            "dockerfile": "Dockerfile",
        },
        "container_name": ORCH_FOLDER,
        "command": "orch.py",
        "depends_on": ["redis"],
    }
    logger.debug("Created yaml orchestrator entry")
    return entry


def create_yaml_node_entry(node, group, wrapper, image=None, dockerfile=None):
    """

    :param node:
    :param group:
    :param wrapper:
    :param image:
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
    }

    if image:
        entry["image"] = image

    else:
        if not dockerfile:
            dockerfile = "Dockerfile"

        entry["build"] = {
            "context": node.lower(),
            "dockerfile": dockerfile,
        }

    logger.debug("Created yaml node entry for {}".format(node))
    return entry


def create_yaml_docker_compose(groups):
    """

    :param groups: of the form: {"GRP1": [("node0", "node0_wrapper.py"), ("node1", "node1_wrapper.py")]}
    :return: nothing
    """
    to_dump = dict(BASE)
    to_dump["services"][ORCH_FOLDER] = create_yaml_orch_entry()

    for group, nodes in groups.items():
        for (node, wrapper) in nodes:
            to_dump["services"][node.lower()] = create_yaml_node_entry(node, group, wrapper)

    with open(os.path.join(TEMP_FOLDER, DOCKER_COMPOSE_FILE), "w") as yaml_file:
        yaml.dump(to_dump, yaml_file, default_flow_style=False, indent=2)
        logger.debug("Created complete docker-compose file in {}".format(DOCKER_COMPOSE_FILE))


def run_docker_compose(build=True):
    """

    :param build:
    :return:
    """
    cmd = ["docker-compose", "-f", os.path.join(TEMP_FOLDER, DOCKER_COMPOSE_FILE), "up"]
    if build:
        cmd.append("--build")
    subprocess.run(cmd)

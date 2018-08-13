import os
import yaml
import shutil
import subprocess

from zerobnl.logs import logger
from zerobnl.config import dockerfile_folder, temporary_folder, port_pub_sub, port_push_pull, docker_compose_file

# docker-compose.yml skeleton to fill out using "service" entries.
BASE = {'services': {"redis": {"image": "redis:alpine"}}, 'version': '3'}


def create_sub_folder_in_temporary_folder(sub_folder_name):
    """

    :param sub_folder_name:
    :return:
    """
    sub_folder = os.path.join(temporary_folder, sub_folder_name)
    os.makedirs(sub_folder)
    logger.debug("Folder {} created for {}".format(sub_folder, sub_folder_name))


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
    if os.path.isdir(temporary_folder):
        shutil.rmtree(temporary_folder)
        logger.debug("Deleted {}".format(temporary_folder))
    else:
        logger.warning("{} does not exist".format(temporary_folder))


def create_yaml_orch_entry():
    """

    :return:
    """
    entry = {
        "build": {
            "context": os.path.join(temporary_folder, "ORCH"),
            "dockerfile": os.path.join(dockerfile_folder, "Dockerfile")
        },
        "container_name": "orch",
        "command": "orch.py",
        "depends_on": ["redis"]
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
        "container_name": node,
        "environment": {
            "ZMQ_PUSH_ADDRESS": "tcp://orch:{}".format(port_push_pull),
            "ZMQ_SUB_ADDRESS": "tcp://orch:{}".format(port_pub_sub),
        },
        "command": "{} {} {}".format(wrapper, node, group),
        "depends_on": ["orch"]
    }

    if image:
        entry["image"] = image

    else:
        if not dockerfile:
            dockerfile = "Dockerfile"

        entry["build"] = {
            "context": os.path.join(temporary_folder, node),
            "dockerfile": os.path.join(dockerfile_folder, dockerfile)
        }

    logger.debug("Created yaml node entry for {}".format(node))
    return entry


def create_yaml_docker_compose(groups):
    """

    :param groups: of the form: {"GRP1": [("node0", "node0_wrapper.py"), ("node1", "node1_wrapper.py")]}
    :return: nothing
    """
    to_dump = dict(BASE)
    to_dump["services"]["orch"] = create_yaml_orch_entry()

    for group, nodes in groups.items():
        for (node, wrapper) in nodes:
            to_dump["services"][node] = create_yaml_node_entry(node, group, wrapper)

    with open(os.path.join(temporary_folder, docker_compose_file), 'w') as yaml_file:
        yaml.dump(to_dump, yaml_file, default_flow_style=False, indent=2)
        logger.debug("Created complete docker-compose file in {}".format(docker_compose_file))


def run_docker_compose(build=True):
    """

    :param build:
    :return:
    """
    cmd = ["docker-compose", "-f", os.path.join(temporary_folder, docker_compose_file), "up"]
    if build:
        cmd.append("--build")
    subprocess.run(cmd)

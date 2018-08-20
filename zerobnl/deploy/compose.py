import os
import sys
import yaml
import json
import redis
import docker
import shutil
import subprocess

from zerobnl.logs import logger
from zerobnl.config import *

# docker-compose.yml skeleton to fill out using "service" entries.
BASE = {"services": {}, "version": "3"}


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


def run_redis():
    """

    :return:
    """
    client = docker.from_env()

    try:
        client.containers.run("redis:alpine", name="redis_db", ports={"6379/tcp": REDIS_PORT}, detach=True,
                              auto_remove=True)
        while client.containers.get("ict_red").status != "running":
            pass
        logger.debug("RedisDB is running")
    except docker.errors.APIError:
        redis_db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        redis_db.flushall()
        logger.debug("RedisDB is already running")


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
            "REDIS_URL": "redis://redis_db:6379"
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


def run_docker_compose():
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
        # "--force-recreate",
        # "--abort-on-container-exit"
    ]
    with open('nodes.log', "w") as outfile:
        subprocess.call(cmd, stdout=outfile)

import pytest

import docker
from zerobnl.config import *


def pytest_sessionstart(session):
    """ before session.main() is called. """
    clean_containers()


def pytest_sessionfinish(session, exitstatus):
    """ whole test run finishes. """
    clean_containers()


def clean_containers():
    client = docker.from_env()
    for c in client.containers.list():
        print(c.name)
        if TEMP_FOLDER.lower() in c.name:
            c.kill()

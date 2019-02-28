import pytest

import docker
from zerobnl.config import *

@pytest.fixture
def clean_docker(scope="function"):
    """

	"""
    import docker

    yield True
    client = docker.from_env()
    for c in client.containers.list():
        c.kill()

@pytest.fixture
def clean_folder(scope="function"):
    """

	"""
    import shutil

    yield True
    try:
        shutil.rmtree(TEMP_FOLDER)
    except FileNotFoundError:
        pass

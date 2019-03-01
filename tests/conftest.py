import pytest

import docker
from zerobnl.config import *

@pytest.fixture
def clean_docker(scope="function"):
    """
    This fixture stop all the docker containers.
	"""
    import docker

    yield 0
    client = docker.from_env()
    for c in client.containers.list(all=True):
        c.remove(force=True)

@pytest.fixture
def clean_folder(scope="function"):
    """
    This fixture removes the temporary folder (if it exists).
	"""
    import shutil

    yield 0
    try:
        shutil.rmtree(TEMP_FOLDER)
    except FileNotFoundError:
        pass

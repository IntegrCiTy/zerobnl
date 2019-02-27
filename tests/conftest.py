import pytest

import docker
from zerobnl.config import *

@pytest.fixture
def clean(scope="function"):
    """

	"""
    import docker

    yield True
    client = docker.from_env()
    for c in client.containers.list():
        if "ict_" in c.name:
            c.kill()

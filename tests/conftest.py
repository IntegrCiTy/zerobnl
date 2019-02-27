import pytest

import docker
from zerobnl.config import *

# TODO: -> https://docs.pytest.org/en/latest/fixture.html#conftest-py-sharing-fixture-functions

@pytest.fixture
def clean(scope="function"):
    """

	"""
    import docker

    yield True
    client = docker.from_env()
    for c in client.containers.list():
        if TEMP_FOLDER.lower() in c.name:
            c.kill()

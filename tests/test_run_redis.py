import pytest

import docker
from zerobnl.deploy.compose import *


@pytest.fixture()
def clean_existing_redis_containers():
    client = docker.from_env()
    for c in client.containers.list():
        if "redis" in c.name:
            c.kill()
    return client


def test_run_redis():
    client = clean_existing_redis_containers()
    run_redis()
    assert client.containers.get(REDIS_NAME).status == "running"

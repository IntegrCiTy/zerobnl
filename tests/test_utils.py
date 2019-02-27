import redis
import pickle
import docker
import numpy as np
import pandas as pd

import pytest

from zerobnl.config import *

from zerobnl.utils import save_to_redis, decode_pickle_float, encode_pickle_float

@pytest.fixture
def redis_fix(scope="function"):
    """

	"""
    import docker

    docker_client = docker.from_env()
    redis_test = docker_client.containers.run(
        "redis:5-alpine",
        name="ict_test_redis",
        ports={"{}/tcp".format(REDIS_PORT): REDIS_PORT},
        auto_remove=True,
        detach=True
    )
    yield redis_test
    c = docker_client.containers.get(redis_test.name)
    c.kill()

def test_encode_pickle_float_return_float():
    assert type(encode_pickle_float(2.0)) is float
    assert type(encode_pickle_float(2)) is float

def test_encode_pickle_float_return_bytes():
    df = pd.DataFrame(np.random.uniform(size=(10, 5)))
    assert type(encode_pickle_float(df)) is bytes

def test_decode_pickle_float_return_float():
    value = pickle.dumps(2.0)
    assert type(decode_pickle_float(value)) is float

def test_decode_pickle_float_return_df():
    df = pd.DataFrame(np.random.uniform(size=(10, 5)))
    value = pickle.dumps(df)
    assert type(decode_pickle_float(value)) is pd.DataFrame

def test_save_to_redis_float(redis_fix):
    r = redis.Redis(host='localhost', port=REDIS_PORT, db=0)
    save_to_redis(r, "name", "attr", "X", 1.0, "1991/08/09 11:32:00")
    save_to_redis(r, "name", "attr", "X", 2.0, "1994/12/02 20:17:00")
    key = "{}||{}||{}".format("X", "name", "attr")
    res = r.lrange(key, 0, -1)
    assert {decode_pickle_float(val) for val in res} == {1.0, 2.0}
    res = r.lrange(key + "||time", 0, -1)
    assert {val.decode("utf-8") for val in res} == {"1991/08/09 11:32:00", "1994/12/02 20:17:00"}

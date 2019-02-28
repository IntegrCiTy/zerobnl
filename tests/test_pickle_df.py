import os
import redis
import pandas as pd

import pytest

from zerobnl.config import *
from zerobnl import CoSim

@pytest.fixture()
def create_model():
    sim = CoSim()

    sim.create_meta_model("MetaBase", [("a", "unit")], [("b", "unit")])

    sim.create_environment(
        "EnvBase",
        os.path.join("tests", "wrappers", "dfwrap.py"),
        os.path.join("tests", "dockerfiles", "Dockerfile")
    )

    sim.add_node("Base0", "MetaBase", "EnvBase", init_values={"c": 0.50})
    sim.add_node("Base1", "MetaBase", "EnvBase", init_values={"c": 0.25})

    sim.add_link("Base0", "b", "Base1", "a")
    sim.add_link("Base1", "b", "Base0", "a")

    sim.create_sequence([["Base0"], ["Base1"]])
    sim.set_time_unit("seconds")
    sim.create_steps([15] * 4 * 60)

    return sim

def test_simulation_store_results_to_redis(create_model, clean_docker, clean_folder):
    sim = create_model
    sim.run()

    r = redis.StrictRedis(host="localhost", port=REDIS_PORT, db=0)
    assert len(r.keys()) > 0

def test_get_results_by_pattern(create_model, clean_docker, clean_folder):
    sim = create_model
    sim.run()

    sim.connect_to_results_db()
    res = sim.get_results_by_pattern("X*Base0*")
    assert set(res) == {"X||Base0||y", "X||Base0||df"}

def test_return_data_type(create_model, clean_docker, clean_folder):
    sim = create_model
    sim.run()
    sim.connect_to_results_db()
    res = sim.get_results_by_pattern("X*Base0*")

    assert type(res["X||Base0||y"]) is pd.Series
    assert type(res["X||Base0||df"]) is pd.DataFrame

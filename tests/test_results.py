import pandas as pd
import redis

from zerobnl.config import *
from tests.test_deploy import create_scenario


def test_simulation_store_results_to_redis(create_scenario, clean_docker, clean_folder):
    sim = create_scenario
    sim.run()

    r = redis.StrictRedis(host="localhost", port=REDIS_PORT, db=0)
    assert len(r.keys()) > 0


def test_get_list_of_available_results(create_scenario, clean_docker, clean_folder):
    sim = create_scenario
    sim.run()

    sim.connect_to_results_db()
    df = sim.get_list_of_available_results()

    assert type(df) == pd.DataFrame
    assert set(list(df.columns)) == {"Node", "IN/OUT", "Attribute"}
    assert len(df.index) == 9


def test_get_results_by_pattern(create_scenario, clean_docker, clean_folder):
    sim = create_scenario
    sim.run()

    sim.connect_to_results_db()
    res = sim.get_results_by_pattern("OUT*Netw*")
    assert set(res) == {"OUT||Netw||total"}
    assert type(res["OUT||Netw||total"]) == pd.Series
    assert len(res["OUT||Netw||total"].index) == 24

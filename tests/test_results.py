import pandas as pd

from tests.test_deploy import create_scenario


def test_full_simulation_results(create_scenario):
    sim = create_scenario
    sim.run()
    sim.connect_to_results_db()

    df = sim.get_list_of_available_results()
    assert type(df) == pd.DataFrame
    assert set(list(df.columns)) == {"Node", "IN/OUT", "Attribute"}
    assert len(df.index) == 17

    res = sim.get_results_by_pattern("OUT*Netw*")
    assert set(res) == {"OUT||Netw||total"}
    assert type(res["OUT||Netw||total"]) == pd.Series
    assert len(res["OUT||Netw||total"].index) == 24

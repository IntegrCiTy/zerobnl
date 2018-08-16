import pandas as pd

from tests.test_main import fix_create


def test_the_list_of_available_simulation_results():
    test_sim = fix_create()
    test_sim.run_simulation()
    test_sim.results.connect_to_results_db()
    df = test_sim.results.list_of_available_results
    assert type(df) == pd.DataFrame
    assert set(list(df.columns)) == {"Node", "IN/OUT", "Attribute"}
    assert len(df.index) == 6

    res = test_sim.results.get_results_by_pattern("IN*Base0*")
    assert set(res) == {"IN||Base0||a"}
    assert type(res["IN||Base0||a"]) == pd.Series
    assert len(res["IN||Base0||a"].index) == 9

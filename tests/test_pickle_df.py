import os
import pytest

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

def test_run(create_model, clean):
    sim = create_model
    sim.run()

    sim.connect_to_results_db()
    res = sim.get_results_by_pattern("*")
    assert res.keys == {}

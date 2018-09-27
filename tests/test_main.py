import os
import pytest
from zerobnl import Simulator as Sim


@pytest.fixture()
def fix_create():
    """
    Fixture for testing purpose creating a ready-to-run simple co-simulation

    :return: zerobnl.Simulator() with meta, models, nodes, links, groups, sequence and steps implemented
    """
    sim = Sim()

    sim.edit.add_meta(name="BaseMeta", set_attrs=["a"], get_attrs=["b"])

    sim.edit.add_model(
        name="BaseModel",
        meta="BaseMeta",
        wrapper=os.path.join("tests", "wrappers", "wrapper.py"),
        files=[os.path.join("tests", "files_to_add", "empty_file_for_testing_purpose.txt")]
    )

    sim.edit.add_node(name="Base0", model="BaseModel", init_values={"c": 0.50})

    sim.edit.add_node(name="Base1", model="BaseModel", init_values={"c": 0.25})

    sim.edit.add_link(get_node="Base0", get_attr="b", set_node="Base1", set_attr="a")
    sim.edit.add_link(get_node="Base1", get_attr="b", set_node="Base0", set_attr="a")

    grp0 = sim.edit.create_group("GRP0", "Base0")
    grp1 = sim.edit.create_group("GRP1", "Base1")

    sim.edit.create_sequence(grp0, grp1)
    sim.edit.create_steps([60] * 10)

    return sim


def test_run_simulation():
    test_sim = fix_create()
    test_sim.run_simulation()


# def test_run_simulation_logs(caplog):
#     test_sim = fix_create()
#     test_sim.run_simulation()
#     for record in caplog.records:
#         assert record.levelname in ["DEBUG", "INFO"]

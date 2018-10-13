import os
import pytest
from zerobnl.config import *

from zerobnl.simulation import CoSimDeploy


@pytest.fixture()
def create_scenario():
    sim = CoSimDeploy()

    sim.create_meta_model("MetaNetw", [("consoA", "kW"), ("consoB", "kW")], [])
    sim.create_meta_model("MetaProd", [("io", "binary")], [("conso", "kW"), ("o_flow", "m3/s")])
    sim.create_meta_model("MetaStor", [("i_flow", "m3/s")], [("SoC", "%")])
    sim.create_meta_model("MetaCtrl", [("flow", "m3/s"), ("SoC", "%")], [("io", "binary")])

    sim.create_environment("EnvBase", os.path.join("tests", "wrappers", "basewrap.py"), "DockBase")

    sim.add_node(
        "Netw",
        "MetaNetw",
        "EnvBase",
        files=[os.path.join("tests", "models", "network.py")],
        init_val={"model": "network"},
    )

    for x in ["A", "B"]:
        sim.add_node(
            "Prod{}".format(x),
            "MetaProd",
            "EnvBase",
            files=[os.path.join("tests", "models", "production.py")],
            init_val={"model": "production", "p_nom": 100.0},
        )
        sim.add_node(
            "Stor{}".format(x),
            "MetaStor",
            "EnvBase",
            files=[os.path.join("tests", "models", "storage.py")],
            init_val={"model": "storage", "capacity": 500.0},
        )
        sim.add_node(
            "Ctrl{}".format(x),
            "MetaCtrl",
            "EnvBase",
            files=[os.path.join("tests", "models", "control.py")],
            init_val={"model": "control"},
        )

    for x in ["A", "B"]:
        sim.add_link("Prod{}".format(x), "conso", "Netw", "conso{}".format(x))
        sim.add_link("Prod{}".format(x), "o_flow", "Stor{}".format(x), "i_flow")
        sim.add_link("Prod{}".format(x), "o_flow", "Ctrl{}".format(x), "flow")
        sim.add_link("Stor{}".format(x), "SoC", "Ctrl{}".format(x), "SoC")
        sim.add_link("Ctrl{}".format(x), "io", "Prod{}".format(x), "io")

    sim.create_sequence([["ProdA", "ProdB"], ["CtrlA", "CtrlB"], ["StorA", "StorB", "Netw"]])

    return sim


def test_create_and_fill_folders_to_mount_into_nodes():
    sim = create_scenario()
    sim.create_and_fill_folders_to_mount_into_nodes()
    assert set(os.listdir(TEMP_FOLDER)) == set([node.lower() for node in sim.nodes.index])
    for node in sim.nodes.index:
        assert len(os.listdir(os.path.join(TEMP_FOLDER, node.lower()))) == 4

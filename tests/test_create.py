import pandas as pd
import networkx as nx

import pytest
from zerobnl.simulation import CoSimCreator


def test_create_meta_model():
    sim = CoSimCreator()
    sim.create_meta_model("MetaBase", [("conso", "kW")], [("temp", "C")])
    assert sim.meta_models["MetaBase"] == {"ToSet": [("conso", "kW")], "ToGet": [("temp", "C")]}


def test_create_environment():
    sim = CoSimCreator()
    sim.create_environment("EnvBase", "WrapBase", "DockBase")
    assert sim.environments["EnvBase"] == {"Wrapper": "WrapBase", "Dockerfile": "DockBase"}


def test_add_node():
    sim = CoSimCreator()
    sim.create_meta_model("MetaBase", [("conso", "kW")], [("temp", "C")])
    sim.create_environment("EnvBase", "WrapBase", "DockBase")
    sim.add_node("Base0", "MetaBase", "EnvBase")
    waited = [[("conso", "kW")], [("temp", "C")], {}, {}, "WrapBase", "DockBase", [], False]
    assert type(sim.nodes.loc["Base0"]) is pd.Series
    assert sim.nodes.loc["Base0"].values.tolist() == waited
    sim.add_node("Base1", "MetaBase", "EnvBase", init_values={"c": 0.5}, files=["f1.csv"], local=True)
    waited = [[("conso", "kW")], [("temp", "C")], {"c": 0.5}, {}, "WrapBase", "DockBase", ["f1.csv"], True]
    assert sim.nodes.loc["Base1"].values.tolist() == waited


def test_add_node_no_meta():
    sim = CoSimCreator()
    sim.create_environment("EnvBase", "WrapBase", "DockBase")
    with pytest.raises(AssertionError) as e_info:
        sim.add_node("Base0", "MetaBase", "EnvBase")
    assert "Meta-model MetaBase is not defined !" in str(e_info.value)


def test_add_node_no_env():
    sim = CoSimCreator()
    sim.create_meta_model("MetaBase", [("conso", "kW")], [("temp", "C")])
    with pytest.raises(AssertionError) as e_info:
        sim.add_node("Base0", "MetaBase", "EnvBase")
    assert "Environment EnvBase is not defined !" in str(e_info.value)


def test_add_link():
    sim = CoSimCreator()
    sim.create_meta_model("MetaBase", [("a", "kW")], [("b", "kW")])
    sim.create_environment("EnvBase", "WrapBase", "DockBase")
    sim.add_node("Base0", "MetaBase", "EnvBase")
    sim.add_node("Base1", "MetaBase", "EnvBase")
    sim.add_link("Base0", "b", "Base1", "a")
    assert type(sim.links.iloc[0]) is pd.Series
    assert sim.links.iloc[0].values.tolist() == ["Base0", "b", "Base1", "a", "kW"]


def test_add_link_diff_unit():
    sim = CoSimCreator()
    sim.create_meta_model("MetaBase", [("a", "kW")], [("b", "m3/s")])
    sim.create_environment("EnvBase", "WrapBase", "DockBase")
    sim.add_node("Base0", "MetaBase", "EnvBase")
    sim.add_node("Base1", "MetaBase", "EnvBase")
    with pytest.raises(AssertionError) as e_info:
        sim.add_link("Base0", "b", "Base1", "a")
    assert "Base0.b ---> m3/s != kW ---> Base1.a" in str(e_info.value)


def test_check_node_attr_exists_and_return_unit():
    sim = CoSimCreator()
    sim.create_meta_model("MetaBase", [("a", "kW")], [("b", "kW")])
    sim.create_environment("EnvBase", "WrapBase", "DockBase")
    sim.add_node("Base0", "MetaBase", "EnvBase")
    assert sim._check_node_attr_exists_and_return_unit("Base0", "a", "ToSet") == "kW"


def test_check_node_attr_exists_and_return_unit_no_node():
    sim = CoSimCreator()
    sim.create_meta_model("MetaBase", [("a", "kW")], [("b", "kW")])
    sim.create_environment("EnvBase", "WrapBase", "DockBase")
    with pytest.raises(AssertionError) as e_info:
        sim._check_node_attr_exists_and_return_unit("Base0", "a", "ToSet")
    assert "Node Base0 is not defined !" in str(e_info.value)


def test_check_node_attr_exists_and_return_unit_no_attr():
    sim = CoSimCreator()
    sim.create_meta_model("MetaBase", [("a", "kW")], [("b", "kW")])
    sim.create_environment("EnvBase", "WrapBase", "DockBase")
    sim.add_node("Base0", "MetaBase", "EnvBase")
    with pytest.raises(AssertionError) as e_info:
        sim._check_node_attr_exists_and_return_unit("Base0", "x", "ToSet")
    assert "Attribute x is not defined for node Base0!" in str(e_info.value)


# TODO: implement test_get_graph
def test_get_graph():
    pass


# TODO: implement test_create_sequence
def test_create_sequence():
    pass


# TODO: implement test_get_input_map
def test_get_input_map():
    pass

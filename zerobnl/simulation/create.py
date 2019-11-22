import pandas as pd
import networkx as nx

from zerobnl.config import *


# TODO: write complete docstrings
class CoSimCreator:
    """

    """
    def __init__(self):
        self.meta_models = {}
        self.environments = {}

        self.nodes = pd.DataFrame(
            columns=["ToSet", "ToGet", "InitVal", "Parameters", "Wrapper", "Dockerfile", "Files", "Local", "Meta", "Env"]
        )

        self.links = pd.DataFrame(columns=["GetNode", "GetAttr", "SetNode", "SetAttr", "Unit"])

        self.sequence = None
        self.steps = None

        self.start = START
        self.time_unit = "seconds"

    def create_meta_model(self, meta_model, list_of_attrs_to_set, list_of_attrs_to_get):
        """Create a meta-model defining attributes to set (inputs) and attributes to get (output)

        :param meta_model:The name of the meta-model
        :param list_of_attrs_to_set: The list of attributes to get as tuple with unit
        :param list_of_attrs_to_get: The list of attributes to set as tuple with unit

        >>> from zerobnl import CoSim
        >>> sim = CoSim()
        >>> sim.create_meta_model("Meta", [("a", "binary")], [("b", "m3/s"), ("c", "kW")])
        """
        self.meta_models[meta_model] = {"ToSet": list_of_attrs_to_set, "ToGet": list_of_attrs_to_get}

    def create_environment(self, env, wrapper, dockerfile):
        """Create a simulation environment defining the wrapper for interacting with the model and the Dockerfile
        to deploy the environment

        :param env: The name of the environment
        :param wrapper: The path to the wrapper
        :param dockerfile: The path to the Dockerfile

        >>> from zerobnl import CoSim
        >>> sim = CoSim()
        >>> sim.create_environment("Env", "wrappers/my_wrapper.py", "dockerfiles/MyDockerfile")
        """
        self.environments[env] = {"Wrapper": wrapper, "Dockerfile": dockerfile}

    def add_node(self, node, meta, env, init_values=None, parameters=None, files=None, local=False):
        """Add a node defining the meta-model and the simulation environment

        :param node: The name of the created node
        :param meta: The name of the associated meta-model
        :param env: The name of the associated environment
        :param init_values: A dict of initial values to set to the node (default None)
        :param parameters: A dict of parameters to use in the node (default None)
        :param files: A list of path of files to add in the environment (default None)
        :param local: A boolean indicating if the node will be run manually and locally or automatically (default False)

        >>> from zerobnl import CoSim
        >>> sim = CoSim()
        ---> Create Meta meta-model and Env environement
        >>> sim.add_node("Node", "Meta", "Env", init_values={"d": 0.5}, parameters={"data_file": "mydata.csv"}, files=["data/mydata.csv"], local=True)
        """
        assert meta in self.meta_models, "Meta-model {} is not defined !".format(meta)
        assert env in self.environments, "Environment {} is not defined !".format(env)

        if not init_values:
            init_values = {}
        if not parameters:
            parameters = {}
        if not files:
            files = []

        self.nodes.loc[node] = [
            self.meta_models[meta]["ToSet"],
            self.meta_models[meta]["ToGet"],
            init_values,
            parameters,
            self.environments[env]["Wrapper"],
            self.environments[env]["Dockerfile"],
            files,
            local,
            meta,
            env
        ]

    def add_link(self, get_node, get_attr, set_node, set_attr):
        """Add a link between the attributes of two nodes

        This method check if both nodes and attributes exist and share the same unit.

        :param get_node: The name of the node to get output
        :param get_attr: The name of the attribute to get the value
        :param set_node: The name of the node to set input
        :param set_attr: The name of the attribute to set the value

        >>> from zerobnl import CoSim
        >>> sim = CoSim()
        ---> Create NodeA and NodeB
        >>> sim.add_link("NodeA", "sink_flow", "NodeB", "srce_flow")
        """
        get_unit = self._check_node_attr_exists_and_return_unit(get_node, get_attr, "ToGet")
        set_unit = self._check_node_attr_exists_and_return_unit(set_node, set_attr, "ToSet")

        assert get_unit == set_unit, "{}.{} ---> {} != {} ---> {}.{}".format(
            get_node, get_attr, get_unit, set_unit, set_node, set_attr
        )

        self.links.loc[len(self.links.index)] = [get_node, get_attr, set_node, set_attr, get_unit]

    def _check_node_attr_exists_and_return_unit(self, node, attr, set_or_get):
        """Check if a node and its associated attribute exist and return the unit of the attribute

        :param node: The name of the node to check
        :param attr: The name of the associated attribute
        :param set_or_get: A str indicating if the attribute is to set (input) or to get (output), must be in ["ToSet", "ToGet"]
        :return: The unit of the attribute
        """
        assert set_or_get in ["ToSet", "ToGet"]
        assert node in self.nodes.index, "Node {} is not defined !".format(node)

        dict_attr_unit = {n[0]: n[1] for n in self.nodes.loc[node][set_or_get]}
        assert attr in dict_attr_unit.keys(), "Attribute {} is not defined for node {}!".format(attr, node)

        return dict_attr_unit[attr]

    def get_graph(self):
        """Create and return a Networkx.DiGraph from the defined co-simulation graph

        This method create a graph using simulation node as node and links as edges.

        :return: A Networkx.Digraph

        >>> from zerobnl import CoSim
        >>> sim = CoSim()
        --> Create complete co-simulation graph (meta-models, environments, nodes and links)
        >>> g = sim.get_graph()
        """
        g = nx.DiGraph()

        for n, data in self.nodes.iterrows():
            g.add_node(n, **data.to_dict())

        for _, l in self.links.iterrows():
            g.add_edge(l["GetNode"], l["SetNode"], get_attr=l["GetAttr"], set_attr=l["SetAttr"], unit=l["Unit"])

        return g

    def create_sequence(self, sequence):
        """Define the co-simulation sequence, which nodes will be run in parallel or in sequential and in which order

        This method check that two nodes to be run in parallel doesn't share a direct link.

        :param sequence: A list of groups of nodes, each group is a list of names of nodes

        >>> from zerobnl import CoSim
        >>> sim = CoSim()
        --> Create nodes and links
        >>> sim.create_sequence([["NodeA1", "NodeA2"], ["NodeB"], ["NodeC1", "NodeC2", "NodeC3"]])
        """
        g = self.get_graph().to_undirected()

        for i, group in enumerate(sequence):
            h = g.subgraph(group)
            assert len(h.nodes) == len(group), "Node {} is not defined !".format(list(set(group) - set(h.nodes))[0])
            assert len(h.edges) == 0, "Group {} contains linked nodes !".format(i)

        self.sequence = sequence

    def _get_input_map(self, node):
        """Create an return the input map of a node

        :param node: a dict mapping a tuple containing the node and the attribute to get a value from and the attribute to update in the given node
        :return: a dict with {(GetNode, GetAttr): SetAttr}
        """
        return {
            (link["GetNode"], link["GetAttr"]): link["SetAttr"]
            for _, link in self.links.loc[self.links.SetNode == node].iterrows()
        }

    def create_steps(self, steps):
        """Define the steps to run during the simulation

        :param steps: a list of step values to run during the simulation
        >>> from zerobnl import CoSim
        >>> sim = CoSim()
        >>> sim.create_steps([10]*60*5)  # This will create 5*60=300 steps of 10 defined time unit
        """
        self.steps = steps

    def _get_node_group(self, node):
        """Return the index of a node in a defined sequence

        :param node: The name of the chosen node
        :return: the index of the node in the simulation sequence
        """
        return [node in g for g in self.sequence].index(True)

    def set_start_time(self, start):
        """Set the start date of the simulation, if not called the default value is 2000-01-01 00:00:00

        :param start: a str convertible to a datatime.datetime
        >>> from zerobnl import CoSim
        >>> sim = CoSim()
        >>> sim.set_start_time("1991-08-09 11:22:00")
        """
        self.start = start

    def set_time_unit(self, time_unit):
        """Set the time unit used in the simulation

        :param time_unit: a str defining the unit of the considered time steps
        >>> from zerobnl import CoSim
        >>> sim = CoSim()
        >>> sim.set_time_unit("minutes")
        """
        self.time_unit = time_unit

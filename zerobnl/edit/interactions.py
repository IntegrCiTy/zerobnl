import networkx as nx
import pandas as pd
import numpy as np

from zerobnl.logs import logger
from zerobnl.config import *


__all__ = ["GraphCreator"]


class Node:
    """
    Class defined to store the node's data into the networkx.MultiDiGraph() structure
    """

    def __init__(self, name, model, init_values):
        self.name = name

        self.model = model
        self.init_values = init_values

    def __repr__(self):
        return str(self.model) + " -> " + str(self.init_values)


class GraphCreator:
    """
    Class for gathering methods allowing the creation of a co-simulation graph
    """

    UNIT = UNIT

    def __init__(self):
        self.meta_models = {}
        self.models = {}
        self.graph = nx.MultiDiGraph()

        self.groups = {}
        self.sequence = []
        self.steps = []

        logger.debug("GraphCreator initialized")

    @property
    def nodes(self):
        """
        :return: a pandas.DataFrame() containing all information about the simulation nodes
        """
        return pd.DataFrame.from_dict(
            {
                node: {
                    "meta": self.models[data["node"].model]["meta"],
                    "model": data["node"].model,
                    "to_set": self.meta_models[self.models[data["node"].model]["meta"]]["set_attrs"],
                    "to_get": self.meta_models[self.models[data["node"].model]["meta"]]["get_attrs"],
                    "image": self.models[data["node"].model]["image"],
                    "dockerfile": self.models[data["node"].model]["dockerfile"],
                    "wrapper": self.models[data["node"].model]["wrapper"],
                    "files": self.models[data["node"].model]["files"],
                    "init_values": data["node"].init_values,
                }
                for node, data in self.graph.nodes(data=True)
            },
            orient="index",
        )

    @property
    def links(self):
        """
        :return: a pandas.DataFrame() containing all information about the links between the simulation nodes
        """
        return pd.DataFrame(
            [
                {
                    "get_node": get_node,
                    "get_attr": data["link"]["get_attr"],
                    "set_node": set_node,
                    "set_attr": data["link"]["set_attr"],
                }
                for get_node, set_node, data in self.graph.edges(data=True)
            ]
        )

    def add_meta(self, name, set_attrs=list(), get_attrs=list()):
        """
        Create a meta-model defining attributes to set (inputs) and to get (outputs)

        :param name: string defining the name of the meta-model
        :param set_attrs: list of string, default: None
        :param get_attrs: list of string, default: None
        :return:
        """
        self.meta_models[name] = {"set_attrs": set_attrs, "get_attrs": get_attrs}
        logger.info("Meta-model {} created.".format(name))
        return name

    def add_model(self, name, meta, wrapper, image=None, dockerfile=None, *files):
        """
        Create a model based on the corresponding meta-model

        :param name: string defining the name of the model
        :param meta: name of the corresponding meta-model
        :param wrapper: wrapper file for the model
        :param image: docker image containing environments with all the model's dependencies
        :param dockerfile: used to build the image at runtime
        :param files: optional files to add into the model's container
        :return:
        """
        if not image and not dockerfile:
            logger.error("Model {} not created: missing dockerfile or image")
            return name

        self.models[name] = {"meta": meta, "image": image, "dockerfile": dockerfile, "wrapper": wrapper, "files": files}
        logger.info("Model {} created.".format(name))
        return name

    def add_node(self, name, model, init_values=None):
        """
        Create a node based on the corresponding model

        :param name: string defining the name of the node
        :param model: name of the corresponding model
        :param init_values: a dict mapping the initial values to the model's parameters, default: None
        :return: the node's name
        """
        if init_values is None:
            init_values = {}
        node = Node(name, model, init_values)
        self.graph.add_node(node.name, node=node)
        logger.info("Node {} created.".format(name))
        return node.name

    def add_link(self, get_node, set_node, get_attr, set_attr, unit="unit"):
        """
        Create a link between two node, defining attribute to get (output) and to set (input)

        :param get_node: name of the node to get a value from
        :param set_node: name of the node to set a value to
        :param get_attr: name of the get_node's attribute to get
        :param set_attr: name of the set_node's attribute to set
        :param unit: , default: "unit" (without unit)
        :return: nothing :)
        """
        self.graph.add_edge(get_node, set_node, link={"get_attr": get_attr, "set_attr": set_attr, "unit": unit})
        logger.info("Link created {} -> {}.".format(get_node, set_node))

    def add_multiple_links_between_two_nodes(self, get_node, set_node, get_attrs, set_attrs, units=None):
        """
        Create multiple links between two nodes, defining a list of attributes to get (outputs) and to set (inputs)

        :param get_node: name of the node to get a value from
        :param set_node: name of the node to set a value to
        :param get_attrs: list of names of the get_node's attribute to get
        :param set_attrs: list of names of the set_node's attribute to set
        :param units: list of the corresponding attributes units
        :return: nothing :)
        """
        if not units:
            units = ["unit"] * len(get_attrs)
        for get_attr, set_attr, unit in zip(get_attrs, set_attrs, units):
            self.add_link(get_node, set_node, get_attr, set_attr, unit)

    def reset_graph(self):
        """
        Delete all nodes and links (without removing meta-models and models)

        :return: nothing
        """
        self.graph = nx.MultiDiGraph()
        logger.info("Reset graph")

    @property
    def interaction_graph(self):
        """
        :return: a dict containing the information about the interaction between the nodes and the co-simulation graph
        """
        return {
            "nodes": {node: {"input": row["to_set"], "output": row["to_get"]} for node, row in self.nodes.iterrows()},
            "links": [
                {
                    "output": {"node": link["get_node"], "attribute": link["get_attr"]},
                    "input": {"node": link["set_node"], "attribute": link["set_attr"]},
                }
                for i, link in self.links.iterrows()
            ],
        }

    @property
    def group_sequence(self):
        return [[grp[0], len(grp[1])] for grp in self.sequence]

    def create_group(self, name, *nodes):
        """
        Create a group for the simulation sequence verifying that none of the group's nodes are directly connected

        :param name: the name of the group
        :param nodes: some nodes names
        :return: selected nodes names as a list
        """
        h = self.graph.subgraph(nodes)
        try:
            assert len(h.edges) == 0
            logger.info("The group {} have been created.".format(nodes))
            self.groups[name] = nodes
            return [name, nodes]
        except AssertionError:
            for get_node, set_node, _ in h.edges:
                logger.warning("A direct link exists from {} to {} !".format(get_node, set_node))

    def create_sequence(self, *groups):
        """
        Create the simulation's sequence

        :param groups: some groups as list of nodes (created by self.create_group)
        :return: nothing :)
        """
        self.sequence = [g for g in groups]
        logger.info("The sequence {} have been created.".format(self.sequence))

    def create_steps(self, steps, unit="seconds"):
        """
        Create the simulation's steps

        :param steps: list of simulation time-steps to run
        :param unit: time unit of steps (default: seconds)
        :return: nothing :)
        """
        steps = np.array(steps) * self.UNIT[unit]
        self.steps = steps.tolist()
        logger.info("{} steps have been created.".format(len(steps)))

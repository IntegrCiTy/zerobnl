import pandas as pd
import networkx as nx


class CoSimCreator:
    def __init__(self):
        self.meta_models = {}
        self.environments = {}

        self.nodes = pd.DataFrame(columns=["ToSet", "ToGet", "InitVal", "Wrapper", "Dockerfile", "Files", "Local"])

        self.links = pd.DataFrame(columns=["GetNode", "GetAttr", "SetNode", "SetAttr", "Unit"])

        self.sequence = []

    def create_meta_model(self, meta_model, list_of_attrs_to_set, list_of_attrs_to_get):
        """

        :param meta_model:
        :param list_of_attrs_to_set:
        :param list_of_attrs_to_get:
        """
        self.meta_models[meta_model] = {"ToSet": list_of_attrs_to_set, "ToGet": list_of_attrs_to_get}

    def create_environment(self, env, wrapper, dockerfile):
        """

        :param env:
        :param wrapper:
        :param dockerfile:
        """
        self.environments[env] = {"Wrapper": wrapper, "Dockerfile": dockerfile}

    def add_node(self, node, meta, env, init_val=None, files=None, local=False):
        """

        :param node:
        :param meta:
        :param env:
        :param init_val:
        :param files:
        :param local:
        """
        assert meta in self.meta_models, "Meta-model {} is not defined !".format(meta)
        assert env in self.environments, "Environment {} is not defined !".format(env)

        if not init_val:
            init_val = {}
        if not files:
            files = []

        self.nodes.loc[node] = [
            self.meta_models[meta]["ToSet"],
            self.meta_models[meta]["ToGet"],
            init_val,
            self.environments[env]["Wrapper"],
            self.environments[env]["Dockerfile"],
            files,
            local
        ]

    def add_link(self, get_node, get_attr, set_node, set_attr):
        """

        :param get_node:
        :param get_attr:
        :param set_node:
        :param set_attr:
        """
        get_unit = self.check_node_attr_exists_and_return_unit(get_node, get_attr, "ToGet")
        set_unit = self.check_node_attr_exists_and_return_unit(set_node, set_attr, "ToSet")

        assert get_unit == set_unit, "{}.{} ---> {} != {} ---> {}.{}".format(get_node, get_attr, get_unit, set_unit,
                                                                             set_node, set_attr)

        self.links.loc[len(self.links.index)] = [get_node, get_attr, set_node, set_attr, get_unit]

    def check_node_attr_exists_and_return_unit(self, node, attr, set_or_get):
        """

        :param node:
        :param attr:
        :param set_or_get:
        :return:
        """
        assert node in self.nodes.index, "Node {} is not defined !".format(node)

        dict_attr_unit = {n[0]: n[1] for n in self.nodes.loc[node][set_or_get]}
        assert attr in dict_attr_unit.keys(), "Attribute {} is not defined for node {}!".format(attr, node)

        return dict_attr_unit[attr]

    def get_graph(self):
        """

        :return:
        """
        g = nx.DiGraph()

        for n, data in self.nodes.iterrows():
            g.add_node(n, **data.to_dict())

        for _, l in self.links.iterrows():
            g.add_edge(l["GetNode"], l["SetNode"], get_attr=l["GetAttr"], set_attr=l["SetAttr"], unit=l["Unit"])

        return g

    def create_sequence(self, sequence):
        """

        :param sequence:
        """
        g = self.get_graph().to_undirected()

        for i, group in enumerate(sequence):
            h = g.subgraph(group)
            assert len(h.nodes) == len(group), "Node {} is not defined !".format(list(set(group) - set(h.nodes))[0])
            assert len(h.edges) == 0, "Group {} contains linked nodes !".format(i)

        self.sequence = sequence

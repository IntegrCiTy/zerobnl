import json
import numpy as np
import pandas as pd
import pandapower as pp

from zerobnl.kernel import Node


class Grid(Node):
    def __init__(self):
        super().__init__()

        self.net = pp.create_empty_network()

        for i in ["bus", "bus_geodata", "line", "switch", "trafo", "ext_grid", "load"]:
            df = pd.DataFrame(json.load(open('{}.json'.format(i))))
            df.index = map(int, df.index)
            setattr(self.net, i, df)

    def set_attribute(self, attr, value):
        super().set_attribute(attr, value)
        table, name, col = attr.split("/")
        idx = pp.get_element_index(self.net, table, name)
        df = getattr(self.net, table)
        df.loc[idx, col] = value

    def get_attribute(self, attr):
        super().get_attribute(attr)
        if attr in ["res_line", "res_bus"]:
            return getattr(self.net, attr)
        else:
            table, name, col = attr.split("/")
            idx = pp.get_element_index(self.net, table, name)
            df = getattr(self.net, "res_"+table)
            return df.loc[idx, col]

    def step(self, value):
        super().step(value)
        pp.runpp(self.net, numba=False)
        for key in ["ext_grid/Feeder/p_kw", "ext_grid/Feeder/q_kvar"]:
            self.save_attribute(key)
        self.save_attribute("res_bus")
        self.save_attribute("res_line")

if __name__ == "__main__":
    node = Grid()
    node.run()

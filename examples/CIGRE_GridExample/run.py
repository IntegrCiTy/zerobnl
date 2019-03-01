import os
import json
import pandas as pd
import networkx as nx

import matplotlib.pyplot as plt

from zerobnl import CoSim

sim = CoSim()

data_power_grid_folder = "PowerGridData"

loads = pd.DataFrame(json.load(open(os.path.join(data_power_grid_folder, 'load.json'))))
loads.index = map(int, loads.index)

set_attrs = [("load/{}/p_kw".format(load), "kw") for load in loads.name]
set_attrs += [("load/{}/q_kvar".format(load), "kvar") for load in loads.name]

sim.create_meta_model("MetaGrid", set_attrs, [])
sim.create_environment("EnvGrid", "wrapper_grid.py", "Dockerfile_grid")

files = [os.path.join(data_power_grid_folder, f) for f in os.listdir(data_power_grid_folder)]
sim.add_node("Grid", "MetaGrid", "EnvGrid", files=files)


sim.create_meta_model("MetaLoad", [], [("p_kw", "kw"), ("q_kvar", "kvar")])
sim.create_environment("EnvLoad", "wrapper_load.py", "Dockerfile_load")

for load in loads.name:
    sim.add_node(load, "MetaLoad", "EnvLoad", init_values={"loc": 5.0, "scale": 0.5})

for load in loads.name:
    sim.add_link(load, "p_kw", "Grid", "load/{}/p_kw".format(load))
    sim.add_link(load, "q_kvar", "Grid", "load/{}/q_kvar".format(load))

sim.create_sequence([[load for load in loads.name], ["Grid"]])
sim.set_time_unit("minutes")
sim.create_steps([60] * 6)

sim.run()

sim.connect_to_results_db()
res = sim.get_results_by_pattern("X*Grid*res*")
res['X||Grid||res_line'].to_csv("res_line.csv")
res['X||Grid||res_bus'].to_csv("res_bus.csv")

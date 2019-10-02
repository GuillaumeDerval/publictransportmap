import json
import scipy.sparse.csgraph

import numpy as np
from heapq import heappop, heappush

data = json.load(open("../train_bus_simplified.json"))
walking_time = json.load(open("../distance_walking.json"))

graph = {}
for x in data:
    nei = {}
    for y, ta, tb in data[x]["nei"]:
        if y not in nei or nei[y] > tb-ta:
            nei[y] = tb-ta
    for t, y in walking_time[x]:
        if y not in nei or nei[y] > t:
            nei[y] = t
    graph[x] = nei

idx_to_name = list(graph.keys())
name_to_idx = {x: i for i, x in enumerate(idx_to_name)}

matrix = np.ones((len(idx_to_name), len(idx_to_name))) * (30*60*60)
for x, nei in graph.items():
    for y, t in nei.items():
        matrix[name_to_idx[x],name_to_idx[y]] = t
print("Matrix computed")
scipy.sparse.csgraph.floyd_warshall(matrix, overwrite=True)
print("Flow warshall done")
np.save("../allpairs_lower.npz", matrix)
#matrix = scipy.sparse.csgraph.csgraph_from_dense(matrix)

import json
import time
from collections import deque


"""
    rajoute des connection pour pouvoir faire un trajet qui s'etant sur 2 jour ???

    in  : ../produce/train_bus_simplified.json
    out : ../produce/out.json
"""

MAX_TIME = 28*60*60//10 #todo 24 or 28

print("--- Loading data")
data = json.load(open("../produce/train_bus_simplified.json"))

idx_to_name = list(data.keys())
name_to_idx = {x: i for i, x in enumerate(idx_to_name)}
print(name_to_idx)

#walking_time = json.load(open("../produce/distance_walking.json"))
#walking_time = {name_to_idx[x]: [(a, name_to_idx[b]) for a,b in y] for x, y in walking_time.items()}

def wtf(c, b):
    raise Exception("wtf")
    return b+1
data = {name_to_idx[x]: [(name_to_idx[a], b, (c if c >= b else wtf(c, b))) for a,b,c in y["nei"] if 0 <= b < MAX_TIME and 0 <= c < MAX_TIME] for x, y in data.items()}
data = [data[x] for x in range(0, len(idx_to_name))]

print("--- Computing nodes to create")
used_nodes = [set() for _ in range(0, len(idx_to_name))]
for source, y in enumerate(data):
    for dest, start, end in y:
        used_nodes[source].add(start)
        used_nodes[dest].add(end)

#base_used_nodes = used_nodes
#used_nodes = [set() for _ in range(0, len(idx_to_name))]
#for source, times in enumerate(base_used_nodes):
#    for wt, dest in walking_time[source]:
#        for bt in times:
#            used_nodes[dest].add(bt+wt)
#    used_nodes[source] = used_nodes[source].union(base_used_nodes[source])

print("NB ORIG NODES {}".format(len(data)))
print("NB GRAPH NODES {}".format(sum([len(y) for y in used_nodes])))

def process_nodes(data):
    d = dict()
    for name, content in enumerate(data):
        for x, y in process_node(name, content):
            d[x] = y
    return d

def process_node(name, content):
    connections = sorted(content, key=lambda x: x[1])
    possible_times = sorted(used_nodes[name])
    c_id = 0

    for p_id, time in enumerate(possible_times):
        nei = []

        while c_id != len(connections) and connections[c_id][1] == time:
            nei.append((connections[c_id][0] * MAX_TIME + connections[c_id][2]))
            c_id += 1

        if p_id + 1 != len(possible_times):
            nei.append((name * MAX_TIME + possible_times[p_id + 1]))

        yield ((name * MAX_TIME + time), nei)

print("--- Computing graph")
print(time.time())
graph = process_nodes(data)
print(time.time())

# print("--- Computing toposort")
#
# def toposort():
#     entering = {x: 0 for x in graph}
#     for x,y in graph.items():
#         for z in y:
#             entering[z] += 1
#
#     empty = deque(x for x, y in entering.items() if y == 0)
#     topo = []
#     while len(empty) != 0:
#         node = empty.pop()
#         topo.append(node)
#         for z in graph[node]:
#             entering[z] -= 1
#             if entering[z] == 0:
#                 empty.append(z)
#
#     error = [x for x in entering if entering[x] != 0]
#     assert len(error) == 0
#     return topo
#
# print(time.time())
# topo = toposort()
# print(time.time())

print("--- Saving")
json.dump({"idx_to_name": idx_to_name, "max_time": MAX_TIME, #"topo": topo,
           "graph": graph, "used_nodes": [list(sorted(x)) for x in used_nodes]
           }, open("../produce/out.json", 'w'))

print("--- Done")
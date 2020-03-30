# Lancer _2_compute_walking_time.py before this program

#Sophie


# Ce programme à pour but d'ajouter des edge a graph.json
# Ces nouvelle arret representerons les trajet faisable a pied
from Program.Unused.path import PATH_CHARLEROI as PATH
import json

with open(PATH.WALKING) as walk_file:
    walk = json.load(walk_file)

with open(PATH.GRAPH_TC) as graph_file:
    graph_tc = json.load(graph_file)

idx_to_name = graph_tc["idx_to_name"]
name_to_idx = {x: i for i, x in enumerate(idx_to_name)}
max_time = graph_tc["max_time"]
used_time = graph_tc["used_times"]
graph_walk_tc = graph_tc.copy()

for org_name in walk.keys():
    org_idx = name_to_idx[org_name]
    org_time = used_time[org_idx]          # Time are already sorted
    for walk_time, dest_name in walk[org_name]:
        dest_idx = name_to_idx[dest_name]
        dest_time = used_time[dest_idx]     # Time are already sorted
        for o_time in org_time:
            i = 0
            while dest_time[i] < o_time + walk_time:
                i += 1
            graph_walk_tc["graph"][str(org_idx*max_time + o_time)].append(dest_idx*max_time + dest_time[i])

with open(PATH.GRAPH_TC_WALK,"w") as out:
    json.dump(graph_walk_tc, out)




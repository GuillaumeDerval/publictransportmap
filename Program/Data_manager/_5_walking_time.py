import json
import math
import progressbar
import numpy as np
import sklearn.neighbors

from utils import haversine
from Program.Data_manager.path import PATH


def compute_stations_walking_time(param):
    """
        For each paire of station located at less than MAX_RADIUS, add an edge between the 2 stations.
        the time of this edge correspond to a straight ahead walk between the stations

        in  : PATH.SIMPLIFIED
        out : PATH.WALKING
    """
    data = json.load(open(PATH.SIMPLIFIED))
    MAX_RADIUS = param.MAX_RADIUS()

    def distance_to_walking_time(dist_km):
        minutes = (dist_km * 1000) / param.WALKING_SPEED()
        return round(minutes)

    def hexacontaround(x):
        return int(round(x / 60) * 60)

    idxes = list(data.keys())

    latlon = np.array([[math.radians(data[x]["lat"]), math.radians(data[x]["lon"])] for x in idxes])
    tree = sklearn.neighbors.BallTree(latlon, metric="haversine")

    out = {x: [] for x in idxes}

    bar = progressbar.ProgressBar()
    for i in bar(range(0, len(idxes))):
        idx1 = idxes[i]

        result = tree.query_radius([latlon[i]], r=MAX_RADIUS)[0]
        for j in result:
            idx2 = idxes[j]
            distance = haversine(data[idx1]["lon"], data[idx1]["lat"], data[idx2]["lon"], data[idx2]["lat"])
            distance_time = hexacontaround(max(0, distance_to_walking_time(distance)))
            out[idx1].append((distance_time, idx2))
            # out[idx2].append((distance_time, idx1)) will be done the other way!

    out = {x: sorted(y)[0:50] for x, y in out.items()}
    json.dump(out, open(PATH.WALKING, "w"))





# Lancer _2_compute_walking_time.py before this program

# Sophie


def compute_walking_edges():
    # Ce programme à pour but d'ajouter des edge a graph.json
    # Ces nouvelle arret representerons les trajet faisable a pied
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

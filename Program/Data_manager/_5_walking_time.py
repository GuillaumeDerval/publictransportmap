import json
import math
import progressbar
import numpy as np
import sklearn.neighbors

from utils import haversine
from Program.distance_and_conversion import distance_Eucli


def compute_stations_walking_time1(param):
    """
        For each paire of station located at less than MAX_RADIUS, add an edge between the 2 stations.
        the time of this edge correspond to a straight ahead walk between the stations

        in  : PATH.SIMPLIFIED
        out : PATH.WALKING
    """
    with open(param.PATH.SIMPLIFIED) as s:
        data = json.load(s)
    max_radius = param.MAX_RADIUS()

    def distance_to_walking_time(dist_km):
        minutes = (dist_km * 1000) / param.WALKING_SPEED()
        return round(minutes)

    #def hexacontaround(x):
        #return int(round(x / 60) * 60)

    idxes = list(data.keys())

    latlon = np.array([[math.radians(data[x]["lat"]), math.radians(data[x]["lon"])] for x in idxes])
    tree = sklearn.neighbors.BallTree(latlon, metric="haversine")

    out = {x: [] for x in idxes}

    #bar = progressbar.ProgressBar()
    #for i in bar(range(0, len(idxes))):
    for i in range(0, len(idxes)):
        idx1 = idxes[i]

        result = tree.query_radius([latlon[i]], r=max_radius)[0]
        for j in result:
            idx2 = idxes[j]
            distance = haversine(data[idx1]["lon"], data[idx1]["lat"], data[idx2]["lon"], data[idx2]["lat"])
            #distance_time = hexacontaround(max(0, distance_to_walking_time(distance)))
            distance_time = max(0, distance_to_walking_time(distance))
            out[idx1].append((distance_time, idx2))
            # out[idx2].append((distance_time, idx1)) will be done the other way!

    out = {x: sorted(y)[0:50] for x, y in out.items()}
    with open(param.PATH.WALKING, "w") as walk_file:
        json.dump(out, walk_file)


def compute_stations_walking_time(param):
    """
        For each paire of station located at less than MAX_RADIUS, add an edge between the 2 stations.
        the time of this edge correspond to a straight ahead walk between the stations

        in  : PATH.SIMPLIFIED
        out : PATH.WALKING
    """
    with open(param.PATH.SIMPLIFIED) as s:
        data = json.load(s)

    with open(param.PATH.STOP_POSITION_LAMBERT) as s:
        stop_lamb = json.load(s)

    names = list(data.keys())
    out = {x: [] for x in names}
    for org in names:
        for dest in names:
            walking_time = distance_Eucli(stop_lamb[org],stop_lamb[dest]) / param.WALKING_SPEED()
            out[org].append((walking_time, dest))

    out = {x: sorted(y)[0:50] for x, y in out.items()}
    with open(param.PATH.WALKING, "w") as walk_file:
        json.dump(out, walk_file)


# Lancer _2_compute_walking_time.py before this program

# Sophie


def compute_walking_edges(path):
    # Ce programme à pour but d'ajouter des edge a graph.json
    # Ces nouvelle arret representerons les trajet faisable a pied
    with open(path.WALKING) as walk_file:
        walk = json.load(walk_file)

    with open(path.GRAPH_TC) as graph_file:
        graph_tc = json.load(graph_file)

    idx_to_name = graph_tc["idx_to_name"]
    name_to_idx = {x: i for i, x in enumerate(idx_to_name)}
    max_time = graph_tc["max_time"]
    used_time = graph_tc["used_times"]
    graph_walk_tc = graph_tc.copy()

    for org_name in walk.keys():
        org_idx = name_to_idx[org_name]
        org_time = used_time[org_idx]          # Time are already sorted
        org_time.sort()
        for walk_time, dest_name in walk[org_name]:
            if dest_name != org_name:
                dest_idx = name_to_idx[dest_name]
                dest_time = used_time[dest_idx]     # Time are already sorted
                dest_time.sort()
                for o_time in org_time:
                    i = 0
                    while i < len(dest_time) and dest_time[i] < o_time + walk_time:
                        i += 1
                    if i < len(dest_time):
                        graph_walk_tc["graph"][str(org_idx*max_time + o_time)].append(dest_idx*max_time + dest_time[i])

    with open(path.GRAPH_TC_WALK, "w") as out:
        json.dump(graph_walk_tc, out)

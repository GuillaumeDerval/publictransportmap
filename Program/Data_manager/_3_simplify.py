import json
import math
from collections import deque

import progressbar
import numpy as np
import sklearn.neighbors

from utils import haversine, distance_to_walking_time, MAX_WALKING_TIME, MAX_RADIUS, mean_latlon, decaround
from Program.path import PATH

"""
Simplifie the time step : departure_time and arrival_time are now given by step of 10 seconds 

in  : PATH.TRANSPORT

out : PATH.SIMPLIFIED

"""
# inside a group of nodes to be merged, two nodes must be at max 200 meters from each others.
# why 200? because it's more than 100 and less than 300 ;-)
MAX_SIMPLIFCATION_RADIUS = 0 #0.2


def elect_leader(data, cluster):
    return min(cluster, key=lambda x: (0 if x.startswith("sncb") else 1, len(data[x]["nei"])))


def simplify_noinbound(data):
    #TODO does not work!
    return data

    # inbound = {x: 0 for x in data}
    # for x, y in data.items():
    #     for z, _, _ in y["nei"]:
    #         inbound[z] += 1
    #
    # n_removed = 0
    # to_remove = deque(x for x,count in inbound.items() if count == 0)
    # while len(to_remove) != 0:
    #     next = to_remove.pop()
    #     for z, _, _ in data[next]["nei"]:
    #         inbound[z] -= 1
    #         if inbound[z] == 0:
    #             to_remove.append(z)
    #     del data[next]
    #     n_removed += 1
    #
    # print("removed unreachable {}".format(n_removed))
    # return data

def simplify_clustering(data):
    idxes = list(data.keys())

    print("NB ORIG NODES {}".format(len(idxes)))
    latlon = np.array([[math.radians(data[x]["lat"]), math.radians(data[x]["lon"])] for x in idxes])
    tree = sklearn.neighbors.BallTree(latlon, metric="haversine")

    done = set()

    bar = progressbar.ProgressBar()
    leaders = {}
    conversions = {}
    for base_node_idx in bar(range(0, len(idxes))):
        if base_node_idx in done:
            continue

        done.add(base_node_idx)
        cluster_content = [idxes[base_node_idx]]
        for j in tree.query_radius([latlon[base_node_idx]], r=MAX_SIMPLIFCATION_RADIUS/6367.0)[0]:
            if j in done:
                continue
            possible_neighbor = idxes[j]

            ok = True
            for i in cluster_content:
                d = haversine(data[possible_neighbor]["lon"], data[possible_neighbor]["lat"], data[i]["lon"], data[i]["lat"])
                if d > MAX_SIMPLIFCATION_RADIUS:
                    ok = False
                    break

            if ok:
                cluster_content.append(possible_neighbor)
                done.add(j)

        leader = elect_leader(data, cluster_content)
        for x in cluster_content:
            conversions[x] = leader

        mean_lon, mean_lat = mean_latlon([(data[x]["lon"], data[x]["lat"]) for x in cluster_content])
        leaders[leader] = dict(data[leader]) #copy
        leaders[leader]["nei"] = sorted(set((a,b,c) for m in cluster_content for a,b,c in data[m]["nei"] if a != leader), key=lambda x: (x[1], x[2], x[0]))
        #print(haversine(mean_lon, mean_lat, data[leader]["lon"], data[leader]["lat"]))
        leaders[leader]["lon"] = mean_lon
        leaders[leader]["lat"] = mean_lat

    for l in leaders:
        leaders[l]["nei"] = [(conversions[a],b,c) for a,b,c in leaders[l]["nei"] if conversions[a] != l]

    print("NB NEW NODES {}".format(len(leaders)))
    return leaders


def simplify_time(data):
    # everything is in seconds. Let us use 10's of seconds
    for x in data:
        data[x]["nei"] = [(a, decaround(b)//10,decaround(c)//10) for a, b, c in data[x]["nei"]]
    return data


print("LOADING")
data = json.load(open(PATH.TRANSPORT))
print("SIMPLIFY")
#data = simplify_noinbound(simplify_clustering(data)) #todo
data = simplify_time(data)
print("SAVING")
json.dump(data, open(PATH.SIMPLIFIED, "w"))
print("END")
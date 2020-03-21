import json
import math
import progressbar
import numpy as np
import sklearn.neighbors

from utils import haversine, decaround
from Program.path import MAX_RADIUS
from Program.distance_and_conversion import distance_to_walking_time
from Program.path import PATH

""" 
    For each paire of station located at less than MAX_RADIUS, add an edge between the 2 stations.
    the time of this edge correspond to a straight ahead walk between the stations
    
    in  : PATH.SIMPLIFIED
    out : PATH.WALKING
"""
def compute_stations_walking_time(data):
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
            distance_time = decaround(max(10, distance_to_walking_time(distance)))//10  #todo
            out[idx1].append((distance_time, idx2))
            # out[idx2].append((distance_time, idx1)) will be done the other way!

    out = {x: sorted(y)[0:50] for x, y in out.items()}
    return out

print("LOADING")
data = json.load(open(PATH.SIMPLIFIED))
print("COMPUTING STATION WALKING TIME")
distance_walking = compute_stations_walking_time(data)
print("SAVING")
json.dump(distance_walking, open(PATH.WALKING, "w"))
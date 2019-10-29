#run this script to launch the complete execution

import json
import math
import numpy as np
#todo

#real_time = np.load("../produce/out/sncb8015345.npy")
#print(real_time)
#print(real_time[14])

#trouver le stop le plus proche
#placer tout les habitant a ce stop calculer temps de trajet
def distance(lon1,lat1, lon2, lat2):
    return math.sqrt((abs(lon1 - lon2) ** 2) + (abs(lat1 - lat2) ** 2))  # todo correct distance metric

def get_closest_stop_muni():
    data_muni = json.load(open("out_dir/municipality_position.json"))
    data_stop = json.load(open("../produce/train_only.json"))

    clst = {}
    for muni in data_muni:
        name = muni["municipality"]
        for stop in data_stop:
            dist = distance(float(muni["mean"][1]),float(muni["mean"][0]), float(data_stop[stop]["lon"]),float(data_stop[stop]["lat"]))
            if not(name in clst):
                clst[name] = {"stop_id": stop,"position": (data_stop[stop]["lon"], data_stop[stop]["lat"]), "dist": dist}
            elif dist < clst[name]["dist"]:
                clst[name] = {"stop_id": stop, "position": (data_stop[stop]["lon"], data_stop[stop]["lat"]), "dist": dist}

    return clst

clst = get_closest_stop_muni()



#
travel = json.load(open("out_dir/travel_small.json"))["travel"]

count_user = 0
tot_time = 0

for trav in travel[:]:
    if not (trav["residence"].upper() in clst) : print (trav["residence"])
    if not (trav["work"].upper() in clst): print(trav["work"])
    stop_rsd = clst[trav["residence"].upper()]
    stop_work = clst[trav["work"].upper()]
    weight = trav["n"]

    #real_time = np.load("../produce/out/sncb8015345.npy")
print("end")
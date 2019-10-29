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
                clst[name] = {"stop": stop,"position": (data_stop[stop]["lon"], data_stop[stop]["lat"]), "dist": dist}
            elif dist < clst[name]["dist"]:
                clst[name] = {"stop": stop, "position": (data_stop[stop]["lon"], data_stop[stop]["lat"]), "dist": dist}

    return clst

clst = get_closest_stop_muni()



#todo remove ____________________________________________________
data = json.loads(open('../produce/out.json').read())
idx_to_name = data["idx_to_name"]
name_to_idx = {x: i for i, x in enumerate(idx_to_name)}

#todo remove ____________________________________________________

#
travel = json.load(open("out_dir/travel_small.json"))["travel"]
travel.sort(key=(lambda x: x["residence"]))
count_user = 0
tot_time = 0

for trav in travel:
    stop_rsd = ""
    travel_time = None
    if clst[trav["residence"].upper()] != stop_rsd:
        stop_rsd = clst[trav["residence"].upper()]["stop"]
        path = "../produce/out/{0}.npy".format(stop_rsd)
        travel_time = np.load(path)

    stop_work = clst[trav["work"].upper()]["stop"]
    n = trav["n"]

    #computation
    count_user += n
    tot_time += n* travel_time[name_to_idx[stop_work]]#travel_time[name_to_idx[stop_work]]

mean = tot_time/count_user
print("mean time in decasecond : ",mean)
print("mean time in {0} h {1} ".format(mean//360,(mean//6)%60))

print("end")
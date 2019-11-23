#run this script to launch the complete execution

import json
import math
import numpy as np


travel = json.load(open("out_dir/travel_user.json"))["travel"]
clst = json.load(open("out_dir/closest_stop.json"))

count_user = 0
tot_time = 0
unreachable = 0 # number of time where a user can't not reach it's destination

#todo remove ____________________________________________________
data = json.loads(open('../produce/out.json').read())
idx_to_name = data["idx_to_name"]
name_to_idx = {x: i for i, x in enumerate(idx_to_name)}

#todo remove ____________________________________________________

travel.sort(key=(lambda x: x["residence"][1]))
for trav in travel:
    stop_rsd = ("",0)
    travel_time = None
    refnis = str(trav["residence"][1])
    if refnis in clst:
        new_stop_rsd = clst[refnis]["stop"]
        if new_stop_rsd != stop_rsd:
            stop_rsd = new_stop_rsd
            path = "../produce/out/{0}.npy".format(stop_rsd)
            travel_time = np.load(path)

        n = int(trav["n"])
        stop_work = clst[str(trav["work"][1])]["stop"]
        count_user += n
        idx = name_to_idx[stop_work]
        time = travel_time[name_to_idx[stop_work]]
        if time >= 0:
            tot_time += n * travel_time[name_to_idx[stop_work]]  # travel_time[name_to_idx[stop_work]]
        else:
            unreachable += n

    else:
        print("error")

mean = tot_time / (count_user-unreachable)
print("mean time in decasecond : ", mean)
print("mean time in {0} h {1} ".format(mean // 360, (mean // 6) % 60))
print(unreachable, "trajet n'ont pas pu etre effectué soit ", unreachable/count_user, "% ")
print("end")



#______________MAIN_____________________
# compute walking distrib
# for org, dest in travel :
#   Tc_travel = ...
#   for stop_org in getReacahable_stop(org)
#        for stop_dest in getReacahable_stop(dest)
#            list_distrib.append(sum_distrib(stop_org,stop_dest)
#   travel_time distrib = min(list_distrib)
#   mean += travel_time distrib.mean()*peopole
# mean /totpeople
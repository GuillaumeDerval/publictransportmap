#run this script to launch the complete execution

import json
import math
import numpy as np




#todo remove ____________________________________________________
data = json.loads(open('../produce/out.json').read())
idx_to_name = data["idx_to_name"]
name_to_idx = {x: i for i, x in enumerate(idx_to_name)}

#todo remove ____________________________________________________

def mean_time_from_closest_station():
    travel = json.load(open("out_dir/travel_user.json"))["travel"]
    clst = json.load(open("out_dir/closest_stop.json"))

    count_user = 0
    tot_time = 0
    unreachable = 0 # number of time where a user can't not reach it's destination

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

from my_program.stat_distrib import *
from my_program.walking_time import *

def mean_min_travel_time():  # only resid -> work

    max_walking_time = 20 #todo change
    time_sum = 0 # mean traveltime
    tot_travel = 0 # number of travel done

    # compute walking distrib
    stops = json.load(open("out_dir/stop_lambert_pos.json", "r"))
    munty = json.load(open("out_dir/travel_small.json"))["cities"] #todo change to user
    refnis = [r[1] for r in munty]
    dico = get_all_walking_time_distrib(stops, refnis, max_walking_time= max_walking_time)

    #travel
    travel = json.load(open("out_dir/travel_user.json"))["travel"]
    travel.sort(key=(lambda x: x["residence"][1])) # sort by residence's refnis


    for trav in travel:
        resid_refnis = str(trav["residence"][1])
        work_refnis = str(trav["work"][1])
        list_distrib = []
        starts= []
        for stop_rsd in get_reachable_stop(stops, resid_refnis, max_walking_time= max_walking_time):
            path = "../produce/out/{0}.npy".format(stop_rsd)
            TC_travel_array = np.load(path)
            for stop_work in get_reachable_stop(stops, work_refnis, max_walking_time=max_walking_time):
                resid_distrib = dico[(stop_rsd, resid_refnis)]
                work_distrib = dico[(stop_work, work_refnis)]
                list_distrib.append(sum_distrib(resid_distrib,work_distrib))
                starts.append(TC_travel_array[name_to_idx[stop_work]])
        travel_time_distrib = min_distrib(list_distrib, starts)
        occurence =  int(trav["n"]) # number of time where this travel is done
        time_sum += travel_time_distrib.mean()* occurence
    return time_sum /tot_travel



if __name__ == '__main__':
    mean_min_travel_time()
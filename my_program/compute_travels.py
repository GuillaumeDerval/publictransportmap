import csv
import json

from my_program.my_utils import *
from my_program.map import *

# Cet class est charger de determiner au mieux les trajet a prendre en compte ainsi que leur poids(nombre d'utilisateur)
"""####################################################################################################################
todo

in  : ../data/TU_CENSUS_2011_COMMUTERS_MUNTY.txt
todo

out :   ../data/travel_user.json
todo
#######################################################################################################################                                               
"""


def extract_travel(in_path, out_path):
    """
    Convert the data from the census into a json with the form :
    {
            cities: [("municipality","refnis"),...],
            travel: [
                {"residence" : ("municipality_residence_fr","munty_refnis_residence")
                "work" : ("municipality_work_fr","munty_refnis_work")
                "n" : 0
                },...

            ]
         }

    in  : ../data/TU_CENSUS_2011_COMMUTERS_MUNTY.txt

    out :   ../data/travel_user.json
    """

    travel = []
    with open(in_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|')
        idx = 0
        for row in reader:
            resid = (row["TX_MUNTY_RESIDENCE_DESCR_FR"],row["CD_MUNTY_REFNIS_RESIDENCE"])
            work = (row["TX_MUNTY_WORK_DESCR_FR"],row["CD_MUNTY_REFNIS_WORK"])
            n = row["OBS_VALUE"]
            if len(travel) > 0  and work == travel[len(travel)-1]["work"] and resid == travel[len(travel)-1]["residence"]:
                travel[len(travel)-1] = {"residence": resid, "work": work, "n": int(n) + int(travel[len(travel)-1]["n"])}
            else :
                travel.append({"residence": resid, "work": work, "n": n})
                idx += 1
    cities = [t["residence"] for t in travel]
    cities = list(dict.fromkeys(cities))
    out = {"cities": cities, "travel":  travel}
    json.dump(out, open(out_path, "w"))


#travel for bruxelles
def extract_small():
    data = json.load(open("out_dir/travel_user.json"))
    cities = data["cities"]
    travel = data["travel"]
    small_cities = cities[68:86]  # Bruxelles
    small_travel = []
    for t in travel:
        if t["residence"] in small_cities and t["work"] in small_cities:
            small_travel.append(t)
    small = {"cities": small_cities, "travel": small_travel}
    json.dump(small, open("out_dir/travel_small.json", "w"))


# find closest stop from a munty center
def get_closest_stop_muni():
    data_travel = json.load(open("out_dir/travel.json"))
    data_stop = json.load(open("../produce/train_only.json"))
    data_pos = get_center_munty()

    #convert stop position into belgian Lambert
    stop_pos = []
    for stop in data_stop:
        id = stop
        pos = WGS84_to_Lambert((float(data_stop[stop]["lon"]), float(data_stop[stop]["lat"])))
        stop_pos.append((id, pos))

    clst = {}
    for muni, refnis in data_travel["cities"]:
        for stop, pos in stop_pos:
            dist = distance_Eucli(data_pos[refnis], pos)
            if not((muni, refnis) in clst) or dist < clst[(muni, refnis)]["dist"]: # if not yet in dico or better value
                clst[(muni, refnis)] = {"stop": stop, "position": pos, "dist": dist} # add/update dico

    return clst
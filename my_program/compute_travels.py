import csv
from my_program.my_utils import *
import my_program.map as my_map

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
            cities: [("municipality",refnis),...],
            travel: [
                {"residence" : ("municipality_residence_fr",munty_refnis_residence)
                "work" : ("municipality_work_fr",munty_refnis_work)
                "n" : 0
                },...

            ]
         }

    in  : data/TU_CENSUS_2011_COMMUTERS_MUNTY.txt

    out :   out_dir/travel_user.json
            out_dir/travel_small.json
            out_dir/closest_stop.json[" ", ""]
    """

    travel = []
    with open(in_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|')
        idx = 0
        for row in reader:
            if not (row["CD_MUNTY_REFNIS_WORK"] in ["", "-"," ","_"] or row["CD_MUNTY_REFNIS_RESIDENCE"] in ["", "-"," ","_"]):
                resid = (row["TX_MUNTY_RESIDENCE_DESCR_FR"],str(row["CD_MUNTY_REFNIS_RESIDENCE"]))
                work = (row["TX_MUNTY_WORK_DESCR_FR"],str(row["CD_MUNTY_REFNIS_WORK"]))
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





# find closest stop from a munty center
def get_closest_stop_muni():
    if my_map.belgium_map is None : map = my_map()
    else: map = my_map.belgium_map
    data_pos = map.get_center_munty()
    data_travel = json.load(open("out_dir/travel_user.json"))



    #convert stop position into belgian Lambert
    stop_pos = get_stop_pos__belgian_lambert()

    clst = {}
    for muni, refnis in data_travel["cities"]:
        for stop, pos in stop_pos:
            center = (data_pos[refnis].x, data_pos[refnis].y)
            dist = distance_Eucli(center, pos)
            if not(refnis in clst) or dist < clst[refnis]["dist"]: # if not yet in dico or better value
                clst[refnis] = {"muni": muni,"stop": stop, "position": pos, "dist": dist} # add/update dico

    json.dump(clst, open("out_dir/closest_stop.json", "w"))
    print("end")

extract_travel("data/TU_CENSUS_2011_COMMUTERS_MUNTY.txt","out_dir/travel_user.json")
#extract_small()
#get_closest_stop_muni()
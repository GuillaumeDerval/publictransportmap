import csv
import json
import os

"""####################################################################################################################
Convert the data from the census into a json with the form :
{
        cities: ["municipality",...],
        travel: [
            {"residence" : "municipality_residence"
            "work" : "municipality_work"
            "count" : 0
            },...
            
        ]
     }

in  : ../data/TU_CENSUS_2011_COMMUTERS_MUNTY.txt

out :   ../data/travel_user.json
#######################################################################################################################                                               
"""

def extract_data(in_path, out_path):
    travel = []
    with open(in_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|')
        idx = 0
        for row in reader:
            resid = row["TX_MUNTY_RESIDENCE_DESCR_FR"]
            work = row["TX_MUNTY_WORK_DESCR_FR"]
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


def extract_small():
    data = json.load(open("data/travel_user.json"))
    cities = data["cities"]
    travel = data["travel"]
    small_cities = cities[68:86]  # Bruxelles
    small_travel = []
    for t in travel:
        if t["residence"] in small_cities and t["work"] in small_cities:
            small_travel.append(t)
    small = {"cities": small_cities, "travel": small_travel}
    json.dump(small, open("data/travel_small.json", "w"))

extract_data("data/TU_CENSUS_2011_COMMUTERS_MUNTY.txt","data/travel_user.json")
extract_small()
print("finish")
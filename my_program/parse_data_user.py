import csv
import json
import os

"""####################################################################################################################
todo

in  : ../data/TU_CENSUS_2011_COMMUTERS_MUNTY.txt
todo

out :   ../data/travel_user.json
todo
#######################################################################################################################                                               
"""


def extract_locality_municipality(pos_loc_path, loc_muni_path, out_path):
    """
    Associate municipality locality and position
     [
        {
            municipality: "name",
            post : 0000,
            locality : "name",
            position: (lat, lon)
        }
     ]

    """
    def sort_loc(loc):
        return loc["zip"]

    pos_loc = json.load(open(pos_loc_path))
    pos_loc.sort(key=sort_loc)
    idx = 0
    out = []

    with open(os.path.join(loc_muni_path), newline= '') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            while row["\ufeffCode postal"] > pos_loc[idx]["zip"]:
                print("miss", row["\ufeffCode postal"], pos_loc[idx]["zip"])
                idx += 1

            while idx < len(pos_loc) and row["\ufeffCode postal"] == pos_loc[idx]["zip"]:
                out.append({"municipality": row["Commune principale"], "post" :pos_loc[idx]["zip"], "locality": pos_loc[idx]["city"],
                            "position": (pos_loc[idx]["lat"], pos_loc[idx]["lng"])})
                idx += 1
    json.dump(out, open(out_path, "w"))


def municipality_position(locality_municipality_path, out_path):
    """
    Give the position of each locality in a municipality and their mean:
    [
        {
            municipality: "name",
            mean : (lat,lon)
            positions: [(lat, lon), ...]
        }
    ]
    """
    def sort_muni(loc):
        return loc["municipality"]

    pos = json.load(open(locality_municipality_path))
    print(pos)
    pos.sort(key = sort_muni)
    i = 0
    mun_pos = []
    while i < len(pos):
        m = pos[i]["municipality"]
        pos_list = [(pos[i]["position"])]
        lat_mean = pos[i]["position"][0]
        lon_mean = pos[i]["position"][1]
        while i +1 < len(pos) and m == pos[i + 1]["municipality"]:
            i += 1
            pos_list.append((pos[i]["position"]))
            lat_mean += pos[i]["position"][0]
            lon_mean += pos[i]["position"][1]

        mun_pos.append({"municipality": m, "mean": (lat_mean/len(pos_list),lon_mean/len(pos_list)), "position" : pos_list})
        i+= 1
    print(len(mun_pos))
    json.dump(mun_pos, open(out_path, "w"))


def extract_travel(in_path, out_path):
    """
    Convert the data from the census into a json with the form :
    {
            cities: ["municipality",...],
            travel: [
                {"residence" : "municipality_residence"
                "work" : "municipality_work"
                "n" : 0
                },...

            ]
         }

    in  : ../data/TU_CENSUS_2011_COMMUTERS_MUNTY.txt

    out :   ../data/travel_user.json
    """
    def clean_parenthesis(str):
        ind  = str.find("(")
        if ind >= 0:
            str = str[:ind].strip()
        return str



    travel = []
    with open(in_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|')
        idx = 0
        for row in reader:
            resid = clean_parenthesis(row["TX_MUNTY_RESIDENCE_DESCR_FR"])
            work = clean_parenthesis(row["TX_MUNTY_WORK_DESCR_FR"])
            n = row["OBS_VALUE"]
            if len(travel) > 0  and work == travel[len(travel)-1]["work"] and resid == travel[len(travel)-1]["residence"]:
                travel[len(travel)-1] = {"residence": resid, "work": work, "n": int(n) + int(travel[len(travel)-1]["n"])}
            else :
                travel.append({"residence": resid, "work": work, "n": n})
                idx += 1
    cities = [t["residence"] for t in travel]
    cities = list(dict.fromkeys(cities))
    out = {"cities": cities, "travel":  travel}
    print(len(out["cities"]))
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



extract_locality_municipality(pos_loc_path="data/zipcode-belgium.json", loc_muni_path="data/zipcodes_num_fr_new.csv",
                              out_path="out_dir/locality_municipality.json")
municipality_position("out_dir/locality_municipality.json", "out_dir/municipality_position.json")
extract_travel(in_path="data/TU_CENSUS_2011_COMMUTERS_MUNTY.txt", out_path= "out_dir/travel_user.json")
extract_small()
print("finish")
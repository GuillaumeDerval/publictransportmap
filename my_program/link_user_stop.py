import json
import math


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
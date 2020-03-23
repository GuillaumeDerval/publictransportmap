import json
import Program.map as my_map
from shapely.geometry import Point


def valid_stop_square(data,min_lat,max_lat, min_lon, max_lon):
    """
    Renvoie une liste contenant les stop valide
    C'est à dire le stop positionné dans le carré defini min/max_lat et min/max_lon
    """
    # Trouver la liste des stop_name valable
    valid = []
    for name in data.keys():
        lat = data[name]["lat"]
        lon = data[name]["lon"]
        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
            valid.append(name)
    return valid

def valid_stop_munty_list(data,munty_list):
    """
    Renvoie une liste contenant les stop valide
    C'est à dire le stop positionné dans une commune de munty_list
    """
    # Trouver la liste des stop_name valable
    valid = []
    position_lamber = json.load(open("../my_program/data/stop_lambert_all.json", "r"))
    map = my_map.my_map.get_map(path_shape=path.SHAPE, path_pop=path.POP)
    for munty in munty_list:
        munty_shape = map.get_shape_munty(munty)

        for name in data.keys():
            pos = position_lamber[name]
            pos_point = Point(pos[0], pos[1])

            if munty_shape.contains(pos_point):
                valid.append(name)
    return valid

# Reduire les donné au stop valables
def reduce_data(data,valid_stop_list):
    """
    Creer et renvoie un nouveau set de donnee plus petit ne contenantnque les stop de valid_stop_list
    """
    reduced_data = {}
    for name in data.keys():
        if name in valid_stop_list:
            content = data[name]
            stop = {"name": content["name"], "lat": content["lat"], "lon": content["lon"], "nei" : []}
            for nei in content["nei"]:
                if nei[0] in valid_stop_list:
                    stop["nei"].append(nei)
            reduced_data[name] = stop
    return reduced_data

if __name__ == '__main__':
    in_paths = ["../produce/train_only.json", "../produce/bus_only.json","../produce/train_bus.json"]
    out_paths = ["../produce/train_only_reduced.json", "../produce/bus_only_reduced.json", "../produce/train_bus_reduced.json"]
    for path,out in zip(in_paths,out_paths):
        print("Reduce data in : ", path, "and store it into", out)
        with open(path) as file:
            data = json.load(file)
        #valid = valid_stop_square(data, 50.45, 50.5, 5.55,5.6)
        charleroi_refnis = ["52010", "52011", "52012", "52015", "52018", "52021", "52022", "52025", "52043",
                            "52055", "52063", "52048", "52074","52075"]
        valid = valid_stop_munty_list(data, charleroi_refnis)
        reduced = reduce_data(data, valid)
        json.dump(reduced, open(out, "w"))


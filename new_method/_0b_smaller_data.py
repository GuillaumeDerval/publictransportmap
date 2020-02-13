import new_method._0_parse_gtfs
import json



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

def valid_stop_province(data,province):
    """
    Renvoie une liste contenant les stop valide
    C'est à dire le stop positionné dans la province province
    """
    # Trouver la liste des stop_name valable
    valid = []
    #todo
    raise Exception


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
    in_paths = ["../produce/train_only.json","../produce/bus_only.json","../produce/train_bus.json"]
    out_paths = ["../produce/train_only_reduced.json", "../produce/bus_only_reduced.json", "../produce/train_bus_reduced.json"]
    for path,out in zip(in_paths,out_paths):
        print("Reduce data in : ", path, "and store it into", out)
        data = json.load(open(path))
        valid = valid_stop_square(data, 50.0, 50.200, 5.80,6.0)
        reduced = reduce_data(data, valid)
        json.dump(reduced, open(out, "w"))

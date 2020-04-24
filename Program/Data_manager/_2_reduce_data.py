import csv
import json
import os
from geojson import dump
from shapely.geometry import Point

from Program.map import my_map



def reduce_rsd_work(PATH_BELGIUM,PATH,locations_list):
    with open(PATH_BELGIUM.RSD_WORK, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|')
        with open(PATH.RSD_WORK, mode='w') as out:
            writer = csv.DictWriter(out, fieldnames=reader.fieldnames, delimiter='|')
            writer.writeheader()
            refnis = []
            for row in reader:
                resid = row["TX_ADM_DSTR_WORK_DESCR_FR"]
                work = row["TX_ADM_DSTR_RESIDENCE_DESCR_FR"]
                if resid in locations_list and work in locations_list:
                    writer.writerow(row)
                    refnisRsd = row["CD_MUNTY_REFNIS_RESIDENCE"]
                    refnisWork = row["CD_MUNTY_REFNIS_WORK"]
                    if refnisRsd not in refnis: refnis.append(refnisRsd)
                    if refnisWork not in refnis: refnis.append(refnisWork)

    return refnis


# geojson
def reduce_map(PATH_BELGIUM, PATH, refnis_list):
    with open(PATH_BELGIUM.MAP_SHAPE) as f:

        features = json.load(f)["features"]
        feature_collection = []  # key = refnis
        for elem in features:
            refnis = str(elem["properties"]["CD_MUNTY_REFNIS"])
            if refnis in refnis_list:
                feature_collection.append(elem)

    out = {
        'type': 'FeatureCollection',
        "features": feature_collection
    }
    with open(PATH.MAP_SHAPE, 'w') as w:
        dump(out, w)

def reduce_pop_sector(PATH_BELGIUM, PATH,refnis_list):
    with open(PATH_BELGIUM.MAP_POP,"r") as in_file:
        with open(PATH.MAP_POP,"w") as out_file:
            reader = csv.DictReader(in_file, delimiter=';')
            writer = csv.DictWriter(out_file, fieldnames=reader.fieldnames, delimiter=';')
            writer.writeheader()
            for row in reader:
                refnis = str(row["\ufeffCD_REFNIS"])
                if refnis in refnis_list:
                    writer.writerow(row)



def reduce_stop(PATH_BELGIUM, PATH, parsed_gtfs_path,refnis_list, transport, param):
    """
    Renvoie une liste contenant les stop valide
    C'est à dire le stop positionné dans une commune de munty_list
    Necessite map
    """
    # todo improve pour avoir tout les stop atteingnable et pas uniquement ceux au sein de l'arrondissement

    # Trouver la liste des stop_name valable
    with open(parsed_gtfs_path) as file:
        parsed_gtfs = json.load(file)

    with open(PATH.STOP_POSITION_LAMBERT, "w") as out:
        json.dump({}, out)

    reduced_stop = {}
    position_lamber = json.load(open(PATH_BELGIUM.STOP_POSITION_LAMBERT[transport], "r"))
    mmap = my_map.get_map(param)
    for refnis in refnis_list:
        munty_shape = mmap.get_shape_refnis(refnis)

        for name in parsed_gtfs.keys():
            pos = position_lamber[name]
            pos_point = Point(pos[0], pos[1])

            if munty_shape.contains(pos_point):
                reduced_stop[name] = position_lamber[name]
    my_map.belgium_map = None
    os.remove(PATH.STOP_POSITION_LAMBERT)
    with open(PATH.STOP_POSITION_LAMBERT, "w") as out:
        json.dump(reduced_stop, out)


# Reduire les donné au stop valables
def reduce_parsed_gtfs(PATH, parsed_gtfs_path, out):
    """
    Creer et renvoie un nouveau set de donnee plus petit ne contenant que les stop de valid_stop_list
    """
    with open(PATH.STOP_POSITION_LAMBERT) as file:
        stop_list = json.load(file)

    with open(parsed_gtfs_path) as file:
        parsed_gtfs = json.load(file)
    reduced_data = {}
    for name in parsed_gtfs.keys():
        if name in stop_list:
            content = parsed_gtfs[name]
            stop = {"name": content["name"], "lat": content["lat"], "lon": content["lon"], "nei" : []}
            for nei in content["nei"]:
                if nei[0] in stop_list:
                    stop["nei"].append(nei)
            reduced_data[name] = stop
    json.dump(reduced_data, open(out, "w"))







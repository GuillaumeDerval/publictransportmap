from geojson import dump
from shapely.geometry import mapping, LineString, Point
from my_program.my_utils import WGS84_to_Lambert
import time
import json

# mix a map with the stop positions
def map_stop(in_path, out_path):
    feature_collection = []

    data_stop = json.load(open(in_path))

    # obtenir la position de chaque stop avec son nom
    stop_pos = {}
    step = 500
    print("target: ",len(data_stop.keys()))
    for i in range(44500, 47500, step): #len(data_stop.keys())

        listkey = list(data_stop.keys())
        for stop in listkey[i: i+step]:
            #stop = data_stop[stop]
            pos = WGS84_to_Lambert((float(data_stop[stop]["lon"]), float(data_stop[stop]["lat"])))
            stop_pos[stop] = pos
        with open('data/stop_lambert_bus.json', 'a') as w:
            json.dump(stop_pos, w),
            stop_pos = {}
            print(i)
            #time.sleep(20)

    #stop_Lamb = json.load(open("output/stop_lambert_pos.json", "r"))

    #for s in stop_Lamb:
    #    stop_pos[s[0]] = s[1]

    stop_pos = json.load(open("data/stop_lambert_bus.json", "r")) #44500
    print("len ", len(stop_pos))

    # Creer lien entre les stop
    """
    for stop in stop_pos.keys():
        # feature_collection.append(elem)
        x,y = stop_pos[stop]

        point = Point(x,y).buffer(20)
        point_dico = {'type': 'feature','properties': {'Type': "stop", 'pos_x': x, 'pos_y': y},'geometry': mapping(point)}
        feature_collection.append(point_dico)
        point = Point(x, y)

        nei = data_stop[stop]["nei"]
        nei_stops = []
        for n in nei:
            if n[0] not in nei_stops:
                n = n[0]
                nei_stops.append(n)
                # add the link
                if n in stop_pos:
                    nei_point = Point(stop_pos[n][0], stop_pos[n][1])
                    LineString([point, nei_point])
                    link = {'type': 'feature', 'properties': {'Type': "link"},
                                  'geometry': mapping(LineString([point, nei_point]))}
                    feature_collection.append(link)

    out = {
            'type': 'FeatureCollection',
            "features": feature_collection
        }

    with open(out_path, 'w') as w:
        dump(out, w)
    """

map_stop("../produce/bus_only.json",'data/tiny_data/bus_lines.geojson')

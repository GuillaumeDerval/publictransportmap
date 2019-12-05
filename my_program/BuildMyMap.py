from my_program.map import *
from geojson import dump
from shapely.geometry import mapping
from my_program.monte_carlo import *

# mix a map with the stop positions
def map_stop(map_path,   out_path,  stop_lamber):
    with open(map_path) as f:



        features = json.load(f)["features"]
        feature_collection = []
        for stop in stop_lamber:
            name = stop[0]
            x = stop[1][0]
            y = stop[1][1]
            #feature_collection.append(elem)
            point  = Point(x,  y). buffer(200)
            point_dico = {'type' : 'feature',
             'properties': {'Name': name, 'pos_x' : x, 'pos_y': y},
                 'geometry' :  mapping(point)
             }
            feature_collection.append(point_dico)
    out = {
            'type': 'FeatureCollection',
            "features": feature_collection
        }

    with open(out_path, 'w') as w:
        dump(out, w)


def munty_shape_map(map, out_path, munty_list):

    feature_collection = []
    for refnis in munty_list:
        name = refnis
        shape = map.get_shape_munty(refnis)
        dico = {'type': 'feature',
                      'properties': {'Name': name},
                      'geometry': mapping(shape)
                      }
        feature_collection.append(dico)
    out = {
        'type': 'FeatureCollection',
        "features": feature_collection
    }

    with open(out_path, 'w') as w:
        dump(out, w)


if my_map.belgium_map is None : map = my_map()
else: map = my_map.belgium_map

stops = json.load(open("out_dir/stop_lambert_pos.json", "r"))

munty = json.load(open("out_dir/tiny/travel_user.json"))["cities"] #todo change to user
refnis = [str(r[1]) for r in munty]
m_stops = []
for r in refnis:
    m_stops += get_reachable_stop(r, stops,map, 0)

map_stop("data/tiny_data/sh_statbel_statistical_sectors.geojson", 'data/tiny_data/mixmap.geojson', m_stops)
munty_shape_map(map, 'data/tiny_data/muntymap.geojson', refnis)


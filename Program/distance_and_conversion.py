from math import sqrt
from pyproj import Proj, transform
import json
from Program.path import WALKING_SPEED


# Set of use-full function for conversion and distance


def WGS84_to_Lambert(point):
    """ IN: point : (longitude, latitude)
        OUT: (x,y) in Belgian lambert
    """
    in_proj = Proj(init='epsg:4326')
    out_proj = Proj(init='epsg:31370')  #EPSG:31370
    return transform(in_proj, out_proj, point[0], point[1])


def Lambert_to_WGS84(point):
    """ IN: point : ((x,y) in Belgian lambert
        OUT: (longitude, latitude)
     """
    in_proj = Proj(init='epsg:31370')
    out_proj = Proj(init='epsg:4326')
    return transform(in_proj, out_proj, point[0], point[1])


def distance_Eucli(p1, p2):
    return sqrt(abs(p1[0]-p2[0])**2 + abs(p1[1]-p2[1])**2)


def distanceWGS84(p1, p2):
    #todo
    assert 0==1, "unimplemented"


def get_stop_pos__belgian_lambert():
    data_stop = json.load(open("../produce/train_only.json"))
    stop_pos = []
    for stop in data_stop:
        id = stop
        pos = WGS84_to_Lambert((float(data_stop[stop]["lon"]), float(data_stop[stop]["lat"])))
        stop_pos.append((id, pos))
    return stop_pos


def distance_to_walking_time(dist_km):
    hours = dist_km / WALKING_SPEED
    minutes = hours*60
    seconds = minutes*60
    return round(seconds)

# stop id / name convertions
#__idx_to_name = json.loads(open(PATH.GRAPH).read())["idx_to_name"]
#my_name_to_idx = {x: i for i, x in enumerate(__idx_to_name)}

#def name_to_idx(name):
#    return my_name_to_idx[name]



from geojson import dump
from shapely.geometry import mapping, Point
import Program.metric.monte_carlo_dynamic as MC
import json
import time
from Program.Data_manager.path import Parameters


# mix a map with the stop positions
def map_stop(param : Parameters):
    out_path, stop_lamber_path = param.PATH.OUT_STOP_MAP, param.PATH.STOP_POSITION_LAMBERT
    feature_collection = []
    with open(stop_lamber_path) as f:
        stop_lamber = json.load(f)
    for stop in stop_lamber.items():
        name = stop[0]
        x = stop[1][0]
        y = stop[1][1]
        #feature_collection.append(elem)
        point = Point(x,  y). buffer(50)
        point_dico = {'type' : 'feature',
         'properties': {'Name': name, 'pos_x': x, 'pos_y': y},
             'geometry' :  mapping(point)
         }
        feature_collection.append(point_dico)
    out = {
            'type': 'FeatureCollection',
            "features": feature_collection
        }

    with open(out_path, 'w') as w:
        dump(out, w)


def munty_shape_map(param : Parameters):
    mmap, out_path = param.MAP(), param.PATH.OUT_MUNTY_MAP
    feature_collection = []
    for refnis in mmap.get_all_munty_refnis():
        name = refnis
        shape = mmap.get_shape_refnis(refnis)
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


def country_shape_map(map, out_path):

    shape = map.get_total_shape()
    dico = {'type': 'feature',
                  'properties': {'Name': "country"},
                  'geometry': mapping(shape)
                  }
    feature_collection = [dico]
    out = {
        'type': 'FeatureCollection',
        "features": feature_collection
    }

    with open(out_path, 'w') as w:
        dump(out, w)

def travel_time_shape_map(param:Parameters,metric):
    out_path = param.PATH.OUT_TIME_MAP

    all_results = metric.all_results

    feature_collection = []
    for refnis in param.MAP().get_all_munty_refnis():
        name = refnis
        shape = param.MAP().get_shape_refnis(refnis)
        if refnis not in all_results.keys():
            dico = {'type': 'feature',
                        'properties': {'name': name, "time": None , "var": None,
                                    "walk1" : None, "walk2" : None,
                                    "walk" : None,"TC" : None,
                                    "distance": None, "prop_TC_users": None,
                                    "unreachable": None,"iteration": None},
                        'geometry': mapping(shape)
                        }
        else:
            result = all_results[refnis]
            dico = {'type': 'feature',
                    'properties': {'name': name, "time": result.mean(), "var": result.var(),
                                    "walk1" : result.walk1(), "walk2" : result.walk2(),
                                    "walk" : result.walk1() + result.walk2(),"TC" : result.TC(),"TC_user_only": result.TC_user_only(),
                                   "distance": result.mean_dist_reachable(), "prop_TC_users" : result.prop_TC_users(),
                                    "unreachable": result.prop_unreachable(),"iteration": result.iteration},
                    'geometry': mapping(shape)
                    }
        feature_collection.append(dico)
    out = {
        'type': 'FeatureCollection',
        "features": feature_collection
    }

    with open(out_path, 'w') as w:
        dump(out, w)


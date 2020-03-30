from geojson import dump
from shapely.geometry import mapping, Point
import Program.metric.monte_carlo_opti as MC
import json
import time
from Program.Unused.path import PATH


# mix a map with the stop positions
def map_stop( out_path,  stop_lamber):
    feature_collection = []
    for stop in stop_lamber:
        name = stop[0]
        x = stop[1][0]
        y = stop[1][1]
        #feature_collection.append(elem)
        point  = Point(x,  y). buffer(100)
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
        shape = map.get_shape_refnis(refnis)
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

def travel_time_shape_map(out_path):
    #compute mean travel time
    munty = json.load(open(PATH.TRAVEL))["cities"]
    munty_list = [str(r[1]) for r in munty]

    m_stops = []
    for r in munty_list:
        m_stops += MC.stop_munty.get_reachable_stop_munty(r)

    time = MC.monte_carlo(PATH.TRAVEL)

    feature_collection = []
    for refnis in munty_list:
        name = refnis
        shape = map.get_shape_refnis(refnis)
        if refnis not in time:
            dico = {'type': 'feature',
                        'properties': {'name': name, "time": None , "var": None,
                                    "walk1" : None, "walk2" : None,
                                    "walk" : None,"TC" : None,
                                    "distance": None, "prop_TC_users": None,
                                    "unreachable": None,"iteration": None,
                                    "pop" : map.get_pop_refnis(name), "resid": None, "work": None},
                        'geometry': mapping(shape)
                        }
        else:
            result = time[refnis]
            dico = {'type': 'feature',
                    'properties': {'name': name, "time": result.mean(), "var": result.var(),
                                    "walk1" : result.walk1(), "walk2" : result.walk2(),
                                    "walk" : result.walk1() + result.walk2(),"TC" : result.TC(),"TC_user_only": result.TC_user_only(),
                                   "distance": result.mean_dist_reachable(), "prop_TC_users" : result.prop_TC_users(),
                                    "unreachable": result.prop_unreachable(),"iteration": result.iteration,
                                    "pop" : result.pop, "resid": result.resid, "work": result.work},
                    'geometry': mapping(shape)
                    }
        feature_collection.append(dico)
    out = {
        'type': 'FeatureCollection',
        "features": feature_collection
    }

    with open(out_path, 'w') as w:
        dump(out, w)


if __name__ == '__main__':

    start = time.time()

    map = map.my_map.get_map(PATH.MAP_SHAPE, PATH.MAP_POP)
    #country_shape_map(map,'data/maps/Belgium.geojson')
    print('time map genaration : ', time.time() - start)

    start = time.time()
    travel_time_shape_map(PATH.OUT_TIME_MAP)
    print('monte carlo : ',time.time() -start)

    stops = json.load(open(PATH.STOP_POSITION_LAMBERT, "r"))
    munty = json.load(open(PATH.TRAVEL))["cities"]
    refnis = [str(r[1]) for r in munty]
    munty_shape_map(map, PATH.OUT_MUNTY_MAP, refnis)
    m_stops = []
    for r in refnis:
        m_stops += MC.stop_munty.get_reachable_stop_munty(r)

    map_stop(PATH.OUT_STOP_MAP, m_stops)



    """
    
  
    #test get_n_rdm_point
    rdm = get_n_rdm_point(50,"52011")
    rdm = [("a",p) for p in rdm]
    map_stop( 'data/tiny_data/rdmPoint.geojson',rdm)
    """



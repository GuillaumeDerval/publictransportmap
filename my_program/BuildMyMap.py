from geojson import dump
from shapely.geometry import mapping, Point
import my_program.monte_carlo_opti as MC
import json
import my_program.map as MAP
import my_program.path as PATH
import time


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
        shape = map.get_shape_munty(refnis)
        if refnis not in time or time[refnis][0] < 0:
            dico = {'type': 'feature',
                        'properties': {'Name': name, "Unreachable": time.get(refnis, (0,0,None))[2]},
                        'geometry': mapping(shape)
                        }
        else:
            dico = {'type': 'feature',
                    'properties': {'Name': name, "Time": time[refnis][0], "Var": time[refnis][1], "Unreachable": time[refnis][2]},
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

    map = MAP.my_map.get_map(PATH.SHAPE, PATH.POP)
    #country_shape_map(map,'data/maps/Belgium.geojson')
    print('time map genaration : ', time.time() -start)

    start = time.time()
    travel_time_shape_map('data/maps/timeMap.geojson')
    print('monte carlo : ',time.time() -start)

    stops = json.load(open("out_dir/stop_lambert_pos.json", "r"))
    munty = json.load(open(PATH.TRAVEL))["cities"]
    refnis = [str(r[1]) for r in munty]
    munty_shape_map(map, 'data/maps/muntymap.geojson', refnis)
    m_stops = []
    for r in refnis:
        m_stops += MC.stop_munty.get_reachable_stop_munty(r)

    map_stop('data/maps/mixmap.geojson', m_stops)


    """
    
  
    #test get_n_rdm_point
    rdm = get_n_rdm_point(50,"52011")
    rdm = [("a",p) for p in rdm]
    map_stop( 'data/tiny_data/rdmPoint.geojson',rdm)
    """



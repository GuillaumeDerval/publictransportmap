from geojson import dump
from shapely.geometry import mapping
from my_program import monte_carlo


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
    munty = json.load(open("out_dir/tiny/travel_user.json"))["cities"]
    munty_list = [str(r[1]) for r in munty]

    stops = json.load(open("out_dir/stop_lambert_pos.json", "r"))
    m_stops = []
    for r in munty_list:
        m_stops += get_reachable_stop_munty(r, stops)


    time = monte_carlo("out_dir/tiny/travel_user.json", m_stops)

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



    if my_map.belgium_map is None : map = my_map()
    else: map = my_map.belgium_map
    country_shape_map(map,'data/tiny_data/Belgium.geojson')
    print('ok')

    travel_time_shape_map('data/tiny_data/timeMap.geojson')

    stops = json.load(open("out_dir/stop_lambert_pos.json", "r"))
    munty = json.load(open("out_dir/tiny/travel_user.json"))["cities"]
    refnis = [str(r[1]) for r in munty]
    m_stops = []
    for r in refnis:
        m_stops += get_reachable_stop_munty(r, stops)

    map_stop('data/tiny_data/mixmap.geojson', m_stops)

    """
    munty_shape_map(map, 'data/tiny_data/muntymap.geojson', refnis)

    #test get_n_rdm_point
    rdm = get_n_rdm_point(50,"52011")
    rdm = [("a",p) for p in rdm]
    map_stop( 'data/tiny_data/rdmPoint.geojson',rdm)
    """



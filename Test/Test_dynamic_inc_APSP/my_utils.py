import os
import random as rdm
import math
import numpy as np
from Program.dynamic_Inc_APSP.Dynamic_Incremental_All_Pair_Shortest_Path import *
from Program.map import *
from Program.Data_manager.main import DataManager


def compare_results_distance(path_distance_dir_exp, path_distance_dir_actu):
    files_exp = os.listdir(path_distance_dir_exp)
    files_actu = os.listdir(path_distance_dir_actu)
    if len(files_exp) != len(files_actu):
        print("missing files")
        return False
    files_exp.sort()
    files_actu.sort()

    # used to change order of elements inside and array
    with open(path_distance_dir_actu + "__conversion.json", "r")as c:
        conv = list(json.load(c).items())
        conv.sort()
        order_actu = np.array([v for _, v in conv])
    with open(path_distance_dir_exp + "__conversion.json", "r")as c:
        conv = list(json.load(c).items())
        conv.sort()
        order_exp = np.array([v for _, v in conv])

    for f_exp,f_actu in zip(files_exp,files_actu):
        if f_exp != f_actu:
            print("bad_file")
            return False
        elif f_exp.find(".npy") != -1:
            #print("f_exp : ", f_exp,"    f_actu : ",f_actu)
            data_exp = np.load(path_distance_dir_exp + f_exp)
            data_actu = np.load(path_distance_dir_actu + f_actu)
            data_exp = data_exp[order_exp]
            data_actu = data_actu[order_actu]
            if not np.array_equal(data_exp, data_actu):
                print("f_exp : ", f_exp, "    f_actu : ", f_actu)
                print("data expected", data_exp)
                print("data actual", data_actu)
                diff = np.logical_xor(data_exp, data_actu)
                #diff = data_actu-data_exp#np.logical_xor(data_exp, data_actu)
                print("diff", diff)
                return False
    return True


def compare_results_is_path(path_is_path_exp, path_is_path_actu):
    files_exp = set(os.listdir(path_is_path_exp))
    files_actu = os.listdir(path_is_path_actu)
    with open(path_is_path_actu + "__conversion.json", "r")as c:
        conv_actu : dict= json.load(c)
        pos_to_remove = []

    for f in files_actu:
        if f not in files_exp:
            os.remove(path_is_path_actu + f)
            v = f.replace(".npy", "")
            pos_to_remove.append(conv_actu[v])
            conv_actu.pop(v)

    files_actu = os.listdir(path_is_path_actu)
    for f in files_actu:
        if f.find(".npy") != -1:
            data_actu = np.load(path_is_path_actu + f)
            np.delete(data_actu, pos_to_remove)

    with open(path_is_path_actu + "__conversion.json", "w")as c:
        json.dump(conv_actu,c)

    return compare_results_distance(path_is_path_exp, path_is_path_actu)
    #return True

def check_if_correct_modification(modification_function, param: Parameters, param_expect : Parameters):
    with open(param.PATH.TRANSPORT, "r") as transport:
        transport_dico = json.load(transport)
        APSP = Dynamic_APSP(param=param)
        modification_function(APSP, transport_dico)
    with open(param_expect.PATH.TRANSPORT, "w") as transp_expect:
        json.dump(transport_dico,transp_expect)

    APSP.hard_save_graph("data_test/save.json")
    APSP.hard_save_is_reachable("data_test/path_computed/")
    APSP.hard_save_distance("data_test/dist_computed/")

    DataManager.produce_data(param_expect.data_path, param_expect.location_name(), param_expect.transport(),
                             param_expect.MAX_WALKING_TIME(), param_expect.WALKING_SPEED_KM_H(), MAX_TIME=param_expect.MAX_TIME())
    #print(json.load(open(param_expect.PATH.CONFIG)))
    expect = Dynamic_APSP(param_expect)
    expect.hard_save_graph(param_expect.PATH.GRAPH_TC_WALK)
    expect.hard_save_is_reachable("data_test/path_expected/")
    expect.hard_save_distance("data_test/dist_expected/")

    with open("data_test/save.json", "r") as comp:
        computed_graph = json.load(comp)
    with open(param_expect.PATH.GRAPH_TC_WALK, "r") as exp:
        expected_graph = json.load(exp)
    graph_comp = (expected_graph == computed_graph)
    gr = (expected_graph["graph"] == computed_graph["graph"])
    path_comp = compare_results_is_path("data_test/path_expected/", "data_test/path_computed/")
    compar = compare_results_distance("data_test/dist_expected/", "data_test/dist_computed/")
    return graph_comp, path_comp, compar

# ############################################ Modify Parsed GTFS #####################################################


def transport_add_vertex(transp_dico, z_name, z_time, z_position, z_in=None, z_out=None):
    """
    modify the transp_dico in order to add the vertex
    :param transp_dico:
    {
        "stop_name": {
             name: "complete name of the stop",
             lat: 0.0
             lon: 0.0
             nei: [
                 ["name_dest_1", departure_time_1, arrival_time_1],
                 ["name_dest_2", departure_time_2, arrival_time_2],
                 ...
             ]
         }
     }
    :param z_name:
    :param z_time:
    :param z_position:
    :param z_in:
    :param z_out:
    """
    if transp_dico is None: return
    if z_in is None: z_in = []
    if z_out is None: z_out = []

    if z_name not in transp_dico:
        pos = Lambert_to_WGS84(z_position)
        transp_dico[z_name] = {"name": "ADDED","lon": pos[0],"lat": pos[1], "x": z_position[0], "y":  z_position[1], "nei": []}

    transport_add_edge(transp_dico, z_name, z_time, z_name, z_time)
    for u_stop_name, u_time in z_in:
        transport_add_edge(transp_dico, u_stop_name, u_time, z_name, z_time)
    for v_stop_name, v_time in z_out:
        transport_add_edge(transp_dico, z_name, z_time, v_stop_name, v_time)


def transport_add_edge(transp_dico, u_stop_name, u_time,  v_stop_name, v_time, u_position=None, v_position=None):
    if transp_dico is None: return
    if u_stop_name not in transp_dico:
        transport_add_vertex(transp_dico, u_stop_name, u_time, u_position)
    if v_stop_name not in transp_dico:
        transport_add_vertex(transp_dico, v_stop_name, v_time, v_position)

    transp_dico[u_stop_name]["nei"].append([v_stop_name, u_time*60, v_time*60])


# ###################################### RDM Point ###################################################################

def rdm_point_shape(param):
    """pick uniformaly at rdm a point in the shape"""
    mmap = my_map.get_map(param)
    refnis = rdm.sample(mmap.get_all_munty_refnis(), 1)[0]
    shape = mmap.get_shape_refnis(refnis)
    assert shape.area > 0

    minx, miny, maxx, maxy = shape.bounds
    x = rdm.randint(math.ceil(minx), math.floor(maxx))
    y = rdm.randint(math.ceil(miny), math.floor(maxy))
    p = (x, y)  # Point(x, y)
    if shape.contains(Point(x, y)):
        return p
    else:
        return rdm_point_shape(shape)

# ################################# Edge / Vertex Generation ##########################################################


def generate_random_edge(APSP,transp_dico):
    is_new_name1 = rdm.randint(0, 3)
    if is_new_name1 == 0:
        name1 = str(rdm.random())              # on pourrait avoir 2 fois le meme nom mais c'est improbable + pas grave
        time1 = rdm.randint(0, APSP.max_time - 1)
        pos1 = rdm_point_shape(APSP.param)
    else:
        name1 = rdm.sample(APSP.idx_to_name, 1).pop()
        pos1 = None
        is_new_time = rdm.randint(0, 3)
        if is_new_time == 0 or len(APSP.used_time[APSP.name_to_idx[name1]]) == 0:
            time1 = rdm.randint(0, APSP.max_time - 1)
        else:
            time1 = rdm.sample(APSP.used_time[APSP.name_to_idx[name1]], 1).pop()

    is_new_name2 = rdm.randint(0, 3)
    if is_new_name2 == 0:
        name2 = str(rdm.random())
        time2 = rdm.randint(time1, APSP.max_time - 1)
        pos2 = rdm_point_shape(APSP.param)
    else:
        name2 = rdm.sample(APSP.idx_to_name, 1).pop()
        is_new_time = rdm.randint(0, 3)
        if is_new_time == 0:
            time2 = rdm.randint(time1, APSP.max_time - 1)
        else:
            possible_time = []
            for t in APSP.used_time[APSP.name_to_idx[name2]]:
                if t >= time1:
                    possible_time.append(t)
            if len(possible_time) > 0:
                time2 = rdm.sample(possible_time, 1).pop()
            else:
                time2 = rdm.randint(time1, APSP.max_time - 1)
        pos2 = None
    # print("add edge {} time {} to {} time {}".format(name1, time1, name2, time2))
    transport_add_edge(transp_dico,name1, time1, name2, time2, u_position=pos1, v_position=pos2)
    APSP.add_edge(name1, time1, name2, time2, u_position=pos1, v_position=pos2)



def generate_random_vertex(APSP : Dynamic_APSP,transp_dico):
    mmap = my_map.get_map(APSP.param)
    if rdm.randint(0, 1) == 1:                  # New position or not
        # New position
        z_name = str(rdm.random())  # on pourrait avoir 2 fois le meme nom mais c'est improbable + pas grave
        time = rdm.randint(0, APSP.max_time - 1)
        pos = rdm_point_shape(APSP.param)

    else:
        # Old position
        z_name = rdm.sample(APSP.idx_to_name, 1).pop()
        if len(APSP.used_time[APSP.name_to_idx[z_name]]) > 0 and rdm.randint(0, 1) == 1:   # New time or not
            # Old time
            time = rdm.sample(APSP.used_time[APSP.name_to_idx[z_name]], 1).pop()
            pos = None
        else:
            #New time
            time = rdm.randint(0, APSP.max_time - 1)
            pos = mmap.stop_position_dico[z_name]

    z_in, z_out = [], []
    for _ in range(rdm.randint(0, 5)):   # Number of new edge between 0 and 4
        name2 = rdm.sample(APSP.idx_to_name, 1).pop()
        if len(APSP.used_time[APSP.name_to_idx[name2]]) > 0 and rdm.randint(0, 1) == 1 :   # New time or not
            # Old time
            time2 = rdm.sample(APSP.used_time[APSP.name_to_idx[name2]], 1).pop()
        else:
            #New time
            time2 = rdm.randint(0, APSP.max_time - 1)

        if time2 < time:
            z_in.append((name2, time2))
        else:
            z_out.append((name2, time2))

    # print("add vertex {} time {} pos {} :  z_in {} , z_out {}".format(z_name, time, pos, z_in, z_out))
    APSP.add_vertex(z_name, time, pos, z_in, z_out)
    transport_add_vertex(transp_dico, z_name, time, pos, z_in, z_out)


def generate_random_add(APSP,transp_dico):
    if rdm.randint(0,5) == 0:
        generate_random_vertex(APSP, transp_dico)
    else:
        generate_random_edge(APSP, transp_dico)


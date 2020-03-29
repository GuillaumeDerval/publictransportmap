import os
import random as rdm
from Program.dynamic_Inc_APSP.Dynamic_Incremental_All_Pair_Shortest_Path import *
from Program.General.map import *


def compare_results(path_distance_dir_exp, path_distance_dir_actu):
    files_exp = os.listdir(path_distance_dir_exp)
    files_actu = os.listdir(path_distance_dir_actu)
    if len(files_exp) != len(files_actu):
        return False
    files_exp.sort()
    files_actu.sort()
    for f_exp,f_actu in zip(files_exp,files_actu):
        if f_exp != f_actu :
            return False
        elif f_exp.find(".npy") != -1:
            #print("f_exp : ", f_exp,"    f_actu : ",f_actu)
            data_exp = np.load(path_distance_dir_exp + f_exp)
            data_actu = np.load(path_distance_dir_actu + f_actu)
            if not np.array_equal(data_exp, data_actu):
                print("data expected", data_exp)
                print("data actual", data_actu)
                return False
    return True

def check_if_correct_modification(modification_function,graph_path = "data_test/mini.json", mmap = None):

    if mmap is None : mmap = my_map(path_shape="data_test/smallmap.geojson",path_pop="data_test/popsector.csv", stop_list_path="data_test/mini_stop_pos.json")
    APSP = Dynamic_APSP(graph_path, mapmap=mmap)

    modification_function(APSP)
    APSP.hard_save_graph("data_test/save.json")
    APSP.hard_save_is_reachable("data_test/path_computed/")
    APSP.hard_save_distance("data_test/dist_computed/")


    Expect = Dynamic_APSP("data_test/save.json") # todo : mette a jour le graph plutot que d'utiliser la sauvegarde et lancer 2b_walk
    Expect.hard_save_is_reachable("data_test/path_expected/")
    Expect.hard_save_distance("data_test/dist_expected/")
    path_comp = compare_results("data_test/path_expected/", "data_test/path_computed/")
    compar = compare_results("data_test/dist_expected/", "data_test/dist_computed/")
    return path_comp, compar


def generate_random_edge(APSP, min_lat=0, max_lat=10, min_lon=0, max_lon=10):
    is_new_name1 = rdm.randint(0, 3)
    if is_new_name1 == 0:
        name1 = str(rdm.random())               # on pourrait avoir 2 fois le meme nom mais c'est improbable + pas grave
        time1 = rdm.randint(0, APSP.max_time - 1)
        pos1 = (rdm.random() * (max_lat - min_lat) + min_lat, rdm.random() * (max_lon - min_lon) + min_lon)
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
        pos2 = (rdm.random() * (max_lat - min_lat) + min_lat, rdm.random() * (max_lon - min_lon) + min_lon)
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
    APSP.add_edge(name1, time1, name2, time2, u_position=pos1, v_position=pos2)




def generate_random_vertex(APSP, mmap, min_lat, max_lat, min_lon, max_lon):


    if rdm.randint(0, 1) == 1 : # New position or not
        # New position
        z_name = str(rdm.random())  # on pourrait avoir 2 fois le meme nom mais c'est improbable + pas grave
        time = rdm.randint(0, APSP.max_time - 1)
        lat = rdm.random() *(max_lat- min_lat) + min_lat
        lon = rdm.random() * (max_lon - min_lon) + min_lon
        pos = (lat, lon)

    else:
        # Old position
        z_name = rdm.sample(APSP.idx_to_name, 1).pop()
        if len(APSP.used_time[APSP.name_to_idx[z_name]]) > 0 and rdm.randint(0, 1) == 1:   #New time or not
            # Old time
            time = rdm.sample(APSP.used_time[APSP.name_to_idx[z_name]], 1).pop()
            pos =None
        else:
            #New time
            time = rdm.randint(0, APSP.max_time - 1)
            pos = mmap.stop_position_dico[z_name]

    z_in, z_out = [], []
    for _ in range(rdm.randint(0, 5)):   # Number of new edge between 0 and 4
        name2 = rdm.sample(APSP.idx_to_name, 1).pop()
        if len(APSP.used_time[APSP.name_to_idx[name2]]) > 0 and rdm.randint(0, 1) == 1 :   #New time or not
            # Old time
            time2 = rdm.sample(APSP.used_time[APSP.name_to_idx[name2]], 1).pop()
        else:
            #New time
            time2 = rdm.randint(0, APSP.max_time - 1)

        if time2 < time:
            z_in.append((name2, time2))
        else:
            z_out.append((name2, time2))

    #print("add vertex {} time {} pos {} :  z_in {} , z_out {}".format(z_name, time, pos, z_in, z_out))
    APSP.add_vertex(z_name, time, pos, z_in, z_out)


def generate_random_add(APSP,mmap, min_lat, max_lat, min_lon, max_lon):
    if rdm.randint(0,5) == 0:
        generate_random_vertex(APSP,mmap, min_lat, max_lat, min_lon, max_lon)
    else:
        generate_random_edge(APSP, min_lat, max_lat, min_lon, max_lon)


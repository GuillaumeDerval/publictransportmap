import os

from Program.dynamic_Inc_APSP.Dynamic_Incremental_All_Pair_Shortest_Path import *


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

def check_if_correct_modification(modification_function,graph_path = "mini.json"):
    APSP = Dynamic_APSP(graph_path)
    modification_function(APSP)
    APSP.hard_save_graph("data_test/save.json")
    APSP.hard_save_is_reachable("data_test/path_computed/")
    APSP.hard_save_distance("data_test/dist_computed/")

    Expect = Dynamic_APSP("data_test/save.json")
    Expect.hard_save_is_reachable("data_test/path_expected/")
    Expect.hard_save_distance("data_test/dist_expected/")
    path_comp = compare_results("data_test/path_expected/", "data_test/path_computed/")
    compar = compare_results("data_test/dist_expected/", "data_test/dist_computed/")
    return path_comp, compar
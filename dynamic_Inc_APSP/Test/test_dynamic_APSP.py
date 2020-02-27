from unittest import TestCase
import json
import os
import numpy as np
from dynamic_Inc_APSP.Dynamic_Incremental_All_Pair_Shortest_Path import *
import random as rdm


class TestDynamic_APSP(TestCase):
    def setUp(self):
        super().setUp()
        for file_name in os.listdir("data_test/computed/"):
            os.remove("data_test/computed/" + file_name)
        for file_name in os.listdir("data_test/expected/"):
            os.remove("data_test/expected/" + file_name)
        for file_name in os.listdir("data_test/path_computed/"):
            os.remove("data_test/path_computed/" + file_name)
        for file_name in os.listdir("data_test/path_expected/"):
            os.remove("data_test/path_expected/" + file_name)


    def test_save_graph_mini(self):
        APSP = Dynamic_APSP("mini.json")
        APSP.hard_save_graph("data_test/mini_save.json")
        file1 = open("mini.json")
        file2 = open("data_test/mini_save.json")
        self.assertEqual(json.loads(file1.read()), json.loads(file2.read()))
        file1.close()
        file2.close()

    def test_save_graph_medium(self):
        APSP = Dynamic_APSP("medium.json")
        APSP.hard_save_graph("data_test/medium_save.json")
        file1 = open("medium.json")
        file2 = open("data_test/medium_save.json")
        self.assertEqual(json.loads(file1.read()), json.loads(file2.read()))
        file1.close()
        file2.close()

    def test_path_mini(self):
        exp_path = "data_test/path_mini_expected/"
        compu_path = "data_test/computed/"
        np.save(exp_path +"0.npy", np.array([1, 1, 1, 1, 1, 1], dtype= np.bool).astype(np.bool))
        np.save(exp_path + "50.npy", np.array([0, 1, 0, 0, 1, 1], dtype=np.bool).astype(np.bool))
        np.save(exp_path + "110.npy", np.array([0, 1, 1, 1, 1, 1], dtype=np.bool).astype(np.bool))
        np.save(exp_path + "120.npy", np.array([0, 1, 0, 1, 1, 1], dtype=np.bool).astype(np.bool))
        np.save(exp_path + "170.npy", np.array([0, 0, 0, 0, 1, 0], dtype=np.bool).astype(np.bool))
        np.save(exp_path + "270.npy", np.array([0, 0, 0, 0, 0, 1], dtype=np.bool).astype(np.bool))
        for file_name in os.listdir(compu_path):
            os.remove(compu_path + file_name)
        APSP = Dynamic_APSP("mini.json")
        for name, array in zip(APSP.path.pos_to_vertex, APSP.path.is_reach):
            path = compu_path + str(name) + ".npy"
            #print(path, array)
            np.save(path, array)
        comparisson = compare_results(exp_path, compu_path)
        self.assertTrue(comparisson)

    def test_save_distance_mini(self):
        exp_path = "data_test/dist_mini_expected/"
        compu_path = "data_test/computed/"
        # np.save(exp_path + "a.npy", np.array([0, 10, 20]).astype(np.int16))
        # np.save(exp_path + "b.npy", np.array([30, 0, 50]).astype(np.int16))
        # np.save(exp_path + "c.npy", np.array([-1, -1, 0]).astype(np.int16))
        # np.save("data_test/dist_mini_expected/d.npy", np.array([-1, -1, -1]).astype(np.int16))
        # np.save("data_test/dist_mini_expected/e.npy", np.array([-1, -1, -1]).astype(np.int16))

        APSP = Dynamic_APSP("mini.json")
        APSP.hard_save_distance(compu_path)
        comparisson = compare_results(exp_path, compu_path)
        self.assertTrue(comparisson)

    def test_save_distance_medium(self):
        APSP = Dynamic_APSP("medium.json")
        APSP.hard_save_distance("data_test/computed/")
        comparisson = compare_results("data_test/dist_medium_expected/", "data_test/computed/")
        self.assertTrue(comparisson)

    def test_modify_graph(self):
        APSP = Dynamic_APSP("mini.json")

        APSP.add_isolated_vertex("d", 30)
        APSP.add_isolated_vertex("c", 90)
        APSP.add_edge("d", 30, "c", 90)
        APSP.add_edge("b", 10, "c", 90)
        APSP.add_edge("e", 0, "b", 10)
        APSP.add_edge("b", 10, "d", 30)

        APSP.hard_save_graph("data_test/mini_updated_save.json")
        file1 = open("mini_updated.json")
        file2 = open("data_test/mini_updated_save.json")
        self.assertEqual(json.loads(file1.read()), json.loads(file2.read()))
        file1.close()
        file2.close()

    def test_add_isolated_vertex_mini_1(self):
        #add existing vertex
        path_comp, dist_comp = check_if_correct_modification(lambda APSP: APSP.add_isolated_vertex("b",70))
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_isolated_vertex_mini_2(self):
        # add vertex with existing label
        def my_change(APSP):
            APSP.add_isolated_vertex("a", 90)
            APSP.add_isolated_vertex("c", 10)

        path_comp, dist_comp = check_if_correct_modification(my_change)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_isolated_vertex_mini_3(self):
        # add vertex with new label
        def my_change(APSP):
            APSP.add_isolated_vertex("d", 15)
            APSP.add_isolated_vertex("k", 10)

        path_comp, dist_comp = check_if_correct_modification(my_change)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_isolated_vertex_rdm_mini(self):
        # big the for added vertex
        def my_change(APSP):
            rdm.seed(4242)
            i = 10
            for _ in range(30):
                choice = rdm.randint(0, 2)
                idx = rdm.randint(0, len(APSP.name_to_idx) - 1)
                if choice == 0:
                    # add existing
                    idx = rdm.randint(0, len(APSP.name_to_idx) - 1)
                    name = APSP.idx_to_name[idx]
                    if len(APSP.used_time[idx]) != 0:
                        time = APSP.used_time[idx][rdm.randint(0, len(APSP.used_time[idx]) - 1)]
                        APSP.add_isolated_vertex(name, time)
                    APSP.add_isolated_vertex(name, time)
                elif choice == 1:
                    # add vertex with existing label
                    idx = rdm.randint(0, len(APSP.name_to_idx) - 1)
                    name = APSP.idx_to_name[idx]
                    time = rdm.randint(0, APSP.max_time - 1)
                    APSP.add_isolated_vertex(name, time)
                elif choice == 2:
                    # add vertex with new label
                    name = str(i)
                    i += 1
                    time = rdm.randint(0, APSP.max_time - 1)
                    APSP.add_isolated_vertex(name, time)

        path_comp, dist_comp = check_if_correct_modification(my_change)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_isolated_vertex_rdm_medium(self):
        # big the for added vertex
        def my_change(APSP):
            rdm.seed(4243)
            i = 10
            for _ in range(100):
                choice = rdm.randint(0, 2)
                idx = rdm.randint(0, len(APSP.name_to_idx) - 1)
                if choice == 0:
                    # add existing
                    idx = rdm.randint(0, len(APSP.name_to_idx) - 1)
                    name = APSP.idx_to_name[idx]
                    if len(APSP.used_time[idx]) != 0 :
                        time = APSP.used_time[idx][rdm.randint(0, len(APSP.used_time[idx]) - 1)]
                        APSP.add_isolated_vertex(name, time)
                elif choice == 1:
                    # add vertex with existing label
                    idx = rdm.randint(0, len(APSP.name_to_idx) - 1)
                    name = APSP.idx_to_name[idx]
                    time = rdm.randint(0, APSP.max_time - 1)
                    APSP.add_isolated_vertex(name, time)
                elif choice == 2:
                    # add vertex with new label
                    name = str(i)
                    i += 1
                    time = rdm.randint(0, APSP.max_time - 1)
                    APSP.add_isolated_vertex(name, time)

        path_comp, dist_comp = check_if_correct_modification(my_change, "medium.json")
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_edge_mini_0(self):
        # add existing edge
        def my_change(APSP):
            APSP.add_edge("a", 50,"b",70)
            APSP.add_edge("b", 20, "a", 50)
        comparisson = check_if_correct_modification(my_change)
        self.assertTrue(comparisson)

    def test_add_edge_mini_1(self):
        # add edge with no impact
        def my_change(APSP):
            APSP.add_edge("b", 80, "c", 90)
            APSP.add_edge("a", 70, "a", 90)

        path_comp, dist_comp = check_if_correct_modification(my_change)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_edge_mini_2(self):
        # add edge (u,v) where deg_in(u) = 0
        def my_change(APSP):
            APSP.add_edge("d", 0, "a", 0)
            #APSP.add_edge("c", 40, "a", 50)
            #APSP.add_edge("a", 0, "c", 40)

        path_comp, dist_comp = check_if_correct_modification(my_change)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_edge_mini_3(self):
        # add edge (u,v) where deg_out(v) = 0
        def my_change(APSP):
            APSP.add_edge("c", 70, "d", 90)
            APSP.add_edge("a", 50, "d", 90)
            APSP.add_edge("d", 90, "a", 95)

        path_comp, dist_comp = check_if_correct_modification(my_change)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_edge_mini_4(self):
        # add edge (u,v)
        def my_change(APSP):
            #APSP.add_edge("d", 0, "a", 0)
            APSP.add_edge("a", 0, "c", 40)
            APSP.add_edge("c", 40, "a", 50)

        path_comp, dist_comp = check_if_correct_modification(my_change)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_edge_rdm_mini(self):
        def my_change(APSP : Dynamic_APSP):
            rdm.seed(76548)
            i = 10
            for _ in range(100):
                is_new_name1 = rdm.randint(0, 3)
                if is_new_name1 == 0:
                    name1= str(i)
                    i += 1
                    time1 = rdm.randint(0, APSP.max_time -1)
                else:
                    name1 = rdm.sample(APSP.idx_to_name,1).pop()
                    is_new_time = rdm.randint(0, 3)
                    if is_new_time == 0:
                        time1 = rdm.randint(0, APSP.max_time - 1)
                    else: time1 = rdm.sample(APSP.used_time[APSP.name_to_idx[name1]],1).pop()

                is_new_name2 = rdm.randint(0, 3)
                if is_new_name2 == 0:
                    name2 = str(i)
                    i += 1
                    time2 = rdm.randint(time1, APSP.max_time - 1)
                else:
                    name2 = rdm.sample(APSP.idx_to_name,1).pop()
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
                        else: time2 = rdm.randint(time1, APSP.max_time - 1)
                print("add edge {} time {} to {} time {}".format(name1, time1, name2, time2))
                APSP.add_edge(name1, time1, name2, time2)

        path_comp, dist_comp = check_if_correct_modification(my_change)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_edge_rdm_medium(self):
        def my_change(APSP : Dynamic_APSP):
            rdm.seed(654321)
            i = 10
            for _ in range(50):
                is_new_name1 = rdm.randint(0, 3)
                if is_new_name1 == 0:
                    name1= str(i)
                    i += 1
                    time1 = rdm.randint(0, APSP.max_time -1)
                else:
                    name1 = rdm.sample(APSP.idx_to_name,1).pop()
                    is_new_time = rdm.randint(0, 3)
                    if is_new_time == 0 or len(APSP.used_time[APSP.name_to_idx[name1]]) == 0:
                        time1 = rdm.randint(0, APSP.max_time - 1)
                    else: time1 = rdm.sample(APSP.used_time[APSP.name_to_idx[name1]],1).pop()

                is_new_name2 = rdm.randint(0, 3)
                if is_new_name2 == 0:
                    name2 = str(i)
                    i += 1
                    time2 = rdm.randint(time1, APSP.max_time - 1)
                else:
                    name2 = rdm.sample(APSP.idx_to_name,1).pop()
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
                        else: time2 = rdm.randint(time1, APSP.max_time - 1)
                print("add edge {} time {} to {} time {}".format(name1,time1,name2,time2))
                APSP.add_edge(name1, time1, name2, time2)

        path_comp, dist_comp = check_if_correct_modification(my_change, "medium.json")
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    # def test_add_vertex(self):
    #    self.fail()



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
            print("f_exp : ", f_exp,"    f_actu : ",f_actu)
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
    APSP.hard_save_distance("data_test/computed/")

    Expect = Dynamic_APSP("data_test/save.json")
    Expect.hard_save_is_reachable("data_test/path_expected/")
    Expect.hard_save_distance("data_test/expected/")
    path_comp = compare_results("data_test/path_expected/", "data_test/path_computed/")
    comparisson = compare_results("data_test/expected/", "data_test/computed/")
    return path_comp, comparisson





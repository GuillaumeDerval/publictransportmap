from unittest import TestCase
import os
import numpy as np
from Program.Data_manager.main import DataManager
from Program.dynamic_Inc_APSP.Dynamic_Incremental_All_Pair_Shortest_Path import *
from Test.Test_dynamic_inc_APSP.my_utils import compare_results_distance


class TestInitialisationAPSP(TestCase):
    def setUp(self):
        super().setUp()

        self.param_small = DataManager.load_data("./../Data_test", "APSP_mini", "train_only")  # without walk
        self.param_medium = DataManager.load_data("./../Data_test","APSP_medium", "train_bus")

        for file_name in os.listdir("data_test/dist_computed/"):
            os.remove("data_test/dist_computed/" + file_name)

        for file_name in os.listdir("data_test/path_computed/"):
            os.remove("data_test/path_computed/" + file_name)


    def test_save_graph_mini(self):
        APSP = Dynamic_APSP(self.param_small)
        APSP.hard_save_graph("data_test/graph_save.json")
        file1 = open(self.param_small.PATH.GRAPH_TC_WALK)
        file2 = open("data_test/graph_save.json")
        self.assertEqual(json.loads(file1.read()), json.loads(file2.read()))
        file1.close()
        file2.close()

    def test_save_graph_medium(self):
        APSP = Dynamic_APSP(self.param_medium)
        APSP.hard_save_graph("data_test/graph_save.json")
        file1 = open(self.param_medium.PATH.GRAPH_TC_WALK)
        file2 = open("data_test/graph_save.json")
        graph1 = json.loads(file1.read())
        graph2 = json.loads(file2.read())
        self.assertEqual(graph1, graph2)
        file1.close()
        file2.close()

    def test_path_mini(self):
        exp_path = "data_test/path_mini_expected/"
        compu_path = "data_test/path_computed/"
        np.save(exp_path +"0.npy", np.array([1, 1, 1, 1, 1, 1], dtype= np.bool).astype(np.bool))
        np.save(exp_path + "50.npy", np.array([0, 1, 0, 0, 1, 1], dtype=np.bool).astype(np.bool))
        np.save(exp_path + "110.npy", np.array([0, 1, 1, 1, 1, 1], dtype=np.bool).astype(np.bool))
        np.save(exp_path + "120.npy", np.array([0, 1, 0, 1, 1, 1], dtype=np.bool).astype(np.bool))
        np.save(exp_path + "170.npy", np.array([0, 0, 0, 0, 1, 0], dtype=np.bool).astype(np.bool))
        np.save(exp_path + "270.npy", np.array([0, 0, 0, 0, 0, 1], dtype=np.bool).astype(np.bool))
        with open(exp_path+ "__conversion.json",'w') as out:
            json.dump({"0":0,"50":1,"110":2,"120":3,"170":4,"270":5}, out)
        for file_name in os.listdir(compu_path):
            os.remove(compu_path + file_name)
        APSP = Dynamic_APSP(self.param_small)
        APSP.path.hard_save(compu_path)

        comparisson = compare_results_distance(exp_path, compu_path)
        self.assertTrue(comparisson)

    def test_save_distance_mini(self):
        exp_path = "data_test/dist_mini_expected/"
        compu_path = "data_test/dist_computed/"
        # np.save(exp_path + "a.npy", np.array([0, 10, 20]).astype(np.int16))
        # np.save(exp_path + "b.npy", np.array([30, 0, 50]).astype(np.int16))
        # np.save(exp_path + "c.npy", np.array([-1, -1, 0]).astype(np.int16))
        # np.save("data_test/dist_mini_expected/d.npy", np.array([-1, -1, -1]).astype(np.int16))
        # np.save("data_test/dist_mini_expected/e.npy", np.array([-1, -1, -1]).astype(np.int16))
        #with open(exp_path+ "__conversion.json",'w') as out:
        #    json.dump({"a":0,"b":1,"c":2}, out)

        APSP = Dynamic_APSP(self.param_small)
        APSP.hard_save_distance(compu_path)
        comparisson = compare_results_distance(exp_path, compu_path)
        self.assertTrue(comparisson)

    def test_save_distance_medium(self):
        DataManager.produce_data("./../Data_test", "APSP_medium", "train_bus", 0, 0)
        APSP = Dynamic_APSP(self.param_medium)
        APSP.hard_save_distance("data_test/dist_computed/")
        comparisson = compare_results_distance("data_test/dist_medium_expected/", "data_test/dist_computed/")
        self.assertTrue(comparisson)









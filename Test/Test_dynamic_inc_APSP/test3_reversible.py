from unittest import TestCase
from Test.Test_dynamic_inc_APSP.my_utils import *
from Program.dynamic_Inc_APSP.Dynamic_Incremental_All_Pair_Shortest_Path import  *
import random as rdm
import shutil


class TestInitialisationAPSP(TestCase):
    def setUp(self):
        super().setUp()
        my_map.belgium_map = None
        for file_name in os.listdir("data_test/dist_computed/"):
            if file_name.find(".npy") != -1:
                os.remove("data_test/dist_computed/" + file_name)
            else:
                shutil.rmtree("data_test/dist_computed/" + file_name)

        for file_name in os.listdir("data_test/dist_expected/"):
            if file_name.find(".npy") != -1:
                os.remove("data_test/dist_expected/" + file_name)
            else:
                shutil.rmtree("data_test/dist_expected/" + file_name)

        for file_name in os.listdir("data_test/path_computed/"):
            if file_name.find(".npy") != -1:
                os.remove("data_test/path_computed/" + file_name)
            else:
                shutil.rmtree("data_test/path_computed/" + file_name)

        for file_name in os.listdir("data_test/path_expected/"):
            if file_name.find(".npy") != -1:
                os.remove("data_test/path_expected/" + file_name)
            else:
                shutil.rmtree("data_test/path_expected/" + file_name)

    def test_one_level_one_edge(self):
        data_path = "data_test/mini.json"

        mmap = my_map.get_map(path_shape="./../Test_metric/data/smallmap.geojson",
                              path_pop="./../Test_metric/data/popsector.csv",
                              stop_list_path="data_test/mini_stop_pos.json")
        APSP = Dynamic_APSP(data_path, mapmap=mmap)

        rdm.seed(1216)
        branch = []
        for _ in range(30):
            branch.append(generate_random_edge)

        check_save_and_restore(self, APSP, branch,data_path=data_path, path_exp="data_test/path_expected/",
                               dist_exp="data_test/dist_expected/", graph_compu="data_test/graph_compu.json",
                               path_comp="data_test/path_computed/", dist_comp="data_test/dist_computed/")

    def test_one_level_one_edge2(self):
        data_path = "data_test/medium.json"
        APSP = Dynamic_APSP(data_path)
        rdm.seed(1212)

        branch = []
        for _ in range(10):
            branch.append(generate_random_edge)

        check_save_and_restore(self, APSP, branch,data_path=data_path, path_exp="data_test/path_expected/",
                               dist_exp="data_test/dist_expected/", graph_compu="data_test/graph_compu.json",
                               path_comp="data_test/path_computed/", dist_comp="data_test/dist_computed/")

    def test_one_level_multi_edge(self):
        # the modification  add between 0 and 5 edges
        data_path = "data_test/mini.json"
        APSP = Dynamic_APSP(data_path)
        rdm.seed(1212)

        branch = []
        for _ in range(30):
            def multi_edge(APSP):
                n = rdm.randint(0,5)
                for _ in range(n):
                    generate_random_edge(APSP)

            branch.append(multi_edge)

        check_save_and_restore(self, APSP, branch, data_path=data_path, path_exp="data_test/path_expected/",
                               dist_exp="data_test/dist_expected/", graph_compu="data_test/graph_compu.json",
                               path_comp="data_test/path_computed/", dist_comp="data_test/dist_computed/")

    def test_one_level_multi_edge2(self):
        # the modification  add between 0 and 5 edges
        data_path = "data_test/medium.json"
        APSP = Dynamic_APSP(data_path)
        rdm.seed(1212)

        branch = []
        for _ in range(10):
            def multi_edge(APSP):
                n = rdm.randint(0,5)
                for _ in range(n):
                    generate_random_edge(APSP)

            branch.append(multi_edge)

        check_save_and_restore(self, APSP, branch,data_path=data_path, path_exp="data_test/path_expected/",
                               dist_exp="data_test/dist_expected/", graph_compu="data_test/graph_compu.json",
                               path_comp="data_test/path_computed/", dist_comp="data_test/dist_computed/")

    def test_3_level_one_edge(self):
        data_path = "data_test/mini.json"
        APSP = Dynamic_APSP(data_path)
        rdm.seed(1212)

        def multi_level(APSP, level):
            if level < 3:
                os.mkdir("data_test/path_expected/" + str(level))
                os.mkdir("data_test/dist_expected/" + str(level))
                os.mkdir("data_test/path_computed/" + str(level))
                os.mkdir("data_test/dist_computed/" + str(level))
                branch = []
                for _ in range(5):
                    branch.append(generate_random_edge)
                    multi_level(APSP, level + 1)


                check_save_and_restore(self, APSP, branch,data_path=data_path, path_exp= "data_test/path_expected/{}/".format(level),
                                   dist_exp= "data_test/dist_expected/{}/".format(level), graph_compu= ("data_test/graph_compu"+ str(level)+ ".json"),
                                       path_comp= "data_test/path_computed/{}/".format(level), dist_comp= "data_test/dist_computed/{}/".format(level))

                shutil.rmtree("data_test/path_expected/" + str(level))
                shutil.rmtree("data_test/dist_expected/" + str(level))
                shutil.rmtree("data_test/path_computed/" + str(level))
                shutil.rmtree("data_test/dist_computed/" + str(level))

        multi_level(APSP, 0)

    def test_3_level_multi_edge(self):
        data_path = "data_test/mini.json"
        APSP = Dynamic_APSP(data_path)
        rdm.seed(1212)

        def multi_edge(APSP):
            n = rdm.randint(0, 5)
            for _ in range(n):
                generate_random_edge(APSP)

        def multi_level(APSP, level):
            if level < 3:
                os.mkdir("data_test/path_expected/" + str(level))
                os.mkdir("data_test/dist_expected/" + str(level))
                os.mkdir("data_test/path_computed/" + str(level))
                os.mkdir("data_test/dist_computed/" + str(level))
                branch = []
                for _ in range(5):
                    branch.append(multi_edge)
                    multi_level(APSP, level + 1)

                check_save_and_restore(self, APSP, branch,data_path=data_path, path_exp= "data_test/path_expected/{}/".format(level),
                                   dist_exp= "data_test/dist_expected/{}/".format(level), graph_compu= ("data_test/graph_compu"+ str(level)+ ".json"),
                                       path_comp= "data_test/path_computed/{}/".format(level), dist_comp= "data_test/dist_computed/{}/".format(level))

                shutil.rmtree("data_test/path_expected/" + str(level))
                shutil.rmtree("data_test/dist_expected/" + str(level))
                shutil.rmtree("data_test/path_computed/" + str(level))
                shutil.rmtree("data_test/dist_computed/" + str(level))

        multi_level(APSP, 0)





    def test_one_level_one_vertex(self):
        data_path = "data_test/mini.json"

        mmap = my_map.get_map(path_shape="./../Test_metric/data/smallmap.geojson",
                              path_pop="./../Test_metric/data/popsector.csv",
                              stop_list_path="data_test/mini_stop_pos.json")
        APSP = Dynamic_APSP(data_path, mapmap=mmap)

        rdm.seed(1216)
        branch = []
        for _ in range(30):
            branch.append(lambda x: generate_random_vertex(x, mmap, 0, 7000, 0, 3000))

        check_save_and_restore(self, APSP, branch,data_path=data_path, path_exp="data_test/path_expected/",
                               dist_exp="data_test/dist_expected/", graph_compu="data_test/graph_compu.json",
                               path_comp="data_test/path_computed/", dist_comp="data_test/dist_computed/")

    def test_one_level_multi_vertex(self):
        # the modification  add between 0 and 5 edges
        data_path = "data_test/mini.json"
        mmap = my_map.get_map(path_shape="./../Test_metric/data/smallmap.geojson",
                              path_pop="./../Test_metric/data/popsector.csv",
                              stop_list_path="data_test/mini_stop_pos.json")
        APSP = Dynamic_APSP(data_path, mapmap=mmap)

        rdm.seed(1212)

        branch = []
        for _ in range(10):
            def multi_edge(APSP):
                n = rdm.randint(0,5)
                for _ in range(n):
                    generate_random_vertex(APSP, mmap, 0, 7000, 0, 3000)

            branch.append(multi_edge)

        check_save_and_restore(self, APSP, branch,data_path=data_path, path_exp="data_test/path_expected/",
                               dist_exp="data_test/dist_expected/", graph_compu="data_test/graph_compu.json",
                               path_comp="data_test/path_computed/", dist_comp="data_test/dist_computed/")


    def test_3_level_multi_vertex(self):
        data_path = "data_test/mini.json"
        mmap = my_map.get_map(path_shape="./../Test_metric/data/smallmap.geojson",
                              path_pop="./../Test_metric/data/popsector.csv",
                              stop_list_path="data_test/mini_stop_pos.json")
        APSP = Dynamic_APSP(data_path, mapmap=mmap)
        rdm.seed(1212)

        def multi_vertex(APSP):
            n = rdm.randint(0, 5)
            for _ in range(n):
                generate_random_vertex(APSP, mmap, 0, 7000, 0, 3000)

        def multi_level(APSP, level):
            if level < 3:
                os.mkdir("data_test/path_expected/" + str(level))
                os.mkdir("data_test/dist_expected/" + str(level))
                os.mkdir("data_test/path_computed/" + str(level))
                os.mkdir("data_test/dist_computed/" + str(level))
                branch = []
                for _ in range(5):
                    branch.append(multi_vertex)
                    multi_level(APSP, level + 1)

                check_save_and_restore(self, APSP, branch,data_path=data_path, path_exp= "data_test/path_expected/{}/".format(level),
                                   dist_exp= "data_test/dist_expected/{}/".format(level), graph_compu= ("data_test/graph_compu"+ str(level)+ ".json"),
                                       path_comp= "data_test/path_computed/{}/".format(level), dist_comp= "data_test/dist_computed/{}/".format(level))

                shutil.rmtree("data_test/path_expected/" + str(level))
                shutil.rmtree("data_test/dist_expected/" + str(level))
                shutil.rmtree("data_test/path_computed/" + str(level))
                shutil.rmtree("data_test/dist_computed/" + str(level))

        multi_level(APSP, 0)

    def test_one_level_multi_add(self):
        # the modification  add between 0 and 5 edges
        data_path = "data_test/mini.json"
        mmap = my_map.get_map(path_shape="./../Test_metric/data/smallmap.geojson",
                              path_pop="./../Test_metric/data/popsector.csv",
                              stop_list_path="data_test/mini_stop_pos.json")
        APSP = Dynamic_APSP(data_path, mapmap=mmap)
        rdm.seed(123456)

        branch = []
        for _ in range(10):
            def multi_edge(APSP):
                n = rdm.randint(0,5)
                for _ in range(n):
                    generate_random_add(APSP, mmap, 0, 7000, 0, 3000)

            branch.append(multi_edge)

        check_save_and_restore(self, APSP, branch,data_path=data_path, path_exp="data_test/path_expected/",
                               dist_exp="data_test/dist_expected/", graph_compu="data_test/graph_compu.json",
                               path_comp="data_test/path_computed/", dist_comp="data_test/dist_computed/")


    def test_3_level_multi_add(self):
        data_path = "data_test/mini.json"
        mmap = my_map.get_map(path_shape="./../Test_metric/data/smallmap.geojson",
                              path_pop="./../Test_metric/data/popsector.csv",
                              stop_list_path="data_test/mini_stop_pos.json")
        APSP = Dynamic_APSP(data_path, mapmap=mmap)
        rdm.seed(1212)

        def multi_edge(APSP):
            n = rdm.randint(0, 5)
            for _ in range(n):
                generate_random_add(APSP, mmap, 0, 7000, 0, 3000)

        def multi_level(APSP, level):
            if level < 3:
                os.mkdir("data_test/path_expected/" + str(level))
                os.mkdir("data_test/dist_expected/" + str(level))
                os.mkdir("data_test/path_computed/" + str(level))
                os.mkdir("data_test/dist_computed/" + str(level))
                branch = []
                for _ in range(5):
                    branch.append(multi_edge)
                    multi_level(APSP, level + 1)

                check_save_and_restore(self, APSP, branch,data_path=data_path, path_exp= "data_test/path_expected/{}/".format(level),
                                   dist_exp= "data_test/dist_expected/{}/".format(level), graph_compu= ("data_test/graph_compu"+ str(level)+ ".json"),
                                       path_comp= "data_test/path_computed/{}/".format(level), dist_comp= "data_test/dist_computed/{}/".format(level))

                shutil.rmtree("data_test/path_expected/" + str(level))
                shutil.rmtree("data_test/dist_expected/" + str(level))
                shutil.rmtree("data_test/path_computed/" + str(level))
                shutil.rmtree("data_test/dist_computed/" + str(level))

        multi_level(APSP, 0)


def check_save_and_restore(TestCase, APSP, branch, data_path, path_exp, dist_exp,graph_compu, path_comp, dist_comp):
    Expect = Dynamic_APSP(data_path)
    Expect.hard_save_is_reachable(path_exp)
    Expect.hard_save_distance(dist_exp)

    for b_modif in branch:
        APSP.save()

        # check that save don't modify results
        APSP.hard_save_graph(graph_compu)
        APSP.hard_save_is_reachable(path_comp)
        APSP.hard_save_distance(dist_comp)
        with open(data_path) as gr_exp:
            with open(graph_compu) as gr_comp:
                TestCase.assertEqual(json.loads(gr_exp.read()), json.loads(gr_comp.read()))
        TestCase.assertTrue(compare_results(path_exp, path_comp))  # compare path
        TestCase.assertTrue(compare_results(dist_exp, dist_comp))  # compare distance

        b_modif(APSP)
        APSP.restore()

        # check that restore go back to the previus results
        APSP.hard_save_is_reachable(path_comp)
        APSP.hard_save_distance(dist_comp)
        TestCase.assertTrue(compare_results(path_exp, path_comp))  # compare path
        TestCase.assertTrue(compare_results(dist_exp, dist_comp))  # compare distance

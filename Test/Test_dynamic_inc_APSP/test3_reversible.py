from unittest import TestCase
from Test.Test_dynamic_inc_APSP.my_utils import *
from Program.dynamic_Inc_APSP.Dynamic_Incremental_All_Pair_Shortest_Path import *
import random as rdm
import shutil


class TestInitialisationAPSP(TestCase):
    def setUp(self):
        super().setUp()

        self.param_mini: Parameters = DataManager.load_data("./../Data_test", "APSP_mini",
                                                            "train_only")  # without walk
        self.param_medium: Parameters = DataManager.load_data("./../Data_test", "APSP_medium", "train_bus")

        def remove_files(dir_path):
            for file_name in os.listdir(dir_path):
                if file_name.find(".npy") != -1 or file_name.find("__conversion.json") != -1:
                    os.remove(dir_path + file_name)
                else:
                    shutil.rmtree(dir_path + file_name)

        remove_files("data_test/dist_computed/")
        remove_files("data_test/dist_expected/")
        remove_files("data_test/path_computed/")
        remove_files("data_test/path_expected/")

        MyMap.belgium_map = None

    def test_one_level_one_edge(self):
        APSP = Dynamic_APSP(self.param_mini)

        rdm.seed(1216)
        branch = []
        for _ in range(30):
            branch.append(generate_random_edge)

        check_save_and_restore(self, APSP, branch, self.param_mini,
                               graph_exp="data_test/graph_exp.json", path_exp="data_test/path_expected/",
                               dist_exp="data_test/dist_expected/",
                               graph_compu="data_test/graph_compu.json",
                               path_comp="data_test/path_computed/", dist_comp="data_test/dist_computed/")

    def test_one_level_one_edge2(self):
        APSP = Dynamic_APSP(self.param_medium)
        rdm.seed(1212)

        branch = []
        for _ in range(10):
            branch.append(generate_random_edge)

        check_save_and_restore(self, APSP, branch, param=self.param_medium,
                               graph_exp="data_test/graph_exp.json", path_exp="data_test/path_expected/",
                               dist_exp="data_test/dist_expected/",
                               graph_compu="data_test/graph_compu.json",
                               path_comp="data_test/path_computed/", dist_comp="data_test/dist_computed/")

    def test_one_level_multi_edge(self):
        # the modification  add between 0 and 5 edges
        APSP = Dynamic_APSP(self.param_mini)
        rdm.seed(1212)

        branch = []
        for _ in range(30):
            def multi_edge(APSP, transp):
                n = rdm.randint(0, 5)
                for _ in range(n):
                    generate_random_edge(APSP, transp)

            branch.append(multi_edge)

        check_save_and_restore(self, APSP, branch, param=self.param_mini,
                               graph_exp="data_test/graph_exp.json", path_exp="data_test/path_expected/",
                               dist_exp="data_test/dist_expected/",
                               graph_compu="data_test/graph_compu.json",
                               path_comp="data_test/path_computed/", dist_comp="data_test/dist_computed/")

    def test_one_level_multi_edge2(self):
        # the modification  add between 0 and 5 edges
        APSP = Dynamic_APSP(self.param_medium)
        rdm.seed(1212)

        branch = []
        for _ in range(10):
            def multi_edge(APSP,transp):
                n = rdm.randint(0, 5)
                for _ in range(n):
                    generate_random_edge(APSP, transp)

            branch.append(multi_edge)

        check_save_and_restore(self, APSP, branch, self.param_medium,
                               graph_exp="data_test/graph_exp.json", path_exp="data_test/path_expected/",
                               dist_exp="data_test/dist_expected/",
                               graph_compu="data_test/graph_compu.json",
                               path_comp="data_test/path_computed/", dist_comp="data_test/dist_computed/")

    def test_3_level_one_edge(self):
        APSP = Dynamic_APSP(self.param_mini)
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

                check_save_and_restore(self, APSP, branch, self.param_mini,
                                       graph_exp=("data_test/graph_exp" + str(level) + ".json"),
                                       path_exp="data_test/path_expected/{}/".format(level),
                                       dist_exp="data_test/dist_expected/{}/".format(level),
                                       graph_compu=("data_test/graph_compu" + str(level) + ".json"),
                                       path_comp="data_test/path_computed/{}/".format(level),
                                       dist_comp="data_test/dist_computed/{}/".format(level))

                shutil.rmtree("data_test/path_expected/" + str(level))
                shutil.rmtree("data_test/dist_expected/" + str(level))
                shutil.rmtree("data_test/path_computed/" + str(level))
                shutil.rmtree("data_test/dist_computed/" + str(level))

        multi_level(APSP, 0)

    def test_3_level_multi_edge(self):
        APSP = Dynamic_APSP(self.param_mini)
        rdm.seed(1212)

        def multi_edge(APSP, transp):
            n = rdm.randint(0, 5)
            for _ in range(n):
                generate_random_edge(APSP, transp)

        def multi_level(param, APSP, level):
            if level < 3:
                os.mkdir("data_test/path_expected/" + str(level))
                os.mkdir("data_test/dist_expected/" + str(level))
                os.mkdir("data_test/path_computed/" + str(level))
                os.mkdir("data_test/dist_computed/" + str(level))
                branch = []
                for _ in range(5):
                    branch.append(multi_edge)
                    multi_level(param,APSP, level + 1)

                check_save_and_restore(self, APSP, branch, param,
                                       graph_exp=("data_test/graph_exp" + str(level) + ".json"),
                                       path_exp="data_test/path_expected/{}/".format(level),
                                       dist_exp="data_test/dist_expected/{}/".format(level),
                                       graph_compu=("data_test/graph_compu" + str(level) + ".json"),
                                       path_comp="data_test/path_computed/{}/".format(level),
                                       dist_comp="data_test/dist_computed/{}/".format(level))

                shutil.rmtree("data_test/path_expected/" + str(level))
                shutil.rmtree("data_test/dist_expected/" + str(level))
                shutil.rmtree("data_test/path_computed/" + str(level))
                shutil.rmtree("data_test/dist_computed/" + str(level))

        multi_level(self.param_mini, APSP, 0)

    def test_one_level_one_vertex(self):
        APSP = Dynamic_APSP(self.param_mini)

        rdm.seed(1216)
        branch = []
        for _ in range(30):
            branch.append(lambda x, y: generate_random_vertex(x, y))

        check_save_and_restore(self, APSP, branch, self.param_mini,
                               graph_exp="data_test/graph_exp.json", path_exp="data_test/path_expected/",
                               dist_exp="data_test/dist_expected/",
                               graph_compu="data_test/graph_compu.json",
                               path_comp="data_test/path_computed/", dist_comp="data_test/dist_computed/")

    def test_one_level_multi_vertex(self):
        # the modification  add between 0 and 5 edges
        APSP = Dynamic_APSP(self.param_mini)

        rdm.seed(1212)

        branch = []
        for _ in range(10):
            def multi_edge(APSP, transp):
                n = rdm.randint(0, 5)
                for _ in range(n):
                    generate_random_vertex(APSP, transp)

            branch.append(multi_edge)

        check_save_and_restore(self, APSP, branch, self.param_mini,
                               graph_exp="data_test/graph_exp.json", path_exp="data_test/path_expected/",
                               dist_exp="data_test/dist_expected/",
                               graph_compu="data_test/graph_compu.json",
                               path_comp="data_test/path_computed/", dist_comp="data_test/dist_computed/")

    def test_3_level_multi_vertex(self):
        APSP = Dynamic_APSP(self.param_mini)
        rdm.seed(1212)

        def multi_vertex(APSP, transp):
            n = rdm.randint(0, 5)
            for _ in range(n):
                generate_random_vertex(APSP, transp)

        def multi_level(param,APSP, level):
            if level < 3:
                os.mkdir("data_test/path_expected/" + str(level))
                os.mkdir("data_test/dist_expected/" + str(level))
                os.mkdir("data_test/path_computed/" + str(level))
                os.mkdir("data_test/dist_computed/" + str(level))
                branch = []
                for _ in range(5):
                    branch.append(multi_vertex)
                    multi_level(param, APSP, level + 1)

                check_save_and_restore(self, APSP, branch, param,
                                       graph_exp=("data_test/graph_exp" + str(level) + ".json"),
                                       path_exp="data_test/path_expected/{}/".format(level),
                                       dist_exp="data_test/dist_expected/{}/".format(level),
                                       graph_compu=("data_test/graph_compu" + str(level) + ".json"),
                                       path_comp="data_test/path_computed/{}/".format(level),
                                       dist_comp="data_test/dist_computed/{}/".format(level))

                shutil.rmtree("data_test/path_expected/" + str(level))
                shutil.rmtree("data_test/dist_expected/" + str(level))
                shutil.rmtree("data_test/path_computed/" + str(level))
                shutil.rmtree("data_test/dist_computed/" + str(level))

        multi_level(self.param_mini, APSP, 0)

    def test_one_level_multi_add(self):
        # the modification  add between 0 and 5 edges
        APSP = Dynamic_APSP(self.param_mini)
        rdm.seed(123456)

        branch = []
        for _ in range(10):
            def multi_edge(APSP, transp):
                n = rdm.randint(0, 5)
                for _ in range(n):
                    generate_random_add(APSP, transp)

            branch.append(multi_edge)

        check_save_and_restore(self, APSP, branch, self.param_mini,
                               graph_exp="data_test/graph_exp.json", path_exp="data_test/path_expected/",
                               dist_exp="data_test/dist_expected/",
                               graph_compu="data_test/graph_compu.json",
                               path_comp="data_test/path_computed/", dist_comp="data_test/dist_computed/")

    def test_3_level_multi_add(self):

        APSP = Dynamic_APSP(self.param_mini)
        rdm.seed(1212)

        def multi_add(APSP, transp):
            n = rdm.randint(0, 5)
            for _ in range(n):
                generate_random_add(APSP, transp)

        def multi_level(param, APSP, level):
            if level < 3:
                os.mkdir("data_test/path_expected/" + str(level))
                os.mkdir("data_test/dist_expected/" + str(level))
                os.mkdir("data_test/path_computed/" + str(level))
                os.mkdir("data_test/dist_computed/" + str(level))
                branch = []
                for _ in range(5):
                    branch.append(multi_add)
                    multi_level(param, APSP, level + 1)

                check_save_and_restore(self, APSP, branch, param,
                                       graph_exp=("data_test/graph_exp" + str(level) + ".json"),
                                       path_exp="data_test/path_expected/{}/".format(level),
                                       dist_exp="data_test/dist_expected/{}/".format(level),
                                       graph_compu=("data_test/graph_compu" + str(level) + ".json"),
                                       path_comp="data_test/path_computed/{}/".format(level),
                                       dist_comp="data_test/dist_computed/{}/".format(level))

                shutil.rmtree("data_test/path_expected/" + str(level))
                shutil.rmtree("data_test/dist_expected/" + str(level))
                shutil.rmtree("data_test/path_computed/" + str(level))
                shutil.rmtree("data_test/dist_computed/" + str(level))

        multi_level(self.param_mini, APSP, 0)


def check_save_and_restore(TestCase, APSP, branch,param,graph_exp, path_exp, dist_exp,graph_compu, path_comp, dist_comp):
    Expect = Dynamic_APSP(param)
    Expect.hard_save_graph(graph_exp)
    Expect.hard_save_is_reachable(path_exp)
    Expect.hard_save_distance(dist_exp)

    for b_modif in branch:
        APSP.save()

        # check that save don't modify results
        APSP.hard_save_graph(graph_compu)
        APSP.hard_save_is_reachable(path_comp)
        APSP.hard_save_distance(dist_comp)
        with open(graph_exp) as gr_exp:
            with open(graph_compu) as gr_comp:
                TestCase.assertEqual(json.loads(gr_exp.read()), json.loads(gr_comp.read()))
        TestCase.assertTrue(compare_results_is_path(path_exp, path_comp))  # compare path
        TestCase.assertTrue(compare_results_distance(dist_exp, dist_comp))  # compare distance

        b_modif(APSP, None)
        APSP.restore()

        # check that restore go back to the previus results
        APSP.hard_save_is_reachable(path_comp)
        APSP.hard_save_distance(dist_comp)
        TestCase.assertTrue(compare_results_is_path(path_exp, path_comp))  # compare path
        TestCase.assertTrue(compare_results_distance(dist_exp, dist_comp))  # compare distance

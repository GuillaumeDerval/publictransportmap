from unittest import TestCase
from dynamic_Inc_APSP.Test.test_my_utils import *
from dynamic_Inc_APSP.Dynamic_Incremental_All_Pair_Shortest_Path import  *
import math
import random as rdm

class TestInitialisationAPSP(TestCase):
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


    def test_one_level_one_edge(self):
        data_path = "mini.json"
        APSP = Dynamic_APSP(data_path)
        rdm.seed(1212)


        branch = []
        for _ in range(10):
            branch.append(generate_random_edge)

        check_save_and_restore(self, APSP, branch,data_path=data_path, path_exp= "data_test/path_expected/",
                               dist_exp= "data_test/expected/", path_comp= "data_test/path_computed/", dist_comp= "data_test/computed/")

    def test_one_level_one_edge2(self):
        data_path = "medium.json"
        APSP = Dynamic_APSP(data_path)
        rdm.seed(1212)


        branch = []
        for _ in range(10):
            branch.append(generate_random_edge)

        check_save_and_restore(self, APSP, branch,data_path=data_path, path_exp= "data_test/path_expected/",
                               dist_exp= "data_test/expected/", path_comp= "data_test/path_computed/", dist_comp= "data_test/computed/")


    def test_one_level_multi_edge(self):
        # the modification  add between 0 and 5 edges
        data_path = "mini.json"
        APSP = Dynamic_APSP(data_path)
        rdm.seed(1212)

        branch = []
        for _ in range(10):
            def multi_edge(APSP):
                n = rdm.randint(0,5)
                for _ in range(n):
                    generate_random_edge(APSP)

            branch.append(multi_edge)


        check_save_and_restore(self, APSP, branch,data_path=data_path, path_exp= "data_test/path_expected/",
                               dist_exp= "data_test/expected/", path_comp= "data_test/path_computed/", dist_comp= "data_test/computed/")

    def test_one_level_multi_edge2(self):
        # the modification  add between 0 and 5 edges
        data_path = "medium.json"
        APSP = Dynamic_APSP(data_path)
        rdm.seed(1212)

        branch = []
        for _ in range(10):
            def multi_edge(APSP):
                n = rdm.randint(0,5)
                for _ in range(n):
                    generate_random_edge(APSP)

            branch.append(multi_edge)


        check_save_and_restore(self, APSP, branch,data_path=data_path, path_exp= "data_test/path_expected/",
                               dist_exp= "data_test/expected/", path_comp= "data_test/path_computed/", dist_comp= "data_test/computed/")


    def test_3_level_one_edge(self):
        data_path = "mini.json"
        APSP = Dynamic_APSP(data_path)
        rdm.seed(1212)

        def multi_level(APSP, level):
            while level < 3:
                os.mkdir("data_test/path_expected/" + str(level))
                os.mkdir("data_test/dist_expected/" + str(level))
                os.mkdir("data_test/path_computed/" + str(level))
                os.mkdir("data_test/dist_computed/" + str(level))
                branch = []
                for _ in range(10):
                    branch.append(generate_random_edge)
                    multi_level(APSP, level + 1)


                check_save_and_restore(self, APSP, branch,data_path=data_path, path_exp= "data_test/path_expected/",
                                   dist_exp= "data_test/expected/", path_comp= "data_test/path_computed/", dist_comp= "data_test/computed/")


                os.rmdir("data_test/path_expected/" + str(level))
                os.rmdir("data_test/dist_expected/" + str(level))
                os.rmdir("data_test/path_computed/" + str(level))
                os.rmdir("data_test/dist_computed/" + str(level))

        multi_level(APSP, 0)

    def test_3_level_multi_edge(self):
        data_path = "mini.json"
        APSP = Dynamic_APSP(data_path)
        rdm.seed(1212)

        def multi_edge(APSP):
            n = rdm.randint(0, 5)
            for _ in range(n):
                generate_random_edge(APSP)

        def multi_level(APSP, level):
            while level < 3:
                os.mkdir("data_test/path_expected/" + str(level))
                os.mkdir("data_test/dist_expected/" + str(level))
                os.mkdir("data_test/path_computed/" + str(level))
                os.mkdir("data_test/dist_computed/" + str(level))
                branch = []
                for _ in range(5):
                    branch.append(multi_edge)
                    multi_level(APSP, level + 1)

                check_save_and_restore(self, APSP, branch, data_path=data_path, path_exp="data_test/path_expected/",
                                       dist_exp="data_test/expected/", path_comp="data_test/path_computed/",
                                       dist_comp="data_test/computed/")

                os.rmdir("data_test/path_expected/" + str(level))
                os.rmdir("data_test/dist_expected/" + str(level))
                os.rmdir("data_test/path_computed/" + str(level))
                os.rmdir("data_test/dist_computed/" + str(level))

        multi_level(APSP, 0)



def generate_random_edge(APSP):
    is_new_name1 = rdm.randint(0, 3)
    if is_new_name1 == 0:
        name1 = str(rdm.random())               # on pourrait avoir 2 fois le meme nom mais c'est improbable + pas grave
        time1 = rdm.randint(0, APSP.max_time - 1)
    else:
        name1 = rdm.sample(APSP.idx_to_name, 1).pop()
        is_new_time = rdm.randint(0, 3)
        if is_new_time == 0:
            time1 = rdm.randint(0, APSP.max_time - 1)
        else:
            time1 = rdm.sample(APSP.used_time[APSP.name_to_idx[name1]], 1).pop()

    is_new_name2 = rdm.randint(0, 3)
    if is_new_name2 == 0:
        name2 = str(rdm.random())
        time2 = rdm.randint(time1, APSP.max_time - 1)
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
    # print("add edge {} time {} to {} time {}".format(name1, time1, name2, time2))
    APSP.add_edge(name1, time1, name2, time2)


def check_save_and_restore(TestCase, APSP, branch, data_path, path_exp, dist_exp, path_comp, dist_comp):
    Expect = Dynamic_APSP(data_path)
    Expect.hard_save_is_reachable(path_exp)
    Expect.hard_save_distance(dist_exp)

    for b_modif in branch:
        APSP.save()

        # check that save don't modify results
        APSP.hard_save_is_reachable(path_comp)
        APSP.hard_save_distance(dist_comp)
        TestCase.assertTrue(compare_results(path_exp, path_comp))  # compare path
        TestCase.assertTrue(compare_results(dist_exp, dist_comp))  # compare distance

        b_modif(APSP)
        APSP.restore()

        # check that restore go back to the previus results
        APSP.hard_save_is_reachable(path_comp)
        APSP.hard_save_distance(dist_comp)
        TestCase.assertTrue(compare_results(path_exp, path_comp))  # compare path
        TestCase.assertTrue(compare_results(dist_exp, dist_comp))  # compare distance



# todo test distance.get_changes
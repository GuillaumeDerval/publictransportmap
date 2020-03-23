from unittest import TestCase

from Test.Test_dynamic_inc_APSP.my_utils import *


class TestDynamicAPSP(TestCase):
    def setUp(self):
        super().setUp()
        for file_name in os.listdir("data_test/dist_computed/"):
            os.remove("data_test/dist_computed/" + file_name)
        for file_name in os.listdir("data_test/dist_expected/"):
            os.remove("data_test/dist_expected/" + file_name)
        for file_name in os.listdir("data_test/path_computed/"):
            os.remove("data_test/path_computed/" + file_name)
        for file_name in os.listdir("data_test/path_expected/"):
            os.remove("data_test/path_expected/" + file_name)

        my_map.belgium_map = None

    def test_modify_graph(self):
        APSP = Dynamic_APSP("data_test/mini.json")

        APSP._Dynamic_APSP__add_isolated_vertex("d", 30, (0, 0))
        APSP._Dynamic_APSP__add_isolated_vertex("c", 90, None)
        APSP.add_edge("d", 30, "c", 90)
        APSP.add_edge("b", 10, "c", 90)
        APSP.add_edge("e", 0, "b", 10, (0, 0))
        APSP.add_edge("b", 10, "d", 30)
        # todo add vertex

        APSP.hard_save_graph("data_test/mini_updated_save.json")
        file1 = open("data_test/mini_updated.json")
        file2 = open("data_test/mini_updated_save.json")
        self.assertEqual(json.loads(file1.read()), json.loads(file2.read()))
        file1.close()
        file2.close()

    def test_add_isolated_vertex_mini_1(self):
        # add existing vertex
        path_comp, dist_comp = check_if_correct_modification(
            lambda APSP: APSP._Dynamic_APSP__add_isolated_vertex("b", 70, None))
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_isolated_vertex_mini_2(self):
        # add vertex with existing label
        def my_change(APSP):
            APSP._Dynamic_APSP__add_isolated_vertex("a", 90, None)
            APSP._Dynamic_APSP__add_isolated_vertex("c", 10, None)

        path_comp, dist_comp = check_if_correct_modification(my_change)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_isolated_vertex_mini_3(self):
        # add vertex with new label
        def my_change(APSP):
            APSP._Dynamic_APSP__add_isolated_vertex("d", 15, (0, 0))
            APSP._Dynamic_APSP__add_isolated_vertex("k", 10, (0, 0))

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
                if choice == 0:
                    # add existing
                    idx = rdm.randint(0, len(APSP.name_to_idx) - 1)
                    name = APSP.idx_to_name[idx]
                    if len(APSP.used_time[idx]) != 0:
                        time = APSP.used_time[idx][rdm.randint(0, len(APSP.used_time[idx]) - 1)]
                        APSP._Dynamic_APSP__add_isolated_vertex(name, time, None)
                        APSP._Dynamic_APSP__add_isolated_vertex(name, time, None)
                elif choice == 1:
                    # add vertex with existing label
                    idx = rdm.randint(0, len(APSP.name_to_idx) - 1)
                    name = APSP.idx_to_name[idx]
                    time = rdm.randint(0, APSP.max_time - 1)
                    APSP._Dynamic_APSP__add_isolated_vertex(name, time, None)
                elif choice == 2:
                    # add vertex with new label
                    name = str(i)
                    i += 1
                    time = rdm.randint(0, APSP.max_time - 1)
                    APSP._Dynamic_APSP__add_isolated_vertex(name, time, (rdm.randint(0,50000)/10, rdm.randint(0,50000)/10))

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
                        APSP._Dynamic_APSP__add_isolated_vertex(name, time, None)
                elif choice == 1:
                    # add vertex with existing label
                    idx = rdm.randint(0, len(APSP.name_to_idx) - 1)
                    name = APSP.idx_to_name[idx]
                    time = rdm.randint(0, APSP.max_time - 1)
                    APSP._Dynamic_APSP__add_isolated_vertex(name, time,  None)
                elif choice == 2:
                    # add vertex with new label
                    name = str(i)
                    i += 1
                    time = rdm.randint(0, APSP.max_time - 1)
                    APSP._Dynamic_APSP__add_isolated_vertex(name, time, (rdm.randint(0,50000)/10, rdm.randint(0,50000)/10))

        path_comp, dist_comp = check_if_correct_modification(my_change, "data_test/medium.json")
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)
        self.assertTrue(dist_comp)

    # ######################################### TEST ADDING EDGE ####################################################
    def test_add_edge_mini_0(self):
        # add existing edge
        def my_change(APSP):
            APSP.add_edge("a", 50, "b", 70)
            APSP.add_edge("b", 20, "a", 50)

        compa = check_if_correct_modification(my_change)
        self.assertTrue(compa)

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
            APSP.add_edge("d", 0, "a", 0, (0, 0))
            APSP.add_edge("c", 40, "a", 50)
            APSP.add_edge("a", 0, "c", 40)

        path_comp, dist_comp = check_if_correct_modification(my_change)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_edge_mini_3(self):
        # add edge (u,v) where deg_out(v) = 0
        def my_change(APSP):
            APSP.add_edge("c", 70, "d", 90, (0, 0), (0, 0))
            APSP.add_edge("a", 50, "d", 90)
            APSP.add_edge("d", 90, "a", 95)

        path_comp, dist_comp = check_if_correct_modification(my_change)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_edge_mini_4(self):
        # add edge (u,v)
        def my_change(APSP):
            APSP.add_edge("d", 0, "a", 0, (0, 0))
            APSP.add_edge("a", 0, "c", 40)
            APSP.add_edge("c", 40, "a", 50)

        path_comp, dist_comp = check_if_correct_modification(my_change)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_edge_rdm_mini(self):
        def my_change(APSP: Dynamic_APSP):
            rdm.seed(76548)
            for _ in range(100):
                generate_random_edge(APSP)

        path_comp, dist_comp = check_if_correct_modification(my_change)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_edge_rdm_medium(self):
        def my_change(APSP: Dynamic_APSP):
            rdm.seed(654321)
            i = 10
            for _ in range(50):
                generate_random_edge(APSP)

        path_comp, dist_comp = check_if_correct_modification(my_change, "data_test/medium.json")
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    # ######################################### TEST ADDING VERTEX ####################################################

    def test_add_vertex_mini(self):
        mmap = my_map.get_map(path_shape="./../Test_metric/data/smallmap.geojson",
                              path_pop="./../Test_metric/data/popsector.csv",
                              stop_list_path="data_test/mini_stop_pos.json")

        def my_change(APSP: Dynamic_APSP):
            rdm.seed(76548)
            for _ in range(100):
                generate_random_vertex(APSP,mmap, 0, 7000, 0, 3000)

        path_comp, dist_comp = check_if_correct_modification(my_change, mmap=mmap)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_vertex_medium(self):
        #todo
        pass #self.fail()
    # ######################################### TEST ALL ADD ####################################################

    def test_add_mini(self):
        mmap = my_map.get_map(path_shape="./../Test_metric/data/smallmap.geojson",
                              path_pop="./../Test_metric/data/popsector.csv",
                              stop_list_path="data_test/mini_stop_pos.json")

        def my_change(APSP: Dynamic_APSP):
            rdm.seed(76548)
            for _ in range(100):
                generate_random_add(APSP, mmap, 0, 7000, 0, 3000)

        path_comp, dist_comp = check_if_correct_modification(my_change, mmap=mmap)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_medium(self):
        # todo
        pass #self.fail()








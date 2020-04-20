from unittest import TestCase

from Test.Test_dynamic_inc_APSP.my_utils import *
from Program.Data_manager.main import DataManager


class TestDynamicAPSP(TestCase):
    def setUp(self):
        super().setUp()

        self.param_mini = DataManager.load_data("./../Data_test", "APSP_mini", "train_only")  # without walk
        self.param_mini_exp = DataManager.load_data("./../Data_test", "APSP_mini_exp", "train_only")  # without walk
        self.param_medium = DataManager.load_data("./../Data_test", "APSP_medium", "train_bus")
        self.param_medium_exp = DataManager.load_data("./../Data_test", "APSP_medium_exp", "train_bus")

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
        APSP = Dynamic_APSP(param=self.param_mini)

        APSP.add_vertex("d", 30, (3000.0, 3000.0))  # isolated vertex
        APSP.add_vertex("c", 90, None)    # isolated vertex
        APSP.add_edge("d", 30, "c", 90)
        APSP.add_edge("b", 10, "c", 90)
        APSP.add_edge("e", 0, "b", 10, (6000.0, 5000.0))
        APSP.add_edge("b", 10, "d", 30)
        APSP.add_vertex("f", 50, (0.0, 0.0), z_stop_in=[("a", 15), ("d", 30)], z_stop_out=[("d", 80)])

        APSP.hard_save_graph("data_test/mini_updated_save.json")
        file1 = open("data_test/mini_updated.json")
        file2 = open("data_test/mini_updated_save.json")
        self.assertEqual(json.loads(file1.read()), json.loads(file2.read()))
        file1.close()
        file2.close()
        os.remove("./data_test/mini_updated_save.json")

    def test_add_isolated_vertex_mini_1(self):
        # add existing vertex

        def my_change(APSP,transp_dico):
            APSP.add_vertex("b", 70, None)
            transport_add_vertex(transp_dico,"b", 70, None)

        graph_comp, path_comp, dist_comp = check_if_correct_modification(my_change, self.param_mini,
                                                                         self.param_mini_exp)
        self.assertTrue(graph_comp)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_isolated_vertex_mini_2(self):
        # add vertex with existing label
        def my_change(APSP, transp_dico):
            APSP.add_vertex("a", 90, None)
            transport_add_vertex(transp_dico, "a", 90, None)
            APSP.add_vertex("c", 10, None)
            transport_add_vertex(transp_dico, "c", 10, None)

        _, path_comp, dist_comp = check_if_correct_modification(my_change, self.param_mini, self.param_mini_exp)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_isolated_vertex_mini_3(self):
        # add vertex with new label
        def my_change(APSP, transp_dico):
            APSP.add_vertex("d", 15, (0, 0))
            transport_add_vertex(transp_dico, "d", 15, (0, 0))
            APSP.add_vertex("k", 10, (1000, 0))
            transport_add_vertex(transp_dico, "k", 10, (1000, 0))

        _, path_comp, dist_comp = check_if_correct_modification(my_change, self.param_mini,self.param_mini_exp)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_isolated_vertex_rdm_mini(self):
        # big the for added vertex
        def my_change(APSP, transp_dico):
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
                        APSP.add_vertex(name, time, None)
                        transport_add_vertex(transp_dico,name,time,None)

                elif choice == 1:
                    # add vertex with existing label
                    idx = rdm.randint(0, len(APSP.name_to_idx) - 1)
                    name = APSP.idx_to_name[idx]
                    time = rdm.randint(0, APSP.max_time - 1)
                    APSP.add_vertex(name, time, None)
                    transport_add_vertex(transp_dico, name, time, None)
                elif choice == 2:
                    # add vertex with new label
                    name = str(i)
                    i += 1
                    time = rdm.randint(0, APSP.max_time - 1)
                    APSP.add_vertex(name, time, (rdm.randint(0,50000)/10, rdm.randint(0,50000)/10))
                    transport_add_vertex(transp_dico,name, time, (rdm.randint(0,50000)/10, rdm.randint(0,50000)/10))

        _, path_comp, dist_comp = check_if_correct_modification(my_change, self.param_mini, self.param_mini_exp)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_isolated_vertex_rdm_medium(self):
        # big the for added vertex
        def my_change(APSP: Dynamic_APSP, transp_dico):
            rdm.seed(4243)
            i = 10
            for _ in range(20):
                choice = rdm.randint(0, 2)
                idx = rdm.randint(0, len(APSP.name_to_idx) - 1)
                if choice == 0:
                    # add existing
                    idx = rdm.randint(0, len(APSP.name_to_idx) - 1)
                    name = APSP.idx_to_name[idx]
                    if len(APSP.used_time[idx]) != 0 :
                        time = APSP.used_time[idx][rdm.randint(0, len(APSP.used_time[idx]) - 1)]
                        APSP.add_vertex(name, time, None)
                        transport_add_vertex(transp_dico, name, time, None)
                elif choice == 1:
                    # add vertex with existing label
                    idx = rdm.randint(0, len(APSP.name_to_idx) - 1)
                    name = APSP.idx_to_name[idx]
                    time = rdm.randint(0, APSP.max_time - 1)
                    APSP.add_vertex(name, time, None)
                    transport_add_vertex(transp_dico, name, time, None)
                elif choice == 2:
                    # add vertex with new label
                    name = str(i)
                    i += 1
                    time = rdm.randint(0, APSP.max_time - 1)
                    APSP.add_vertex(name, time, rdm_point_shape(APSP.param))
                    transport_add_vertex(transp_dico, name, time,
                                         rdm_point_shape(APSP.param))

        graph_comp, path_comp, dist_comp = check_if_correct_modification(my_change, param=self.param_medium,
                                                                         param_expect=self.param_medium_exp)
        self.assertTrue(dist_comp)

    # ######################################### TEST ADDING EDGE ####################################################
    def test_add_edge_mini_0(self):
        # add existing edge
        def my_change(APSP, transp_dico):
            APSP.add_edge("a", 50, "b", 70)
            APSP.add_edge("b", 20, "a", 50)
            transport_add_edge(transp_dico,"a", 50, "b", 70)
            transport_add_edge(transp_dico, "b", 20, "a", 50)

        graph_comp, path_comp, dist_comp = check_if_correct_modification(my_change, self.param_mini,
                                                                         self.param_mini_exp)
        self.assertTrue(graph_comp)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_edge_mini_1(self):
        # add edge with no impact
        def my_change(APSP, transp_dico):
            APSP.add_edge("b", 80, "c", 90)
            APSP.add_edge("a", 70, "a", 90)
            transport_add_edge(transp_dico, "b", 80, "c", 90)
            transport_add_edge(transp_dico, "a", 70, "a", 90)

        graph_comp, path_comp, dist_comp = check_if_correct_modification(my_change, self.param_mini,
                                                                         self.param_mini_exp)
        self.assertTrue(graph_comp)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_edge_mini_2(self):
        # add edge (u,v) where deg_in(u) = 0
        def my_change(APSP, transp_dico):
            APSP.add_edge("d", 0, "a", 0, (0, 0))
            APSP.add_edge("c", 40, "a", 50)
            APSP.add_edge("a", 0, "c", 40)
            transport_add_edge(transp_dico, "d", 0, "a", 0, (0, 0))
            transport_add_edge(transp_dico, "c", 40, "a", 50)
            transport_add_edge(transp_dico, "a", 0, "c", 40)

        graph_comp, path_comp, dist_comp = check_if_correct_modification(my_change, self.param_mini,
                                                                         self.param_mini_exp)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_edge_mini_3(self):
        # add edge (u,v) where deg_out(v) = 0
        def my_change(APSP, transp_dico):
            APSP.add_edge("c", 70, "d", 90, (0, 0), (50000, 0))
            APSP.add_edge("a", 50, "d", 90)
            APSP.add_edge("d", 90, "a", 95)
            transport_add_edge(transp_dico, "c", 70, "d", 90, (0, 0), (50000, 0))
            transport_add_edge(transp_dico, "a", 50, "d", 90)
            transport_add_edge(transp_dico, "d", 90, "a", 95)

        graph_comp, path_comp, dist_comp = check_if_correct_modification(my_change, self.param_mini,
                                                                         self.param_mini_exp)
        self.assertTrue(graph_comp)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_edge_mini_4(self):
        # add edge (u,v)
        def my_change(APSP, transp_dico):
            APSP.add_edge("d", 0, "a", 0, (0, 0))
            APSP.add_edge("a", 0, "c", 40)
            APSP.add_edge("c", 40, "a", 50)
            transport_add_edge(transp_dico, "d", 0, "a", 0, (0, 0))
            transport_add_edge(transp_dico, "a", 0, "c", 40)
            transport_add_edge(transp_dico, "c", 40, "a", 50)

        graph_comp, path_comp, dist_comp = check_if_correct_modification(my_change, self.param_mini,
                                                                         self.param_mini_exp)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_edge_rdm_mini(self):
        def my_change(APSP: Dynamic_APSP, transp_dico):
            rdm.seed(543)
            for _ in range(100):
                generate_random_edge(APSP, transp_dico)

        graph_comp, path_comp, dist_comp = check_if_correct_modification(my_change, self.param_mini,
                                                                         self.param_mini_exp)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_edge_rdm_medium(self):
        def my_change(APSP: Dynamic_APSP, transp_dico):
            rdm.seed(6543210)
            for i in range(50):
                generate_random_edge(APSP, transp_dico)

        graph_comp, path_comp, dist_comp = check_if_correct_modification(my_change, self.param_medium,
                                                                         self.param_medium_exp)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    # ######################################### TEST ADDING VERTEX ####################################################

    def test_add_vertex_mini(self):
        def my_change(APSP: Dynamic_APSP, transp_dico):
            rdm.seed(76548)
            for i in range(100):
                generate_random_vertex(APSP, transp_dico)

        _, path_comp, dist_comp = check_if_correct_modification(my_change, self.param_mini, self.param_mini_exp)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_vertex_medium(self):
        def my_change(APSP: Dynamic_APSP, transp_dico):
            rdm.seed(7168)
            for _ in range(50):
                generate_random_vertex(APSP, transp_dico)

        _, path_comp, dist_comp = check_if_correct_modification(my_change, self.param_medium, self.param_medium_exp)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)
    # ######################################### TEST ALL ADD ####################################################

    def test_add_mini(self):
        def my_change(APSP: Dynamic_APSP, transp_dico):
            rdm.seed(7654)
            for _ in range(200):
                generate_random_add(APSP, transp_dico)

        _, path_comp, dist_comp = check_if_correct_modification(my_change, self.param_mini, self.param_mini_exp)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)

    def test_add_medium(self):
        def my_change(APSP: Dynamic_APSP, transp_dico):
            rdm.seed(765)
            for _ in range(50):
                generate_random_add(APSP, transp_dico)

        _, path_comp, dist_comp = check_if_correct_modification(my_change, self.param_medium, self.param_medium_exp)
        self.assertTrue(path_comp)
        self.assertTrue(dist_comp)








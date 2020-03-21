from unittest import TestCase
import json
from Program.path import PATH

PATH.MINIMAL_TRAVEL_TIME_TC = "data/out/"
PATH.GRAPH_TC = "data/out.json"

import Program.metric.map as map
import Program.metric.monte_carlo_dynamic as mc
import numpy as np


class DistanceOracle:
    def __init__(self, distance_path, idx_to_name, distance_path_before = None, idx_to_name_before = None):
        if distance_path_before is None:
            distance_path_before = distance_path
            idx_to_name_before = idx_to_name

        self.path = distance_path
        self.path_before = distance_path_before
        self.name_to_idx = {x: i for i, x in enumerate(idx_to_name)}
        self.name_to_idx_before = {x: i for i, x in enumerate(idx_to_name_before)}

    def dist(self, s_name: str, d_name: str) -> float:
        path = self.path + "{0}.npy".format(s_name)
        return np.load(path)[self.name_to_idx[d_name]]

    def dist_from(self, s_name):
        path = self.path + "{0}.npy".format(s_name)
        return np.load(path), self.name_to_idx

    def dist_before_change(self, s_name: str, d_name: str):
        if s_name not in self.name_to_idx_before or d_name not in self.name_to_idx_before:
            return -1
        path = self.path_before + "{0}.npy".format(s_name)
        return np.load(path)[self.name_to_idx_before[d_name]]


class TestMonte_carlo(TestCase):


    def setUp(self):
        #PATH.MINIMAL_TRAVEL_TIME_TC = "data/out/"
        #PATH.GRAPH = "data/out.json"

        mc.SPEED = 33.334  # m/min  #2km/h
        mc.MAX_WALKING_TIME = 60

        with open("data/graph.json") as file:
            graph = json.loads(file.read())
            self.idx_to_name = graph["idx_to_name"]

        self.travel_path = "data/travel_user.json"
        self.distance_oracle = DistanceOracle("data/out/", self.idx_to_name)
        self.reducing_factor = 1
        self.mapmap = map.my_map.get_map("data/smallmap.geojson", "data/popsector.csv")
        self.stop_list_path = "data/stop_pos.json"
        self.travel_model = mc.TravellersModelisation(travel_path=self.travel_path,
                                                      distance_oracle=self.distance_oracle,
                                                      reducing_factor=self.reducing_factor,
                                                      mapmap=self.mapmap,
                                                      stop_list_path=self.stop_list_path)

    # ######################################### TEST INITIALISATION ###################################################
    def test_virtual_travellers(self):
        travell_loc = self.travel_model.traveller_locations

        self.assertIn(("A","B"), travell_loc.keys())
        self.assertIn(("C", "A"), travell_loc.keys())
        self.assertIn(("B", "B"), travell_loc.keys())
        self.assertIn(("D", "C"), travell_loc.keys())
        self.assertIn(("A", "D"), travell_loc.keys())
        self.assertEqual(len(travell_loc[("A","B")]),4)
        self.assertEqual(len(travell_loc[("C", "A")]), 3)
        self.assertEqual(len(travell_loc[("B", "B")]), 10)
        self.assertEqual(len(travell_loc[("D", "C")]), 1)
        self.assertEqual(len(travell_loc[("A", "D")]), 5)


    def test_get_reachable_stop_munty(self):
        stops = [elem[0] for elem in self.travel_model.reachable_stop_from_munty["A"]]
        for stop in ["S0", "S4"]:
            self.assertIn(stop, stops)
        for stop in ["S1", "S3","S5"]:
            self.assertNotIn(stop, stops)

        stops = [elem[0] for elem in self.travel_model.reachable_stop_from_munty["C"]]
        for stop in ["S0","S1","S3", "S4"]:
            self.assertIn(stop, stops)
        for stop in [ "S5"]:
            self.assertNotIn(stop, stops)

    def test_get_reachable_stop_pt(self):
        pt = (0.0, 0.0)
        stops = [elem[0] for elem in self.travel_model.get_reachable_stop_pt(pt,"A")]
        for stop in ["S0","S1", "S3","S4", "S5"]:
            self.assertNotIn(stop, stops)

        pt = (1000.0, 2000.0)
        stops = [elem[0] for elem in self.travel_model.get_reachable_stop_pt(pt, "A")]
        for stop in ["S0"]:
            self.assertIn(stop, stops)
        for stop in ["S1", "S3", "S4", "S5"]:
            self.assertNotIn(stop, stops)

        pt = (2000.0, 4000.0)
        stops = [elem[0] for elem in self.travel_model.get_reachable_stop_pt(pt, "C")]
        for stop in ["S0","S3","S4"]:
            self.assertIn(stop, stops, "fail munty C")
        for stop in ["S1", "S5"]:
            self.assertNotIn(stop, stops)

    def test_get_min_max_time(self):
        self.assertEqual(0,self.travel_model.get_min_time("A","B"))
        self.assertEqual(60, self.travel_model.get_max_time("A", "B"))

        self.assertEqual(15, self.travel_model.get_min_time("A", "D"))
        self.assertEqual(25, self.travel_model.get_max_time("A", "D"))

        self.assertEqual(40, self.travel_model.get_max_time("D", "C"))
        self.assertEqual(15, self.travel_model.get_min_time("D", "C"))

    def test_optimal_travel_time1(self):
        #opti path with only walk
        rsd = (3000.0,4000.0)
        work = (3000.0,1000.0)
        time_exp = 3000/mc.SPEED
        time = self.travel_model.optimal_travel_time(rsd, "C", work, "A")[1][0]  # should take path rsd->work
        self.assertAlmostEqual(time_exp, time, 0.01)

    def test_optimal_travel_time2(self):
        #opti path with only walk
        rsd = (2000.0,1000.0)
        work = (3000.0,4000.0)
        time_exp = 2000/mc.SPEED + 10
        time = self.travel_model.optimal_travel_time(rsd, "A", work, "C")[1][0]   # should take path rsd->S0->S4->work
        self.assertAlmostEqual(time_exp, time, 0.01)

    def test_optimal_travel_time3(self):
        #opti path with only walk
        rsd = (6000.0,5000.0)
        work = (3000.0,6100.0)
        time_exp = 1005/mc.SPEED + 35
        time = self.travel_model.optimal_travel_time(rsd, "D", work, "C")[1][0]    # should take path S5->S3->work
        self.assertAlmostEqual(time_exp, time, 1)

    def test_monte_carlo(self):
        #todo
        self.fail()

    def test_small_inc_dynamic(self):
        for seed in range(300, 330):
            updated_model = mc.TravellersModelisation(travel_path=self.travel_path,
                                                       distance_oracle=DistanceOracle("data/out2/", self.idx_to_name+ ["S6"],
                                                                                      "data/out/",
                                                                                      self.idx_to_name),
                                                       reducing_factor=self.reducing_factor,
                                                       mapmap=self.mapmap,
                                                       stop_list_path=self.stop_list_path, my_seed=seed)
            change = {"size": (6, 5),
                     "added_stop_name" : [("S6",(2500.0, 2500.0))],
                     "change_distance": {"S0": {"S2" : (20, -1)},
                                         "S1": {"S0": (5, 35),"S6": (30, -1)},
                                         "S4": {"S5": (5, 15)},
                                         "S6": {"S1": (30, -1),"S3": (35, -1)}}
                    }
            updated_model.update(change)

            expected_model = mc.TravellersModelisation(travel_path=self.travel_path,
                                                          distance_oracle=DistanceOracle("data/out2/", self.idx_to_name + ["S6"]),
                                                          reducing_factor=self.reducing_factor,
                                                          mapmap=self.mapmap,
                                                          stop_list_path="data/stop_pos2.json", my_seed=seed)

            self.assertEqual(expected_model.reachable_stop_from_munty, updated_model.reachable_stop_from_munty)
            self.assertEqual(expected_model.reachable_munty_from_stop, updated_model.reachable_munty_from_stop)
            self.assertEqual(expected_model.traveller_locations,updated_model.traveller_locations)
            self.assertEqual(expected_model.all_results, updated_model.all_results)

    def test_big_inc_dynamic(self):
        seed = 1234
        #todo
        self.fail()



from unittest import TestCase
import json
import numpy as np
from Program.Data_manager.main import DataManager
import Program.General.map as map
import Program.metric.monte_carlo_dynamic as mc


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


class TestMonteCarlo(TestCase):

    def setUp(self):
        self.param = DataManager.load_data("./../Data_test", "small1", "train_only")
        self.param.PATH.MINIMAL_TRAVEL_TIME_TC = "./../Data_test/produced/minimal_distance/small1_mc"
        # Speed :33.334 m/min =  2km/h # Max_time : 60 min

        with open(self.param.PATH.GRAPH_TC) as file:
            graph = json.loads(file.read())
            self.idx_to_name = graph["idx_to_name"]

        self.distance_oracle = DistanceOracle("./../Data_test/produced/minimal_distance/small1_mc/", self.idx_to_name)
        self.reducing_factor = 1
        self.mapmap = map.my_map.get_map(self.param, path_pop="./../Data_test/intermediate/small1_train_only/popsector.csv")
        self.travel_model = mc.TravellersModelisation(param=self.param,
                                                      travel_path=self.param.PATH.TRAVEL,
                                                      distance_oracle=self.distance_oracle,
                                                      reducing_factor=self.reducing_factor,
                                                      mapmap=self.mapmap)
    def tearDown(self):
        map.my_map.belgium_map =  None

    # ######################################### TEST INITIALISATION ###################################################
    def test_virtual_travellers(self):
        travel_loc = self.travel_model.traveller_locations

        self.assertIn(("A","B"), travel_loc.keys())
        self.assertIn(("C", "A"), travel_loc.keys())
        self.assertIn(("B", "B"), travel_loc.keys())
        self.assertIn(("D", "C"), travel_loc.keys())
        self.assertIn(("A", "D"), travel_loc.keys())
        self.assertEqual(len(travel_loc[("A","B")]),4)
        self.assertEqual(len(travel_loc[("C", "A")]), 3)
        self.assertEqual(len(travel_loc[("B", "B")]), 10)
        self.assertEqual(len(travel_loc[("D", "C")]), 1)
        self.assertEqual(len(travel_loc[("A", "D")]), 5)

    def test_get_min_max_time(self):
        self.assertEqual(0, self.travel_model.get_min_time("A","B"))
        self.assertEqual(60, self.travel_model.get_max_time("A", "B"))

        self.assertEqual(15, self.travel_model.get_min_time("A", "D"))
        self.assertEqual(25, self.travel_model.get_max_time("A", "D"))

        self.assertEqual(40, self.travel_model.get_max_time("D", "C"))
        self.assertEqual(15, self.travel_model.get_min_time("D", "C"))

    def test_optimal_travel_time1(self):
        # opti path with only walk
        rsd = (3000.0,4000.0)
        work = (3000.0,1000.0)
        time_exp = 3000/self.param.WALKING_SPEED()
        time = self.travel_model.optimal_travel_time(rsd, "C", work, "A")[1][0]  # should take path rsd->work
        self.assertAlmostEqual(time_exp, time, 0.01)

    def test_optimal_travel_time2(self):
        #opti path with only walk
        rsd = (2000.0,1000.0)
        work = (3000.0,4000.0)
        time_exp = 2000/self.param.WALKING_SPEED() + 10
        time = self.travel_model.optimal_travel_time(rsd, "A", work, "C")[1][0]   # should take path rsd->S0->S4->work
        self.assertAlmostEqual(time_exp, time, 0.01)

    def test_optimal_travel_time3(self):
        #opti path with only walk
        rsd = (6000.0,5000.0)
        work = (3000.0,6100.0)
        time_exp = 1005/self.param.WALKING_SPEED() + 35
        time = self.travel_model.optimal_travel_time(rsd, "D", work, "C")[1][0]    # should take path S5->S3->work
        self.assertAlmostEqual(time_exp, time, 1)

    def test_monte_carlo(self):
        #todo
        pass # self.fail()

    def test_small_inc_dynamic(self):
        for seed in range(300, 315):
            updated_model = mc.TravellersModelisation(self.param,
                                                      travel_path=self.param.PATH.TRAVEL,
                                                      distance_oracle=DistanceOracle("./../Data_test/produced/minimal_distance/small2_mc/", self.idx_to_name+ ["S6"],
                                                                                      "./../Data_test/produced/minimal_distance/small1_mc/",
                                                                                      self.idx_to_name),
                                                      reducing_factor=self.reducing_factor,
                                                      mapmap=self.mapmap,
                                                      my_seed=seed)
            change = {"size": (6, 5),
                     "added_stop_name" : [("S6",(2500.0, 2500.0))],
                     "change_distance": {"S0": {"S2" : (20, -1)},
                                         "S1": {"S0": (5, 35), "S6": (30, -1)},
                                         "S4": {"S5": (5, 15)},
                                         "S6": {"S1": (30, -1), "S3": (35, -1)}}
                    }
            self.mapmap.add_stop("S6", (2500.0, 2500.0))
            updated_model.update(change)


            expected_model = mc.TravellersModelisation(self.param,
                                                       travel_path=self.param.PATH.TRAVEL,
                                                       distance_oracle=DistanceOracle("./../Data_test/produced/minimal_distance/small2_mc/", self.idx_to_name + ["S6"]),
                                                       reducing_factor=self.reducing_factor,
                                                       mapmap=self.mapmap,
                                                       my_seed=seed)

            self.assertEqual(expected_model.map.reachable_stop_from_munty, updated_model.map.reachable_stop_from_munty)
            self.assertEqual(expected_model.map.reachable_munty_from_stop, updated_model.map.reachable_munty_from_stop)
            self.assertEqual(expected_model.traveller_locations, updated_model.traveller_locations)
            self.assertEqual(expected_model.all_results, updated_model.all_results)

    def test_big_inc_dynamic(self):
        seed = 1234
        #todo
        pass #self.fail()



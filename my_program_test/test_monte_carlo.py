from unittest import TestCase
import json
import my_program.path as PATH

PATH.TRAVEL_TIME = "data/out/"
PATH.OUT = "data/out.json"

import my_program.map as map
import my_program.monte_carlo_opti as mc


class TestMonte_carlo(TestCase):

    def setUp(self):
        PATH.TRAVEL_TIME = "data/out/"
        PATH.OUT = "data/out.json"

        mc.map = map.my_map.get_map("data/smallmap.geojson", "data/popsector.csv")
        with open("data/stop_pos.json", "r") as file:
            mc.stop_munty.stop_list = json.load(file)


        mc.SPEED = 33.334  # m/min  #2km/h
        mc.MAX_WALKING_TIME = 60



    def test_get_n_rdm_point(self):
        iter = 1000
        rdm = mc.get_n_rdm_point(iter, "C")
        meanx, meany = 0, 0
        for pt in rdm:
            meanx += pt[0]
            meany += pt[1]
        meanx, meany = meanx/iter, meany/iter
        self.assertAlmostEqual(2000., meanx, delta=100)
        self.assertAlmostEqual(4625., meany, delta=100)

    def test_get_reachable_stop_munty(self):
        stops = [elem[0] for elem in mc.stop_munty.get_reachable_stop_munty("A")]
        for stop in ["S0", "S4"]:
            self.assertIn(stop, stops)
        for stop in ["S1","S2", "S3","S5"]:
            self.assertNotIn(stop, stops)

        stops = [elem[0] for elem in mc.stop_munty.get_reachable_stop_munty("C")]
        for stop in ["S0","S1","S3", "S4"]:
            self.assertIn(stop, stops)
        for stop in ["S2" ,"S5"]:
            self.assertNotIn(stop, stops)

    def test_get_reachable_stop_pt(self):
        pt = (0.0, 0.0)
        stops = [elem[0] for elem in mc.stop_munty.get_reachable_stop_pt(pt,"A")]
        for stop in ["S0","S1", "S2", "S3","S4", "S5"]:
            self.assertNotIn(stop, stops)

        pt = (1000.0, 2000.0)
        stops = [elem[0] for elem in mc.stop_munty.get_reachable_stop_pt(pt, "A")]
        for stop in ["S0"]:
            self.assertIn(stop, stops)
        for stop in ["S1", "S2", "S3", "S4", "S5"]:
            self.assertNotIn(stop, stops)

        pt = (2000.0, 4000.0)
        stops = [elem[0] for elem in mc.stop_munty.get_reachable_stop_pt(pt, "C")]
        for stop in ["S0","S3","S4"]:
            self.assertIn(stop, stops, "fail munty C")
        for stop in ["S1", "S2", "S5"]:
            self.assertNotIn(stop, stops)

    def test_get_min_max_time(self):
        self.assertEqual(0,mc.stop_munty.get_min_time("A","B"))
        self.assertEqual(60, mc.stop_munty.get_max_time("A", "B"))

        self.assertEqual(15, mc.stop_munty.get_min_time("A", "D"))
        self.assertEqual(25, mc.stop_munty.get_max_time("A", "D"))

        self.assertEqual(40, mc.stop_munty.get_max_time("D", "C"))
        self.assertEqual(15, mc.stop_munty.get_min_time("D", "C"))

    def test_optimal_travel_time(self):
        self.fail()

    def test_monte_carlo_travel(self):
        self.fail()

    def test_monte_carlo(self):
        self.fail()

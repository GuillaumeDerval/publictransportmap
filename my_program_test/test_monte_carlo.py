from unittest import TestCase
import json
import my_program.map as map
import my_program.monte_carlo_opti as mc

class TestMonte_carlo(TestCase):

    def setUp(self):
        mc.map = map.my_map.get_map("data/smallmap.geojson", "data/popsector.csv")
        mc.stop_munty.stop_list = json.load(open("data/stop_pos.json", "r"))

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
        self.fail()

    def test_get_reachable_stop_pt(self):
        self.fail()

    def test_optimal_travel_time(self):
        self.fail()

    def test_monte_carlo_travel(self):
        self.fail()

    def test_monte_carlo(self):
        self.fail()

from unittest import TestCase
from shapely.geometry import shape

from Program.map import my_map
from Program.Data_manager.main import DataManager


class TestMy_map(TestCase):

    mapp = None

    def setUp(self):
        self.param = DataManager.load_data("./../Data_test","small1", "train_only")
        TestMy_map.mapp = my_map.get_map(self.param,  path_pop="./../Data_test/intermediate/small1_train_only/pop_sector.csv")

    def tearDown(self):
        my_map.belgium_map = None

    def test_get_map(self):
        self.assertIsNotNone(TestMy_map.mapp)

    def test_get_shape_sector(self):
        A1 = shape({'type': 'Polygon', 'coordinates':[[[1000., 1000.], [1000., 2000.],[2000., 2000.], [2000., 1000.],[1000., 1000.]]]})
        self.assertTrue(TestMy_map.mapp.get_shape_sector("A1").equals(A1))

    def test_get_shape_munty(self):
        A = shape({'type': 'Polygon', 'coordinates': [
            [[0., 0.], [0., 3000.], [3000., 3000.], [3000., 0.], [0., 0.]]]})
        self.assertTrue(TestMy_map.mapp.get_shape_refnis("A").equals(A))
        B = shape({'type': 'Polygon', 'coordinates':
           [[[3000., 0.],[3000., 2000.], [5000., 2000.],[5000., 0.], [3000., 0.]]]})
        self.assertTrue(TestMy_map.mapp.get_shape_refnis("B").equals(B))
        C = shape({'type': 'Polygon', 'coordinates':
            [[[1000., 3000.], [1000., 7000.], [3000., 7000.], [3000., 3000.], [1000., 3000.]]]})
        self.assertTrue(TestMy_map.mapp.get_shape_refnis("C").equals(C))

    def test_get_pop_sector(self):
        self.assertEqual(TestMy_map.mapp.get_pop_sector("A1"), 20)
        self.assertEqual(TestMy_map.mapp.get_pop_sector("A2"), 8)
        self.assertEqual(TestMy_map.mapp.get_pop_sector("B1"), 100)
        self.assertEqual(TestMy_map.mapp.get_pop_sector("C3"), 10)

    def test_get_pop_munty(self):
        self.assertEqual(TestMy_map.mapp.get_pop_refnis("A"), 28)
        self.assertEqual(TestMy_map.mapp.get_pop_refnis("B"), 100)
        self.assertEqual(TestMy_map.mapp.get_pop_refnis("C"), 80)

    def test_get_sector_ids(self):
        for id in ["C1","C2","C3"]:
            self.assertIn(id,TestMy_map.mapp.get_sector_ids("C"))
        self.assertIn("B1", TestMy_map.mapp.get_sector_ids("B"))

    def test_get_reachable_stop_munty(self):
        stops = [elem[0] for elem in TestMy_map.mapp.reachable_stop_from_munty["A"]]
        for stop in ["S0", "S4"]:
            self.assertIn(stop, stops)
        for stop in ["S1", "S3","S5"]:
            self.assertNotIn(stop, stops)

        stops = [elem[0] for elem in TestMy_map.mapp.reachable_stop_from_munty["C"]]
        for stop in ["S0","S1","S3", "S4"]:
            self.assertIn(stop, stops)
        for stop in ["S5"]:
            self.assertNotIn(stop, stops)

    def test_get_reachable_stop_pt(self):
        pt = (0.0, 0.0)
        stops = [elem[0] for elem in TestMy_map.mapp.get_reachable_stop_pt(pt, "A")]
        for stop in ["S0","S1", "S3","S4", "S5"]:
            self.assertNotIn(stop, stops)

        pt = (1000.0, 2000.0)
        stops = [elem[0] for elem in TestMy_map.mapp.get_reachable_stop_pt(pt, "A")]
        for stop in ["S0"]:
            self.assertIn(stop, stops)
        for stop in ["S1", "S3", "S4", "S5"]:
            self.assertNotIn(stop, stops)

        pt = (2000.0, 4000.0)
        stops = [elem[0] for elem in TestMy_map.mapp.get_reachable_stop_pt(pt, "C")]
        for stop in ["S0","S3","S4"]:
            self.assertIn(stop, stops, "fail munty C")
        for stop in ["S1", "S5"]:
            self.assertNotIn(stop, stops)

    # todo other tests
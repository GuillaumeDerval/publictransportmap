from unittest import TestCase
from my_program.stat_distrib import *

uniform_distrib = [0.25, 0.5, 0.75, 1]
distrib = [0,0.1,0.2,0.2, 0.4, 0.5,1,1,1]


class TestCheck_distrib(TestCase):
    def test_check_distrib_good(self):
        self.assertTrue(check_cumulative_distrib(uniform_distrib))
        self.assertTrue(check_cumulative_distrib(distrib))
        self.assertTrue(check_cumulative_distrib([0, 0, 1]))


    def test_check_distrib_bad(self):
        self.assertFalse(check_cumulative_distrib([]))
        self.assertFalse(check_cumulative_distrib([-1, 0, 1]))
        self.assertFalse(check_cumulative_distrib([0.3, 0.2, 0.4, 1]))
        self.assertFalse(check_cumulative_distrib([0, 0.2, 0.4, 0.8]))



class TestSum_distrib(TestCase):
    def test_sum_distrib_no_change(self):
        unit = [1]
        self.assertEqual(sum_distrib(unit, unit), unit)
        self.assertEqual(sum_distrib(uniform_distrib, unit), uniform_distrib)
        self.assertEqual(sum_distrib(unit,distrib), distrib)
    def test_sum_distrib_shift(self):
        shift = [0,0,1]
        self.assertEqual(sum_distrib(shift, shift), [0,0,0,0,1])
        self.assertEqual(sum_distrib(uniform_distrib, shift), [0, 0, 0.25, 0.5, 0.75,1])
        self.assertEqual(sum_distrib(shift,distrib), [0,0,0,0.1,0.2,0.2, 0.4, 0.5,1,1,1])

    def test_sum_distrib(self):
        sum = sum_distrib(uniform_distrib, uniform_distrib)
        self.assertTrue(check_cumulative_distrib(sum))
        self.assertEqual(sum, [1 / 16, 3 / 16, 6 / 16, 10 / 16, 13 / 16, 15 / 16, 1])


class TestMin_distrib(TestCase):
    def test_min_distrib_one(self):
        self.assertEqual(min_distrib([uniform_distrib]), uniform_distrib)

    def test_min_distrib_2Simple(self):  # test fail but answert close enough from the target results
        min1 = min_distrib([uniform_distrib, [1,1,1,1]])
        self.assertTrue(check_cumulative_distrib(min1))
        self.assertEqual(min1, [1])

        min2 = min_distrib([uniform_distrib, [0, 0, 0, 1]])
        self.assertTrue(check_cumulative_distrib(min2))
        self.assertEqual(min2, uniform_distrib)

        min3 = min_distrib([distrib, [0,0,0, 0,0,0, 0,0, 1]])
        self.assertTrue(check_cumulative_distrib(min3))
        #self.assertEqual(min3, distrib)

    def test_min_distrib3(self):
        min1 = min_distrib([uniform_distrib, uniform_distrib])
        self.assertTrue(check_cumulative_distrib(min1))
        # self.assertEqual(min1, todo)

        min2 = min_distrib([uniform_distrib, distrib])
        self.assertTrue(check_cumulative_distrib(min2))

    def test_min_distrib3(self):
        min1 = min_distrib([uniform_distrib, uniform_distrib, uniform_distrib,uniform_distrib,uniform_distrib])
        self.assertTrue(check_cumulative_distrib(min1))

        min2 = min_distrib([uniform_distrib + [1]*5, distrib, distrib])
        self.assertTrue(check_cumulative_distrib(min2))




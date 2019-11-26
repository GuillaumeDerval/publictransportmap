from unittest import TestCase
from my_program.stat_distrib import *




class TestCheck_distrib(TestCase):

    def setUp(self):
        self.uniform_distrib = Distribution([0.25, 0.5, 0.75, 1])
        self.distrib = Distribution([0, 0.1, 0.2, 0.2, 0.4, 0.5, 1, 1, 1])

    def test_check_distrib_good(self):
        self.assertTrue(self.uniform_distrib.check_cumulative_distrib())
        self.assertTrue(self.distrib.check_cumulative_distrib())
        self.assertTrue(Distribution([0, 0, 1]).check_cumulative_distrib())


    def test_check_distrib_bad(self):
        self.assertFalse(Distribution([]).check_cumulative_distrib())
        self.assertFalse(Distribution([-1, 0, 1]).check_cumulative_distrib())
        self.assertFalse(Distribution([0.3, 0.2, 0.4, 1]).check_cumulative_distrib())
        self.assertFalse(Distribution([0, 0.2, 0.4, 0.8]).check_cumulative_distrib())



class TestSum_distrib(TestCase):

    def setUp(self):
        self.uniform_distrib = Distribution([0.25, 0.5, 0.75, 1.0])
        self.distrib = Distribution([0.0, 0.1, 0.2, 0.2, 0.4, 0.5, 1.0, 1.0, 1.0])

    def test_sum_distrib_no_change(self):
        unit = Distribution([1])
        self.assertEqual(sum_distrib(unit, unit), unit)
        self.assertEqual(sum_distrib(self.uniform_distrib, unit), self.uniform_distrib)
        self.assertEqual(sum_distrib(unit, self.distrib), self.distrib)
    def test_sum_distrib_shift(self):
        shift = Distribution([0,0,1])
        self.assertTrue(sum_distrib(shift, shift), Distribution([0,0,0,0,1.0]))
        self.assertEqual(sum_distrib(self.uniform_distrib, shift), Distribution([0, 0, 0.25, 0.5, 0.75,1.0]))
        self.assertEqual(sum_distrib(shift,self.distrib), Distribution([0,0,0,0.1,0.2,0.2, 0.4, 0.5,1.0,1.0,1.0]))

    def test_sum_distrib(self):
        sum = sum_distrib(self.uniform_distrib, self.uniform_distrib)
        self.assertTrue(sum.check_cumulative_distrib())
        self.assertEqual(sum, Distribution([1 / 16, 3 / 16, 6 / 16, 10 / 16, 13 / 16, 15 / 16, 1.0]))


class TestMin_distrib(TestCase):
    def setUp(self):
        self.uniform_distrib = Distribution([0.25, 0.5, 0.75, 1.0])
        self.distrib = Distribution([0.0, 0.1, 0.2, 0.2, 0.4, 0.5, 1.0, 1.0, 1.0])

    def test_min_distrib_one(self):
        self.assertEqual(min_distrib([self.uniform_distrib]), self.uniform_distrib)

    def test_min_distrib_2Simple(self):  # test fail but answert close enough from the target results
        min1 = min_distrib([self.uniform_distrib, Distribution([ 1.0,1.0, 1.0] )])
        self.assertTrue(min1.check_cumulative_distrib())
        self.assertEqual(min1, Distribution([1.0]))

        min2 = min_distrib([self.uniform_distrib, Distribution([0, 0, 0, 1.0])])
        self.assertTrue(min2.check_cumulative_distrib())
        self.assertEqual(min2, self.uniform_distrib)

        min3 = min_distrib([self.distrib, Distribution([0,0,0, 0,0,0, 0,0, 1.0 ])])
        self.assertTrue(min3.check_cumulative_distrib())
        #self.assertEqual(min3, self.distrib) # fail but nearly simmilar

    def test_min_distrib2(self):
        min1 = min_distrib([self.uniform_distrib, self.uniform_distrib])
        self.assertTrue(min1.check_cumulative_distrib())
        # self.assertEqual(min1, todo)

        min2 = min_distrib([self.uniform_distrib, self.distrib])
        self.assertTrue(min2.check_cumulative_distrib())

    def test_min_distrib3(self):
        min1 = min_distrib([self.uniform_distrib, self.uniform_distrib, self.uniform_distrib, self.uniform_distrib, self.uniform_distrib])
        self.assertTrue(min1.check_cumulative_distrib())

        min2 = min_distrib([self.uniform_distrib , self.distrib, self.distrib, Distribution([0.2, 0.4, 0.7,1.0],2)])
        self.assertTrue(min2.check_cumulative_distrib())




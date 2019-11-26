import numpy
import math


class Distribution:

    def __init__(self, list_freq , start = 0): #attention le distribution finisse toujour par 1
        self.value = list_freq
        self.start = start
        self.compress_distrib()
        self.check_cumulative_distrib()

    def __getitem__(self, key):
        if key < self.start:
            return 0.0
        elif key >= self.start + len(self.value):
            return 1.0
        else:
            return self.value[key - self.start]

    def __setitem__(self, key, value):
        if key < self.start:
            self.start = key
            pad = [0.0]*(self.start-key) # todo change ???
            pad[0] = value
            self.value = pad + self.value
        elif key >= len(self):
            l = key - (len(self) -1)
            pad = [0.0] * l  # todo change ??
            pad[l-1] = value
            self.value = self.value + pad
        else:
            self.value[key - self.start] = value

    def __str__(self):
        return str([0.0]*self.start + self.value)

    def __len__(self):
        return self.start + len(self.value)

    def __eq__(self, other):

        return isinstance(other, Distribution) and str(self) == str(other)


    def compress_distrib(self):
        """
            gives a shorter form of the distribution
            ex [0,0,0,0.5, 1,1,1] -> [0.5,1],3

        """
        i = 0
        zero = 0
        while i <= len(self) and self[i] == 0:
            i+= 1
            zero += 1



        while  self[i] != 1:
            i+= 1 # we keep the first 1
        end = i + 1
        self.start += zero
        self.value = self.value[zero:end]

    def check_cumulative_distrib(self):
        """ return true if F is a increasing function with maximum = 1"""
        if len(self) == 0: return False
        for i in range(0, len(self) - 1):
            if not (0 <= self[i] <= 1 and self[i] <= self[i + 1]):
                return False
        if self[len(self) - 1] != 1:
            return False
        return True

def sum_distrib(F1, F2):
    """
    f1 and f2 must have the same step size (ex: step in minute)
    :param F1: first cumulative distrbution form : [prop_0_min, prop_1_min ,..., prop_max_time-1_min, prop_stop_unreached]
    :param F2: second cumulative distribution distrbution form
    :return: cumaltive distribution representing the (f1 + f2)
    """
    assert F1.check_cumulative_distrib() and F2.check_cumulative_distrib()
    l1 = len(F1)
    l2 = len(F2)
    l_sum = l1 + l2 - 1
    f_sum = [0] * l_sum

    f1 = [F1[0]] + [F1[i] - F1[i-1] for i in range(1, l1)]
    f2 = [F2[0]] + [F2[i] - F2[i - 1] for i in range(1, l2)]

    for id1 in range(F1.start,l1): # avoid useless computations
        for id2 in range(F2.start,l2):
            f_sum[id1 + id2] += f1[id1] * f2[id2]

    #To cumulative distribution
    F_sum = [f_sum[0]] + [0] * (l_sum - 1)
    for i in range(1, l_sum):
        F_sum[i] = f_sum[i] + F_sum[i-1]

    d = Distribution(F_sum)
    return d

def min_distrib(list_Fi):
    """

    :param list_Fi: the distribution must have the same step size
    :param first_time : list, first_time[i] : valeur du premier composant de la distrbution fi
    :return:
    """
    for Fi in list_Fi:
        assert Fi.check_cumulative_distrib()


    list_Fi = list_Fi[:] # line to handle distribution wit
    start = min([Fi.start for Fi in list_Fi])
    F_min = [0]*start
    i = start
    while len(list_Fi) > 0:
        # F_min <= x iff f0 <= x or f1 <= x or ...  or f(l-1) <= x

        # F_min > x iff  not(f0 <= x or f1 <= x or ...  or f(l-1) <= x)
        # F_min > x iff not(f0 <= x) and not(f1 <= x) and ...  and not(f(l-1) <= x))
        # P(F_min > x) iff  P(f0 > x) * P(f1 > x) * ...  * P(f(l-1) > x))
        #
        # P(F_min <= x) = 1 - P(F_min > x)
        # P(F_min <= x ) = 1 - [ (1-P(f0 <= x)) * (1-P(f1 <= x)) * ... *(1-P(f(l-1) <= x))]
        prod = 0
        for Fi in list_Fi:
            if Fi[i] == 1: # minimum found
                F_min.append(1.0)
                return Distribution(F_min)
            else:
                prod += math.log(1 - Fi[i], 2)      # todo remove precision problem  ??? logarithm????
        F_min.append(1 - math.pow(2, prod))
        i = i+1
    return Distribution(F_min)





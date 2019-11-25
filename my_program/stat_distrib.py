import numpy

def sum_distrib(F1, F2):
    """
    f1 and f2 must have the same step size (ex: step in minute)
    :param F1: first cumulative distrbution form : [prop_0_min, prop_1_min ,..., prop_max_time-1_min, prop_stop_unreached]
    :param F2: second cumulative distribution distrbution form
    :return: cumaltive distribution representing the (f1 + f2)
    """
    assert check_cumulative_distrib(F1) and check_cumulative_distrib(F2)
    l1 = len(F1)
    l2 = len(F2)
    l_sum = l1 + l2 - 1
    f_sum = [0] * (l_sum)

    f1 = [F1[0]] + [F1[i] - F1[i-1] for i in range(1,l1)]
    f2 = [F2[0]] + [F2[i] - F2[i - 1] for i in range(1, l2)]

    for id1 in range(l1):
        for id2 in range(l2):
            f_sum[id1 + id2] += f1[id1] * f2[id2]

    #To cumulative distribution
    F_sum = [f_sum[0]] + [0] * (l_sum - 1)
    for i in range(1, l_sum):
        F_sum[i] = f_sum[i] + F_sum[i-1]
    assert check_cumulative_distrib(F_sum)  # check for safety
    return F_sum

def min_distrib(list_Fi):
    """

    :param list_Fi: the distribution must have the same len and step
    :return:
    """
    for fi in list_Fi:
        assert check_cumulative_distrib(fi)

    #unfinished_list_Fi = list_Fi[:] # line to handle distribution wit
    l = len(list_Fi[0])
    F_min = [0] * l
    for i in range(l):
        # F_min <= x iff f0 <= x or f1 <= x or ...  or f(l-1) <= x

        # F_min > x iff  not(f0 <= x or f1 <= x or ...  or f(l-1) <= x)
        # F_min > x iff not(f0 <= x) and not(f1 <= x) and ...  and not(f(l-1) <= x))
        # P(F_min > x) iff  P(f0 > x) * P(f1 > x) * ...  * P(f(l-1) > x))
        #
        # P(F_min <= x) = 1 - P(F_min > x)
        # P(F_min <= x ) = 1 - [ (1-P(f0 <= x)) * (1-P(f1 <= x)) * ... *(1-P(f(l-1) <= x))]
        prod = 1
        for fi in list_Fi:
            prod *= (1- fi[i])
        F_min[i] = 1 - prod
    assert check_cumulative_distrib(F_min) # check for safety
    return F_min

def check_cumulative_distrib(F):
    """ return true if F is a increasing function with maximum = 1"""
    if len(F) == 0: return False
    for i in range(0, len(F)-1):
        if not (0 <= F[i] <= 1 and F[i] <=  F[i+1]):
            return False
    if F[len(F)-1] != 1:
        return False
    return True

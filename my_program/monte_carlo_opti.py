#Monte carlo

################################## Pick a rdm travel ##################################################


# Trouver la distribution des temps de marche par rapport a un stop (id) Pour chaque commune
# nb les stop pourraient se trouver hors de la commune
# Hypothèse
# pour chaque secteur la population est repartie uniformement

# function of cumulative distribution =  function of repartition
from utils import WALKING_SPEED
from shapely.geometry import MultiPolygon, Point
import random
import math
from my_program.my_utils import *
from my_program.map import my_map
import numpy as np
import my_program.path as PATH


MAX_WALKING_TIME = 60 # in min
SPEED = WALKING_SPEED /0.06 #in m/min
SPEED = 15/0.06



def get_n_rdm_point(n, munty):
    "pick a rdm point in the shape, the probability of select a point depend on the number of people in the sector"
    map = my_map.get_map()

    def rdm_point_shape(shape):
        "pick uniformaly at rdm a point in the shape"
        assert shape.area > 0

        minx, miny, maxx, maxy = shape.bounds
        x = random.randint(math.ceil(minx), math.floor(maxx))
        y = random.randint(math.ceil(miny), math.floor(maxy))
        p = (x,y) #Point(x, y)
        if shape.contains(Point(x, y)):
            return p
        else:
            return rdm_point_shape(shape)

    def get_n_rdm_sector(n, sect_ids):
        sect_pop = [int(map.get_pop_sector(id)) for id in sect_ids]
        tot_pop = map.get_pop_munty(munty)

        sect_cumul_pop = [sect_pop[0] / tot_pop]
        for i in range(1, len(sect_pop)):
            sect_cumul_pop.append(sect_pop[i] / tot_pop + sect_cumul_pop[i - 1])  #todo add in map ???

        # select a sector depending of the number of person in this sector
        for _ in range(n):
            rdm = random.random()

            def bin_search_le(arr, value):
                # return the max index i such that l[i] <= value
                l = 0
                r = len(arr) - 1
                mid = 0
                while l <= r:

                    mid = l + (r - l) // 2

                    # Check if x is present at mid
                    if arr[mid] == value:
                        return mid

                        # If x is greater, ignore left half
                    elif arr[mid] < value:
                        l = mid + 1

                    # If x is smaller, ignore right half
                    else:
                        r = mid - 1

                if arr[mid] < value : return mid + 1
                return mid

            i = bin_search_le(sect_cumul_pop,rdm)
            yield sect_ids[i]




    sect_ids = map.get_sector_ids(munty)
    rdm_sectors = get_n_rdm_sector(n, sect_ids)

    out = []
    for id in rdm_sectors:
        shape = map.get_shape_sector(id)
        out.append(rdm_point_shape(shape))
    return out



################################## Compute the optimal time for a given travel ########################

class stop_munty:
    stop_list = json.load(open(PATH.STOP_LIST, "r"))
    __reachable_stop_munty = {}
    __min_max_time = {}  # store min and max time for each couple of munty orgin -> munty dest

    @classmethod
    def get_reachable_stop_munty(cls, munty):
        """
        Compute a list containing every reachable stop in a walking_time < max_walking_time for a given munty

        :param stop_list: [(stop_id, (coord_x, coord_y))]
        :param munty: refnis of the municipality
        :return: [(stop_id, (coord_x, coord_y))] where distance (munty, stop) < max_walking_time
        """

        map = my_map.get_map()
        reachable_stop = cls.__reachable_stop_munty.get(munty, None)
        if reachable_stop is None:
            reachable_stop = []

            munty_shape = map.get_shape_munty(munty)

            for stop in cls.stop_list:
                pos_point = Point(stop[1][0], stop[1][1])

                if munty_shape.contains(pos_point):
                    reachable_stop.append(stop)  #stop in the municipality

                elif isinstance(munty_shape, MultiPolygon):      #stop not in the municipality and municipality in several part
                    for poly in munty_shape:
                        dist = poly.exterior.distance(pos_point)
                        if dist < MAX_WALKING_TIME * SPEED:
                            reachable_stop.append(stop)
                            break
                else:        #stop not in the municipality and one block municipality
                    dist = munty_shape.exterior.distance(pos_point)
                    if dist < MAX_WALKING_TIME * SPEED:
                        reachable_stop.append(stop)

            cls.__reachable_stop_munty[munty] = reachable_stop

        return reachable_stop

    @classmethod
    def get_reachable_stop_pt(cls, point, munty):
        """
            Compute a list containing every reachable stop in a walking_time < max_walking_time for a given point

            :param stop_list: [(stop_id, (coord_x, coord_y))]
            :param point: (x,y) coordinates of the point
            :return: [(stop_id, (coord_x, coord_y))] where distance (point, stop) < max_walking_time
            """
        stop_list_munty = cls.get_reachable_stop_munty(munty)
        reachable_stop = []
        for stop in stop_list_munty:
            if distance_Eucli(point, stop[1]) < MAX_WALKING_TIME * SPEED:
                reachable_stop.append(stop)
        return reachable_stop

    @classmethod
    def get_min_time(cls, munty_org, munty_dest):
        if munty_org in cls.__min_max_time and munty_dest in cls.__min_max_time[munty_org]:
            return cls.__min_max_time[munty_org][munty_dest][0]
        else :
            min_time = math.inf
            max_time = -1
            for org, _ in cls.get_reachable_stop_munty(munty_org):
                path = PATH.TRAVEL_TIME + "{0}.npy".format(org)
                TC_travel_array = np.load(path)
                for dest, _ in cls.get_reachable_stop_munty(munty_dest):
                    time = TC_travel_array[name_to_idx(dest)]
                    if time >= 0:
                        min_time = min(min_time, time)
                        max_time = max(max_time, time)

            #save result
            if munty_org not in cls.__min_max_time:
                cls.__min_max_time[munty_org] = {}
            cls.__min_max_time[munty_org][munty_dest]= (min_time, max_time)
            return min_time

    @classmethod
    def get_max_time(cls, munty_org, munty_dest):
        if munty_org not in cls.__min_max_time or munty_dest not in cls.__min_max_time[munty_org]:
            cls.get_min_time(munty_org, munty_dest)  # trigger min/max time computation

        return cls.__min_max_time[munty_org][munty_dest][1]

################################## Monte Carlo #########################################################
def optimal_travel_time(resid,munty_rsd, work, munty_work):
    stop_list_rsd = stop_munty.get_reachable_stop_pt(resid, munty_rsd)
    stop_list_work = stop_munty.get_reachable_stop_pt(work, munty_work)

    dist_without_TC = distance_Eucli(resid, work)/SPEED         # without Tc
    opti_time = dist_without_TC

    for stop_rsd in stop_list_rsd:
        walk1 = distance_Eucli(resid,stop_rsd[1])/SPEED  # walking time
        path = PATH.TRAVEL_TIME + "{0}.npy".format(stop_rsd[0])
        TC_travel_array = np.load(path)
        for stop_work in stop_list_work:
            walk2 = distance_Eucli(work, stop_work[1])/SPEED
            time = walk1 + walk2 + TC_travel_array[name_to_idx(stop_work[0])]
            opti_time = min(time, opti_time)

    if opti_time == dist_without_TC > 2*MAX_WALKING_TIME:
        return (dist_without_TC, "unreachable")
    return opti_time, "reachable"



def __iter_by_pop(pop, reducing_factor):
    iteration = pop // reducing_factor
    #avoid bias
    remaining = (pop % reducing_factor) / reducing_factor
    if random.random() < remaining:
        iteration += 1
    return iteration

def monte_carlo_travel(travel, iter,  get_total = False):
    if iter <= 0: return (0,0,0)

    tot_time= 0
    tot_time2 = 0
    unreachable = 0

    rsd_munty = str(travel["residence"][1])
    work_munty = str(travel["work"][1])

    resid_list = get_n_rdm_point(iter, rsd_munty)
    work_list = get_n_rdm_point(iter, work_munty)
    for rsd, work in zip(resid_list, work_list):
        time, is_reachable = optimal_travel_time(rsd,rsd_munty, work, work_munty)
        if is_reachable == "unreachable":
            unreachable += 1
        else:
            tot_time += time
            tot_time2 += time ** 2

    if get_total : return tot_time, tot_time2, unreachable

    mean = tot_time/(iter - unreachable)               # todo case iter - unreachable = 0
    var = tot_time2/(iter - unreachable - 1)          # todo check iter or iter -1
    return mean, var, unreachable


def monte_carlo(travel_path, get_total= False): # todo improve by sorting

    REDUCING_FACTOR = 100

    travel = json.load(open(travel_path))["travel"]
    assert len(travel) > 0
    #travel.sort(key=(lambda x: x["residence"][1]))

    time_munty = {}
    for trav in travel:
        rsd_munty = trav["residence"][1]
        n = int(trav["n"])
        iters = __iter_by_pop(n, REDUCING_FACTOR)
        print("monte carlo", trav, "iteration :", iters)
        tot_Time, tot_time2, unreachable = monte_carlo_travel(trav, iters, get_total=True)
        if rsd_munty not in time_munty:
            time_munty[rsd_munty] = (tot_Time, tot_time2, unreachable, iters, n)
        else:
            old_tot_time, old_tot_time2, old_unreachable, old_iter, old_n = time_munty[rsd_munty]
            time_munty[rsd_munty] = (tot_Time + old_tot_time, tot_time2 + old_tot_time2, unreachable + old_unreachable,
                                     iters + old_iter, n + old_n)

    if get_total : return time_munty

    #comupte mean and var
    for munty in time_munty.keys():
        tot_Time, tot_time2, unreachable, iters, n = time_munty[munty]
        if (iters - unreachable) > 0: mean = tot_Time / (iters - unreachable)
        else: mean = -1
        if (iters - unreachable -1) > 0: var = tot_time2 / (iters - unreachable -1)
        else: var = -1
        time_munty[munty] = (mean, var, unreachable /iters, iters, n)
    return time_munty





if __name__ == '__main__':
    map = my_map.get_map(path_shape = PATH.SHAPE, path_pop  = PATH.POP)
    computations = monte_carlo(PATH.TRAVEL)



# amelioration monte carlo : liste par comumne a utiliser
# ordonner les temps à pied (org -> Tc et TC-> dest) et l'utiliser comme borne inferieur
# ??? ainsi que  temps de trajet max et min entre 2 commune ??? 2 arrondisement ????
#Monte carlo

################################## Pick a rdm travel ##################################################


# Trouver la distribution des temps de marche par rapport a un stop (id) Pour chaque commune
# nb les stop pourraient se trouver hors de la commune
# Hypothèse
# pour chaque secteur la population est repartie uniformement

# function of cumulative distribution =  function of repartition
from Program.Data_manager.path_data import PATH
from shapely.geometry import MultiPolygon, Point
import random
import math
from Program.distance_and_conversion import *
from Program.map import MyMap
import numpy as np
import time

def get_n_rdm_point(n, munty):
    "pick a rdm point in the shape, the probability of select a point depend on the number of people in the sector"
    map = MyMap.get_map()

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
        tot_pop = map.get_pop_refnis(munty)

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
    stop_list = json.load(open(PATH.STOP_POSITION_LAMBERT, "r"))
    __reachable_stop_munty = {}
    __min_max_time = {}  # store min and max time for each couple of munty orgin -> munty dest

    @classmethod
    def get_reachable_stop_munty(cls, munty):
        """
        Compute a list containing every reachable stop in a walking_time < max_walking_time for a given munty

        lazy: stop_munty n'est calculer que si elle est demandée

        :param munty: refnis of the municipality
        :return: [(stop_id, (coord_x, coord_y))] where distance (munty, stop) < max_walking_time
        """

        map = MyMap.get_map()
        reachable_stop = cls.__reachable_stop_munty.get(munty, None)
        if reachable_stop is None:
            reachable_stop = []

            munty_shape = map.get_shape_refnis(munty)

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

            :param point: (x,y) coordinates of the point
            :param munty: munnicipality where the point is located
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
                path = PATH.MINIMAL_TRAVEL_TIME_TC + "{0}.npy".format(org)
                TC_travel_array = np.load(path)
                for dest, _ in cls.get_reachable_stop_munty(munty_dest):
                    time = TC_travel_array[name_to_idx[dest]]
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
def optimal_travel_time(resid_pt, munty_rsd, work_pt, munty_work):
    stop_list_rsd = stop_munty.get_reachable_stop_pt(resid_pt, munty_rsd)
    stop_list_work = stop_munty.get_reachable_stop_pt(work_pt, munty_work)

    dist = distance_Eucli(resid_pt, work_pt)
    time_without_TC =  dist/ SPEED         # without Tc
    #opti time : (time, walk1, walk2, TC,dist, unreachable)
    if time_without_TC > (2 * MAX_WALKING_TIME) : unreachable = 1
    else :  unreachable = 0
    opti_time = (time_without_TC, time_without_TC/2, time_without_TC/2, 0,dist,unreachable)



    if len(stop_list_rsd) == 0 or len(stop_list_work) == 0 : return opti_time


    stop_list_rsd.sort(key=lambda x: distance_Eucli(x[1], resid_pt))
    stop_list_work.sort(key=lambda x: distance_Eucli(x[1], work_pt))
    min_walk2 = distance_Eucli(stop_list_work[0][1], work_pt) / SPEED
    min_trav = stop_munty.get_min_time(munty_rsd, munty_work)

    for stop_rsd in stop_list_rsd:
        walk1 = distance_Eucli(resid_pt, stop_rsd[1]) / SPEED  # walking time
        if walk1 + min_walk2 + min_trav >= opti_time[0]: return opti_time
        path = PATH.MINIMAL_TRAVEL_TIME_TC + "{0}.npy".format(stop_rsd[0])
        TC_travel_array = np.load(path)
        for stop_work in stop_list_work:
            walk2 = distance_Eucli(work_pt, stop_work[1]) / SPEED
            if walk1 + walk2 + min_trav >= opti_time[0]: return opti_time
            TC = TC_travel_array[name_to_idx[stop_work[0]]]
            if TC > 0:
                time = walk1 + walk2 + TC
                if opti_time[0] > time:
                    opti_time = (time, walk1, walk2, TC, dist, 0)

    return opti_time





def monte_carlo(travel_path, get_total= False):

    REDUCING_FACTOR = 25

    class result:
        def __init__(self):
            self.tot_time = 0
            self.tot_time2 = 0  # sum of squared(time)
            self.tot_walk1 = 0
            self.tot_walk2 = 0
            self.tot_TC = 0
            self.tot_TC_user_only = 0
            self.tot_dist = 0.0
            self.iteration = 0
            self.unreachable = 0
            self.TC_user = 0
            self.pop = 0        # nb resident according to sector pop
            self.resid = 0      # nb resident  according to travel
            self.work = 0       # nb workers  according to travel

        def add(self, time , walk1 = 0, walk2 = 0, TC = 0, dist = 0,iter = 1, unreachable =0):
            self.unreachable += unreachable
            self.iteration += iter
            if unreachable == 0:
                self.tot_time += time
                self.tot_time2 += time**2
                self.tot_walk1 += walk1
                self.tot_walk2 += walk2
                self.tot_TC += TC
                self.tot_dist += dist
                if TC > 0 :
                    self.TC_user += 1
                    self.tot_TC_user_only += TC

        def remove(self, time , walk1 = 0, walk2 = 0, TC = 0, dist = 0,iter = 1, unreachable =0):
            self.unreachable -= unreachable
            self.iteration -= iter
            if unreachable == 0 :
                self.tot_time -= time
                self.tot_time2 -= time**2
                self.tot_walk1 -= walk1
                self.tot_walk2 -= walk2
                self.tot_TC -= TC
                self.tot_dist -= dist
            if TC > 0:
                self.TC_user -= 1
                self.tot_TC_user_only -= TC


        def __str__(self):
            "(mean time {}, var {},mean_dist {}, iteration {})".format(self.tot_time/self.iteration,
                                                                       self.tot_time2/self.iteration-1,
                                                                       self.tot_dist/self.iteration,
                                                                       self.iteration)

        def mean(self):
            n = self.iteration - self.unreachable
            if n > 0 : return self.tot_time/ n
            else: return None

        def walk1(self):
            n = self.iteration - self.unreachable
            if n > 0 : return self.tot_walk1/ n
            else: return None

        def walk2(self):
            n = self.iteration - self.unreachable
            if n > 0 : return self.tot_walk2/ n
            else: return None

        def TC(self):
            n = self.iteration - self.unreachable
            if n > 0 : return self.tot_TC/ n
            else: return None

        def TC_user_only(self):
            n = self.TC_user
            if n > 0:
                return self.tot_TC_user_only / n
            else:
                return None

        def mean_dist(self):
            n = self.iteration
            if n > 0 : return self.tot_dist/ n
            else: return None

        def mean_dist_reachable(self):
            n = self.iteration - self.unreachable
            if n > 0: return self.tot_dist / n
            else: return None

        def var(self):
            n = self.iteration - self.unreachable -1 #todo check unbiased var
            if n > 0 : return self.tot_time2/ n
            else: return None

        def prop_unreachable(self):
            n = self.iteration
            if n > 0 : return self.unreachable/n
            else: return None

        def prop_TC_users(self):
            n = self.iteration - self.unreachable
            if n > 0 : return self.TC_user/n
            else: return None

    def __iter_by_pop(pop, reducing_factor):
        iteration = pop // reducing_factor
        # avoid bias
        remaining = (pop % reducing_factor) / reducing_factor
        if random.random() < remaining:
            iteration += 1
        return iteration

    travel = json.load(open(travel_path))["travel"]
    assert len(travel) > 0
    travel.sort(key=(lambda x: x["residence"][1]))

    all_results = {}                # contains result for each munty
    for trav in travel:
        rsd_munty = str(trav["residence"][1])
        work_munty = str(trav["work"][1])
        res = all_results.get(rsd_munty, result())
        n = int(trav["n"])
        res.resid += n
        res.pop = MyMap.get_map().get_pop_refnis(rsd_munty)

        # compute monte carlo for iter travel
        iters = __iter_by_pop(n, REDUCING_FACTOR)
        print("monte carlo", trav, "iteration :", iters)
        resid_list = get_n_rdm_point(iters, rsd_munty)
        work_list = get_n_rdm_point(iters, work_munty)
        for rsd, work in zip(resid_list, work_list):
            (time, walk1, walk2, TC, dist, unreachable) = optimal_travel_time(rsd, rsd_munty, work, work_munty)
            res.add(time, walk1, walk2, TC,dist,1, unreachable)

        all_results[rsd_munty] = res

        # number of worker
        w = all_results.get(work_munty, result())
        w.work += n
        all_results[work_munty] = w

    return all_results




if __name__ == '__main__':
    map = MyMap.get_map(path_shape = PATH.MAP_SHAPE, path_pop  = PATH.MAP_POP)

    start = time.time()
    computations = monte_carlo(PATH.TRAVEL)
    end = time.time()
    print("time : ", end - start)


# amelioration monte carlo : liste par comumne a utiliser
# ordonner les temps à pied (org -> Tc et TC-> dest) et l'utiliser comme borne inferieur
# ??? ainsi que  temps de trajet max et min entre 2 commune ??? 2 arrondisement ????
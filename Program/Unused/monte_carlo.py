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
from Program.my_utils import *
import numpy as np
import Program.General.map as mapp
import csv
import Program.path as path
import time

population_by_sector_2011_path = "data/OPEN_DATA_SECTOREN_2011.csv"

max_walking_time = 60 # in min
SPEED = WALKING_SPEED /0.06 #in m/min
SPEED = 15/0.06

#map
map = mapp.my_map.get_map(path.SHAPE, path.POP)




def sectors_population2011( path = "data/OPEN_DATA_SECTOREN_2011.csv"):
    sectors_pop = {}
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            name = str(row["\ufeffCD_REFNIS"]) + str(row["CD_SECTOR"])
            sectors_pop[name] = row["POPULATION"]
    return sectors_pop


def get_n_rdm_point(n, munty):
    "pick a rdm point in the shape, the probability of select a point depend on the number of people in the sector"


    def rdm_point_shape(shape):
        "pick uniformaly at rdm a point in the shape"
        minx, miny, maxx, maxy = shape.bounds
        x = random.randint(math.ceil(minx), math.floor(maxx))
        y = random.randint(math.ceil(miny), math.floor(maxy))
        p = (x,y) #Point(x, y)
        if shape.contains(Point(x, y)):
            return p
        else:
            return rdm_point_shape(shape)

    def get_n_rdm_sector(n, sect_ids, all_sector_pop):
        sect_pop = [int(all_sector_pop[id]) for id in sect_ids]
        tot_pop = sum(sect_pop)

        sect_cumul_pop = [sect_pop[0] / tot_pop]
        for i in range(1, len(sect_pop)):
            sect_cumul_pop.append(sect_pop[i] / tot_pop + sect_cumul_pop[i - 1])

        # select a sector depending of the number of person in this sector
        for _ in range(n):
            rdm = random.random()
            # todo improve binary search
            i = 0
            while i < len(sect_cumul_pop) and rdm > sect_cumul_pop[i]:
                i += 1
            yield sect_ids[i]


    sect_ids = map.get_sector_ids(munty)
    all_sector_pop = sectors_population2011()
    rdm_sectors = get_n_rdm_sector(n, sect_ids, all_sector_pop)


    out = []
    for id in rdm_sectors:
        shape = map.get_shape_sector(id)
        out.append(rdm_point_shape(shape))
    return out



################################## Compute the optimal time for a given travel ########################


def get_reachable_stop_munty( munty, stop_list):
    """
    Compute a list containing every reachable stop in a walking_time < max_walking_time for a given munty

    :param stop_list: [(stop_id, (coord_x, coord_y))]
    :param munty: refnis of the municipality
    :return: [(stop_id, (coord_x, coord_y))] where distance (munty, stop) < max_walking_time
    """
    reachable_stop = []

    munty_shape = map.get_shape_refnis(munty)

    for stop in stop_list:
        pos_point = Point(stop[1][0], stop[1][1])

        if munty_shape.contains(pos_point):
            reachable_stop.append(stop)  #stop in the municipality

        elif isinstance(munty_shape, MultiPolygon):      #stop not in the municipality and municipality in several part
            for poly in munty_shape:
                dist = poly.exterior.distance(pos_point)
                if dist < max_walking_time * SPEED:
                    reachable_stop.append(stop)
                    break
        else:        #stop not in the municipality and one block municipality
            dist = munty_shape.exterior.distance(pos_point)
            if dist < max_walking_time * SPEED:
                reachable_stop.append(stop)
    return reachable_stop

def get_reachable_stop_pt( point, stop_list):
    """
        Compute a list containing every reachable stop in a walking_time < max_walking_time for a given point

        :param stop_list: [(stop_id, (coord_x, coord_y))]
        :param point: (x,y) coordinates of the point
        :return: [(stop_id, (coord_x, coord_y))] where distance (point, stop) < max_walking_time
        """
    reachable_stop = []
    for stop in stop_list:
        if distance_Eucli(point, stop[1]) < max_walking_time * SPEED:
            reachable_stop.append(stop)
    return reachable_stop


def optimal_travel_time(resid, work, stop_list_rsd, stop_list_work):
    stop_list_rsd = get_reachable_stop_pt(resid, stop_list_rsd)
    stop_list_work = get_reachable_stop_pt(work, stop_list_work)

    dist_without_TC = distance_Eucli(resid, work)/SPEED         # without Tc
    opti_time = dist_without_TC

    for stop_rsd in stop_list_rsd:
        walk1 = distance_Eucli(resid,stop_rsd[1])/SPEED  # walking time
        path = "../produce/out/{0}.npy".format(stop_rsd[0])
        TC_travel_array = np.load(path)
        for stop_work in stop_list_work:
            walk2 = distance_Eucli(work, stop_work[1])/SPEED
            time = walk1 + walk2 + TC_travel_array[name_to_idx(stop_work[0])]
            opti_time = min(time, opti_time)

    if opti_time == dist_without_TC > 2*max_walking_time:
        return (dist_without_TC, "unreachable")
    return opti_time, "reachable"

################################## Monte Carlo #########################################################

def __iter_by_pop(pop, reducing_factor):
    iteration = pop // reducing_factor
    #avoid bias
    remaining = (pop % reducing_factor) / reducing_factor
    if random.random() < remaining:
        iteration += 1
    return iteration

def monte_carlo_travel(travel, iter, stop_list_rsd, stop_list_work, get_total = False):
    if iter <= 0: return (0,0,0)

    tot_time= 0
    tot_time2 = 0
    unreachable = 0

    rsd_munty = str(travel["residence"][1])
    work_munty = str(travel["work"][1])

    resid_list = get_n_rdm_point(iter, rsd_munty)
    work_list = get_n_rdm_point(iter, work_munty)
    for rsd, work in zip(resid_list, work_list):
        time, is_reachable = optimal_travel_time(rsd, work, stop_list_rsd, stop_list_work)
        if is_reachable == "unreachable":
            unreachable += 1
        else:
            tot_time += time
            tot_time2 += time ** 2

    if get_total : return tot_time, tot_time2, unreachable

    mean = tot_time/(iter - unreachable)               # todo case iter - unreachable = 0
    var = tot_time2/(iter - unreachable - 1)          # todo check iter or iter -1
    return mean, var, unreachable


def monte_carlo(travel_path,stop_list, get_total= False): # todo improve by sorting and get_reachable_stop_munty

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
        tot_Time, tot_time2, unreachable = monte_carlo_travel(trav, iters, stop_list, stop_list, get_total=True)
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

    start = time.time()
    computations = monte_carlo("data/tiny_data/travel_user.json", json.load(open("out_dir/stop_lambert_pos.json", "r")))
    end = time.time()
    print("time : " , end - start)


# amelioration monte carlo : liste par comumne a utiliser
# ordonner les temps à pied (org -> Tc et TC-> dest) et l'utiliser comme borne inferieur
# ??? ainsi que  temps de trajet max et min entre 2 commune ??? 2 arrondisement ????
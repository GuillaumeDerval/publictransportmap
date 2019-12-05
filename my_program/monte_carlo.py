#Monte carlo

################################## Pick a rdm travel ##################################################


# Trouver la distribution des temps de marche par rapport a un stop (id) Pour chaque commune
# nb les stop pourraient se trouver hors de la commune
# Hypothèse
# pour chaque secteur la population est repartie uniformement

# function of cumulative distrribution =  function of repartition
import csv
from utils import WALKING_SPEED
from shapely.geometry import MultiPolygon, Polygon, Point
from my_program.Unused.stat_distrib import Distribution
from my_program.map import *
import random
import math

population_by_sector_2011_path = "data/OPEN_DATA_SECTOREN_2011.csv"

SPEED = WALKING_SPEED /0.06 #in m/s



def sectors_population2011( path = "data/OPEN_DATA_SECTOREN_2011.csv"):
    sectors_pop = {}
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            name = str(row["\ufeffCD_REFNIS"]) + str(row["CD_SECTOR"])
            sectors_pop[name] = row["POPULATION"]
    return sectors_pop


def get_n_rdm_point(n, munty, map):
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

        # select a sector depending of the number of person in ths sector
        for _ in range(n):
            rdm = random.random()
            # todo improve binary search
            i = 0
            while i < len(sect_cumul_pop) and rdm > sect_cumul_pop[i]:
                i += 1
            yield sect_ids[i]

    print("map")

    sect_ids = map.get_sector_ids(munty)
    all_sector_pop = sectors_population2011()
    rdm_sectors = get_n_rdm_sector(n, sect_ids, all_sector_pop)


    out = []
    for id in rdm_sectors:
        shape = map.get_shape_sector(id)
        out.append(rdm_point_shape(shape))
    return out



################################## Compute the optimal time for a given travel ########################


def get_reachable_stop( munty, stop_list, map,  max_walking_time):
    """
    Compute a list containing every reachable stop in a walking_time < max_walking_time for a given munty

    :param stop_list: [(stop_id, (coord_x, coord_y))]
    :param munty: refnis of the municipality
    :param max_walking_time:
    :return: [(stop_id, (coord_x, coord_y))] where distance (munty, stop) < max_walking_time
    """
    reachable_stop = []

    munty_shape = map.get_shape_munty(munty)

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

def optimal_travel_time(resid,rsd_munty, work, work_munty):
    # todo
    raise NotImplementedError

################################## Monte Carlo #########################################################

def monte_carlo(travel):
    # todo
    raise NotImplementedError


if __name__ == '__main__':

    if my_map.belgium_map is None : map = my_map()
    else: map = my_map.belgium_map

    a = get_n_rdm_point(20, "52011", map)
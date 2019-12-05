
# Trouver la distribution des temps de marche par rapport a un stop (id) Pour chaque commune
# nb les stop pourraient se trouver hors de la commune
# Hypothèse
# pour chaque secteur la population est repartie uniformement

# function of cumulative distrribution =  function of repartition
import csv
from utils import WALKING_SPEED
from shapely.geometry import Point, Polygon, MultiPolygon
from my_program.stat_distrib import Distribution
from my_program.map import *

#population_by_sector_2019_path = "data/OPEN_DATA_SECTOREN_2019.csv"
population_by_sector_2011_path = "data/OPEN_DATA_SECTOREN_2011.csv"
# population_by_square = ""
SPEED = WALKING_SPEED /0.06 #in m/s

SPEED = 50 /0.06 #in m/s # todo because to fast



def sectors_population2019( path):
    sectors_pop = {}
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            sectors_pop[row["CD_SECTOR"]] = row["POPULATION"]
    return sectors_pop

def sectors_population2011( path = "data/OPEN_DATA_SECTOREN_2011.csv"):
    sectors_pop = {}
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            name = str(row["\ufeffCD_REFNIS"]) + str(row["CD_SECTOR"])
            sectors_pop[name] = row["POPULATION"]
    return sectors_pop


def walking_time_distrib_sector(stop, munty, max_walking_time):
    """
    the cumulative distribution's function of the walking_time to go to stop for people in municipality munty

    :param stop: (stop_id, (coord_x, coord_y))
    :param munty: refnis of munty
    :param max_walking_time: maximum walking distance to reach the stop
    :return: [prop_0_min, prop_1_min ,..., prop_max_time-1_min, prop_stop_unreached]
    """
    if my_map.belgium_map is None : map = my_map()
    else: map = my_map.belgium_map
    # munty_shape = map.get_shape_munty(munty)
    sector_list = map.get_sector_ids(munty)
    sector_pop = sectors_population2011(population_by_sector_2011_path)

    # compute population of the munty
    tot_pop_munty = 0
    for sect in sector_list:
        pop = int(sector_pop[sect])
        if map.get_shape_sector(sect).area > 0: # don't count people that we can't not place
            tot_pop_munty += pop

    #distrib = [-1]* max_walking_time
    #for time in range(max_walking_time):
    distrib = []
    for time in range(1000):
        radius = (time + 0.5)*SPEED         # to get a roughly mean time of radius minutes
        stop_x, stop_y = stop[1]
        circle = Point(stop_x,stop_y).buffer(radius)
        tot = 0
        for sect in sector_list:
            sector_shape = map.get_shape_sector(sect)
            sector_area = sector_shape.area
            if sector_area > 0:
                intersect_area = sector_shape.intersection( circle).area  # intersection
                pop = int(sector_pop[sect])*intersect_area/sector_area
                tot += pop
            else : print("probleme sector area : ",sector_pop[sect], "persons concerned" )
        distrib.append( tot/tot_pop_munty)
        if distrib[time] == 1.0: break
    # distrib[max_walking_time] = tot_pop_munty # unreached
    return Distribution(distrib)





def get_reachable_stop(stop_list, munty, max_walking_time):
    """
    Compute a list containing every reachable stop in a walking_time < max_walking_time for a given munty

    :param stop_list: [(stop_id, (coord_x, coord_y))]
    :param munty: refnis of the municipality
    :param max_walking_time:
    :return: [(stop_id, (coord_x, coord_y))] where distance (munty, stop) < max_walking_time
    """
    reachable_stop = []
    if my_map.belgium_map is None : map = my_map()
    else: map = my_map.belgium_map

    munty_shape = map.get_shape_munty(munty)
    print(munty_shape.type)

    for stop in stop_list:
        pos_point = Point(stop[1][0], stop[1][1])

        if munty_shape.contains(pos_point):

            reachable_stop.append(stop)  #stop in the municipality
            print(stop)
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


def get_all_walking_time_distrib(stop_list, munty_list, max_walking_time):
    """
    Build a dictionnary containing the distribution of the walking_time
            for each stop,munty where min_dist(stop, munty) < max_walking_time
    :param stop_list: [(stop_id, (coord_x, coord_y)),...]
    :param munty_list: list of refnis
    :param max_walking_time: int
    :return: dictionnary : {(stop_id, munty) : (prop_0_min, prop_1_min ,..., prop_max_time_min, prop_not_counted)}
    """
    all_distrib = {}

    print("all distrib")
    for munty in munty_list:
        print(munty)
        reduced_stop_list = get_reachable_stop(stop_list, munty, max_walking_time)
        for stop in reduced_stop_list:
            distrib = walking_time_distrib_sector(stop, munty,  max_walking_time)
            print(distrib)
            stop_id = stop[0]
            all_distrib[(stop_id, munty)] = distrib
    return all_distrib

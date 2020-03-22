# manipulation de la carte de belgique
import csv
from shapely.geometry import shape, MultiPolygon, Point
# from shapely.ops import Point
from Program.distance_and_conversion import *
from Program.path import PATH, PARAMETERS


class my_map:
    belgium_map = None

    @classmethod
    def get_map(cls, path_shape=PATH.MAP_SHAPE, path_pop=PATH.MAP_POP, stop_list_path=PATH.STOP_POSITION_LAMBERT):
        if my_map.belgium_map is None:
            #if (my_map.belgium_map.path_shape is not None and my_map.belgium_map.path_shape != path_shape) or (my_map.belgium_map.path_pop is not None  and my_map.belgium_map.path_pop != path_pop):
            my_map.belgium_map = my_map(path_shape, path_pop, stop_list_path)
        return my_map.belgium_map

    def __init__(self, path_shape, path_pop, stop_list_path):
        self.__sector_map = {}
        self.__munty_map = {}
        self.path_shape = path_shape
        self.path_pop = path_pop

        self.__set_sector()
        self.__set_shape_munty()

        # stop_munty
        with open(stop_list_path, "r") as file:
            stop_list = json.load(file)
            self.stop_position_dico = {name: tuple(pos) for name, pos in stop_list}
        self.reachable_stop_from_munty = {munty: [] for munty in
                                          self.get_all_munty_refnis()}  # contient tout les stop atteignable depuis une commune
        self.reachable_munty_from_stop = {stop_name: [] for stop_name in
                                          self.stop_position_dico.keys()}  # contient tout les commune depuis un stop
        self.__set_reachable_stop_from_munty(self.stop_position_dico.items())

    def __set_sector(self):
        with open(self.path_shape) as f:
            features = json.load(f)["features"]
            sector = {}  # key = refnis
            for elem in features:
                sector_id = elem["properties"]["CD_SECTOR"]
                sector[sector_id] = {"shape": shape(elem["geometry"]).buffer(0), "pop": 0}
        self.__sector_map = sector

        #population 2011
        with open(self.path_pop) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                name = str(row["\ufeffCD_REFNIS"]) + str(row["CD_SECTOR"])
                if name in sector:
                    sector[name]["pop"] = int(row["POPULATION"])

    def __set_shape_munty(self):
        with open(self.path_shape) as f:
              features = json.load(f)["features"]
              for elem in features:
                    refnis = str(elem["properties"]["CD_MUNTY_REFNIS"])
                    sector_id = str(elem["properties"]["CD_SECTOR"])
                    if refnis in self.__munty_map:
                        self.__munty_map[refnis]["shape"] = self.__munty_map[refnis]["shape"].union(shape(elem["geometry"]).buffer(0))
                        self.__munty_map[refnis]["sector_ids"].append(sector_id)
                        self.__munty_map[refnis]["pop"] += self.get_pop_sector(sector_id)
                    else:

                        self.__munty_map[refnis] = {"shape": shape(elem["geometry"]).buffer(0), "sector_ids" : [sector_id],
                                                    "pop": self.get_pop_sector(sector_id)}

    def get_all_munty_refnis(self):
        return self.__munty_map.keys()


    def get_total_shape(self):
        with open(self.path_shape) as f:
              features = json.load(f)["features"]
              first = True
              total_shape = None
              for elem in features:
                  if first:
                      total_shape  = shape(elem["geometry"]).buffer(0)
                      first = False
                  else:
                      total_shape = total_shape.union(shape(elem["geometry"]).buffer(0))
        return total_shape

    def get_shape_sector(self, sector_id):
        return self.__sector_map[sector_id]["shape"]

    def get_shape_munty(self, refnis):
        return self.__munty_map[refnis]["shape"]

    #population
    def get_pop_sector(self, sector_id):
        return self.__sector_map[sector_id]["pop"]

    def get_pop_munty(self, refnis):
        return self.__munty_map[refnis]["pop"]

    def get_sector_ids(self, refnis_munty):
        return self.__munty_map[refnis_munty]["sector_ids"]

    # ##################################### Relation between stop position and municipality ############################

    def __set_reachable_stop_from_munty(self, stop_list):
        """
        Compute a list containing every reachable stop in a walking_time < max_walking_time for a given munty

        :param stop_list : a list containg all stop to considere
        :modify: reachable_stop_from_munty : {munty1 : [stop1,stop2,...]} where walking_time(muntyi,stopi) < MAX_WALKING_TIME
                 reachable_munty_from_stop: {stop_name1 : [munty1,munty2,...]} where walking_time(muntyi,stopi) < MAX_WALK_TIME
        """

        for munty in self.get_all_munty_refnis():
            munty_shape = self.get_shape_munty(munty)

            for stop in stop_list:
                pos_point = Point(stop[1][0], stop[1][1])

                if munty_shape.contains(pos_point):
                    self.reachable_stop_from_munty[munty].append(stop)  # stop in the municipality
                    if stop[0] in self.reachable_munty_from_stop:
                        self.reachable_munty_from_stop[stop[0]].append(munty)
                    else:
                        self.reachable_munty_from_stop[stop[0]] = [munty]

                elif isinstance(munty_shape,MultiPolygon):  # stop not in the municipality and municipality in several part
                    for poly in munty_shape:
                        dist = poly.exterior.distance(pos_point)
                        if dist < PARAMETERS.MAX_WALKING_TIME() * PARAMETERS.WALKING_SPEED():
                            self.reachable_stop_from_munty[munty].append(stop)
                            if stop[0] in self.reachable_munty_from_stop:
                                self.reachable_munty_from_stop[stop[0]].append(munty)
                            else:
                                self.reachable_munty_from_stop[stop[0]] = [munty]
                            break
                else:  # stop not in the municipality and one block municipality
                    dist = munty_shape.exterior.distance(pos_point)
                    if dist < PARAMETERS.MAX_WALKING_TIME() * PARAMETERS.WALKING_SPEED():
                        self.reachable_stop_from_munty[munty].append(stop)
                        if stop[0] in self.reachable_munty_from_stop:
                            self.reachable_munty_from_stop[stop[0]].append(munty)
                        else:
                            self.reachable_munty_from_stop[stop[0]] = [munty]

    def get_reachable_stop_from_munty(self, munty):
        """
        Return a list containing every reachable stop in a walking_time < max_walking_time for a given munty

        :param munty: refnis of the municipality
        :return: [(stop_id, (coord_x, coord_y))] where distance (munty, stop) < max_walking_time
        """
        return self.reachable_stop_from_munty[munty]

    def get_reachable_munty_from_stop(self, stop_name):
        """
        Return a list containing every reachable munty in a walking_time < max_walking_time for a given stop

        :param stop_name: name of the stop          ex : TEC2068
        :return: [refnis_munty1, refnis_munty2, ... ] where distance (munty, stop) < max_walking_time
        """
        return self.reachable_stop_from_munty[stop_name]

    def get_reachable_stop_pt(self, point, munty = None):
        """
            Compute a list containing every reachable stop in a walking_time < max_walking_time for a given point

            :param point: (x,y) coordinates of the point
            :param munty: munnicipality where the point is located
            :return: [(stop_id, (coord_x, coord_y))] where distance (point, stop) < max_walking_time
            """

        if munty is None:
            for m in self.get_all_munty_refnis():
                munty_shape = self.get_shape_munty(m)
                if munty_shape.contains(point):
                    munty = m

        stop_list_munty = self.get_reachable_stop_from_munty(munty)
        reachable_stop = []
        for stop in stop_list_munty:
            if distance_Eucli(point, stop[1]) < PARAMETERS.MAX_WALKING_TIME() * PARAMETERS.WALKING_SPEED():
                reachable_stop.append(stop)
        return reachable_stop

    def add_stop(self, stop_name_pos):
        """
        Ajoute un  stop qui n'était pas present dans la liste de stop initiale
        :param stop_name_pos:
        """

        if not isinstance(stop_name_pos, list):
            stop_name_pos = [stop_name_pos]
        for stop_name, pos in stop_name_pos:
            self.stop_position_dico[stop_name] = pos
        self.__set_reachable_stop_from_munty(stop_name_pos)

    def remove_stop(self, stop_name):
        if not isinstance(stop_name, list):
            stop_name = [stop_name]
        for st in stop_name:
            affected_munty = self.reachable_stop_from_munty.pop(st)
            for munty in affected_munty:
                self.reachable_stop_from_munty[munty].remove(st)
# NOTE: buffer(0) is a trick for fixing scenarios where polygons have overlapping coordinates
# G = GeometryCollection([shape(feature["geometry"]).buffer(0) for feature in features])

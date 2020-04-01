# manipulation de la carte de belgique
import csv
from shapely.geometry import shape, MultiPolygon, Point
# from shapely.ops import Point
from Program.distance_and_conversion import *



class my_map:
    belgium_map = None

    @classmethod
    def get_map(cls, param, path_shape=None, path_pop=None, path_stop_list=None):
        if my_map.belgium_map is None:
            if path_shape is None : path_shape = param.PATH.MAP_SHAPE
            if path_pop is None: path_pop = param.PATH.MAP_POP
            if path_stop_list is None: path_stop_list = param.PATH.STOP_POSITION_LAMBERT
            my_map.belgium_map = my_map(param, path_shape, path_pop, path_stop_list)
        return my_map.belgium_map

    def __init__(self,param, path_shape, path_pop, stop_list_path):
        self.__sector_map = {}
        self.__munty_map = {}
        self.path_shape = path_shape
        self.path_pop = path_pop
        self.param = param


        self.__set_sector()
        self.__set_shape_munty()

        # stop_munty
        with open(stop_list_path, "r") as file:
            stop_list = json.load(file)
            self.stop_position_dico = {name: tuple(pos) for name, pos in stop_list}
        self.reachable_stop_from_munty = {munty: [] for munty in
                                          self.get_all_munty_refnis()}  # contient tout les stop atteignable depuis une commune
        self.reachable_munty_from_stop = {stop_name: set() for stop_name in
                                          self.stop_position_dico.keys()}  # contient tout les commune depuis un stop
        self.__set_reachable_stop_from_munty(self.stop_position_dico.items())

        # reversible structure
        self.__change_log = []      # added_stop_name
        self.__stack_log = []       # permet de faire une recherche sur plusieur etage

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

    def get_shape_refnis(self, refnis):
        return self.__munty_map[refnis]["shape"]

    #population
    def get_pop_sector(self, sector_id):
        return self.__sector_map[sector_id]["pop"]

    def get_pop_refnis(self, refnis):
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
            munty_shape = self.get_shape_refnis(munty)

            for stop in stop_list:
                pos_point = Point(stop[1][0], stop[1][1])

                if munty_shape.contains(pos_point):
                    self.reachable_stop_from_munty[munty].append(stop)  # stop in the municipality
                    self.reachable_munty_from_stop[stop[0]].add(munty)


                elif isinstance(munty_shape,MultiPolygon):  # stop not in the municipality and municipality in several part
                    for poly in munty_shape:
                        dist = poly.exterior.distance(pos_point)
                        if dist < self.param.MAX_WALKING_TIME() * self.param.WALKING_SPEED():
                            self.reachable_stop_from_munty[munty].append(stop)
                            self.reachable_munty_from_stop[stop[0]].add(munty)
                            break
                else:  # stop not in the municipality and one block municipality
                    dist = munty_shape.exterior.distance(pos_point)
                    if dist < self.param.MAX_WALKING_TIME() * self.param.WALKING_SPEED():
                        self.reachable_stop_from_munty[munty].append(stop)
                        self.reachable_munty_from_stop[stop[0]].add(munty)

    def get_reachable_stop_from_munty(self, munty):
        """
        Return a list containing every reachable stop in a walking_time < max_walking_time for a given munty

        :param munty: refnis of the municipality
        :return: [(stop_name, (coord_x, coord_y))] where distance (munty, stop) < max_walking_time
        """
        return self.reachable_stop_from_munty[munty]

    def get_reachable_munty_from_stop(self, stop_name):
        """
        Return a list containing every reachable munty in a walking_time < max_walking_time for a given stop

        :param stop_name: name of the stop          ex : TEC2068
        :return: [refnis_munty1, refnis_munty2, ... ] where distance (munty, stop) < max_walking_time
        """
        return self.reachable_stop_from_munty[stop_name]

    def get_reachable_stop_pt(self, pos, munty = None):
        """
            Compute a list containing every reachable stop in a walking_time < max_walking_time for a given point

            :param pos: (x,y) coordinates of the point
            :param munty: munnicipality where the point is located
            :return: [(stop_name, (coord_x, coord_y))] where distance (point, stop) < max_walking_time
            """
        point = Point(pos[0], pos[1])
        if munty is None:
            for m in self.get_all_munty_refnis():
                munty_shape = self.get_shape_refnis(m)
                if munty_shape.contains(point):
                    munty = m

        if munty is None:
            stop_list_munty = self.stop_position_dico.items() # cas ou le stop est hors de la carte
        else:
            stop_list_munty = self.get_reachable_stop_from_munty(munty)
        reachable_stop = []
        for stop in stop_list_munty:
            if distance_Eucli(pos, stop[1]) < self.param.MAX_WALKING_TIME() * self.param.WALKING_SPEED():
                reachable_stop.append(stop)
        return reachable_stop

    def get_stop(self, stop_name):
        """

            :return: (stop_name, (coord_x, coord_y))
        """
        return stop_name,self.stop_position_dico[stop_name]

    def add_stop(self, stop_name, pos):
        """
        Ajoute un  stop qui n'était pas present dans la liste de stop initiale
        :param stop_name_pos:
        """

        stop_name_pos = stop_name, pos

        self.stop_position_dico[stop_name] = pos
        self.reachable_munty_from_stop[stop_name] = set()
        self.__set_reachable_stop_from_munty([stop_name_pos])
        self.__change_log.append(stop_name_pos)

    def remove_stop(self, stop_name):
        if not isinstance(stop_name, list):
            stop_name = [stop_name]
        for st,pos in stop_name:
            affected_munty = self.reachable_munty_from_stop.pop(st)
            for munty in affected_munty:
                self.reachable_stop_from_munty[munty].remove((st, pos))

    def save(self):
        self.__stack_log.append(self.__change_log)
        self.__change_log = []

    def restore(self):
        #for added_stop in self.__change_log:
        self.remove_stop(self.__change_log)

        self.__change_log = self.__stack_log.pop()

# NOTE: buffer(0) is a trick for fixing scenarios where polygons have overlapping coordinates
# G = GeometryCollection([shape(feature["geometry"]).buffer(0) for feature in features])

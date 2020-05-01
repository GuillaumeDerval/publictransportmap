import os
import json
from Program.Map import MyMapStop


initial = "initial"
intermediate = "intermediate"
produced = "produced"


def make_data_structure(data_path):
    """
    Cree la structure de dossier permettant d'acceuillir les donnees a l'endroit specifier par data_path
    Cette structure comporte 3 dossiers:
        - initial/ : dossier contenant les donnees source. Celles si devron t etre telecharger et mise dans ce dossier

        - intermediate/ : dossier permettant de sauvegarder les donnees du programme
                          sous une formme utilisable pour l'optimisation
        - produced/ : dossier contenant les resultats

    :param data_path: Chemin vers l'endroit ou seront stocker les donnees (ex user/mypath/)
    """
    root = data_path

    for repertoire in [initial, intermediate, produced]:
        path = root + "/" + repertoire
        if not os.path.exists(path):
            os.makedirs(path)

    # gtfs
    if not os.path.exists(root + "/" + initial + "/gtfs"):
        os.makedirs(root + "/" + initial + "/gtfs")

    # produced map
    if not os.path.exists(root + "/" + produced + "/maps"):
        os.makedirs(root + "/" + produced + "/maps")

    # produced minimal distance
    if not os.path.exists(root + "/" + produced + "/minimal_distance"):
        os.makedirs(root + "/" + produced + "/minimal_distance")


class PATH_BELGIUM:

    def __init__(self, root):
        self.root_main = root
        # new method
        self.GTFS = root + "/" + initial + "/gtfs/"
        self.BUS_ONLY = root + "/" + intermediate + "/bus_only.json"
        self.TRAIN_ONLY = root + "/" + intermediate + "/train_only.json"
        self.TRAIN_BUS = root + "/" + intermediate + "/train_bus.json"

        # metric
        self.MAP_SHAPE = root + "/" + initial + "/sh_statbel_statistical_sectors.geojson"
        self.MAP_POP = root + "/" + initial + "/OPEN_DATA_SECTOREN_2011.csv"
        self.RSD_WORK = root + "/" + initial + "/TU_CENSUS_2011_COMMUTERS_MUNTY.txt"
        self.STOP_POSITION_LAMBERT = {"train_only": root + "/" + intermediate + "/stop_lambert_train_only.json",
                                      "bus_only": root + "/" + intermediate + "/stop_lambert_bus_only.json",
                                      "train_bus": root + "/" + intermediate + "/stop_lambert_train_bus.json"}

        # output map
        self.OUT_BELGIUM_MAP = root + "/" + produced + "/maps/Belgium.geojson"
        self.OUT_TRAIN_LINES_MAP = root + "/" + produced + "/maps/train_lines_belgium.geojson"
        self.OUT_BUS_LINES_MAP = root + "/" + produced + "/maps/bus_lines_belgium.geojson"


class PATH:

    def __init__(self, root, location_name, transport):

        path = root + "/" + intermediate + "/" + location_name + "_" + transport
        if not os.path.exists(path):
            os.makedirs(path)
        path = root + "/" + produced + "/is_path/" + location_name + "_" + transport
        if not os.path.exists(path):
            os.makedirs(path)
        path = root + "/" + produced + "/minimal_distance/" + location_name + "_" + transport
        if not os.path.exists(path):
            os.makedirs(path)

        self.root = root
        self.location_name = location_name
        self.transport = transport

        self.CONFIG = "{0}/{1}/{2}_{3}/config.json".format(root, intermediate, location_name, transport)

        # new method
        self.TRANSPORT = "{0}/{1}/{2}_{3}/transport.json".format(root, intermediate, location_name, transport)
        self.SIMPLIFIED = "{0}/{1}/{2}_{3}/simplified.json".format(root, intermediate, location_name, transport)
        self.WALKING = "{0}/{1}/{2}_{3}/distance_walking.json".format(root, intermediate, location_name, transport)

        # metric
        self.MAP_SHAPE = "{0}/{1}/{2}_{3}/map.geojson".format(root, intermediate, location_name, transport)
        self.MAP_POP = "{0}/{1}/{2}_{3}/pop_sector.csv".format(root, intermediate, location_name, transport)
        self.RSD_WORK = "{0}/{1}/{2}_{3}/CENSUS_2011.txt".format(root, intermediate, location_name, transport)
        self.TRAVEL = "{0}/{1}/{2}_{3}/travel_user.json".format(root, intermediate, location_name, transport)
        self.STOP_POSITION_LAMBERT = "{0}/{1}/{2}_{3}/stop_lambert.json".format(root, intermediate, location_name, transport)

        # dynamic APSP
        self.GRAPH_TC = "{0}/{1}/{2}_{3}/graph.json".format(root, intermediate, location_name, transport)
        self.GRAPH_TC_WALK = "{0}/{1}/{2}_{3}/graph_walk.json".format(root, intermediate, location_name, transport)
        self.IS_PATH = "{0}/{1}/is_path/{2}_{3}/".format(root, produced, location_name, transport)
        self.MINIMAL_TRAVEL_TIME_TC = "{0}/{1}/minimal_distance/{2}_{3}/".format(root, produced, location_name, transport)

        # output map
        self.OUT_TIME_MAP = "{0}/{1}/time_map_{2}_{3}.geojson".format(root, produced, location_name, transport)
        self.OUT_MUNTY_MAP = "{0}/{1}/maps/munty_map_{2}_{3}.geojson".format(root, produced, location_name, transport)
        self.OUT_STOP_MAP = "{0}/{1}/maps/stop_map_{2}_{3}.geojson".format(root, produced, location_name, transport)


# Parameters
class Parameters:
    def __init__(self,path: PATH):
        with (open(path.CONFIG, "r")) as conf:
            config = json.load(conf)
        self.PATH: PATH = path
        self.data_path = path.root
        self.__location_name = path.location_name
        self.__transport = path.transport
        self.__MAX_WALKING_TIME = config["max_walking_time"] # in min
        self.__WALKING_SPEED = config["walking_speed"]  # m/min
        self.__max_time = config["max_time"]  # min
        self.__map = None


        # self.__date = date
        # self.__start_time = start_time                        # from "00:00:00" to "25:59:59"
        # self.__end_time = end_time                          # from "00:00:00" to "25:59:59"
    def transport(self):
        return self.__transport

    def location_name(self):
        return self.__location_name

    def MAX_WALKING_TIME(self):
        return self.__MAX_WALKING_TIME

    def WALKING_SPEED(self):
        return self.__WALKING_SPEED

    def WALKING_SPEED_KM_H(self):
        return self.__WALKING_SPEED*60/1000

    def MAX_RADIUS(self):
        return (self.__MAX_WALKING_TIME / 60.0) * self.WALKING_SPEED_KM_H() / 6367.0  # todo check

    def distance_to_walking_time(self, dist_km):
        hours = dist_km / self.__WALKING_SPEED
        minutes = hours * 60
        seconds = minutes * 60
        return round(seconds)

    def MAX_TIME(self):
        return self.__max_time

    def MAP(self):
        if self.__map is None:
            self.__map = MyMapStop(self.PATH, self.MAX_WALKING_TIME(), self.WALKING_SPEED())
        return self.__map

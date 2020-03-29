import os
import datetime
import json

from Program.Data_manager._1_parse_gtfs import time_str_to_int, generate_output_for_gtfs
from Program.Data_manager._2_reduce_data import reduce_rsd_work, reduce_map, reduce_stop, reduce_parsed_gtfs
from Program.Data_manager._3_simplify import *
from Program.Data_manager._3b_compute_travels import *

# produce graph
from Program.Data_manager._4_walking_time import *
from Program.Data_manager._5_produce_extended_graph import *



class DataManager:
    root = "../../../Project/Data/"
    initial = "initial"
    intermediate = "intermediate"
    produced = "produced"

    tc = {"train_only" : ["sncb"], "bus_only" : ["stib", "tec", "delijn"]}
    #tc["train_bus"] = tc["train_only"] + tc["bus_only"]

    # Parameters
    class Parameters:
        def __init__(self, data_path, arrondisement,transport, max_walking_time, walking_speed):
            self.data_path = data_path
            self.__arrondissement = arrondisement
            self.__transport = transport
            self.__MAX_WALKING_TIME = max_walking_time  # in min # in seconds  #todo found units
            self.__WALKING_SPEED = walking_speed # in km/h #todo found units
            #self.__date = date
            #self.__start_time = start_time                        # from "00:00:00" to "25:59:59"
            #self.__end_time = end_time                          # from "00:00:00" to "25:59:59"


        def ARRODNISEMENT(self):
            return self.ARRODNISEMENT()

        def MAX_WALKING_TIME(self):
            return self.__MAX_WALKING_TIME

        def WALKING_SPEED(self):
            return self.__WALKING_SPEED

        def MAX_RADIUS(self):
            return (self.__MAX_WALKING_TIME / 3600.0) * self.__WALKING_SPEED / 6367.0 # todo check


    @staticmethod
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
        DataManager.root = data_path

        for repertoire in [DataManager.initial, DataManager.intermediate, DataManager.produced]:
            path = DataManager.root + repertoire
            if not os.path.exists(path):
                os.makedirs(path)

        #gtfs
        if not os.path.exists(DataManager.root + DataManager.initial + "/gtfs"):
            os.makedirs(DataManager.root + DataManager.initial + "/gtfs")

        # produced map
        if not os.path.exists(DataManager.root + DataManager.produced + "/maps"):
            os.makedirs(DataManager.root + DataManager.produced + "/maps")

        # produced minimal distance
        if not os.path.exists(DataManager.root + DataManager.produced + "/minimal_distance"):
            os.makedirs(DataManager.root + DataManager.produced + "/minimal_distance")

    @staticmethod
    def produce_data_belgium(data_path, date=datetime.date(2019, 12, 2), start_time=time_str_to_int("06:00:00"), end_time=time_str_to_int("10:30:00")):
        assert start_time <= end_time

        DataManager.root = data_path
        PATH_BELGIUM.set_up()

        if not os.path.exists(DataManager.root + DataManager.initial):
            print("You need to run make_data_structure first")
            raise Exception


        print("START: Belgium parse gtfs")
        # parse gtfs
        # produce the json format for each kind of transport in belgium
        stops_train = {}
        if not os.path.exists(PATH_BELGIUM.TRAIN_ONLY) or  not os.path.exists(PATH_BELGIUM.TRAIN_BUS):
            for tc in DataManager.tc["train_only"]:
                print(tc.upper())
                stops_train.update(generate_output_for_gtfs(DataManager.root + "gtfs/" + tc, tc, date, start_time, end_time))

            json.dump(stops_train, open(PATH_BELGIUM.TRAIN_ONLY, "w"))

        stops = {}
        if not os.path.exists(PATH_BELGIUM.BUS_ONLY) or not os.path.exists(PATH_BELGIUM.TRAIN_BUS):
            for tc in DataManager.tc["bus_only"]:
                print(tc.upper())
                stops.update(generate_output_for_gtfs(DataManager.root + "gtfs/" + tc,tc, date, start_time, end_time))

            json.dump(stops, open(PATH_BELGIUM.BUS_ONLY, "w"))

        if not os.path.exists(PATH_BELGIUM.TRAIN_BUS):
            stops.update(stops_train)
            json.dump(stops, open(PATH_BELGIUM.TRAIN_BUS, "w"))

        print("END: Belgium parse gtfs")

    @staticmethod
    def produce_data(data_path, locations, transport, max_walking_time, walking_speed):
        """

        :param data_path:
        :param locations: list of arrodisement
        :param transport: train_only, bus_only, train_bus
        :param max_walking_time: min
        :param walking_speed: km/h
        :param date:
        :param start_time:
        :param end_time:
        :return:
        """
        assert transport in ["train_only", "bus_only", "train_bus"]


        DataManager.root = data_path
        PATH_BELGIUM.set_up()
        PATH.set_up(data_path, locations, transport)

        parameter = DataManager.Parameters(data_path, locations, transport, max_walking_time, walking_speed)

        if not os.path.exists(PATH_BELGIUM.TRAIN_ONLY) or not os.path.exists(PATH_BELGIUM.BUS_ONLY) or not os.path.exists(PATH_BELGIUM.TRAIN_BUS):
            print("You need to run produce_data_belgium first")
            raise Exception

        path = DataManager.root + DataManager.intermediate + "/" + locations + "_" + transport
        if not os.path.exists(path):
            os.makedirs(path)

        refnis_list = reduce_rsd_work(locations)
        reduce_map(refnis_list)
        #reduce_pop()

        if transport == "train_only":
            stop_list = reduce_stop(PATH_BELGIUM.TRAIN_ONLY, refnis_list)
            #reducestop()
            reduce_parsed_gtfs(PATH_BELGIUM.TRAIN_ONLY, stop_list, out=PATH.TRANSPORT)
        elif transport == "bus_only":
            stop_list = reduce_stop(PATH_BELGIUM.BUS_ONLY, refnis_list)
            #reducestop()
            reduce_parsed_gtfs(PATH_BELGIUM.BUS_ONLY, stop_list, out=PATH.TRANSPORT)
        elif transport == "train_bus":
            stop_list = reduce_stop(PATH_BELGIUM.TRAIN_BUS, refnis_list)
            #reducestop()
            reduce_parsed_gtfs(PATH_BELGIUM.TRAIN_BUS, stop_list, out=PATH.TRANSPORT)

        #todo

    @staticmethod
    def load_data(data_path, arrondisement, transport):
        """

        :param data_path:
        :param arrondisement:
        :return:
        """
        #todo
        pass

    @staticmethod
    def update_walk_parameters(data_path, arrondisement, max_walking_time, walking_speed):
        """

        :param data_path:
        :param arrondisement:
        :param max_walking_time:
        :param walking_speed:
        :return:
        """
        #todo
        pass


class PATH_BELGIUM:
    # new method
    GTFS, BUS_ONLY, TRAIN_ONLY, TRAIN_BUS = None, None, None, None
    MAP_SHAPE, MAP_POP, RSD_WORK = None, None, None
    OUT_BELGIUM_MAP, OUT_TRAIN_LINES_MAP, OUT_BUS_LINES_MAP = None, None, None

    @staticmethod
    def set_up():
        # new method
        PATH_BELGIUM.GTFS = DataManager.root + DataManager.initial + "/gtfs/"
        PATH_BELGIUM.BUS_ONLY = DataManager.root + DataManager.intermediate + "/bus_only.json"
        PATH_BELGIUM.TRAIN_ONLY = DataManager.root + DataManager.intermediate + "/train_only.json"
        PATH_BELGIUM.TRAIN_BUS = DataManager.root + DataManager.intermediate + "/train_bus.json"

        # metric
        PATH_BELGIUM.MAP_SHAPE = DataManager.root + DataManager.initial + "/sh_statbel_statistical_sectors.geojson"
        PATH_BELGIUM.MAP_POP = DataManager.root + DataManager.initial + "/OPEN_DATA_SECTOREN_2011.csv"
        PATH_BELGIUM.RSD_WORK = DataManager.root + DataManager.initial + "/TU_CENSUS_2011_COMMUTERS_MUNTY.txt"

        # output map
        PATH_BELGIUM.OUT_BELGIUM_MAP = DataManager.root + DataManager.produced + "/maps/Belgium.geojson"
        PATH_BELGIUM.OUT_TRAIN_LINES_MAP = DataManager.root + DataManager.produced + "/maps/train_lines_belgium.geojson"
        PATH_BELGIUM.OUT_BUS_LINES_MAP = DataManager.root + DataManager.produced + "/maps/bus_lines_belgium.geojson"

class PATH:
    # new method
    TRANSPORT, SIMPLIFIED, WALKING = None, None, None

    # metric
    MAP_SHAPE, MAP_POP, RSD_WORK, TRAVEL, STOP_POSITION_LAMBERT = None, None, None, None, None

    # dynamic APSP
    GRAPH_TC, GRAPH_TC_WALK, MINIMAL_TRAVEL_TIME_TC = None, None, None

    # output map
    OUT_TIME_MAP, OUT_MUNTY_MAP, OUT_STOP_MAP = None, None, None

    @staticmethod
    def set_up(root, localisation, transport):
        # new method
        PATH.TRANSPORT = "{0}{1}/{2}_{3}.json".format(root,DataManager.intermediate, localisation, transport)
        PATH.SIMPLIFIED = "{0}{1}/{2}_{3}/simplified.json".format(root,DataManager.intermediate,localisation, transport)
        PATH.WALKING = "{0}{1}/{2}_{3}/distance_walking.json".format(root,DataManager.intermediate,localisation, transport)

        # metric
        PATH.MAP_SHAPE = "{0}{1}/{2}/sh_statbel_statistical_sectors.geojson".format(root,DataManager.intermediate,localisation)
        PATH.MAP_POP = "{0}{1}/{2}/OPEN_DATA_SECTOREN_2011.csv".format(root,DataManager.intermediate,localisation)
        PATH.RSD_WORK = "{0}{1}/{2}/TU_CENSUS_2011_COMMUTERS_MUNTY.txt".format(root,DataManager.intermediate,localisation)
        PATH.TRAVEL = "{0}{1}/{2}/travel_user.json".format(root,DataManager.intermediate,localisation)
        PATH.STOP_POSITION_LAMBERT = "{0}{1}/{2}/stop_lambert_{3}.json".format(root,DataManager.intermediate,localisation, transport)

        # dynamic APSP
        PATH.GRAPH_TC = "{0}{1}/{2}/graph_{3}.json".format(root,DataManager.intermediate,localisation, transport)
        PATH.GRAPH_TC_WALK = "{0}{1}/{2}/graph_{3}_walk.json".format(root,DataManager.intermediate,localisation, transport)
        PATH.MINIMAL_TRAVEL_TIME_TC = "{0}{1}/minimal_distance/{2}_{3}".format(root,DataManager.produced,localisation, transport)

        # output map
        PATH.OUT_TIME_MAP = "{0}{1}/time_map_{2}_{3}.geojson".format(root,DataManager.produced,localisation, transport)
        PATH.OUT_MUNTY_MAP = "{0}{1}/maps/munty_map_{2}_{3}.geojson".format(root,DataManager.produced,localisation, transport)
        PATH.OUT_STOP_MAP = "{0}{1}/maps/stop_map_{2}_{3}.geojson".format(root,DataManager.produced,localisation, transport)





if __name__ == '__main__':
    #DataManager.make_data_structure(DataManager.root)
    #"Arrondissement de Charleroi"
    pass
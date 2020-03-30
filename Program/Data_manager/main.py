import os
import datetime
import json

from Program.Data_manager.path_data import make_data_structure, PATH_BELGIUM, PATH

from Program.Data_manager._1_parse_gtfs import time_str_to_int, generate_output_for_gtfs
from Program.Data_manager._2_reduce_data import reduce_rsd_work, reduce_map, reduce_stop, reduce_parsed_gtfs
from Program.Data_manager._3_simplify import simplify_time
from Program.Data_manager._3b_compute_travels import extract_travel

# produce graph
from Program.Data_manager._4_produce_extended_graph import produce_exthended_graph
from Program.Data_manager._5_walking_time import *

# Parameters
class Parameters:
    def __init__(self, data_path, arrondisement, transport, max_walking_time, walking_speed):
        self.data_path = data_path
        self.__arrondissement = arrondisement
        self.__transport = transport
        self.__MAX_WALKING_TIME = max_walking_time  # in min
        self.__WALKING_SPEED = walking_speed  # m/min

        # self.__date = date
        # self.__start_time = start_time                        # from "00:00:00" to "25:59:59"
        # self.__end_time = end_time                          # from "00:00:00" to "25:59:59"

    def ARRODNISEMENT(self):
        return self.ARRODNISEMENT()

    def MAX_WALKING_TIME(self):
        return self.__MAX_WALKING_TIME

    def WALKING_SPEED(self):
        return self.__WALKING_SPEED

    def MAX_RADIUS(self):
        return (self.__MAX_WALKING_TIME / 3600.0) * self.__WALKING_SPEED / 6367.0  # todo check

    def distance_to_walking_time(self, dist_km):
        hours = dist_km / self.__WALKING_SPEED
        minutes = hours * 60
        seconds = minutes * 60
        return round(seconds)

class DataManager:
    root = None
    initial = "initial"
    intermediate = "intermediate"
    produced = "produced"

    tc = {"train_only" : ["sncb"], "bus_only" : ["stib", "tec", "delijn"]}
    #tc["train_bus"] = tc["train_only"] + tc["bus_only"]


    #@staticmethod
    #def make_data_structure(data_path):
    #    make_data_structure(data_path)

    @staticmethod
    def produce_data_belgium(data_path, date=datetime.date(2019, 12, 2), start_time=time_str_to_int("06:00:00"), end_time=time_str_to_int("10:30:00")):
        assert start_time <= end_time

        DataManager.root = data_path
        PATH_BELGIUM.set_up(data_path)

        if not os.path.exists(DataManager.root + "/" + DataManager.initial):
            print("You need to run make_data_structure first")
            raise Exception

        print(PATH_BELGIUM.GTFS)
        if not os.path.exists(PATH_BELGIUM.GTFS):
            print("You need to download gtfs data and put it in the gtfs folder")
            raise Exception


        print("START: Belgium parse gtfs")
        # parse gtfs
        # produce the json format for each kind of transport in belgium
        stops_train = {}
        if not os.path.exists(PATH_BELGIUM.TRAIN_ONLY) or  not os.path.exists(PATH_BELGIUM.TRAIN_BUS):
            for tc in DataManager.tc["train_only"]:
                print(tc.upper())
                stops_train.update(generate_output_for_gtfs(PATH_BELGIUM.GTFS+ "/" + tc, tc, date, start_time, end_time))

            json.dump(stops_train, open(PATH_BELGIUM.TRAIN_ONLY, "w"))

        stops = {}
        if not os.path.exists(PATH_BELGIUM.BUS_ONLY) or not os.path.exists(PATH_BELGIUM.TRAIN_BUS):
            for tc in DataManager.tc["bus_only"]:
                print(tc.upper())
                stops.update(generate_output_for_gtfs(PATH_BELGIUM.GTFS+ "/" + tc, tc, date, start_time, end_time))

            json.dump(stops, open(PATH_BELGIUM.BUS_ONLY, "w"))

        if not os.path.exists(PATH_BELGIUM.TRAIN_BUS):
            stops.update(stops_train)
            json.dump(stops, open(PATH_BELGIUM.TRAIN_BUS, "w"))

        print("END: Belgium parse gtfs")

    @staticmethod
    def reduce_data(data_path, locations, location_name, transport):
        """
        Les donnes sont reduites afin de ne considerer que les commune situe dans les arrondissement donne par locations
        Les stop et trajet considere ne seront que ceux ce situant dans ces communes
        :param data_path:
        :param locations: list of arrodisement
        :param locations: Nom utiliser pour representer la localisation choisie
        :param transport: train_only, bus_only, train_bus
        """
        assert transport in ["train_only", "bus_only", "train_bus"]

        DataManager.root = data_path
        PATH_BELGIUM.set_up(data_path)
        PATH.set_up(data_path, location_name, transport)

        parameter = Parameters(data_path, locations, transport, 0,0)



        #reduce data
        refnis_list = reduce_rsd_work(locations)
        reduce_map(refnis_list)

        if transport == "train_only":
            reduce_stop(PATH_BELGIUM.TRAIN_ONLY, refnis_list, "train_only", parameter)
            reduce_parsed_gtfs(PATH_BELGIUM.TRAIN_ONLY, out=PATH.TRANSPORT)
        elif transport == "bus_only":
            reduce_stop(PATH_BELGIUM.BUS_ONLY, refnis_list,"bus_only", parameter)
            reduce_parsed_gtfs(PATH_BELGIUM.BUS_ONLY, out=PATH.TRANSPORT)
        elif transport == "train_bus":
            reduce_stop(PATH_BELGIUM.TRAIN_BUS, refnis_list,"train_bus", parameter )
            reduce_parsed_gtfs(PATH_BELGIUM.TRAIN_BUS, out=PATH.TRANSPORT)


    @staticmethod
    def produce_data(data_path, location_name, transport,  max_walking_time, walking_speed):
        """

        :param data_path:
        :param location_name:
        :param transport: train_only, bus_only, train_bus
        :param max_walking_time: min
        :param walking_speed: received in km/h and converted in m/min
        :return:
        """
        assert walking_speed >= 0
        assert max_walking_time >= 0
        walking_speed = walking_speed * 1000 / 60

        PATH.set_up(data_path, location_name, transport)
        with (open(PATH.CONFIG, "w")) as conf:
            config = {"locations": location_name, "location_name": location_name, "transport": transport,
                      "max_walking_time": max_walking_time, "walking_speed": walking_speed}
            json.dump(config, conf)

        with open(PATH.TRANSPORT, "r") as tr:
            with open(PATH.SIMPLIFIED, "w") as s:
                json.dump(simplify_time(json.load(tr)),s)   # set time in min instead of seconds

        extract_travel(PATH.RSD_WORK, PATH.TRAVEL)   # 3b

        produce_exthended_graph(MAX_TIME=28 * 60)   # 28 car certaine donnees depasse 24h pour des raisons pratiques

        parameter = Parameters(data_path, location_name, transport, max_walking_time, walking_speed)
        if max_walking_time > 0:
            compute_stations_walking_time(param=parameter)
            compute_walking_edges()

        return parameter




    @staticmethod
    def load_data(data_path, location_name, transport):

        PATH.set_up(data_path, location_name, transport)
        with (open(PATH.CONFIG, "r")) as conf:
            config = json.load(conf)
        param = Parameters(data_path=data_path, arrondisement=location_name, transport=transport,
                           max_walking_time=config["max_walking_time"], walking_speed=config["walking_speed"])
        return param


if __name__ == '__main__':
    data_path = "/Users/DimiS/Documents/Gotta_go_fast/Project/Data"
    #make_data_structure(data_path)
    #DataManager.produce_data_belgium(data_path)
    DataManager.reduce_data(data_path, "Arrondissement de Malines","Malines", "train_only", 15, 5)
    DataManager.produce_data(data_path,"Malines", "train_only")
    #"Arrondissement de Charleroi"
    pass
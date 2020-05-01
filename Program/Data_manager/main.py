import os
import shutil
import datetime
import json

from Program.Data_manager.path import Parameters, make_data_structure, PATH_BELGIUM, PATH

from Program.Data_manager._1_parse_gtfs import time_str_to_int, generate_output_for_gtfs
from Program.Data_manager._2_reduce_data import reduce_rsd_work, reduce_map, reduce_pop_sector,reduce_stop, reduce_parsed_gtfs
from Program.Data_manager._3_simplify import simplify_time
from Program.Data_manager._3b_compute_travels import extract_travel

# produce graph
from Program.Data_manager._4_produce_extended_graph import produce_exthended_graph
from Program.Data_manager._5_walking_time import compute_stations_walking_time, compute_walking_edges


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
    def produce_data_belgium(data_path, date=datetime.date(2019, 12, 2), start_time=time_str_to_int("06:00:00"),
                             end_time=time_str_to_int("10:30:00")):
        assert start_time <= end_time

        DataManager.root = data_path
        path_Belgium = PATH_BELGIUM(data_path)

        if not os.path.exists(DataManager.root + "/" + DataManager.initial):
            print("You need to run make_data_structure first")
            raise Exception

        print(path_Belgium.GTFS)
        if not os.path.exists(path_Belgium.GTFS):
            print("You need to download gtfs data and put it in the gtfs folder")
            raise Exception

        print("START: Belgium parse gtfs")
        # parse gtfs
        # produce the json format for each kind of transport in belgium
        stops_train = {}
        if not os.path.exists(path_Belgium.TRAIN_ONLY) or  not os.path.exists(path_Belgium.TRAIN_BUS):
            for tc in DataManager.tc["train_only"]:
                print(tc.upper())
                stops_train.update(generate_output_for_gtfs(path_Belgium.GTFS+ "/" + tc, tc, date, start_time, end_time))

            json.dump(stops_train, open(path_Belgium.TRAIN_ONLY, "w"))

        stops = {}
        if not os.path.exists(path_Belgium.BUS_ONLY) or not os.path.exists(path_Belgium.TRAIN_BUS):
            for tc in DataManager.tc["bus_only"]:
                print(tc.upper())
                stops.update(generate_output_for_gtfs(path_Belgium.GTFS+ "/" + tc, tc, date, start_time, end_time))

            json.dump(stops, open(path_Belgium.BUS_ONLY, "w"))

        if not os.path.exists(path_Belgium.TRAIN_BUS):
            stops.update(stops_train)
            json.dump(stops, open(path_Belgium.TRAIN_BUS, "w"))

        print("END: Belgium parse gtfs")

    @staticmethod
    def reduce_data(data_path, locations, location_name, transport, data_path_Belgium=None):
        """
        Les donnes sont reduites afin de ne considerer que les commune situe dans les arrondissement donne par locations
        Les stop et trajet considere ne seront que ceux ce situant dans ces communes
        :param data_path:
        :param locations: list of arrodisement
        :param locations: Nom utiliser pour representer la localisation choisie
        :param transport: train_only, bus_only, train_bus
        """
        assert transport in ["train_only", "bus_only", "train_bus"]

        if data_path_Belgium is None : data_path_Belgium = data_path

        DataManager.root = data_path
        path_Belgium = PATH_BELGIUM(data_path_Belgium)
        path = PATH(data_path, location_name, transport)
        with (open(path.CONFIG, "w")) as conf:
            config = {"locations": location_name, "location_name": location_name, "transport": transport,
                      "max_walking_time": 0, "walking_speed": 0, "max_time": 28*60}
            json.dump(config, conf)

        parameter = Parameters(path)


        # reduce data
        print("reduce Census")
        refnis_list = reduce_rsd_work(path_Belgium, path, locations)
        print("reduce map")
        reduce_map(path_Belgium, path, refnis_list)
        print("reduce pop sector")
        reduce_pop_sector(path_Belgium, path, refnis_list)

        print("reduce stop")
        if transport == "train_only":
            reduce_stop(path_Belgium, path, path_Belgium.TRAIN_ONLY, refnis_list, "train_only", parameter)
            reduce_parsed_gtfs(path, path_Belgium.TRAIN_ONLY, out=path.TRANSPORT)
        elif transport == "bus_only":
            reduce_stop(path_Belgium, path, path_Belgium.BUS_ONLY, refnis_list,"bus_only", parameter)
            reduce_parsed_gtfs(path, path_Belgium.BUS_ONLY, out=path.TRANSPORT)
        elif transport == "train_bus":
            reduce_stop(path_Belgium, path, path_Belgium.TRAIN_BUS, refnis_list,"train_bus", parameter)
            reduce_parsed_gtfs(path, path_Belgium.TRAIN_BUS, out=path.TRANSPORT)

        os.remove(path.CONFIG)

    @staticmethod
    def produce_data(data_path, location_name, transport,  max_walking_time, walking_speed, MAX_TIME= 28 * 60):
        """

        :param data_path:
        :param location_name:
        :param transport: train_only, bus_only, train_bus
        :param max_walking_time: min
        :param walking_speed: received in km/h and converted in m/min
        :param MAX_TIME: 28*60 car certaine donnees depasse 24h pour des raisons pratiques
        :return:
        """
        assert walking_speed >= 0
        assert max_walking_time >= 0
        walking_speed = walking_speed * 1000 / 60

        path = PATH(data_path, location_name, transport)
        with (open(path.CONFIG, "w")) as conf:
            config = {"locations": location_name, "location_name": location_name, "transport": transport,
                      "max_walking_time": max_walking_time, "walking_speed": walking_speed, "max_time": MAX_TIME}
            json.dump(config, conf)

        with open(path.TRANSPORT, "r") as tr:
            with open(path.SIMPLIFIED, "w") as s:
                json.dump(simplify_time(json.load(tr)), s)   # set time in min instead of seconds

        extract_travel(path.RSD_WORK, path.TRAVEL)   # 3b

        produce_exthended_graph(PATH=path, MAX_TIME=MAX_TIME)

        parameter = Parameters(path)
        if max_walking_time > 0:
            compute_stations_walking_time(param=parameter)
            compute_walking_edges(path=path)
        else:
            shutil.copyfile(path.GRAPH_TC, path.GRAPH_TC_WALK)

        return parameter

    @staticmethod
    def load_data(data_path, location_name, transport):
        path = PATH(data_path, location_name, transport)
        param = Parameters(path)
        return param


if __name__ == '__main__':
    data_path = "/Users/DimiS/Documents/Gotta_go_fast/Project/Data"
    #make_data_structure(data_path)
    #DataManager.produce_data_belgium(data_path)
    DataManager.reduce_data(data_path, "Arrondissement de Malines","Malines", "bus_only")
    #DataManager.produce_data(data_path,"Malines", "train_only", 15, 5)
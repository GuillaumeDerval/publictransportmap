# This file contains the path for the data
class PATH_BELGIUM:

    localisation = "Belgium"
    transport = "train_only"  # "bus_only" "train_bus"

    # new method
    GTFS = "../../Data_initial/gtfs/"
    BUS_ONLY = "../../Data_intermediate/bus_only.json"
    TRAIN_ONLY = "../../Data_intermediate/train_only.json"
    TRAIN_BUS = "../../Data_intermediate/train_bus.json"
    TRANSPORT = "../../Data_intermediate/{}.json".format(transport)
    SIMPLIFIED = "../../Data_intermediate/{}_simplified.json".format(transport)
    WALKING = "../../Data_intermediate/distance_walking.json"

    # metric
    MAP_SHAPE = "../../Data_initial/sh_statbel_statistical_sectors.geojson"
    MAP_POP = "../../Data_initial/OPEN_DATA_SECTOREN_2011.csv"
    RSD_WORK = "../../Data_initial/TU_CENSUS_2011_COMMUTERS_MUNTY.txt"
    TRAVEL = "../../Data_intermediate/travel_user.json"
    STOP_POSITION_LAMBERT = "../../Data_intermediate/stop_lambert_{0}.json".format(transport)

    # dynamic APSP
    GRAPH = "../../Data_intermediate/graph.json"
    MINIMAL_TRAVEL_TIME_TC = "../../Data_produced/minimal_distance/"

    # output map
    OUT_TIME_MAP = "../../Data_produced/maps/time_map_belgium.geojson"
    OUT_MUNTY_MAP = "../../Data_produced/maps/munty_map_belgium.geojson"
    OUT_BELGIUM_MAP = "../../Data_produced/maps/Belgium.geojson"
    OUT_STOP_MAP = "data/maps/stop_map_belgium.geojson"
    OUT_TRAIN_LINES_MAP = "../../Data_produced/maps/train_lines_belgium.geojson"
    OUT_BUS_LINES_MAP = "../../Data_produced/maps/bus_lines_belgium.geojson"

class PATH_CHARLEROI:

    localisation = "Charleroi"
    transport = "train_only"        # "bus_only" "train_bus"

    # new method
    BUS_ONLY = "../../Data_intermediate/{0}/bus_only.json".format(localisation)
    TRAIN_ONLY = "../../Data_intermediate/{0}/train_only.json".format(localisation)
    TRAIN_BUS = "../../Data_intermediate/{0}/train_bus.json".format(localisation)
    TRANSPORT = "../../Data_intermediate/{0}/{1}.json".format(localisation, transport)
    SIMPLIFIED = "../../Data_intermediate/{0}/{1}_simplified.json".format(localisation, transport)
    WALKING = "../../Data_intermediate/{0}/distance_walking_{1}.json".format(localisation, transport)

    # metric
    MAP_SHAPE = "../../Data_intermediate/{0}/sh_statbel_statistical_sectors.geojson".format(localisation)
    MAP_POP = "../../Data_intermediate/{0}/OPEN_DATA_SECTOREN_2011.csv".format(localisation)
    RSD_WORK = "../../Data_intermediate/{0}/TU_CENSUS_2011_COMMUTERS_MUNTY.txt".format(localisation)
    TRAVEL = "../../Data_intermediate/{0}/travel_user.json".format(localisation)
    STOP_POSITION_LAMBERT = "../../Data_intermediate/{0}/stop_lambert_{1}.json".format(localisation,transport)

    # dynamic APSP
    GRAPH = "../../Data_intermediate/{0}/graph_{1}.json".format(localisation, transport)
    MINIMAL_TRAVEL_TIME_TC = "../../Data_produced/{0}/minimal_distance/".format(localisation)

    # output map
    OUT_TIME_MAP = "../../Data_produced/maps/time_map_{0}.geojson".format(localisation)
    OUT_MUNTY_MAP = "data/maps/munty_map_{0}.geojson".format(localisation)
    OUT_STOP_MAP = "data/maps/stop_map_{0}.geojson".format(localisation)


class PATH(PATH_CHARLEROI):
    pass

#path all data metric
'''
SHAPE = "../../my_program/data/sh_statbel_statistical_sectors.geojson"
POP = "../../my_program/data/OPEN_DATA_SECTOREN_2011.csv"
TRAVEL = "../../my_program/out_dir/travel_user.json"
TRAVEL_TIME = "../../produce/out/"
STOP_LIST = "../../my_program/out_dir/stop_lambert_pos.json"
OUT_TIME_MAP = "data/maps/time_map_belgium.geojson"
OUT_MUNTY_MAP = "data/maps/munty_map_belgium.geojson"
OUT_STOP_MAP = "data/maps/stop_map_belgium.geojson"
'''
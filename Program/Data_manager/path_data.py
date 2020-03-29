import os


root = None
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
    # new method
    GTFS, BUS_ONLY, TRAIN_ONLY, TRAIN_BUS = None, None, None, None
    MAP_SHAPE, MAP_POP, RSD_WORK, STOP_POSITION_LAMBERT = None, None, None, None
    OUT_BELGIUM_MAP, OUT_TRAIN_LINES_MAP, OUT_BUS_LINES_MAP = None, None, None

    @staticmethod
    def set_up(data_path):
        root = data_path
        # new method
        PATH_BELGIUM.GTFS = root + "/" + initial + "/gtfs/"
        PATH_BELGIUM.BUS_ONLY = root + "/" + intermediate + "/bus_only.json"
        PATH_BELGIUM.TRAIN_ONLY = root + "/" + intermediate + "/train_only.json"
        PATH_BELGIUM.TRAIN_BUS = root + "/" + intermediate + "/train_bus.json"

        # metric
        PATH_BELGIUM.MAP_SHAPE = root + "/" + initial + "/sh_statbel_statistical_sectors.geojson"
        PATH_BELGIUM.MAP_POP = root + "/" + initial + "/OPEN_DATA_SECTOREN_2011.csv"
        PATH_BELGIUM.RSD_WORK = root + "/" + initial + "/TU_CENSUS_2011_COMMUTERS_MUNTY.txt"
        PATH_BELGIUM.STOP_POSITION_LAMBERT = {  "train_only" : root + "/" + intermediate + "/stop_lambert_train_only.json",
                                                "bus_only": root + "/" + intermediate + "/stop_lambert_bus_only.json",
                                                "train_bus": root + "/" + intermediate + "/stop_lambert_train_bus.json"}

        # output map
        PATH_BELGIUM.OUT_BELGIUM_MAP = root + "/" + produced + "/maps/Belgium.geojson"
        PATH_BELGIUM.OUT_TRAIN_LINES_MAP = root + "/" + produced + "/maps/train_lines_belgium.geojson"
        PATH_BELGIUM.OUT_BUS_LINES_MAP = root + "/" + produced + "/maps/bus_lines_belgium.geojson"


class PATH:
    CONFIG = None
    # new method
    TRANSPORT, SIMPLIFIED, WALKING = None, None, None

    # metric
    MAP_SHAPE, MAP_POP, RSD_WORK, TRAVEL, STOP_POSITION_LAMBERT = None, None, None, None, None

    # dynamic APSP
    GRAPH_TC, GRAPH_TC_WALK, MINIMAL_TRAVEL_TIME_TC = None, None, None

    # output map
    OUT_TIME_MAP, OUT_MUNTY_MAP, OUT_STOP_MAP = None, None, None

    @staticmethod
    def set_up(data_path, localisation_name, transport):
        root = data_path

        path = root + "/" + intermediate + "/" + localisation_name + "_" + transport
        if not os.path.exists(path):
            os.makedirs(path)

        PATH.CONFIG = "{0}/{1}/{2}_{3}/config.json".format(root, intermediate, localisation_name, transport)

        # new method
        PATH.TRANSPORT = "{0}/{1}/{2}_{3}/transport.json".format(root, intermediate, localisation_name, transport)
        PATH.SIMPLIFIED = "{0}/{1}/{2}_{3}/simplified.json".format(root, intermediate, localisation_name, transport)
        PATH.WALKING = "{0}/{1}/{2}_{3}/distance_walking.json".format(root, intermediate, localisation_name, transport)

        # metric
        PATH.MAP_SHAPE = "{0}/{1}/{2}_{3}/map.geojson".format(root, intermediate, localisation_name, transport)
        PATH.MAP_POP = PATH_BELGIUM.MAP_POP
        PATH.RSD_WORK = "{0}/{1}/{2}_{3}/CENSUS_2011.txt".format(root, intermediate, localisation_name, transport)
        PATH.TRAVEL = "{0}/{1}/{2}_{3}/travel_user.json".format(root, intermediate, localisation_name,transport)
        PATH.STOP_POSITION_LAMBERT = "{0}/{1}/{2}_{3}/stop_lambert.json".format(root, intermediate, localisation_name, transport)

        # dynamic APSP
        PATH.GRAPH_TC = "{0}/{1}/{2}_{3}/graph.json".format(root, intermediate, localisation_name, transport)
        PATH.GRAPH_TC_WALK = "{0}/{1}/{2}_{3}/graph_walk.json".format(root, intermediate, localisation_name, transport)
        PATH.MINIMAL_TRAVEL_TIME_TC = "{0}/{1}/minimal_distance/{2}_{3}".format(root, produced, localisation_name, transport)

        # output map
        PATH.OUT_TIME_MAP = "{0}/{1}/time_map_{2}_{3}.geojson".format(root, produced, localisation_name, transport)
        PATH.OUT_MUNTY_MAP = "{0}/{1}/maps/munty_map_{2}_{3}.geojson".format(root, produced, localisation_name, transport)
        PATH.OUT_STOP_MAP = "{0}/{1}/maps/stop_map_{2}_{3}.geojson".format(root, produced, localisation_name, transport)



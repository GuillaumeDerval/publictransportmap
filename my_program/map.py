# manipulation de la carte de belgique
import json
from shapely.geometry import shape, GeometryCollection
from shapely.ops import cascaded_union, Point


class my_map:
    belgium_map = None

    def __init__(self, path = "data/tiny_data/sh_statbel_statistical_sectors.geojson"):
        self.__sector_map = {}
        self.__munty_map = {}
        self.__set_shape_sector(path)
        self.__set_shape_munty(path)
        my_map.belgium_map = self

    def __set_shape_sector(self,path):
        with open(path) as f:
            features = json.load(f)["features"]
            sector = {}  # key = refnis
            for elem in features:
                sector_id = elem["properties"]["CD_SECTOR"]
                sector[sector_id] = shape(elem["geometry"]).buffer(0)
        self.__sector_map = sector


    def __set_shape_munty(self, path):
        with open(path) as f:
              features = json.load(f)["features"]
              for elem in features:
                    refnis = str(elem["properties"]["CD_MUNTY_REFNIS"])
                    sector_id = str(elem["properties"]["CD_SECTOR"])
                    if refnis in self.__munty_map:
                        self.__munty_map[refnis]["shape"] = self.__munty_map[refnis]["shape"].union(shape(elem["geometry"]).buffer(0))
                        self.__munty_map[refnis]["sector_ids"].append(sector_id)
                    else:
                        self.__munty_map[refnis] = {"shape": shape(elem["geometry"]).buffer(0), "sector_ids" : [sector_id]}

    def get_shape_sector(self, sector_id):
        return self.__sector_map[sector_id]

    def get_shape_munty(self, refnis):
        return self.__munty_map[refnis]["shape"]

    def get_sector_ids(self, refnis_munty):
        return self.__munty_map[refnis_munty]["sector_ids"]

    def get_center_munty(self):
        munty_shapes = self.__munty_map
        munty_center = {}
        for refnis in munty_shapes:
            munty_center[refnis] = munty_shapes[refnis].centroid
            print("refnis",refnis, munty_shapes[refnis].centroid)
        return munty_center
# NOTE: buffer(0) is a trick for fixing scenarios where polygons have overlapping coordinates
#G = GeometryCollection([shape(feature["geometry"]).buffer(0) for feature in features])

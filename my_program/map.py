# manipulation de la carte de belgique
import json
import csv
from shapely.geometry import shape, GeometryCollection
from shapely.ops import cascaded_union, Point


class my_map:
    belgium_map = None

    @classmethod
    def get_map(cls, path_shape = None, path_pop = None):
        if my_map.belgium_map is None:
            #if (my_map.belgium_map.path_shape is not None and my_map.belgium_map.path_shape != path_shape) or (my_map.belgium_map.path_pop is not None  and my_map.belgium_map.path_pop != path_pop):
            my_map.belgium_map = my_map(path_shape, path_pop)
        return my_map.belgium_map

    def __init__(self, path_shape, path_pop ):
        self.__sector_map = {}
        self.__munty_map = {}
        self.path_shape = path_shape
        self.path_pop = path_pop

        self.__set_sector()
        self.__set_shape_munty()

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

    """def get_center_munty(self):
        munty_shapes = self.__munty_map
        munty_center = {}
        for refnis in munty_shapes:
            munty_center[refnis] = munty_shapes[refnis].centroid
            print("refnis",refnis, munty_shapes[refnis].centroid)
        return munty_center"""
# NOTE: buffer(0) is a trick for fixing scenarios where polygons have overlapping coordinates
#G = GeometryCollection([shape(feature["geometry"]).buffer(0) for feature in features])

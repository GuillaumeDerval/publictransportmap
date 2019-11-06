# manipulation de la carte de belgique
import json
from shapely.geometry import shape, GeometryCollection
from shapely.ops import cascaded_union, Point

def get_center_munty():
    with open("data/sh_statbel_statistical_sectors.geojson") as f:
      features = json.load(f)["features"]
      munty = {} #key = refnis
      for elem in features[:50]:
            refnis = elem["properties"]["CD_MUNTY_REFNIS"]
            if refnis in munty:
                munty[refnis].union(shape(elem["geometry"]).buffer(0))
            else:
                munty[refnis] = shape(elem["geometry"]).buffer(0)
      for refnis in munty:
          munty[refnis] = munty[refnis].centroid
          print(munty[refnis].centroid)
    return munty

# NOTE: buffer(0) is a trick for fixing scenarios where polygons have overlapping coordinates
#G = GeometryCollection([shape(feature["geometry"]).buffer(0) for feature in features])



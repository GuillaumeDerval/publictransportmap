from math import sqrt
from pyproj import Proj, transform


# Set of use-full function for conversion and distance


def WGS84_to_Lambert(point):
    """ IN: point : (longitude, latitude)
        OUT: (x,y) in Belgian lambert
    """
    in_proj = Proj(init='epsg:4326')
    out_proj = Proj(init='epsg:2154')
    return transform(in_proj, out_proj, point[0], point[1])


def Lambert_to_WGS84(point):
    """ IN: point : ((x,y) in Belgian lambert
        OUT: (longitude, latitude)
     """
    in_proj = Proj(init='epsg:2154')
    out_proj = Proj(init='epsg:4326')
    return transform(in_proj, out_proj, point[0], point[1])


def distance_Eucli(p1, p2):
    return sqrt(abs(p1[0]-p2[0])**2 + abs(p1[1]-p2[1]))


def distanceWGS84(p1, p2):
    #todo
    pass

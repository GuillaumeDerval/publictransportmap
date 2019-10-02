import bisect
import json
import math
import progressbar
import numpy as np
import sklearn.neighbors

WALKING_SPEED = 3.0 #in km/h
MAX_WALKING_TIME = 30*60 # in seconds
MAX_RADIUS = (MAX_WALKING_TIME/3600.0) * WALKING_SPEED / 6367.0

def distance_to_walking_time(dist_km):
    hours = dist_km / WALKING_SPEED
    minutes = hours*60
    seconds = minutes*60
    return round(seconds)

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees).
    Source: https://gis.stackexchange.com/a/56589/15183
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2.0)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2.0 * math.asin(math.sqrt(a))
    km = 6367.0 * c
    return km

def mean_latlon(points): #points is [(lon, lat)]
    points = [[math.radians(y) for y in x] for x in points]
    points = [(math.cos(lat)*math.cos(lon), math.cos(lat)*math.sin(lon), math.sin(lat)) for lon,lat in points]
    x,y,z = [sum([x[i] for x in points])/len(points) for i in range(3)]
    lon = math.atan2(y, x)
    hyp = math.sqrt(x * x + y * y)
    lat = math.atan2(z, hyp)
    return math.degrees(lon), math.degrees(lat)

class ParetoFront:
    def __init__(self, max_time):
        self.max_time = max_time
        self.s = []
        self.a = []

    def add(self, started_time, arrival_time):
        #if self.max_time < arrival_time - started_time:
        #    return False

        insertion_pos = bisect.bisect_left(self.s, started_time)
        if insertion_pos != len(self.s) and self.a[insertion_pos] <= arrival_time:
            ParetoFront.refused += 1
            return False

        restart_pos = min(bisect.bisect_left(self.a, arrival_time), insertion_pos)
        if insertion_pos != len(self.s) and self.s[insertion_pos] == started_time:
            insertion_pos += 1
        self.s = self.s[0:restart_pos] + [started_time] + self.s[insertion_pos:]
        self.a = self.a[0:restart_pos] + [arrival_time] + self.a[insertion_pos:]
        return True

    def is_in(self, started_time, arrival_time):
        pos = bisect.bisect_left(self.s, started_time)
        return pos != len(self.s) and self.s[pos] == started_time and self.a[pos] == arrival_time

    def best(self):
        return min([y-x for x, y in zip(self.s, self.a)]) if len(self.s) != 0 else self.max_time+1

    def print(self):
        print(list(zip(self.s, self.a)))

ParetoFront.refused = 0
ParetoFront.removed = 0
ParetoFront.added = 0

def test_pareto():
    p = ParetoFront(1000)
    p.add(1, 1)
    p.add(2, 2)
    p.add(3, 3)
    p.add(4, 4)
    p.add(5, 5)
    p.add(6, 6)

    p.print()
    p.add(1, 2)
    p.print()
    p.add(2, 3)
    p.print()
    p.add(2, 2)
    p.print()
    p.add(2, 0)
    p.print()
    p.add(5, 4)
    p.print()

def decaround(x):
    return int(round(x / 10)*10)
import csv
import json
from shapely.geometry import shape, mapping, LineString
#import geojson
from geojson import dump
import numpy as np


# map creation : geojson
A1 = {'type': 'feature', 'properties': {'CD_SECTOR': "A1", 'CD_MUNTY_REFNIS' : 'A'},
      'geometry': {'type': 'Polygon', 'coordinates':[[[1000., 1000.], [1000., 2000.],[2000., 2000.], [2000., 1000.],[1000., 1000.]]]}}


A2shape = shape({'type': 'Polygon',
        'coordinates': [[[0., 0.],[0., 3000.], [3000., 3000.], [3000., 0.],[0., 0.]]]})
A2shape = A2shape.difference(shape(A1['geometry']))
A2 = {'type': 'feature', 'properties': {'CD_SECTOR': "A2", 'CD_MUNTY_REFNIS' : 'A'},
      'geometry': mapping(A2shape)}

B1 = {'type': 'feature', 'properties': {'CD_SECTOR': "B1", 'CD_MUNTY_REFNIS' : 'B'},
       'geometry': {'type': 'Polygon', 'coordinates':
           [[[3000., 0.],[3000., 2000.], [5000., 2000.],[5000., 0.], [3000., 0.]]]}}

C1 = {'type': 'feature', 'properties': {'CD_SECTOR': "C1", 'CD_MUNTY_REFNIS' : 'C'},
       'geometry': {'type': 'Polygon', 'coordinates':
           [[[1000., 3000.],[1000., 4000.], [3000., 4000.],[3000., 3000.], [1000., 3000.]]]}}
C2 = {'type': 'feature', 'properties': {'CD_SECTOR': "C2", 'CD_MUNTY_REFNIS' : 'C'},
       'geometry': {'type': 'Polygon', 'coordinates':
           [[[1000., 4000.],[1000., 6000.], [3000., 6000.],[3000., 4000.], [1000., 4000.]]]}}
C3 = {'type': 'feature', 'properties': {'CD_SECTOR': "C3", 'CD_MUNTY_REFNIS' : 'C'},
       'geometry': {'type': 'Polygon', 'coordinates':
           [[[1000., 6000.],[1000., 7000.], [3000., 7000.],[3000., 6000.], [1000., 6000.]]]}}

D1 = {'type': 'feature', 'properties': {'CD_SECTOR': "D1", 'CD_MUNTY_REFNIS' : 'D'},
       'geometry': {'type': 'Polygon', 'coordinates':
           [[[5000., 4000.],[7000., 4000.], [7000., 6000.],[5000., 6000.], [5000., 4000.]]]}}

feature_collection = [A1,A2, B1,C1,C2,C3,D1]  # key = refnis

out = {
        'type': 'FeatureCollection',
        "features": feature_collection
    }

with open('data/smallmap.geojson', 'w') as w:
    dump(out, w)


# Time of travel1
y = np.array([0,35,-1,30,10,25], dtype=np.int)
np.save("data/out/S0.npy", y.astype(np.int16))
y = np.array([35,0,-1,5,25,40], dtype=np.int)
np.save("data/out/S1.npy", y.astype(np.int16))
y = np.full((6,), -1, dtype=np.int)
np.save("data/out/S2.npy", y.astype(np.int16))
y = np.array([30,5,-1,0,20,35], dtype=np.int)
np.save("data/out/S3.npy", y.astype(np.int16))
y = np.array([60,25,-1,20,0,15], dtype=np.int)
np.save("data/out/S4.npy", y.astype(np.int16))
y = np.array([25,40,-1,35,15,0], dtype=np.int)
np.save("data/out/S5.npy", y.astype(np.int16))


# Time of travel2
y = np.array([0,35,20,30,10,25,-1], dtype=np.int)
np.save("data/out2/S0.npy", y.astype(np.int16))
y = np.array([5,0,-1,5,25,40, 30], dtype=np.int)
np.save("data/out2/S1.npy", y.astype(np.int16))
y = np.full((7,), -1, dtype=np.int)
np.save("data/out2/S2.npy", y.astype(np.int16))
y = np.array([30,5,-1,0,20,35, -1], dtype=np.int)
np.save("data/out2/S3.npy", y.astype(np.int16))
y = np.array([60,25,-1,20,0,5, -1], dtype=np.int)
np.save("data/out2/S4.npy", y.astype(np.int16))
y = np.array([25,40,-1,35,15,0,-1], dtype=np.int)
np.save("data/out2/S5.npy", y.astype(np.int16))
y = np.array([-1,30,-1,35,-1,-1,0], dtype=np.int)
np.save("data/out2/S6.npy", y.astype(np.int16))
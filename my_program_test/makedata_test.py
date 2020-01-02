import csv
import json
from shapely.geometry import shape, mapping, LineString
#import geojson
from geojson import dump



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



feature_collection = [A1,A2, B1,C1,C2,C3]  # key = refnis

out = {
        'type': 'FeatureCollection',
        "features": feature_collection
    }

with open('data/smallmap.geojson', 'w') as w:
    dump(out, w)


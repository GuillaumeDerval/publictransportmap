import os
import json
from shapely.geometry import shape, mapping, LineString
#import geojson
from geojson import dump
import numpy as np
from Program.Data_manager.main import DataManager

# Structure creation
if not os.path.exists("./Data_test"):
    os.makedirs("./Data_test")
if not os.path.exists("./Data_test/intermediate"):
    os.makedirs("./Data_test/intermediate")
if not os.path.exists("./Data_test/intermediate/small1_train_only"):
    os.makedirs("./Data_test/intermediate/small1_train_only")
if not os.path.exists("./Data_test/intermediate/small2_train_only"):
    os.makedirs("./Data_test/intermediate/small2_train_only")
if not os.path.exists("./Data_test/produced"):
    os.makedirs("./Data_test/produced")
if not os.path.exists("./Data_test/produced/minimal_distance"):
    os.makedirs("./Data_test/produced/minimal_distance")


def small_map():
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

    feature_collection = [A1, A2, B1, C1, C2, C3, D1]  # key = refnis

    out = {
            'type': 'FeatureCollection',
            "features": feature_collection
        }

    with open('./Data_test/intermediate/small1_train_only/map.geojson', 'w') as w:
        dump(out, w)


def artifical_travel_time():

    path1 = "./Data_test/produced/minimal_distance/small1_mc"
    path2 = "./Data_test/produced/minimal_distance/small2_mc"
    if not os.path.exists(path1):
        os.makedirs(path1)
    if not os.path.exists(path2):
        os.makedirs(path2)

    # Time of travel1
    y = np.array([0,35,-1,30,10,25], dtype=np.int)
    np.save(path1 + "/S0.npy", y.astype(np.int16))
    y = np.array([35,0,-1,5,25,40], dtype=np.int)
    np.save(path1 + "/S1.npy", y.astype(np.int16))
    y = np.full((6,), -1, dtype=np.int)
    np.save(path1 + "/S2.npy", y.astype(np.int16))
    y = np.array([30,5,-1,0,20,35], dtype=np.int)
    np.save(path1 + "/S3.npy", y.astype(np.int16))
    y = np.array([60,25,-1,20,0,15], dtype=np.int)
    np.save(path1 + "/S4.npy", y.astype(np.int16))
    y = np.array([25,40,-1,35,15,0], dtype=np.int)
    np.save(path1 + "/S5.npy", y.astype(np.int16))


    # Time of travel2
    y = np.array([0,35,20,30,10,25,-1], dtype=np.int)
    np.save(path2 + "/S0.npy", y.astype(np.int16))
    y = np.array([5,0,-1,5,25,40, 30], dtype=np.int)
    np.save(path2 + "/S1.npy", y.astype(np.int16))
    y = np.full((7,), -1, dtype=np.int)
    np.save(path2 + "/S2.npy", y.astype(np.int16))
    y = np.array([30,5,-1,0,20,35, -1], dtype=np.int)
    np.save(path2 + "/S3.npy", y.astype(np.int16))
    y = np.array([60,25,-1,20,0,5, -1], dtype=np.int)
    np.save(path2 + "/S4.npy", y.astype(np.int16))
    y = np.array([25,40,-1,35,15,0,-1], dtype=np.int)
    np.save(path2 + "/S5.npy", y.astype(np.int16))
    y = np.array([-1,30,-1,35,-1,-1,0], dtype=np.int)
    np.save(path2 + "/S6.npy", y.astype(np.int16))

#TODO other files

#medium
DataManager.reduce_data("./Data_test","Arrondissement de Dixmude", "medium","train_only", "./../Data")
DataManager.produce_data("./Data_test","medium","train_only", 15, 5)

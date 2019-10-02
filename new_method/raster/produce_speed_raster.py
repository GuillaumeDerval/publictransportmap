import math

import rasterio

import orjson
import numpy as np
from utils import WALKING_SPEED
from pyproj import CRS, Transformer
import datetime

WSG84 = CRS.from_epsg(4326)
Lambert = CRS.from_epsg(3812)
proj = Transformer.from_crs(WSG84.geodetic_crs, Lambert)


graph = orjson.loads(open('../../produce/out.json').read())
idx_to_name = graph["idx_to_name"]
name_to_idx = {x: y for y, x in enumerate(idx_to_name)}

data = orjson.loads(open("../../produce/train_bus_simplified.json").read())

source_idx = "sncbS8814001"
source_lat = data[source_idx]["lat"]
source_lon = data[source_idx]["lon"]
source_x, source_y = proj.transform(source_lat, source_lon)
print(source_x, source_y)

with rasterio.open('sncbS8814001.tif') as dataset:
    print("Reading raster")
    time_in_hours = dataset.read(1)/(60.0)

    speed = np.copy(time_in_hours)

    x, y = np.where(time_in_hours > 0)
    todo = np.stack(dataset.transform * np.stack([y, x])).transpose()

    print("Computing distance/time")
    for i in range(len(x)):
        p_x, p_y = todo[i,:]
        dist_in_kilometers = math.sqrt((p_x-source_x)**2 + (p_y - source_y)**2)/1000.0
        speed[x[i], y[i]] = dist_in_kilometers / time_in_hours[x[i], y[i]]

    print("Outputting raster")
    profile = dataset.profile
    profile.update(
        dtype=rasterio.float32,
        count=1,
        compress='lzw')
    with rasterio.open('sncbS8814001.speed.tif', 'w', **profile) as dst:
        dst.write(speed.astype(rasterio.float32), 1)
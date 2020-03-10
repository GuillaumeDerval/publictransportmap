import rasterio

from Program.new_method_guillaume.raster.cython.fast_resolver import resolve

import orjson
import numpy as np
from pyproj import CRS, Transformer
import datetime

WSG84 = CRS.from_epsg(4326)
Lambert = CRS.from_epsg(3812)
proj = Transformer.from_crs(WSG84.geodetic_crs, Lambert)


graph = orjson.loads(open('../../produce/out.json').read())
idx_to_name = graph["idx_to_name"]
name_to_idx = {x: y for y, x in enumerate(idx_to_name)}

data = orjson.loads(open("../../produce/train_bus_simplified.json").read())


def produce_raster(infile, outfile):
    dists = np.load(infile)

    points = np.array([
        [*proj.transform(data[x]["lat"], data[x]["lon"]), dists[name_to_idx[x]]] for x in data if dists[name_to_idx[x]] >= 0
    ], dtype=np.float64)

    with rasterio.open('../../gadm34_BEL_shp/lambert_grid.tif') as dataset:
        print("Reading raster")
        band1 = dataset.read(1)

        print("Computing todo list")
        x,y = np.where(band1 > 0.5)
        todo = np.stack(dataset.transform * np.stack([y, x])).transpose()

        print("Computing neighbors")
        print(todo.shape)
        cur = datetime.datetime.now()
        to_be_processed = todo.shape[0]
        out = resolve(points, todo[0:to_be_processed, :])
        print(datetime.datetime.now() - cur)

        print("Outputting raster")
        cur = datetime.datetime.now()
        for i in range(to_be_processed):
            band1[x[i], y[i]] = out[i]/6.0 #put it in minutes
        print(datetime.datetime.now() - cur)

        profile = dataset.profile
        profile.update(
            dtype=rasterio.float32,
            count=1,
            compress='lzw')
        with rasterio.open(outfile, 'w', **profile) as dst:
            dst.write(band1.astype(rasterio.float32), 1)

produce_raster("../../produce/out/{}.npy".format("sncbS8814001"), "{}.tif".format("sncbS8814001"))
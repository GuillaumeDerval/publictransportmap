import os
import shutil
import subprocess
import json
import tempfile
import numpy as np

from utils import WALKING_SPEED
from multiprocessing import Pool
from Program.path import PATH

def process(dist_file, out_file, border_shape, idx_to_name, complete_data):
    tmpdir = tempfile.mkdtemp()

    real_time = np.load(dist_file)

    out = {
        'type': 'FeatureCollection',
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        complete_data[idx_to_name[x]]["lon"],
                        complete_data[idx_to_name[x]]["lat"]
                    ]
                },
                "properties": {
                    "name": complete_data[idx_to_name[x]]["name"],
                    "idx": idx_to_name[x],
                    "time": int(real_time[x])
                }
            }
            for x in range(real_time.shape[0])
            if real_time[x] >= 0
        ]
    }

    with open(os.path.join(tmpdir, "orig_distfile.json"), 'w') as geojson_distfile:
        json.dump(out, geojson_distfile)

    levels = list(range(10, 481, 10))

    c = ["ogr2ogr", os.path.join(tmpdir, "result_blambert.json"), "-t_srs", "EPSG:3812", os.path.join(tmpdir, "orig_distfile.json"), "-f", "GeoJSON"]
    #print(" ".join(c))
    subprocess.call(c)

    content = json.load(open(os.path.join(tmpdir, 'result_blambert.json')))

    old_level = None

    for l in levels:
        #print(l)
        features = []

        if old_level is not None:
            delta_t = (l - old_level)
            distance = (float(delta_t) / 60) * WALKING_SPEED*1000 #convert to meters
            distance = max(distance, 0.01)

            geometry = json.load(open(os.path.join(tmpdir,"{}_d.json".format(old_level))))["features"][0]["geometry"]
            if geometry["type"] == "Polygon":
                features.append({
                        "type": "Feature",
                        "geometry": geometry,
                        "properties": {"v": distance}
                    }
                )
            else:
                for poly in geometry["coordinates"]:
                    features.append({
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": poly},
                        "properties": {"v": distance}
                    })

        for entry in content["features"]:
            if entry["properties"]["time"] <= l*6:
                delta_t = l*6 - entry["properties"]["time"]
                distance = (float(delta_t)/360)*WALKING_SPEED*1000 #convert to meters
                distance = max(distance, 10.0)
                features.append({"type": "Feature", "geometry": entry["geometry"], "properties": {"v": distance}})

        content["features"] = list(filter(lambda entry: entry["properties"]["time"] > l*6, content["features"]))

        #print("length", len(features))
        json.dump({
            'type': 'FeatureCollection',
            'name': 'level', "features":features,
            'crs': {'type': 'name', "properties": {"name": "urn:ogc:def:crs:EPSG::3812"}}},
            open(os.path.join(tmpdir,"{}.json".format(l)), "w"))

        sql = "SELECT Simplify(ST_Union(ST_Buffer(geometry, v)), 10.0), {} as l FROM level".format(l)
        c = ["ogr2ogr", os.path.join(tmpdir,"{}_d.json".format(l)), os.path.join(tmpdir,"{}.json".format(l)), "-f", "GeoJSON", "-dialect" ,"sqlite", "-sql", sql]
        #print(" ".join(c))
        subprocess.call(c)

        if old_level is not None:
            content_ogrvrt = """<OGRVRTDataSource>
            <OGRVRTLayer name="top">
                    <SrcLayer>level</SrcLayer>
                    <SrcDataSource>{}</SrcDataSource>
            </OGRVRTLayer>
            <OGRVRTLayer name="bottom">
                    <SrcLayer>level</SrcLayer>
                    <SrcDataSource>{}</SrcDataSource>
            </OGRVRTLayer>
        </OGRVRTDataSource>""".format(os.path.join(tmpdir, "{}_d.json".format(l)), os.path.join(tmpdir, "{}_d.json".format(old_level)))

            with open(os.path.join(tmpdir, 'temp_ogrvrt.ogrvrt'), 'w') as v:
                v.write(content_ogrvrt)

            sql = "SELECT ST_DIFFERENCE(top.geometry, bottom.geometry), top.l as l FROM top LEFT JOIN bottom"
            c = ["ogr2ogr", os.path.join(tmpdir,"{}_c.json".format(l)), os.path.join(tmpdir, 'temp_ogrvrt.ogrvrt'), "-f", "GeoJSON", "-dialect", "sqlite",
                 "-sql", sql]
            #print(" ".join(c))
            subprocess.call(c)
        else:
            open(os.path.join(tmpdir,"{}_c.json".format(l)), "w").write(open(os.path.join(tmpdir,"{}_d.json".format(l))).read())
        old_level = l


    subprocess.call(["ogr2ogr", os.path.join(tmpdir,"levels.shp"), os.path.join(tmpdir,"{}_c.json".format(levels[len(levels)-1]))])
    for l in reversed(levels):
        if l != levels[len(levels)-1]:
            subprocess.call(["ogr2ogr", "-update", "-append", os.path.join(tmpdir,"levels.shp"), os.path.join(tmpdir,"{}_c.json".format(l))])

    subprocess.call(["ogr2ogr", "-clipsrc", border_shape, os.path.join(tmpdir,"levels_clipped.shp"), os.path.join(tmpdir,"levels.shp")])
    subprocess.call(["ogr2ogr", os.path.join(tmpdir,"levels_clipped.json"), os.path.join(tmpdir,"levels_clipped.shp"), "-f", "GeoJSON", "-t_srs", "EPSG:4326"])
    subprocess.call(["geo2topo", "--id-property", "none", "-p", "name=l", "-o", out_file, "--", os.path.join(tmpdir,"levels_clipped.json")])

    shutil.rmtree(tmpdir)


bordershape = "../gadm34_BEL_shp/border_blambert.shp"
data = json.loads(open(PATH.GRAPH_TC).read())
idx_to_name = data["idx_to_name"]

def process_thread(x):
    distfile = "{0}{1}.npy".format(PATH.MINIMAL_TRAVEL_TIME_TC, x)
    outfile = "{0}{1}.json".format(PATH.MINIMAL_TRAVEL_TIME_TC, x)
    data = json.load(open(PATH.SIMPLIFIED))
    process(distfile, outfile, bordershape, idx_to_name, data)
    return x

pool = Pool(94)
for x in pool.imap_unordered(process_thread, [x for x in idx_to_name if x.startswith("sncb")]):
    print(x)
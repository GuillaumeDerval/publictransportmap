import json
import subprocess
from multiprocessing import Pool
import os.path
from Program.path import PATH

data = json.loads(open(PATH.GRAPH_TC).read())
idx_to_name = data["idx_to_name"]

def process_thread(x):
    if os.path.exists("{0}{1}.geo.json".format(PATH.MINIMAL_TRAVEL_TIME_TC,x)):
        a = subprocess.call(["topo2geo", "-i", "0}{1}.json".format(PATH.MINIMAL_TRAVEL_TIME_TC, x), "levels_clipped={0}{1}.geo.json".format(PATH.MINIMAL_TRAVEL_TIME_TC, x)])
        b = subprocess.call(["tippecanoe", "--simplification=10", "--simplify-only-low-zooms", "--detect-shared-borders",
                         "--output-to-directory= produce/tiles/{}".format(x), "-Z7", "-z12", "--drop-densest-as-needed",
                         "--no-tile-compression", "--layer=distance", "{0}{1}.geo.json".format(PATH.MINIMAL_TRAVEL_TIME_TC, x)])
        return a == 0 and b == 0, x

pool = Pool(1)
for status, x in pool.imap_unordered(process_thread, [x for x in idx_to_name if x.startswith("sncb")]):
    print(x, status)
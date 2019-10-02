import json
import subprocess
from multiprocessing import Pool
import os.path

data = json.loads(open('../produce/out.json').read())
idx_to_name = data["idx_to_name"]

def process_thread(x):
    if os.path.exists("../produce/out/{}.geo.json".format(x)):
        a = subprocess.call(["topo2geo", "-i", "../produce/out/{}.json".format(x), "levels_clipped=../produce/out/{}.geo.json".format(x)])
        b = subprocess.call(["tippecanoe", "--simplification=10", "--simplify-only-low-zooms", "--detect-shared-borders",
                         "--output-to-directory=../produce/tiles/{}".format(x), "-Z7", "-z12", "--drop-densest-as-needed",
                         "--no-tile-compression", "--layer=distance", "../produce/out/{}.geo.json".format(x)])
        return a == 0 and b == 0, x

pool = Pool(1)
for status, x in pool.imap_unordered(process_thread, [x for x in idx_to_name if x.startswith("sncb")]):
    print(x, status)
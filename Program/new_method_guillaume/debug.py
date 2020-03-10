import orjson
import numpy as np

graph = orjson.loads(open('../produce/out.json').read())
name_to_idx = {x:y for y,x in enumerate(graph["idx_to_name"])}

dists = np.load('../produce/out/sncbS8814001.npy')

# Marloie TRAIN
idx = name_to_idx["sncbS8864345"]
print("TRAIN", dists[idx])

# Marloie BUS
idx = name_to_idx["tecX902afb"]
print("GARE QUAI 2", dists[idx])
idx = name_to_idx["tecX937aeb"]
print("QUAI DE L'OURTHE", dists[idx])

idx = name_to_idx["tecX736aaa"]
print("BUS 2", dists[idx])
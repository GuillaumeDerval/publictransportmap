import json
import numpy as np

from utils import haversine

pos = json.load(open('../train_bus.json'))
print(sum(len(x["nei"]) for x in pos.values()))
idx_to_name = json.load(open('../out.json'))["idx_to_name"]
data = json.load(open('ottignies.json'))

base_lat = pos["sncbS8811601"]["lat"]
base_lon = pos["sncbS8811601"]["lon"]

x = [haversine(pos[idx_to_name[y]]["lon"], pos[idx_to_name[y]]["lat"], base_lon, base_lat)/(data[y]/(6*60)) for y in range(len(data)) if data[y] > 0]
print(np.mean(x))
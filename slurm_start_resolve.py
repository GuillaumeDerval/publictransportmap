import json
import random
import subprocess

data = json.load(open("train_bus.json"))
sncb = list(filter(lambda x: x.startswith("sncb"),data.keys()))
random.shuffle(sncb)
print(len(sncb))
for n in sncb:
    args = ["sbatch", "slurm_start_resolve.sh", str(data[n]["lat"]), str(data[n]["lon"]), "dist/{}.json".format(n)]
    print(data[n]["name"])
    print(args)
    #subprocess.call(args)
    break
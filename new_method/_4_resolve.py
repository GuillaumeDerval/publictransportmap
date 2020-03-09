import json
import numpy as np
import datetime
from multiprocessing import Pool


"""
in  :   /produce/out.json
        /produce/distance_walking.json
out :        
"""


data = json.loads(open('../produce/out.json').read())
walking_time = json.loads(open('../produce/distance_walking.json').read())
print("JSON parsed")

idx_to_name = data["idx_to_name"]
name_to_idx = {x: i for i, x in enumerate(idx_to_name)}
graph = {int(x): y for x, y in data["graph"].items()}
MAX_TIME = data["max_time"]
used_times = data["used_times"]
data = None


#gare la meme structure que walking time mais remplace le  nom du stop par son id
#{stop_id1 : [(distance_time, stop_id_2), ...], ...}
walking_time = {name_to_idx[x]: [(a, name_to_idx[b]) for a, b in y] for x, y in walking_time.items()}

# Generate graph points
#used_times_next_time = [[-1] * MAX_TIME for x in used_times]
used_times_next_time = np.full(shape=(len(used_times), MAX_TIME), fill_value=-1, dtype=np.int)
print("Array created")

def gen_next_time(idx):
    last_time = -1
    for x in used_times[idx]:
        used_times_next_time[idx][last_time+1:x+1] = x
        #for y in range(last_time+1, x+1):
        #    used_times_next_time[idx][y] = x
        last_time = x


def get_node_next_time(idx, t):
    if t >= MAX_TIME:
        return -1
    return used_times_next_time[idx,t]


for x in range(len(used_times)):
    gen_next_time(x)

print("Processing done")

def compute_for_node(idx):  #idx =  stop_id (only sncb)
    todo = [[] for _ in range(0, MAX_TIME)]

    distance = {x: np.int(-1) for x in graph} #un noeud  x pour chaque stop_time.

    for time in used_times[idx]:   #time(in 10sec)
        distance[idx*MAX_TIME+time] = np.int(0) # distance to reach the source node(idx*MAX_TIME+time) = 0
        todo[time].append(idx*MAX_TIME+time)

    min_dist_to_node = np.full((len(idx_to_name),), -1, dtype=np.int)
    min_dist_to_node[idx] = 0

    for cur_time in range(0, MAX_TIME):
        # we use this while loop rather than a for one as new entries may be added during computation
        # as sometime departure from a node == arrival to the next one ;-(
        todo_idx = 0
        while todo_idx != len(todo[cur_time]):
            next = todo[cur_time][todo_idx]
            next_node_idx = next // MAX_TIME
            bdist = distance[next]
            if bdist == -1 : print( "bdist = -1")

            #perme dobtenir la distance minimum pour chaque stop (ie. dist min pour tout les temps)
            if min_dist_to_node[next_node_idx] == -1 or min_dist_to_node[next_node_idx] > bdist:
                min_dist_to_node[next_node_idx] = bdist

            #Tester les trajet à pied
            for delta_t, nei_idx in walking_time[next_node_idx]:
                dist_from_source = bdist + delta_t
                if min_dist_to_node[nei_idx] == -1 or min_dist_to_node[nei_idx] > dist_from_source:
                    min_dist_to_node[nei_idx] = dist_from_source
                # find node immediately after and walk to it
                reached_at = cur_time + delta_t
                t = get_node_next_time(nei_idx, reached_at)
                if t != -1:
                    nei = nei_idx*MAX_TIME+t
                    new_delta_t = t - cur_time
                    if distance[nei] == -1:
                        todo[t].append(nei)
                        distance[nei] = bdist + new_delta_t
                    elif distance[nei] > bdist + new_delta_t:
                        distance[nei] = bdist + new_delta_t

            for nei in graph[next]:
                nei_time = nei % MAX_TIME
                delta_t = nei_time - cur_time
                if distance[nei] == -1:
                    todo[nei_time].append(nei)
                    distance[nei] = bdist + delta_t
                elif distance[nei] > bdist + delta_t:
                    if nei_time == cur_time:
                        todo[nei_time].append(nei) # recompute if we are at the current time.
                    distance[nei] = bdist + delta_t

            todo_idx += 1

        todo[cur_time] = None

    return min_dist_to_node

def process_thread(x):
    start = datetime.datetime.now()
    y = compute_for_node(name_to_idx[x])
    np.save("../produce/out/" + x + ".npy", y.astype(np.int16))
    return x, datetime.datetime.now() - start


# process_thread("sncb8015345")
pool = Pool(94)
#for x in pool.imap_unordered(process_thread, [x for x in name_to_idx if x.startswith("sncb")]):
for x in pool.imap_unordered(process_thread, [x for x in name_to_idx]):
    print(x)

print("end 4bis_resolve.py")
#print(process_thread("sncbS8814001"))
#print(process_thread("tecX902afb"))
#print(process_thread("tecX660afa"))

#start = datetime.datetime.now()
#y = compute_for_node(name_to_idx["sncbS8811601"])
#print(datetime.datetime.now()-start)
#np.save("ottignies.npy", y)
#open('ottignies.json', 'w').write(orjson.dumps(y))
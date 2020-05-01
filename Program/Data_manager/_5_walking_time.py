import json

from Program.DistanceAndConversion import distance_Eucli, WGS84_to_Lambert


def compute_stations_walking_time(param):
    """
        For each paire of station located at less than MAX_RADIUS, add an edge between the 2 stations.
        the time of this edge correspond to a straight ahead walk between the stations

        in  : PATH.SIMPLIFIED
        out : PATH.WALKING
    """
    with open(param.PATH.SIMPLIFIED) as s:
        data = json.load(s)

    with open(param.PATH.STOP_POSITION_LAMBERT) as s:
        stop_lamb = json.load(s)

    names = list(data.keys())
    out = {x: [] for x in names}
    for org in names:
        for dest in names:
            if org not in stop_lamb:
                if "x" in data[org] and "y" in data[org]: stop_lamb[org] = (data[org]["x"], data[org]["y"])
                else: stop_lamb[org] = WGS84_to_Lambert((data[org]["lon"], data[org]["lat"]))
            if dest not in stop_lamb:
                if "x" in data[dest] and "y" in data[dest]: stop_lamb[dest] = (data[dest]["x"], data[dest]["y"])
                else: stop_lamb[dest] = WGS84_to_Lambert((data[dest]["lon"], data[dest]["lat"]))

            walking_time = distance_Eucli(stop_lamb[org], stop_lamb[dest]) / param.WALKING_SPEED()
            if walking_time <= param.MAX_WALKING_TIME() and org != dest:
                # print("compute station time: ", org, " to ",dest, " trav time", walking_time)
                out[org].append((walking_time, dest))

    out = {x: sorted(y)[0:50] for x, y in out.items()}
    with open(param.PATH.WALKING, "w") as walk_file:
        json.dump(out, walk_file)


# Lancer _2_compute_walking_time.py before this program

# Sophie


def compute_walking_edges(path):
    # Ce programme à pour but d'ajouter des edge a graph.json
    # Ces nouvelle arret representerons les trajet faisable a pied
    with open(path.WALKING) as walk_file:
        walk = json.load(walk_file)

    with open(path.GRAPH_TC) as graph_file:
        graph_tc = json.load(graph_file)

    idx_to_name = graph_tc["idx_to_name"]
    name_to_idx = {x: i for i, x in enumerate(idx_to_name)}
    max_time = graph_tc["max_time"]
    used_time = graph_tc["used_times"]
    graph_walk_tc = graph_tc.copy()

    for org_name in walk.keys():
        org_idx = name_to_idx[org_name]
        org_time = used_time[org_idx]          # Time are already sorted
        org_time.sort()
        for walk_time, dest_name in walk[org_name]:
            if dest_name != org_name:
                dest_idx = name_to_idx[dest_name]
                dest_time = used_time[dest_idx]     # Time are already sorted
                dest_time.sort()
                for o_time in org_time:
                    i = 0
                    while i < len(dest_time) and dest_time[i] < o_time + walk_time:
                        i += 1
                    if i < len(dest_time):
                        # print("static: ",org_name, o_time, " to ", dest_name, dest_time[i])
                        graph_walk_tc["graph"][str(org_idx*max_time + o_time)].append(dest_idx*max_time + dest_time[i])

    with open(path.GRAPH_TC_WALK, "w") as out:
        json.dump(graph_walk_tc, out)

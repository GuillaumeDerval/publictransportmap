import json
import time
from Program.Data_manager.path_data import PATH
# from collections import deque


"""
    rajoute des connection pour pouvoir faire un trajet qui s'etant sur 2 jour ???
    
    transformation des noeud : passage de nom, temps  à un seul chiffre ????

    in  : PATH.SIMPLIFIED
    out : PATH.GRAPH
"""
def produce_exthended_graph(MAX_TIME):


    print("--- Loading data")
    data = json.load(open(PATH.SIMPLIFIED))

    #A chaque nom de stop associe un nombre et vice-versa
    idx_to_name = list(data.keys())
    name_to_idx = {x: i for i, x in enumerate(idx_to_name)}
    #print(name_to_idx)

    #walking_time = json.load(open(PATH.WALKING))
    #walking_time = {name_to_idx[x]: [(a, name_to_idx[b]) for a,b in y] for x, y in walking_time.items()}

    def wtf(c, b):
        raise Exception("wtf")

    #change le format des donnee : {id:[(id_nei, departure_time, arrival_time), ...], ...}
    data = {name_to_idx[x]: [(name_to_idx[a], b, (c if c >= b else wtf(c, b))) for a,b,c in y["nei"] if 0 <= b < MAX_TIME and 0 <= c < MAX_TIME] for x, y in data.items()}
    #change le format des donnee : [[(id_nei, departure_time, arrival_time), ...]] L'index correspond au stop d'origine
    data = [data[x] for x in range(0, len(idx_to_name))]


    #Cree une liste qui  pour chaque stop :
    #     cree un set qui contient tout les temps pour lequel un  TC arrive ou part de ce stop
    print("--- Computing nodes to create")
    used_times = [set() for _ in range(0, len(idx_to_name))]
    for source, y in enumerate(data):
        for dest, start, end in y:
            used_times[source].add(start)
            used_times[dest].add(end)

    #base_used_times = used_times
    #used_times = [set() for _ in range(0, len(idx_to_name))]
    #for source, times in enumerate(base_used_times):
    #    for wt, dest in walking_time[source]:
    #        for bt in times:
    #            used_times[dest].add(bt+wt)
    #    used_times[source] = used_times[source].union(base_used_times[source])

    print("NB ORIG NODES {}".format(len(data)))
    print("NB GRAPH NODES {}".format(sum([len(y) for y in used_times])))



    def process_nodes(data):
        """
        Les donnee sont mise sous une forme transformable en graph (matrice d'adjacance)
        -> chaque noeud regroup l'id du stop et les temps
        :param data:
        :return:
        """
        def process_node(name, content):
            connections = sorted(content, key=lambda x: x[1])  # sort by start time
            possible_times = sorted(used_times[name])
            c_id = 0

            for p_id, time in enumerate(possible_times):
                nei = []

                #arret representant une connection
                while c_id != len(connections) and connections[c_id][1] == time:
                    new_connect = connections[c_id][0] * MAX_TIME + connections[c_id][2]
                    if new_connect not in nei:
                        nei.append(new_connect)
                    c_id += 1

                #arret representant le passage d'un temps à un autre (rester sur place)
                if p_id + 1 != len(possible_times):
                    new_connect = name * MAX_TIME + possible_times[p_id + 1]
                    if new_connect not in nei:
                        nei.append(new_connect)

                yield ((name * MAX_TIME + time), nei)

        d = dict()
        for name, content in enumerate(data):
            for x, y in process_node(name, content):
                d[x] = y
        return d



    print("--- Computing graph")
    print(time.time())
    graph = process_nodes(data)
    print(time.time())

    # print("--- Computing toposort")
    #
    # def toposort():
    #     entering = {x: 0 for x in graph}
    #     for x,y in graph.items():
    #         for z in y:
    #             entering[z] += 1
    #
    #     empty = deque(x for x, y in entering.items() if y == 0)
    #     topo = []
    #     while len(empty) != 0:
    #         node = empty.pop()
    #         topo.append(node)
    #         for z in graph[node]:
    #             entering[z] -= 1
    #             if entering[z] == 0:
    #                 empty.append(z)
    #
    #     error = [x for x in entering if entering[x] != 0]
    #     assert len(error) == 0
    #     return topo
    #
    # print(time.time())
    # topo = toposort()
    # print(time.time())

    print("--- Saving")
    json.dump({"idx_to_name": idx_to_name, "max_time": MAX_TIME, #"topo": topo,
               "graph": graph, "used_times": [list(sorted(x)) for x in used_times]
               }, open(PATH.GRAPH_TC, 'w'))

    print("--- Done")
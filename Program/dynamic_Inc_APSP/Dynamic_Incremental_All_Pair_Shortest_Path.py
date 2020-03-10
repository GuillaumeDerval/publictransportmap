from collections import deque
from Program.dynamic_Inc_APSP.Data_structure_reversible import *
import json
#from dynamic_Inc_APSP.Data_structure import *
from Program.path import PATH

"""Ce code est base sur les algorithmes proposé dans l'article  Faster Incremental All-pairs Shortest Paths"""


class Dynamic_APSP:
    def __init__(self, path=PATH.GRAPH):
        with open(path) as file:
            out = json.loads(file.read())
        self.graph = Graph(out)
        self.idx_to_name = out["idx_to_name"]
        self.name_to_idx = {x: i for i, x in enumerate(self.idx_to_name)}
        self.max_time = out["max_time"]
        self.used_time = out["used_times"]
        assert len(self.used_time) == len(self.idx_to_name) == len(self.name_to_idx)
        #sort used_time by time
        for used in self.used_time:
            used.sort()

        self.path = PathPresence(self.graph, self.max_time)
        self.distance = Distance(self.name_to_idx, self.idx_to_name, self.max_time, self.used_time, self.path)

        # reversible state -> record change
        self.__change_log = []
        self.__stack_log = []

    def add_isolated_vertex(self, stop_name: str, time: int):
        if stop_name in self.name_to_idx:
            idx = self.name_to_idx[stop_name]
            z = idx * self.max_time + time
            if time in self.used_time[idx]:
                return idx
            else:
                self.used_time[idx].append(time)
                self.__change_log.append(("add_time", stop_name, time))
        else:
            idx = len(self.name_to_idx)
            self.idx_to_name.append(stop_name)
            self.name_to_idx[stop_name] = idx
            z = idx * self.max_time + time
            self.used_time.append([time])
            self.__change_log.append(("add_name", stop_name))
            self.__change_log.append(("add_time", stop_name, time))

        self.graph.add_vertex(z)
        self.path.add_vertex(z)
        self.distance.up_to_date = False

        return idx

    def add_edge(self, u_stop_name, u_time, v_stop_name, v_time):
        assert v_time >= u_time
        self.distance.up_to_date = False

        u_id = self.add_isolated_vertex(u_stop_name, u_time)
        v_id = self.add_isolated_vertex(v_stop_name, v_time)
        u = u_id * self.max_time + u_time
        v = v_id * self.max_time + v_time

        # w = v % self.__max_time - u % self.__max_time
        self.graph.add_edge(u, v)
        # 4 cas sont possibles lors de l'ajout d'aret :

        # cas 1 : u->v doesn't impact the rest of the graph
        if self.graph.in_degree(u) == 0 and self.graph.out_degree(v) == 0:
            self.path.set_is_path(u, v, True)

        # cas 2 : no path to u
        elif self.graph.in_degree(u) == 0:
            # if path v-> . then dist(u, . ) = dist(v,.) + dist(u,v)
            self.path.or_in_place(u, v)

        # cas 3 : no path continue from v
        elif self.graph.out_degree(v) == 0:
            # for node x :compute dist v a partir de dist(.,u)
            for x in self.graph.vertex:
               is_path_u = self.path.is_path(x, u)
               if is_path_u:
                   self.path.set_is_path(x, v, True)

        # cas 4 : neither u neither v is a leaf
        else:
            self.__APSP_edge(self.path, self.graph, u, v)

    def add_vertex(self, z_stop_id, z_time, z_name, Z_in, Z_out):
        self.distance.up_to_date = False
        # todo
        raise Exception("unimplemented")

    def dist(self, s_name: str, d_name: str) -> float:
        """
        Return the minimal distance between u_name and v_name
        """
        return self.distance.dist(s_name, d_name)

    def dist_from(self, s_name : str) -> list:
        """
        Return the list of the minimal distance from source  s (id)
        """
        return self.distance.dist_from(s_name)

    def hard_save_distance(self, out_directory_path=PATH.MINIMAL_TRAVEL_TIME_TC):
        self.distance.hard_save(out_directory_path)

    def hard_save_is_reachable(self, out_directory_path=PATH.MINIMAL_TRAVEL_TIME_TC):
        self.path.hard_save(out_directory_path)

    def hard_save_graph(self, out_path=PATH.GRAPH):
        with open(out_path, 'w') as out_file:
            json.dump({"idx_to_name": self.idx_to_name, "max_time": self.max_time,
                       "graph": self.graph.adj_matrix, "used_times": self.used_time
                       }, out_file)

    def save(self):
        self.graph.save()
        self.path.save()
        self.distance.save()

        self.__stack_log.append(self.__change_log)
        self.__change_log = []

    def restore(self):
        self.graph.restore()
        self.path.restore()
        self.distance.restore()

        self.__change_log.reverse()
        for log in self.__change_log:
            if log[0] == "add_name":
                self.name_to_idx.pop(log[1])
                self.idx_to_name.pop()
                self.used_time.pop()
            elif log[0] == "add_time":
                idx = self.name_to_idx[log[1]]
                self.used_time[idx].remove(log[2])
            else:
                raise Exception("Unhandeled log")

        self.__change_log = self.__stack_log.pop()

    def get_changes(self):
        """
        Return the change done from the last save
        retourne l'ensemble de nouvelle valeur de is_reach, leur stop_name est indique par les cle du dictionnaire
        (new_value, old_value)
        :return: A dictionnary : {"size": (new_number_of_stop, old_number of stop),
                                  "added_stop_name" = [added_stop_name1 , ...]
                                  "change_distance": {org_name : {dest_name : (new_dist, old_dist)}}
        """
        changes = self.distance.get_changes()
        old_size = changes["size"][1]
        new_stop_name = self.idx_to_name[old_size:]
        changes["added_stop_name"] = new_stop_name
        return changes


    #################################################################################################################

    @staticmethod
    def __find_affected_sources(path : PathPresence, graph : Graph, u :int, v : int):
        """
        Find affected sources
        Suit l'algo 4
        :param u:
        :param v:
        :return:
        """
        S = []  # affected source
        if not path.is_path(u, v):  # w < self.dist(u,v)
            Q = deque()
            Q.append(u)
            graph.vis[u] = True
            while len(Q) > 0:
                x = Q.popleft()
                for z in graph.reversed_adj_matrix[x]:
                    if not graph.vis[z] and not path.is_path(z, v) and path.is_path(z, u):  # .dist(z, v) > self.dist(z,u) + w
                        Q.append(z) # Q.appendleft(z)
                        graph.vis[z] = True
                        S.append(z)

            graph.vis = {v: False for v in graph.vertex}  # Reset vis(·) to false
        return S

    @staticmethod
    def __APSP_edge(path: PathPresence, graph: Graph, u: int, v: int):
        """
        Ajout non trivial d'une arete dans le graph
        :param graph: a Data_Structure graph
        :param u: number of the node
        :param v: number of the node
        :return:
        """
        # ajout d'un edge entre 2 vertex dejà existant u,v:
        # - w est defini par la difference de temps entre u et v
        # - si il existait deja un moyen de joindre v à patir de u , dist(u,v) = difference de temps entre u et v = w
        # - mis à jour inutile si il existe deja un chemin entre u et v
        # - METTRE A JOUR UNIQUEMENT SSI DIST(U,V) = -1

        # algo 1

        if not path.is_path(u, v):
            S, P = {}, {}
            S[v] = Dynamic_APSP.__find_affected_sources(path, graph, u, v)
            path.set_is_path(u, v, True)
            Q = deque()
            P[v] = v
            Q.append(v)
            y = -1
            graph.vis[v] = True
            while len(Q) > 0:
                y = Q.popleft()
                # update distances for source nodes
                #if len(S[P[y]]) > 0:
                for x in S.get(P[y],[]):
                    if not path.is_path(x, y) and path.is_path(x, u) and path.is_path(v, y):
                        path.set_is_path(x, y, True)
                        if y != v:
                            if y not in S: S[y] = [x]
                            else: S[y].append(x)

                # enqueue all neighbors that get closer to u
                for w in graph.adj_matrix[y]:
                    if not graph.vis[w] and not path.is_path(u, w) and path.is_path(v, w) and path.is_path(v, y):
                        path.set_is_path(u, w, True)
                        Q.append(y)
                        Q.append(w)
                        graph.vis[w] = True
                        P[w] = y

    @staticmethod
    def __APSP_edge_set(path: PathPresence, graph: Graph, u: int, v: int):
        """
        Ajout non trivial d'une arete dans le graph
        :param graph: a Data_Structure graph
        :param u: number of the node
        :param v: number of the node
        :return:
        """
        # ajout d'un edge entre 2 vertex dejà existant u,v:
        # - w est defini par la difference de temps entre u et v
        # - si il existait deja un moyen de joindre v à patir de u , dist(u,v) = difference de temps entre u et v = w
        # - mis à jour inutile si il existe deja un chemin entre u et v
        # - METTRE A JOUR UNIQUEMENT SSI DIST(U,V) = -1

        # algo 1

        if not path.is_path(u, v):
            S, P = {}, {}
            S[v] = Dynamic_APSP.__find_affected_sources(path, graph, u, v)
            path.set_is_path(u, v, True)
            Q = deque()
            P[v] = set()
            P[v].add(v)
            Q.append(v)
            y = -1
            graph.vis[v] = True
            while len(Q) > 0:
                y = Q.popleft()
                # update distances for source nodes
                print(P[y])
                for pred in P[y]:
                    for x in S[pred]:
                        if not path.is_path(x, y) and path.is_path(x, u) and path.is_path(v, y):
                            path.set_is_path(x, y, True)
                            if y != v:
                                if not y in S: S[y] = []
                                S[y].append(x)


                # enqueue all neighbors that get closer to u
                for w in graph.adj_matrix[y]:
                    if not graph.vis[w] and not path.is_path(u, w) and path.is_path(v, w) and path.is_path(v, y):
                        path.set_is_path(u, w, True)
                        Q.append(y)
                        Q.append(w)
                        graph.vis[w] = True
                        if w not in P: P[w] = set()
                        P[w].add(y)

    def __APSP_vertex(self,graph, z, Z_in, Z_out):
        # todo algo 5
        raise Exception("unimplemented")




if __name__ == '__main__':
    print("start")
    print("creation data structure + graph")
    APSP = Dynamic_APSP()
    print("creation is_path + initialisation")
    APSP.initialisation()
    print("add vertex")
    APSP.add_isolated_vertex("d",30)
    print("add vertex2")
    APSP.add_isolated_vertex("c", 90)
    print("add supid edge d30 -> c90")
    APSP.add_edge("d",30,"c",90)
    print("add edge b10 -> c90")
    APSP.add_edge("b", 10, "c", 90)
    print("add edge e0 -> b10")
    APSP.add_edge("e", 0, "b", 10)
    print("add edge b10 -> d30")
    APSP.add_edge("b", 10, "d", 30)
    print("finish")
    #{"idx_to_name": ["a", "b", "c"], "max_time": 100, "graph": {"0": [110,170, 270, 50],"50" : [170,270],"110": [120], "120":[50,170],"170":[],"270":[] }, "used_times": [[10,50],  [110,120,170], [270] ]}

    #{"idx_to_name": ["a", "b", "c","d","e"], "max_time": 100,
  #"graph": {"0": [110,170, 270, 50],"50" : [170,270],"110": [120,290,330], "120":[50,170],"170":[],"270":[],"290": [],"330":[290],"400":[110] },
  #"used_times": [[10,50],  [110,120,170], [270,290], [330],[400]]}



# reflexion
# Si on veut rester coehrent avec se qui a été fait precedament lorsqu'on veut ajouter une arrete (entre id1, id2),
# on  cree potentiellement 2 moment de temps t1, t2 et donc 2 nouveau vertex u = id1*max + t1 et v = id2*max + t2


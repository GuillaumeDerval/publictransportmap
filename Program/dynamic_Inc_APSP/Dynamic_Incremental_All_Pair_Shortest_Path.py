from collections import deque
from Program.dynamic_Inc_APSP.Data_structure_reversible import *
import json
import heapq
#from dynamic_Inc_APSP.Data_structure import *
from Program.path import PATH, PARAMETERS
from Program.map import my_map
from Program.distance_and_conversion import distance_Eucli

"""Ce code est base sur les algorithmes proposé dans l'article  Faster Incremental All-pairs Shortest Paths"""


class Dynamic_APSP:
    def __init__(self, path=PATH.GRAPH_TC, mapmap = None):
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

        if mapmap is not None: self.map = mapmap
        else: self.map = my_map.get_map()

        # reversible state -> record change
        self.__change_log = []
        self.__stack_log = []

    def __add_isolated_vertex(self, stop_name: str, time: int, position: (float, float)):
        if stop_name in self.name_to_idx:
            idx = self.name_to_idx[stop_name]
            z = idx * self.max_time + time
            if time in self.used_time[idx]:
                return idx
            else:
                self.used_time[idx].append(time)
                self.__change_log.append(("add_time", stop_name, time))
        else:
            assert position is not None
            idx = len(self.name_to_idx)
            self.idx_to_name.append(stop_name)
            self.map.add_stop((stop_name, position))
            self.name_to_idx[stop_name] = idx
            z = idx * self.max_time + time
            self.used_time.append([time])
            self.__change_log.append(("add_name", stop_name))
            self.__change_log.append(("add_time", stop_name, time))

        self.graph.add_vertex(z)
        self.path.add_vertex(z)
        self.distance.up_to_date = False

        return idx

    def add_vertex(self, z_name, z_time, z_position, z_stop_in=[], z_stop_out=[]):
        """

        :param z_name:
        :param z_time:
        :param z_position: peut etre None si le stop_time etait deja cree
        :param z_stop_in:  [(name_in1, time_in1),...] name_in should be a already generated stop
        :param z_stop_out: [(name_out1, time_out1),...] name_out should be a already generated stop
        :return:
        """

        self.distance.up_to_date = False

        z_idx = self.__add_isolated_vertex(z_name, z_time, z_position)
        z = z_idx * self.max_time + z_time

        if z_name in self.name_to_idx and z_time in self.used_time[self.name_to_idx[z_name]]:
            # algo don't work, add edge one after the other
            for name_in, time_in in z_stop_in:
                self.add_edge(name_in, time_in, z_name, z_time)
            for name_out, time_out in z_stop_out:
                self.add_edge(z_name, z_time, name_out, time_out)

        else:
            assert z_position is not None

            # walking : find each node reachable thanks to walk
            reachable_stop = self.map.get_reachable_stop_pt(z_position)
            walk_in = []
            walk_out = []
            for walk_name, walk_pos in reachable_stop:
                walk_idx = self.name_to_idx[walk_name]
                walking_time = distance_Eucli(z_position, walk_pos) / PARAMETERS.WALKING_SPEED()

                i = len(self.used_time[walk_idx])
                while self.used_time[walk_idx][i] + walking_time > z_time:
                    i -= 1
                walk_in.append((walk_name, self.used_time[walk_idx][i], None))

                i = 0
                while self.used_time[walk_idx][i] < z_time + walking_time:
                    i += 1
                walk_out.append((walk_name, self.used_time[walk_idx][i], None))


            # add vertex to the graph structure
            for s_name, s_time in z_stop_in:
                assert s_time <= z_time
                s_id = self.__add_isolated_vertex(s_name, s_time,None)
                s = s_id * self.max_time + s_time
                self.graph.add_edge(s, z)

            for d_name, d_time in z_stop_in:
                assert d_time >= z_time
                d_id = self.__add_isolated_vertex(d_name, d_time, None)
                d = d_id * self.max_time + d_time
                self.graph.add_edge(z, d)

            # conversion name, time, pos -> node
            z_in = [self.name_to_idx[n] * self.max_time + t for n, t in z_stop_in + walk_in]
            z_out = [self.name_to_idx[n] * self.max_time + t for n, t in z_stop_out + walk_out]

            self.__APSP_vertex(z, z_in, z_out)

    def add_edge(self, u_stop_name, u_time,  v_stop_name, v_time,u_position=None, v_position=None):  #todo tester l'efficacité de separer en plusieur cas
        assert v_time >= u_time
        self.distance.up_to_date = False

        u_id = self.__add_isolated_vertex(u_stop_name, u_time, u_position)
        v_id = self.__add_isolated_vertex(v_stop_name, v_time, v_position)
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

    def hard_save_graph(self, out_path=PATH.GRAPH_TC):
        with open(out_path, 'w') as out_file:
            json.dump({"idx_to_name": self.idx_to_name, "max_time": self.max_time,
                       "graph": self.graph.adj_matrix, "used_times": self.used_time
                       }, out_file)

    def save(self):
        self.graph.save()
        self.path.save()
        self.distance.save()
        self.map.save()
        #todo save new positions

        self.__stack_log.append(self.__change_log)
        self.__change_log = []

    def restore(self):
        self.graph.restore()
        self.path.restore()
        self.distance.restore()
        self.map.restore()

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
                                  "added_stop_name": [added_stop_name1 , ...]
                                  "change_distance": {org_name : {dest_name : (new_dist, old_dist)}}
        """
        changes = self.distance.get_changes()
        old_size = changes["size"][1]
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
                #print(P[y])
                for pred in P[y]:
                    for x in S[pred]:
                        if not path.is_path(x, y) and path.is_path(x, u) and path.is_path(v, y):
                            path.set_is_path(x, y, True)
                            if y != v:
                                if y not in S: S[y] = []
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


    def __APSP_vertex(self, z, Z_in, Z_out):
        path: PathPresence = self.path
        graph: Graph = self.graph
        z_time = z * self.max_time

        S, P = {}, {}
        S[z] = []
        PQ = []     # priority queue
        heapq.heappush(PQ, (0, z))
        while len(PQ) > 0:
            d_xz, x = heapq.heappop(PQ)
            for q in graph.reversed_adj_matrix[x]:
                if not path.is_path(q,z) and path.is_path(q ,x):
                    path.set_is_path(q, z, True)
                    d_qz = z_time - (q % self.max_time)
                    heapq.heappush(PQ, (d_qz, q))
                    S[z].append(q)

        heapq.heappush(PQ, (0, z))
        while len(PQ) > 0:
            d_zy, y = heapq.heappop(PQ)
            if y != z:
                for pred in P[y]:
                    for x in S[pred]:
                        if not path.is_path(x,y) and path.is_path(x,z): # always true : path.is_path(z,y):
                            path.set_is_path(x,y, True)
                            if y not in S: S[y] = []
                            S[z].append(x)

            for w in graph.adj_matrix[y]:
                if not path.is_path(z, w) and path.is_path(y,w):
                    d_zw = (w % self.max_time) - z_time
                    heapq.heappush(d_zw, w)
                    if w not in P: P[w] = set()
                    P[w].add(y)



# reflexion
# Si on veut rester coehrent avec se qui a été fait precedament lorsqu'on veut ajouter une arrete (entre id1, id2),
# on  cree potentiellement 2 moment de temps t1, t2 et donc 2 nouveau vertex u = id1*max + t1 et v = id2*max + t2


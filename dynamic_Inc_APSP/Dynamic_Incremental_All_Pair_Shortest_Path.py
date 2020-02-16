from collections import deque
import my_program.path as PATH
from dynamic_Inc_APSP.Data_structure import *
import numpy as np

"""Ce code est base sur les algorithmes proposé dans l'article  Faster Incremental All-pairs Shortest Paths"""



class Dynamic_APSP:
    def __init__(self, path = PATH.OUT):
        out = json.loads(open(path).read())
        self.graph = Graph(out)
        self.idx_to_name = out["idx_to_name"]
        self.name_to_idx = {x: i for i, x in enumerate(self.idx_to_name)}
        #self.distance = Distance(self.idx_to_name, self.name_to_idx)      # todo verifier si probleme de mise a jour ici
        self.path = Path_presence(self.graph.vertex)
        self.__max_time = out["max_time"]
        self.__used_node = out["used_nodes"]

    def initialisation(self):
        """
        Lance le calcul pour savoir si il existe un chemin entre chaque paire de noeud
        :return:
        """
        # Idee : partir des noeud ayant les temps les plus grand
        #        Les noeud atteingnable par un noeud x sont
        #                   x (lui-meme) et
        #                   tout les noeud atteignable à partir d'un de ces voisin (y tq x-> y in edge)

        # Pour chaque noeud x in Node.sort(decreasing time) :
        #   is_reach[x][x] = True
        #   for nei in X_out:
        #           is_reach[x] = is_reach[x] or is reach[nei]
        node = self.graph.vertex
        node.sort(key = lambda x : x % self.__max_time, reverse = True)
        for x in node:
            self.path.set_is_path(x,x,True)
            for nei in self.graph.adj_matrix[x]:
                path_x = self.path.is_path_from(x)
                np.bitwise_or(path_x, self.path.is_path_from(nei), out = path_x, dtype=np.bool)

    def add_isolated_vertex(self, stop_name, time):
        if stop_name in self.name_to_idx:
            id = self.name_to_idx[stop_name]
            self.__used_node[id].add(time)
        else:
            id = len(self.name_to_idx) +1
            self.idx_to_name.append(stop_name)
            self.name_to_idx[stop_name] = id
            self.__used_node.append(set(time))
        z = id*self.__max_time + time
        self.graph.add_vertex(z)
        self.path.add_vertex(z)

        return id

    def add_edge(self, u_stop_name, u_time, v_stop_name, v_time):
        assert v_time >= u_time

        u_id = self.add_isolated_vertex(u_stop_name, u_time)
        v_id = self.add_isolated_vertex(v_stop_name, v_time)
        u = u_id*self.__max_time + u_time
        v = v_id*self.__max_time + v_time

        #w = v % self.__max_time - u % self.__max_time

        self.graph.add_edge(u, v)

        # 4 cas sont possibles lors de l'ajout d'aret :

        # cas 1 : u and v are leafs
        if self.graph.is_leaf(u) and self.graph.is_leaf(v):
            self.path.set_is_path(u, v, True)

        # cas 2 : u  is a leaf
        elif self.graph.is_leaf(u):
            # if path v-> . then dist(u, . ) = dist(v,.) + dist(u,v)
            is_path_u = self.path.is_path_from(u)
            is_path_v = self.path.is_path_from(v)
            np.bitwise_or(x1=is_path_u, x2 = is_path_v, out= is_path_u, dtype=np.bool)

        # cas 3 : v  is a leaf
        elif self.graph.is_leaf(v):
            # for node x :compute dist v a partir de dist(.,u)
            for x in self.graph.vertex:
                is_path_u = self.path.is_path(x, u)
                if is_path_u:
                    self.path.set_is_path(x, v, True)


        # cas 4 : neither u neither v is a leaf
        else:
            self.__APSP_edge(self.graph, u, v)




        # todo other stuff
        raise Exception("unimplemented")


    def add_vertex(self, z_stop_id, z_time, z_name, Z_in, Z_out):
        # todo
        raise Exception("unimplemented")

    def save_distance(self, out_directory_path):
        #todo
        raise Exception("unimplemented")

    def save_graph(self, out_path):
        # todo
        raise Exception("unimplemented")

#################################################################################################################

    @staticmethod
    def __find_affected_sources(path : Path_presence, graph : Graph, u :int, v : int):
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
                    if not graph.vis[z] and not path.is_path(z, v) and path.is_path(z, u) :  # .dist(z, v) > self.dist(z,u) + w
                        Q.append(z)
                        graph.vis[z] = True
                        S.append(z)

            graph.vis = {v: False for v in graph.vertex}  # Reset vis(·) to false
        return S

    @staticmethod
    def __APSP_edge(path : Path_presence, graph: Graph, u: int, v: int):
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

        if path.is_path(u, v):
            S, P = {}, {}
            S[v] = Dynamic_APSP.__find_affected_sources(path, graph, u, v)
            path.set_is_path(u, v, True)
            Q = deque()
            P[v] = v #todo find best structure
            Q.append(v)
            graph.vis[v] = True
            while len(Q) > 0:
                y = Q.popleft()
                # update distances for source nodes
                for x in S[P[y]]:
                    if not path.is_path(x, y) and path.is_path(x, u) and path.is_path(v, y):
                        path.set_is_path(x, y, True)
                        if y != v:
                            S[y].append(y)

            #enqueue all neighbors that get closer to u
            for z in graph.reversed_adj_matrix(y):
                if not graph.vis(z) and not path.is_path(u, z)  and path.is_path(v, z):
                    path.set_is_path(u, z, True)
                    Q.append([y, z])
                    graph.vis[z] = True
                    P[z] = y


    def __APSP_vertex(self,graph, z, Z_in, Z_out):
        # todo algo 5
        raise Exception("unimplemented")




if __name__ == '__main__':
    print("start")
    print("creation data structure + graph")
    APSP = Dynamic_APSP()
    print("creation is_path + initialisation")
    APSP.initialisation()

    print("finish")
    #{"idx_to_name": ["a", "b", "c"], "max_time": 100, "graph": {"0": [110,170, 270, 50],"50" : [170,270],"110": [120], "120":[50,170],"170":[],"270":[] }, "used_nodes": [[10,50],  [110,120,170], [270] ]}




# reflexion
# Si on veut rester coehrent avec se qui a été fait precedament lorsqu'on veut ajouter une arrete (entre id1, id2),
# on  cree potentiellement 2 moment de temps t1, t2 et donc 2 nouveau vertex u = id1*max + t1 et v = id2*max + t2


from collections import deque
import my_program.path as PATH
from dynamic_Inc_APSP.Data_structure import *


class Dynamic_APSP:
    def __init__(self, path = PATH.OUT):
        out = json.loads(open(path).read())
        self.graph = Graph()
        self.idx_to_name = out["idx_to_name"]
        self.name_to_idx = {x: i for i, x in enumerate(self.idx_to_name)}
        self.distance = Distance(self.idx_to_name, self.name_to_idx)      # todo verifier si probleme de mise a jour ici
        self.__max_time = out["max_time"]
        self.__used_node = out["used_nodes"]

    def add_isolated_vertex(self,stop_name, time):
        if stop_name in self.name_to_idx:
            id = self.name_to_idx[stop_name]
            # todo used_node
        else:
            id = len(self.name_to_idx) +1
            self.idx_to_name.append(stop_name)
            self.name_to_idx[stop_name] = id
            # todo used_node
        z = id*self.__max_time + time
        self.graph.add_vertex(z)

        return id

    def add_edge(self, u_stop_name, u_time, v_stop_name, v_time):
        assert v_time >= u_time

        u_id = self.add_isolated_vertex(u_stop_name, u_time)
        v_id = self.add_isolated_vertex(v_stop_name, v_time)
        u = u_id*self.__max_time + u_time
        v = v_id*self.__max_time + v_time

        w = v % self.__max_time - u % self.__max_time

        self.graph.add_edge(u, v)

        # 4 cas sont possibles lors de l'ajout d'aret :

        # cas 1 : u and v are leafs
        if self.graph.is_leaf(u) and self.graph.is_leaf(v):
            self.distance.update_dist(u, v, w)

        # cas 2 : u  is a leaf
        elif self.graph.is_leaf(u):
            # if path v-> . then dist(u, . ) = dist(v,.) + dist(u,v)
            dist_v = self.distance.dist_from(v)
            def upd(d):
                if d != -1: return d + w
                else: return -1
            dist_u =[upd(d) for d in dist_v]
            dist_u[u] = 0
            self.distance.update_dist_from(u, dist_u)

        # cas 3 : v  is a leaf
        elif self.graph.is_leaf(v):
            # for node x :compute dist v a partir de dist(.,u)
            for x in self.graph.vertex:
                dist_u = self.distance.dist(x, u)
                if dist_u != -1:
                    self.distance.update_dist(x, v, dist_u + w)
            self.distance.update_dist(v, v, 0)

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

    def __find_affected_sources(self,graph, u, v):
        """
        Find affected sources
        Suit l'algo 4
        :param u:
        :param v:
        :return:
        """
        S = []  # affected source
        if graph.dist(u, v) != -1:  # w < self.dist(u,v)
            Q = deque()
            Q.append(u)
            graph.vis[u] = True
            while len(Q) > 0:
                x = Q.popleft()
                for z in graph.reversed_adj_matrix[x]:
                    if not graph.vis[z] and graph.dist(z, v) != -1 and graph.dist(z, u) != -1:  # .dist(z, v) > self.dist(z,u) + w
                        Q.append(z)
                        graph.vis[z] = True
                        S.append(z)

            graph.vis = {v: False for v in graph.vertex}  # Reset vis(·) to false
        return S

    def __APSP_edge(self, graph, u, v):
        """
        Ajout non trivial d'une arete dans le graph
        :param graph: a Data_Structure graph
        :param u: number of the node
        :param v: number of the node
        :return:
        """
        # cas 1 : u et v deja existant
        # ajout d'un edge entre 2 dejà existant u,v:
        # - w est defini par la difference de temps entre u et v
        # - si il existait deja un moyen de joindre v à patir de u , dist(u,v) = difference de temps entre u et v = w
        # - mis à jour inutile si il existe deja un chemin entre u et v
        # - METTRE A JOUR UNIQUEMENT SSI DIST(U,V) = -1
        # todo algo 1





    def __APSP_vertex(self,graph, z, Z_in, Z_out):
        # todo algo 5
        raise Exception("unimplemented")




if __name__ == '__main__':
    Dynamic_APSP()
    print("finish")
    #{"idx_to_name": ["a", "b", "c"], "max_time": 100,
    # "graph": {"0": [110,170, 270, 50],"50" : [170,270],"110": [120], "120":[50,170],"170":[],"270":[] },
    # "used_nodes": [[10,50],  [110,120,170], [270] ]}




# reflexion
# Si on veut rester coehrent avec se qui a été fait precedament lorsqu'on veut ajouter une arrete (entre id1, id2),
# on  cree potentiellement 2 moment de temps t1, t2 et donc 2 nouveau vertex u = id1*max + t1 et v = id2*max + t2


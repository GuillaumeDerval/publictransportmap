import json
import numpy as np
from collections import deque
import my_program.path as PATH
from dynamic_Inc_APSP.Data_structure import *


class Dynamic_APSP:
    def __init__(self):

        self.graph = Graph(out)

    def add_isolated_vertex(self,id, name):
        self.graph.add_vertex(id, name)
        # todo update dynamic APSP strucure
        raise Exception("unimplemented")

    def add_edge_num(self, u,v, u_name = None, v_name = None):
        if u_name is not None: self.add_isolated_vertex(u, u_name)
        if v_name is not None: self.add_isolated_vertex(v, v_name)

        #self.graph.add_edge(u,v)

        # todo other stuff
        raise Exception("unimplemented")

    def add_edge(self, u_stop_id, u_time, v_stop_id, v_time):


    def add_vertex(self, z_stop_id, z_time, z_name, Z_in, Z_out):
        # todo
        raise Exception("unimplemented")

    def save_distance(self, out_directory_path):
        #todo
        raise Exception("unimplemented")

    def save_graph(self, out_path):
        # todo
        raise Exception("unimplemented")



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

    def __APSP_edge(self,graph, u, v):
        # 3 cas sont possibles lors de l'ajout d'aret
        # cas 1 : u et v deja existant
        # cas 2 : u ou v deja existant
        # cas 3 : u et v inexistants

        if u in graph.vertex and v in graph.vertex:
            # cas 1 : u et v deja existant
            # ajout d'un edge entre 2 dejà existant u,v:
            # - w est defini par la difference de temps entre u et v
            # - si il existait deja un moyen de joindre v à patir de u , dist(u,v) = difference de temps entre u et v = w
            # - mis à jour inutile si il existe deja un chemin entre u et v
            # - METTRE A JOUR UNIQUEMENT SSI DIST(U,V) = -1
            # todo algo 1
            raise Exception("cas 1 unimplemented")

        elif v in graph.vertex:
            # cas 2a : v existant et u inexistant, u->v
            # calcul rapide dist(u, . ) = dist(v,.) + dist(u,v)
            raise Exception("cas 2a unimplemented")


        elif u in graph.vertex:
            # cas 2b : u existant et v inexistant, u->v
            # for node x :compute dist v a partir de dist(.,u)
            raise Exception("cas 2b unimplemented")

        else:
            # cas 3 : u et v inexistants
            # cree u, v
            raise Exception("cas 2a unimplemented")



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


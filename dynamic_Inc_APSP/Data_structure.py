import json
import numpy as np
import my_program.path as PATH



#Distance
class Distance:
    def dist(self,u,v):
        """
        Return the minimal distance between u (id) and v (id)
        """
        return self.dist_from(u)[v]
    def dist_from(self,s):
        """
        Return the list of the minimal distance from source  s (id)
        """
        path = PATH.TRAVEL_TIME + "{0}.npy".format(self.idx_to_name[s])
        return np.load(path)
    def update_dist(self, u,v, dist):
        # todo
        # todo optimise
        raise Exception("unimplemented")
    def update_dist_from(self, s, dist_list):
        # todo
        # todo optimise
        raise Exception("unimplemented")
    def update_dist_big_change(self,ids,dist_matrix):
        """
        Effectue une mise a jour des distance de plus grande ampleur
        :param ids: liste des id dont les distances sont mise à jour
        :param dist_matrix:  Liste d'array contenant les nouvelles distance
        :return: None
        """
        # todo
        raise Exception("unimplemented")


class Graph:
    def __init__(self, path = PATH.OUT ):
        out = json.loads(open(path).read())
        self.adj_matrix = out["graph"]
        self.vertex = self.adj_matrix.keys()
        self.V = len(self.adj_matrix)                            # number of vertex
        self.E = sum([len(nei) for nei in self.adj_matrix])      # number of edges

        # adjacency matrix with reversed edge (if u -> v in g the v->u in rev_g)
        self.reversed_adj_matrix = {v: [] for v in self.vertex}
        for org in self.vertex:
            for dest in self.adj_matrix[org]:
                self.reversed_adj_matrix[str(dest)].append(int(org))

        self.vis = {v: False for v in self.vertex}         #indicate if a node have been visited

        self.idx_to_name = out["idx_to_name"]
        self.__max_time = out["max_time"]
        self.__used_node = out["used_nodes"]

    def add_vertex(self, z, name):
        self.adj_matrix[z] = []
        self.reversed_adj_matrix[z] = []
        self.vertex.append([z])
        self.V += 1
        self.vis = {z: False}

        z_id = z // self.__max_time
        assert z_id == self.V + 1
        self.idx_to_name.append(name)

        #todo used_node

    def add_edge(self, u, v):
        assert u in self.vertex
        assert v in self.vertex

        self.E += 1
        self.adj_matrix[u].append(v)
        self.reversed_adj_matrix[v].append(u)


import numpy as np


#Distance
class Distance:

    def __init__(self, idx_to_name, name_to_idx):
        self.idx_to_name = idx_to_name
        self.name_to_idx = name_to_idx

    def dist(self, u: int, v: int) -> float:
        """
        Return the minimal distance between u (id) and v (id)
        """
        return self.dist_from(u)[v]
    def dist_from(self, s):
        """
        Return the list of the minimal distance from source  s (id)
        """
        path = path.TRAVEL_TIME + "{0}.npy".format(self.idx_to_name[s])
        return np.load(path)
    def update_dist(self, u,v, dist):
        # todo
        # todo optimise
        raise Exception("unimplemented")
    def update_dist_from(self, s, dist_list):
        # todo
        # todo optimise
        raise Exception("unimplemented")




class Path_presence:

    def __init__(self, vertex):
        self.pos_to_node = vertex.copy()
        self.node_to_pos = {x: i for i, x in enumerate(self.pos_to_node)}
        self.size = len(vertex)
        self.is_reach = np.zeros((self.size, self.size), dtype=np.bool, order="F")

    def is_path(self, u: int, v: int) -> bool:
        """
        Return the minimal distance between u (id) and v (id)
        """
        return self.is_reach[self.node_to_pos[u]][self.node_to_pos[v]]

    def is_path_from(self, s):
        """
        Return the list of the minimal distance from source  s (id)
        """
        return self.is_reach[self.node_to_pos[s]]

    def set_is_path(self, u, v, is_path):
        """u,v are node number (ie : id*maxtime + time)"""
        self.is_reach[self.node_to_pos[u]][self.node_to_pos[v]] = is_path
        # todo optimise
        #raise Exception("unimplemented")

    def set_is_path_from(self, s, is_path_list):
        self.is_reach[self.node_to_pos[s]] = is_path_list
        # todo optimise
        #raise Exception("unimplemented")

    @staticmethod
    def or_in_place(self,x1, x2):
        """
        :param x1: np.array of bool
        :param x2: np.array of bool
        :after: x1 = x1 and x2, x2 unchanged
        """
        np.bitwise_or(x1, self.path.is_path_from(x2 ), out=x1, dtype=np.bool)



    def add_node(self,n):
        if n not in self.pos_to_node:
            size : int = self.size
            self.pos_to_node.append(n)
            self.node_to_pos[n] = self.size
            self.is_reach.resize(size, size + 1)
            self.is_reach = np.concatenate((self.is_reach, np.zeros((1,self.size +1),dtype = np.bool)), axis=0)
            self.size += 1
            self.is_reach[size][size] = True




class Graph:
    """
    Transforme le out.json en une structure de graph et permet le modification ainsi que leur sauvegarde

    Propriete de ce graph quand il existe un chemin entre 2 de ces noeud il est toujour minimal
    Pas de chemin est indiqué par -1
    """
    def __init__(self, out):
        self.adj_matrix = {int(k): value for k,value in out["graph"].items()}
        self.vertex = [int(v) for v in self.adj_matrix.keys()]
        self.V = len(self.adj_matrix)                            # number of vertex
        self.E = sum([len(nei) for _, nei in self.adj_matrix.items()])      # number of edges

        # adjacency matrix with reversed edge (if u -> v in g the v->u in rev_g)
        self.reversed_adj_matrix = {v: [] for v in self.vertex}
        for org in self.vertex:
            for dest in self.adj_matrix[org]:
                self.reversed_adj_matrix[dest].append(org)

        self.vis = {v: False for v in self.vertex}         #indicate if a node have been visited

    def add_vertex(self, z):
        if z not in self.vertex:
            self.adj_matrix[z] = []
            self.reversed_adj_matrix[z] = []
            self.vertex.append(z)
            self.V += 1
            self.vis = {z: False}

    def add_edge(self, u, v):
        assert u in self.vertex
        assert v in self.vertex

        if v not in self.adj_matrix[u]:                         #keep a simple graph
            self.E += 1
            self.adj_matrix[u].append(v)
            self.reversed_adj_matrix[v].append(u)

    def remove_vertex(self, z):
        assert z in self.vertex

        for dest in self.adj_matrix[z]:
            self.remove_edge(z,dest)
        self.adj_matrix.pop(z)
        for org in self.reversed_adj_matrix[z]:
            self.remove_edge(org,z)
        self.reversed_adj_matrix.pop(z)

        self.vertex.remove(z)
        self.V -= 1
        self.vis.pop(z)

    def remove_edge(self, u, v):
        assert u in self.vertex
        assert v in self.vertex
        assert v in self.adj_matrix[u]
        self.E -= 1
        self.adj_matrix[u].pop(v)
        self.reversed_adj_matrix[v].pop(u)

    def is_isolated(self, v):
        return len(self.adj_matrix[v]) + len(self.reversed_adj_matrix[v]) == 0

    def in_degree(self, v):
        return len(self.reversed_adj_matrix[v])

    def out_degree(self, v):
        return len(self.adj_matrix[v])


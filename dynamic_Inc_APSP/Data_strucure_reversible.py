import json
import numpy as np
import my_program.path as PATH



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


class Path_presence:

    def __init__(self, vertex):
        self.pos_to_vertex = vertex.copy()
        self.vertex_to_pos = {x: i for i, x in enumerate(self.pos_to_vertex)}
        self.size = len(vertex)
        self.is_reach = np.zeros((self.size, self.size), dtype=np.bool, order="F")

        # reversible state -> trailer (see constraint programing)
        self.__true_size = self.size
        self.__backup = []
        self.__backup_stack = []  # permet de faire une recherche sur plusieur etage

    def is_path(self, u: int, v: int) -> bool:
        """
        Return the minimal distance between u (id) and v (id)
        """
        assert u < self.size
        assert v < self.size
        return self.is_reach[self.vertex_to_pos[u]][self.vertex_to_pos[v]]

    def is_path_from(self, s):
        """
        Return the list of the minimal distance from source  s (id)
        """
        assert s < self.size
        return self.is_reach[self.vertex_to_pos[s]]

    def set_is_path(self, u, v, is_path):
        """u,v are node number (ie : id*maxtime + time)"""
        assert u < self.size
        assert v < self.size
        old_value = self.is_reach[self.vertex_to_pos[u]][self.vertex_to_pos[v]]
        self.is_reach[self.vertex_to_pos[u]][self.vertex_to_pos[v]] = is_path
        self.__backup.append(("set_is_path",u,v,old_value))

    def set_is_path_from(self, s, is_path_list):
        assert s < self.size
        old_values = self.is_reach[self.vertex_to_pos[s]]
        self.is_reach[self.vertex_to_pos[s]] = is_path_list
        self.__backup.append(("set_is_path_from", s, old_values))

    @staticmethod
    def or_in_place(self, x1, x2):
        """
        :param x1: np.array of bool
        :param x2: np.array of bool
        :after: x1 = x1 and x2, x2 unchanged
        """
        old_values = self.is_reach[self.node_to_pos[x1]]
        np.bitwise_or(x1, self.path.is_path_from(x2 ), out=x1, dtype=np.bool)
        self.__backup = (("set_is_path_from", x1, old_values))

    def add_vertex(self, n):
        if n not in self.pos_to_vertex:
            size : int = self.size
            self.pos_to_vertex.append(n)
            self.vertex_to_pos[n] = self.size
            if size +1 < self.__true_size:
                self.is_reach.resize(size, size + 1)
                self.is_reach = np.concatenate((self.is_reach, np.zeros((1,self.size +1),dtype = np.bool)), axis=0)
                self.__true_size += 1
            else:   #set values to False
                for i in range(size +1):
                    self.is_reach[i][size] = False
                self.is_reach[size] = np.zeros((1,self.size +1),dtype = np.bool)

            self.size += 1
            self.is_reach[size][size] = True
            self.__backup.append(("add_vertex",n))

    def __remove_vertex(self):
        """
        Remove always the last node added
        :return:
        """
        n = self.pos_to_vertex.pop()
        self.__true_size -= 1
        self.size -= 1
        self.__backup.append(("remove_vertex", n))

    def save(self):
        self.__backup_stack.append(self.__backup)
        self.__backup = []

    def restore(self):
        self.__backup.reverse()
        for log in self.__backup:
            if log[0] == "add_vertex":
                self.__remove_vertex()
            elif log[0] == "rm_vertex":
                self.add_vertex(log[1])
            elif log[0] == "set_is_path":
                self.set_is_path(log[1],log[2])
                self.__backup.pop()
            elif log[0] == "set_is_path_from":
                self.set_is_path_from(log[1],log[2])
                self.__backup.pop()
            else:
                raise Exception("Unhandeled log")

        self.__change_log = self.__backup_stack.pop()




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

        #reversible state -> record change
        self.__change_log = []
        self.__stack_log = [] #permet de faire une recherche sur plusieur etage

    def add_vertex(self, z):
        if z not in self.vertex:
            self.adj_matrix[z] = []
            self.reversed_adj_matrix[z] = []
            self.vertex.append(z)
            self.V += 1
            self.vis = {z: False}

            self.__change_log.append(("add_vertex",z))

    def add_edge(self, u, v):
        assert u in self.vertex
        assert v in self.vertex

        if v not in self.adj_matrix[u]:                         #keep a simple graph
            self.E += 1
            self.adj_matrix[u].append(v)
            self.reversed_adj_matrix[v].append(u)
            self.__change_log.append(("add_edge", u,v))

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
        self.__change_log.append(("rm_vertex", z))

    def remove_edge(self, u, v):
        assert u in self.vertex
        assert v in self.vertex
        assert v in self.adj_matrix[u]
        self.E -= 1
        self.adj_matrix[u].pop(v)
        self.reversed_adj_matrix[v].pop(u)
        self.__change_log.append(("rm_edge", u, v))

    def is_isolated(self, v):
        return len(self.adj_matrix[v]) + len(self.reversed_adj_matrix[v]) == 0

    def in_degree(self, v):
        return len(self.reversed_adj_matrix[v])

    def out_degree(self, v):
        return len(self.adj_matrix[v])

    def save(self):
        self.__stack_log.append(self.__change_log)
        self.__change_log = []

    def restore(self):
        self.__change_log.reverse()
        for log in self.__change_log:
            if log[0] == "add_vertex": self.remove_vertex(log[1])
            elif log[0] == "rm_vertex": self.add_vertex(log[1])
            elif log[0] == "add_edge":self.remove_edge(log[1],log[2])
            elif log[0] == "rm_edge": self.add_edge(log[1],log[2])
            else: raise Exception("Unhandeled log")

        self.__change_log = self.__stack_log.pop()



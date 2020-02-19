import numpy as np
import my_program.path as PATH
from math import inf


# Distance
class Distance:

    # !!! attention le distance sont mise à jour seulement après un appel a update()

    def __init__(self, name_to_idx,idx_to_name, max_time, used_node, path_presence):
        self.name_to_idx = name_to_idx
        self.idx_to_name = idx_to_name
        self.max_time = max_time
        self.used_node = used_node
        self.presence: Path_presence = path_presence
        self.size: int = len(name_to_idx)
        self.distance = [np.full((self.size,), -1, dtype=np.int)]*self.size
        self.__compute_distances()
        self.__backup = {"size": self.size, "change_distance": {}}
        self.__backup_stack = []  # permet de faire une recherche sur plusieur etage
        #todo changeable size

    def __compute_distances(self):
        for source_idx,destination_idx in zip(range(self.size), range(self.size)):
            src, dest = self.used_node[source_idx], self.used_node[destination_idx]
            mini = inf
            for s in src.sort(lambda x: x % self.max_time):
                for d in dest.sort(lambda x: x % self.max_time):
                    if s % self.max_time > d % self.max_time:
                        pass
                        # dest = dest[1:] #todo optimise
                    elif self.presence.is_reach[s][d]:
                        time = d % self.max_time - s % self.max_time
                        mini = min(time, mini)
                        break  # because dest are sorted
            self.distance[source_idx][destination_idx] = mini

    def dist(self, s_name: str, d_name: str) -> float:
        """
        Return the minimal distance between u_name and v_name
        """
        s_idx = self.name_to_idx[s_name]
        d_idx = self.name_to_idx[d_name]
        return self.distance[s_idx][d_idx]

    def dist_from(self, s_name):
        """
        Return the list of the minimal distance from source  s (id)
        """
        s_idx = self.name_to_idx[s_name]
        return self.distance[s_idx]

    def dist_before_change(self, s_name: str, d_name: str) -> float:
        """
        Return the minimal distance between u (id) and v (id)
        """
        if s_name in self.__backup["change_distance"] and d_name in self.__backup["change_distance"][s_name]:
            return self.__backup["change_distance"][s_name][d_name]
        else:
            return self.dist(s_name, d_name)
        #path = PATH.TRAVEL_TIME + "{0}.npy".format(self.idx_to_name[s])
        #return np.load(path)

    def dist_from_before_change(self, s_name):
        """
        Return the list of the minimal distance from source  s (id)
        """
        if s_name in self.__backup["change_distance"]:
            s_idx = self.name_to_idx[s_name]
            distance = self.distance[s_idx].copy()
            for d_name in self.__backup["change_distance"][s_name]:
                d_idx = self.name_to_idx[d_name]
                distance[d_idx] = self.__backup["change_distance"][s_name][d_name]
            return distance
        else:
            s_idx = self.name_to_idx[s_name]
            return self.distance[s_idx]

    def add_isolated_vertex(self, name, idx):
        # inc size
        #update distance
        raise Exception("unimplemented")

    def update(self):
        # hypothese : distance à la bonne taille
        changes = self.presence.get_changes()
        for s, content in changes["single_change"].items():
            s_name = self.idx_to_name[s // self.max_time]
            for d, value in content.items():
                d_name = self.idx_to_name[d // self.max_time]
                time = d % self.max_time - s % self.max_time
                self.single_update(s_name, d_name, time)

        for s, new_line in changes["line_change"].items():
            s_name = s // self.max_time
            for i in range(len(changes["idx_order"])):
                d = changes["idx_order"][i]
                d_name = self.idx_to_name[d // self.max_time]
                time = d % self.max_time - s % self.max_time
                self.single_update(s_name, d_name, time)

    def single_update(self, s_name, d_name, new_time):
        if new_time < self.distance[s_name][d_name]:
            old_value = self.distance[s_name][d_name]
            self.distance[s_name][d_name] = new_time
            # backup : ("change_distance",s,d,old_value)
            if d_name not in self.__backup["change_distance"].get(s_name, {}):
                if s_name not in self.__backup["change_distance"]:
                    self.__backup["change_distance"][s_name] = {}
                self.__backup["change_distance"][s_name][d_name] = old_value

    def save(self):
        self.__backup_stack.append(self.__backup)
        self.__backup = {"size": self.size, "change_distance": {}}

    def restore(self):
        assert self.__backup["size"] <= self.size, "suppression of node is not yet implemented "
        self.size = self.__backup["size"]

        # restore old distance value
        for s_name in self.__backup["change_distance"]:
            for d_name,old_value in self.__backup["change_distance"][s_name].items():
                self.distance[s_name][d_name] = old_value

        self.__backup = self.__backup_stack.pop()

    def get_changes(self):
        """
        retourne l'ensemble de nouvelle valeur de is_reach, leur position est indique par les cle du dictionnaire
        (new_value, old_value)
        :return:
        """
        changes = {"size": (self.size, self.__backup["size"]),"change_distance": {}}
        # distance
        for s_name in self.__backup["change_distance"]:
            for d_name in self.__backup["change_distance"][s_name]:
                if s_name not in changes["change_distance"]:
                    changes["change_distance"][s_name] = {}
                changes["change_distance"][s_name][d_name] = (self.dist(s_name,d_name), self.dist_before_change(s_name, d_name))
        return changes


class Path_presence:

    def __init__(self, vertex):
        self.pos_to_vertex = vertex.copy()
        self.vertex_to_pos = {x: i for i, x in enumerate(self.pos_to_vertex)}
        self.size = len(vertex)
        self.is_reach = np.zeros((self.size, self.size), dtype=np.bool, order="F")

        # reversible state -> trailer (see constraint programing)
        self.__true_size = self.size
        self.__backup = {"size": self.size, "single_change" : {},"line_change" : {} }
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
        # backup : ("set_is_path",u,v,old_value)
        if u not in self.__backup["line_change"]and v not in self.__backup["single_change"].get(u, {}):
            if u not in self.__backup["single_change"]:
                self.__backup["single_change"][u] = {}
            self.__backup["single_change"][u][v] = old_value

    def set_is_path_from(self, s, is_path_list):
        assert s < self.size
        old_values = self.is_reach[self.vertex_to_pos[s]]
        self.is_reach[self.vertex_to_pos[s]] = is_path_list
        # backup : ("set_is_path_from", s, old_values))
        if s not in self.__backup["line_change"]:
            self.__backup["line_change"][s] = old_values
            if s in self.__backup["single_change"]:
                self.__backup["single_change"].pop(s)


    def or_in_place(self, x1, x2):
        """
        :param x1: np.array of bool
        :param x2: np.array of bool
        :after: x1 = x1 and x2, x2 unchanged
        """
        old_values = self.is_reach[self.vertex_to_pos[x1]]
        np.bitwise_or(x1, x2, out=x1, dtype=np.bool)

        #backup
        if x1 not in self.__backup["line_change"]:
            self.__backup["line_change"][x1] = old_values
            if x1 in self.__backup["single_change"]:
                self.__backup["single_change"].pop(x1)

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

    def __remove_vertex(self):
        """
        Remove always the last node added
        :return:
        """
        n = self.pos_to_vertex.pop()
        self.size -= 1
        #self.__backup.rm(n) #todo if we keep remove

    def save(self):
        self.__backup_stack.append(self.__backup)
        self.__backup = []

    def restore(self):
        assert self.__backup["size"] <= self.size, "suppression of node is not yet implemented "
        self.size = self.__backup["size"]
        # restore line
        for s in self.__backup["line_change"]:
            self.is_reach[self.vertex_to_pos[s]] = self.__backup["line_change"][s]
        # restore single value
        for u in self.__backup["single_change"]:
            for v in self.__backup["single_change"][u]:
                self.is_reach[self.vertex_to_pos[u]][self.vertex_to_pos[v]] = self.__backup["single_change"][u][v]

        self.__backup = self.__backup_stack.pop()

    def get_changes(self):
        """
        retourne l'ensemble de nouvelle valeur de is_reach, leur position est indique par les cle du dictionnaire
        :return:
        """
        new_values = {"size": self.size,"idx_order": self.pos_to_vertex, "single_change" : {}, "line_change": {}}
        # restore line
        for s in self.__backup["line_change"]:
            new_values["line_change"][s] = self.is_reach[self.vertex_to_pos[s]]
        # restore single value
        for u in self.__backup["single_change"]:
            for v in self.__backup["single_change"][u]:
                if u not in new_values["single_change"]:
                    new_values["single_change"][u] = {}
                new_values["single_change"][u][v] = self.is_reach[self.vertex_to_pos[u]][self.vertex_to_pos[v]]

        return new_values





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



import numpy as np
from math import inf
# import my_program.path as PATH


# Distance
class Distance:

    # !!! attention le distance sont mise à jour seulement après un appel a update()
    # todo sauvegarde sur des fichiers pour limiter l'utilisation de memoire ???

    def __init__(self, name_to_idx, idx_to_name, max_time, used_time, path_presence):
        self.name_to_idx = name_to_idx
        self.idx_to_name = idx_to_name
        self.max_time = max_time
        self.used_time = used_time                          #used node are sorted by time
        self.is_reachable: PathPresence = path_presence
        self.size: int = len(name_to_idx)
        self.__true_size = self.size
        self.distance = [np.full((self.size,), -1, dtype=np.int) for _ in range(self.size)]
        self.up_to_date = True
        self.__compute_distances()
        self.__backup = {"size": self.size, "change_distance": {}}
        self.__backup_stack = []  # permet de faire une recherche sur plusieur etage

    def __compute_distances(self):
        for source_idx in range(self.size):
            src_time_list = self.used_time[source_idx]
            for destination_idx in range(self.size):
                dest_time_list = self.used_time[destination_idx]
                mini = inf
                for stime in src_time_list:
                    s = source_idx*self.max_time + stime
                    for dtime in dest_time_list:
                        d = destination_idx * self.max_time + dtime
                        if stime > dtime:
                            #pass
                            dest_time_list = dest_time_list[1:]
                        elif self.is_reachable.is_path(s, d):
                            time = d % self.max_time - s % self.max_time
                            mini = min(time, mini)
                            break  # because dest are sorted
                if mini == inf: mini = -1
                self.distance[source_idx][destination_idx] = mini

                # un noeud sans used_time peut se rejoindre lui meme
                if source_idx == destination_idx:
                    self.distance[source_idx][destination_idx] = 0

    def dist(self, s_name: str, d_name: str) -> float:
        """
        Return the minimal distance between u_name and v_name
        """
        s_idx = self.name_to_idx[s_name]
        d_idx = self.name_to_idx[d_name]
        return self.distance[s_idx][d_idx]

    def __set_dist(self, s_name: str, d_name: str, new_value : int):
        """
        Return the minimal distance between u_name and v_name
        """
        s_idx = self.name_to_idx[s_name]
        d_idx = self.name_to_idx[d_name]
        self.distance[s_idx][d_idx] = new_value

    def dist_from(self, s_name):
        """
        Return the list of the minimal distance from source  s (id)
        """
        s_idx = self.name_to_idx[s_name]
        return self.distance[s_idx][:self.size]

    def dist_before_change(self, s_name: str, d_name: str) -> float:
        """
        Return the minimal distance between u (id) and v (id)
        """
        if s_name in self.__backup["change_distance"] and d_name in self.__backup["change_distance"][s_name]:
            return self.__backup["change_distance"][s_name][d_name]
        else:
            return self.dist(s_name, d_name)
        # path = PATH.TRAVEL_TIME + "{0}.npy".format(self.idx_to_name[s])
        # return np.load(path)

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

    def __update_size(self):
        while self.size < len(self.idx_to_name):
            if self.size + 1 > self.__true_size:
                self.distance = np.concatenate((self.distance, np.full((self.size,1),-1, dtype=np.int)), axis=1)
                self.distance = np.concatenate((self.distance, np.full((1, self.size + 1),-1, dtype=np.int)), axis=0)
                self.__true_size += 1
            else:   # set values to False
                for i in range(self.size + 1):
                    self.distance[i][self.size] = -1
                self.distance[self.size] = np.full((1, self.size + 1),-1, dtype=np.int)
            self.distance[self.size][self.size] = 0
            self.size += 1

    def update(self):
        if not self.up_to_date:
            self.__update_size()
            changes = self.is_reachable.get_changes()
            for s, content in changes["single_change"].items():
                s_name = self.idx_to_name[s // self.max_time]
                for d, value in content.items():
                    if value:
                        d_name = self.idx_to_name[d // self.max_time]
                        time = d % self.max_time - s % self.max_time
                        self.single_update(s_name, d_name, time)

            for s, new_line in changes["line_change"].items():
                s_name = self.idx_to_name[s // self.max_time]
                for i in range(len(changes["idx_order"])):
                    if new_line[i]:
                        d = changes["idx_order"][i]
                        d_name = self.idx_to_name[d // self.max_time]
                        time = d % self.max_time - s % self.max_time
                        assert time >= 0
                        self.single_update(s_name, d_name, time)
            self.up_to_date =True

    def single_update(self, s_name, d_name, new_time):
        self.__update_size()
        if new_time < self.dist(s_name, d_name) or self.dist(s_name, d_name) == -1:
            old_value = self.dist(s_name, d_name)
            self.__set_dist(s_name, d_name, new_time)
            # backup : ("change_distance",s,d,old_value)
            if d_name not in self.__backup["change_distance"].get(s_name, {}):
                if s_name not in self.__backup["change_distance"]:
                    self.__backup["change_distance"][s_name] = {}
                self.__backup["change_distance"][s_name][d_name] = old_value

    def save(self):
        if not self.up_to_date: self.update()
        self.__backup_stack.append(self.__backup)
        self.__backup = {"size": self.size, "change_distance": {}}

    def restore(self):
        assert self.__backup["size"] <= self.size, "suppression of node is not yet implemented "
        self.size = self.__backup["size"]

        # restore old distance value
        for s_name in self.__backup["change_distance"]:
            for d_name, old_value in self.__backup["change_distance"][s_name].items():
                self.distance[s_name][d_name] = old_value

        self.__backup = self.__backup_stack.pop()
        self.up_to_date = True

    def get_changes(self):
        """
        retourne l'ensemble de nouvelle valeur de is_reach, leur position est indique par les cle du dictionnaire
        (new_value, old_value)
        :return:
        """
        if not self.up_to_date: self.update()


        changes = {"size": (self.size, self.__backup["size"]), "change_distance": {}}
        # distance
        for s_name in self.__backup["change_distance"]:
            for d_name in self.__backup["change_distance"][s_name]:
                if s_name not in changes["change_distance"]:
                    changes["change_distance"][s_name] = {}
                changes["change_distance"][s_name][d_name] = (self.dist(s_name, d_name), self.dist_before_change(s_name, d_name))
        return changes

    def hard_save(self, out_directory_path):
        if not self.up_to_date: self.update()

        for idx in range(self.size):
            name = self.idx_to_name[idx]
            data = self.distance[idx]
            np.save(out_directory_path + name + ".npy", data.astype(np.int16))


class PathPresence:

    def __init__(self, graph, max_time):
        vertex = graph.vertex
        self.pos_to_vertex = vertex.copy()
        self.vertex_to_pos = {x: i for i, x in enumerate(self.pos_to_vertex)}
        self.size = len(vertex)
        self.is_reach = np.zeros((self.size, self.size), dtype=np.bool, order="F")
        # reversible state -> trailer (see constraint programing)
        self.__true_size = self.size
        self.__backup = {"size": self.size, "single_change": {}, "line_change": {}}
        self.__backup_stack = []  # permet de faire une recherche sur plusieur etage
        self.initialisation(graph, max_time)
        self.__backup = {"size": self.size, "single_change": {}, "line_change": {}}


    def initialisation(self, graph, max_time):
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

        # on peut passer d'un  noeud a l'autre au meme instant

        def init_time_level(time : int, node_list : list, adj_matrix, max_time):
            wait__for_change = {} #{n, m} if the value of n is changed then m must be recomputed
            while len(node_list) > 0:
                x = node_list.pop()
                neightboors = adj_matrix[x]
                for nei in neightboors:
                    old_x_value = self.is_path_from(x).copy()
                    self.or_in_place(x, nei)
                    new_x_value = self.is_path_from(x)
                    if not np.array_equal(new_x_value, old_x_value): #check if change
                        node_list.extend(wait__for_change.get(x, []))
                    if time == nei % max_time:
                        if nei not in wait__for_change: wait__for_change[nei] = [x]
                        else: wait__for_change[nei].append(x)



        node = graph.vertex
        node.sort(key=lambda x: x % max_time, reverse=True)
        time = -1
        node_list = []
        for x in node:
            x_time = x % max_time
            self.set_is_path(x, x, True)
            if x_time != time:
                init_time_level(time, node_list, graph.adj_matrix,max_time)
                node_list = [x]
                time = x_time
            else:
                node_list.append(x)
        init_time_level(time, node_list, graph.adj_matrix,max_time)

    def is_path(self, u: int, v: int) -> bool:
        """
        Return the minimal distance between u (pos-time node) and v (pos-time node)
        """
        assert u in self.vertex_to_pos
        assert v in self.vertex_to_pos
        return self.is_reach[self.vertex_to_pos[u]][self.vertex_to_pos[v]]

    def is_path_from(self, s):
        """
        Return the list of the minimal distance from source  s (id)
        """
        assert s in self.vertex_to_pos
        return self.is_reach[self.vertex_to_pos[s]][:self.size]

    def set_is_path(self, u, v, is_path):
        """u,v are node number (ie : id*maxtime + time)"""
        assert u in self.vertex_to_pos
        assert v in self.vertex_to_pos
        old_value = self.is_path(u,v) #self.is_reach[self.vertex_to_pos[u]][self.vertex_to_pos[v]]
        if old_value != is_path:
            self.is_reach[self.vertex_to_pos[u]][self.vertex_to_pos[v]] = is_path
            # backup : ("set_is_path",u,v,old_value)
            if u not in self.__backup["line_change"]and v not in self.__backup["single_change"].get(u, {}):
                if u not in self.__backup["single_change"]:
                    self.__backup["single_change"][u] = {v: old_value}
                else: self.__backup["single_change"][u][v] = old_value

    def set_is_path_from(self, s, is_path_list):
        assert s in self.vertex_to_pos
        old_values = self.is_reach[self.vertex_to_pos[s]]
        if not np.array_equal(old_values, is_path_list):
            self.is_reach[self.vertex_to_pos[s]] = is_path_list
            # backup : ("set_is_path_from", s, old_values))
            if s not in self.__backup["line_change"]:
                self.__backup["line_change"][s] = old_values
                if s in self.__backup["single_change"]:
                    self.__backup["single_change"].pop(s)

    def or_in_place(self, x1: int, x2 : int):
        """
        :param x1: index of a  np.array of bool indication presence of a path
        :param x2: index of a  np.array of bool indication presence of a path
        :after: is_reach[x1] = is_reach[x1] or is_reach[x2], is_reach[x2] is unchanged
        """
        assert x1 in self.vertex_to_pos
        assert x2 in self.vertex_to_pos
        old_values = self.is_path_from(x1).copy()
        path_x1 = self.is_path_from(x1)
        path_x2 = self.is_path_from(x2)
        np.bitwise_or(path_x1, path_x2, out=path_x1, dtype=np.bool)

        # backup
        if x1 not in self.__backup["line_change"]:
            self.__backup["line_change"][x1] = old_values
            if x1 in self.__backup["single_change"]:
                self.__backup["single_change"].pop(x1)

    def add_vertex(self, n):
        if n not in self.pos_to_vertex:
            size: int = self.size
            self.pos_to_vertex.append(n)
            self.vertex_to_pos[n] = self.size
            if size + 1 > self.__true_size:
                #self.is_reach= np.resize(self.is_reach,(size, size + 1))
                #self.is_reach.resize(size, size + 1)
                self.is_reach = np.concatenate((self.is_reach, np.zeros((self.size,1), dtype=np.bool)), axis=1)
                self.is_reach = np.concatenate((self.is_reach, np.zeros((1, self.size + 1), dtype=np.bool)), axis=0)
                self.__true_size += 1
            else:   # set values to False
                for i in range(size + 1):
                    self.is_reach[i][size] = False
                self.is_reach[size] = np.zeros((1, self.__true_size), dtype=np.bool)

            self.size += 1
            self.is_reach[size][size] = True

    def __remove_vertex(self):
        """
        Remove always the last node added
        :return:
        """
        n = self.pos_to_vertex.pop()
        self.size -= 1
        # self.__backup.rm(n) # todo if we keep remove

    def save(self):
        self.__backup_stack.append(self.__backup)
        self.__backup = {"size": self.size, "single_change": {}, "line_change": {}}

    def restore(self):
        assert self.__backup["size"] <= self.size, "suppression of node is not yet implemented "
        self.size = self.__backup["size"]
        # restore line
        for s in self.__backup["line_change"]:
            self.is_reach[self.vertex_to_pos[s]][:self.size] = self.__backup["line_change"][s][:self.size]
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
        new_values = {"size": self.size, "idx_order": self.pos_to_vertex, "single_change": {}, "line_change": {}}
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

    def hard_save(self, out_directory_path):
        for pos in range(self.size):
            v = self.pos_to_vertex[pos]
            data = self.is_path_from(v)
            np.save(out_directory_path + str(v) + ".npy", data.astype(np.bool))


class Graph:
    """
    Transforme le out.json en une structure de graph et permet le modification ainsi que leur sauvegarde

    Propriete de ce graph quand il existe un chemin entre 2 de ces noeud il est toujour minimal
    Pas de chemin est indiqué par -1
    """
    def __init__(self, out):
        self.adj_matrix = {int(k): value for k,value in out["graph"].items()}
        self.vertex = [int(v) for v in self.adj_matrix.keys()]
        self.V = len(self.adj_matrix)                                       # number of vertex
        self.E = sum([len(nei) for _, nei in self.adj_matrix.items()])      # number of edges

        # adjacency matrix with reversed edge (if u -> v in g the v->u in rev_g)
        self.reversed_adj_matrix = {v: [] for v in self.vertex}
        for org in self.vertex:
            for dest in self.adj_matrix[org]:
                self.reversed_adj_matrix[dest].append(org)

        self.vis = {v: False for v in self.vertex}          # indicate if a node have been visited

        # reversible state -> record change
        self.__change_log = []
        self.__stack_log = []                               # permet de faire une recherche sur plusieur etage

    def add_vertex(self, z):
        if z not in self.vertex:
            self.adj_matrix[z] = []
            self.reversed_adj_matrix[z] = []
            self.vertex.append(z)
            self.V += 1
            self.vis[z] = False

            self.__change_log.append(("add_vertex", z))

    def add_edge(self, u, v):
        assert u in self.vertex
        assert v in self.vertex

        if v not in self.adj_matrix[u]:                         # keep a simple graph
            self.E += 1
            self.adj_matrix[u].append(v)
            self.reversed_adj_matrix[v].append(u)
            self.__change_log.append(("add_edge", u, v))

    def remove_vertex(self, z):
        assert z in self.vertex

        for dest in self.adj_matrix[z]:
            self.remove_edge(z, dest)
        self.adj_matrix.pop(z)
        for org in self.reversed_adj_matrix[z]:
            self.remove_edge(org, z)
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
        self.adj_matrix[u].remove(v)
        self.reversed_adj_matrix[v].remove(u)
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
        for log in self.__change_log.copy():
            if log[0] == "add_vertex": self.remove_vertex(log[1])
            elif log[0] == "rm_vertex": self.add_vertex(log[1])
            elif log[0] == "add_edge":self.remove_edge(log[1], log[2])
            elif log[0] == "rm_edge": self.add_edge(log[1], log[2])
            else: raise Exception("Unhandeled log")

        self.__change_log = self.__stack_log.pop()

    def __eq__(self, other):
        if isinstance(other, Graph):
            if self.V == other.V and self.vertex == other.vertex:
                if self.E == other.E and  self.adj_matrix == other.adj_matrix:
                    return True
                else:
                    print("bad adj matrix")
            else:
                print("bad vertex matrix")
        else:
            print("bad instance")
        return False
        #return isinstance(other, Graph) and self.V == other.V and self.E == other.E and self.vertex == other.vertex and self.adj_matrix == other.adj_matrix

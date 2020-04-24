import numpy as np
import json


class PathPresence:

    def __init__(self, graph, max_time):
        vertex = graph.vertex
        self.pos_to_vertex = vertex.copy()
        self.vertex_to_pos = {x: i for i, x in enumerate(self.pos_to_vertex)}
        self.size = len(vertex)
        self.is_reachable = np.zeros((self.size, self.size), dtype=np.bool, order="F")
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

        #TODO verifer si ne contient pas de bug quand un noeud pointe vers lui même

        def init_time_level(time : int, node_list : list, adj_list, max_time):
            wait__for_change = {} #{n, m} if the value of n is changed then m must be recomputed
            while len(node_list) > 0:
                x = node_list.pop()
                neightboors = adj_list[x]
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
                init_time_level(time, node_list, graph.adj_list,max_time)
                node_list = [x]
                time = x_time
            else:
                node_list.append(x)
        init_time_level(time, node_list, graph.adj_list,max_time)

    def is_path(self, u: int, v: int) -> bool:
        """
        Return the minimal distance between u (pos-time node) and v (pos-time node)
        """
        assert u in self.vertex_to_pos
        assert v in self.vertex_to_pos
        return self.is_reachable[self.vertex_to_pos[u]][self.vertex_to_pos[v]]

    def is_path_from(self, s):
        """
        Return the list of the minimal distance from source  s (id)
        """
        assert s in self.vertex_to_pos
        return self.is_reachable[self.vertex_to_pos[s]][:self.size]

    def set_is_path(self, u, v, is_path):
        """u,v are node number (ie : id*maxtime + time)"""
        assert u in self.vertex_to_pos
        assert v in self.vertex_to_pos
        old_value = self.is_path(u,v) #self.is_reach[self.vertex_to_pos[u]][self.vertex_to_pos[v]]
        if old_value != is_path:
            self.is_reachable[self.vertex_to_pos[u]][self.vertex_to_pos[v]] = is_path
            # backup : ("set_is_path",u,v,old_value)
            if u not in self.__backup["line_change"]and v not in self.__backup["single_change"].get(u, {}):
                if u not in self.__backup["single_change"]:
                    self.__backup["single_change"][u] = {v: old_value}
                else: self.__backup["single_change"][u][v] = old_value

    def set_is_path_from(self, s, is_path_list):
        assert s in self.vertex_to_pos
        old_values = self.is_reachable[self.vertex_to_pos[s]]
        if not np.array_equal(old_values, is_path_list):
            self.is_reachable[self.vertex_to_pos[s]] = is_path_list
            # backup : ("set_is_path_from", s, old_values))
            if s not in self.__backup["line_change"]:
                self.__backup["line_change"][s] = old_values
                if s in self.__backup["single_change"]:
                    self.__backup["single_change"].pop(s)

    def or_in_place(self, idx1: int, idx2 : int):
        """
        :param idx1: index of a  np.array of bool indication presence of a path
        :param idx2: index of a  np.array of bool indication presence of a path
        :after: is_reach[idx1] = is_reach[idx1] or is_reach[idx2], is_reach[idx2] is unchanged
        """
        assert idx1 in self.vertex_to_pos
        assert idx2 in self.vertex_to_pos
        old_values = self.is_path_from(idx1).copy()
        path_x1 = self.is_path_from(idx1)
        path_x2 = self.is_path_from(idx2)
        np.bitwise_or(path_x1, path_x2, out=path_x1, dtype=np.bool)

        # backup
        if idx1 not in self.__backup["line_change"]:
            self.__backup["line_change"][idx1] = old_values
            if idx1 in self.__backup["single_change"]:
                self.__backup["single_change"].pop(idx1)

    def add_vertex(self, v):
        if v not in self.pos_to_vertex:
            size: int = self.size
            self.pos_to_vertex.append(v)
            self.vertex_to_pos[v] = self.size
            if size + 1 > self.__true_size:
                #self.is_reach= np.resize(self.is_reach,(size, size + 1))
                #self.is_reach.resize(size, size + 1)
                self.is_reachable = np.concatenate((self.is_reachable, np.zeros((self.size, 1), dtype=np.bool)), axis=1)
                self.is_reachable = np.concatenate((self.is_reachable, np.zeros((1, self.size + 1), dtype=np.bool)), axis=0)
                self.__true_size += 1
            else:   # set values to False
                for i in range(size + 1):
                    self.is_reachable[i][size] = False
                self.is_reachable[size] = np.zeros((1, self.__true_size), dtype=np.bool)

            self.size += 1
            self.is_reachable[size][size] = True

    def hard_save(self, out_directory_path):
        for pos in range(self.size):
            v = self.pos_to_vertex[pos]
            data = self.is_path_from(v)
            np.save(out_directory_path + str(v) + ".npy", data.astype(np.bool))

        with open(out_directory_path + "__conversion.json", "w") as out:
            json.dump(self.vertex_to_pos, out)

    # #################################################################################################################

    def save(self):
        self.__backup_stack.append(self.__backup)
        self.__backup = {"size": self.size, "single_change": {}, "line_change": {}}

    def restore(self):
        assert self.__backup["size"] <= self.size, "suppression of node is not yet implemented "
        self.size = self.__backup["size"]
        # restore line
        for s in self.__backup["line_change"]:
            self.is_reachable[self.vertex_to_pos[s]][:self.size] = self.__backup["line_change"][s][:self.size]
        # restore single value
        for u in self.__backup["single_change"]:
            for v in self.__backup["single_change"][u]:
                self.is_reachable[self.vertex_to_pos[u]][self.vertex_to_pos[v]] = self.__backup["single_change"][u][v]

        self.__backup = self.__backup_stack.pop()

    def get_changes(self):
        """
        retourne l'ensemble de nouvelle valeur de is_reach, leur position est indique par les cle du dictionnaire
        :return:
        """
        new_values = {"size": self.size, "idx_order": self.pos_to_vertex, "single_change": {}, "line_change": {}}
        # restore line
        for s in self.__backup["line_change"]:
            new_values["line_change"][s] = self.is_reachable[self.vertex_to_pos[s]]
        # restore single value
        for u in self.__backup["single_change"]:
            for v in self.__backup["single_change"][u]:
                if u not in new_values["single_change"]:
                    new_values["single_change"][u] = {}
                new_values["single_change"][u][v] = self.is_reachable[self.vertex_to_pos[u]][self.vertex_to_pos[v]]

        return new_values


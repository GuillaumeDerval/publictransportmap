class Graph:
    """
    Transforme le fichier out.json en une structure de graph et permet le modification ainsi que leur sauvegarde

    Propriete de ce graph quand il existe un chemin entre 2 de ces noeud il est toujour minimal
    Pas de chemin est indiqué par -1
    """
    def __init__(self, out):
        self.adj_matrix: dict = {int(k): value for k,value in out["graph"].items()}
        self.vertex: list = [int(v) for v in self.adj_matrix.keys()]
        self.V: int = len(self.adj_matrix)                                       # number of vertex
        self.E: int = sum([len(nei) for _, nei in self.adj_matrix.items()])      # number of edges

        # adjacency matrix with reversed edge (if u -> v in g the v->u in rev_g)
        self.reversed_adj_matrix: dict = {v: [] for v in self.vertex}
        for org in self.vertex:
            for dest in self.adj_matrix[org]:
                self.reversed_adj_matrix[dest].append(org)

        self.vis = {v: False for v in self.vertex}          # indicate if a node have been visited

        # reversible state -> record change
        self.__change_log = []
        self.__stack_log = []                               # permet de faire une recherche sur plusieur etage

    def add_vertex(self, v):
        if v not in self.vertex:
            self.adj_matrix[v] = []
            self.reversed_adj_matrix[v] = []
            self.vertex.append(v)
            self.V += 1
            self.vis[v] = False

            self.__change_log.append(("add_vertex", v))

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

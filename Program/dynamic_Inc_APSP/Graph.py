class Graph:
    """
    Transform the file graph.json into a graph structure which can be modified
    This class record also the modification done in order to undo them.
    """
    def __init__(self, out):
        self.adj_list: dict = {int(k): value for k, value in out["graph"].items()}   # adjacency lists for outgoing edge
        self.vertex: list = [int(v) for v in self.adj_list.keys()]                   # list of vertex
        self.V: int = len(self.adj_list)                                             # number of vertex
        self.E: int = sum([len(nei) for _, nei in self.adj_list.items()])            # number of edges

        # adjacency list with reversed edge (if u -> v in g the v->u in rev_g)
        self.reversed_adj_list: dict = {v: [] for v in self.vertex}                  # adjacency lists for incoming edge
        for org in self.vertex:
            for dest in self.adj_list[org]:
                self.reversed_adj_list[dest].append(org)

        self.vis = {v: False for v in self.vertex}                                # indicate if a node have been visited

        # reversible state -> record change
        self.__change_log = []
        self.__stack_log = []

    def add_vertex(self, v):
        if v not in self.vertex:
            self.adj_list[v] = []
            self.reversed_adj_list[v] = []
            self.vertex.append(v)
            self.V += 1
            self.vis[v] = False

            self.__change_log.append(("add_vertex", v))

    def add_edge(self, u, v):
        assert u in self.vertex
        assert v in self.vertex

        if v not in self.adj_list[u]:                         # keep the graph simple
            self.E += 1
            self.adj_list[u].append(v)
            self.reversed_adj_list[v].append(u)
            self.__change_log.append(("add_edge", u, v))

    def remove_vertex(self, z):
        assert z in self.vertex

        for dest in self.adj_list[z]:
            self.remove_edge(z, dest)
        self.adj_list.pop(z)
        for org in self.reversed_adj_list[z]:
            self.remove_edge(org, z)
        self.reversed_adj_list.pop(z)

        self.vertex.remove(z)
        self.V -= 1
        self.vis.pop(z)
        self.__change_log.append(("rm_vertex", z))

    def remove_edge(self, u, v):
        assert u in self.vertex
        assert v in self.vertex
        assert v in self.adj_list[u]
        self.E -= 1
        self.adj_list[u].remove(v)
        self.reversed_adj_list[v].remove(u)
        self.__change_log.append(("rm_edge", u, v))

    def in_degree(self, v):
        return len(self.reversed_adj_list[v])

    def out_degree(self, v):
        return len(self.adj_list[v])

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
        return isinstance(other, Graph) and self.V == other.V and self.E == other.E \
               and self.vertex == other.vertex and self.adj_list == other.adj_list

from collections import deque
from Program.dynamic_Inc_APSP.Graph import Graph
from Program.dynamic_Inc_APSP.PathPresence import PathPresence


class SlobbeAlgorithm:
    @staticmethod
    def __find_affected_sources(path : PathPresence, graph: Graph, u: int, v: int):
        # Implementation based on the algo 4 of Slobbe paper
        S = set()  # affected source
        S.add(u)
        graph.vis = {v: False for v in graph.vertex}  # Reset vis(·) to false
        if not path.is_path(u, v):  # w < self.dist(u,v)
            Q = deque()
            Q.append(u)
            graph.vis[u] = True
            while len(Q) > 0:
                x = Q.popleft()
                for z in graph.reversed_adj_list[x]:
                    if not graph.vis[z] and not path.is_path(z, v) and path.is_path(z, u):  # dist(z, v) > dist(z,u) + w
                        Q.append(z)
                        graph.vis[z] = True
                        S.add(z)
            graph.vis = {v: False for v in graph.vertex}  # Reset vis(·) to false
        return S

    @staticmethod
    def APSP_edge(path: PathPresence, graph: Graph, u: int, v: int):
        """
        Ajout non trivial d'une arete dans le graph
        :param graph: a Data_Structure graph
        :param u: number of the node
        :param v: number of the node
        :return:
        """
        # ajout d'un edge entre 2 vertex dejà existant u,v:
        # - w est defini par la difference de temps entre u et v
        # - si il existait deja un moyen de joindre v à patir de u , dist(u,v) = difference de temps entre u et v = w
        # - mis à jour inutile si il existe deja un chemin entre u et v
        # - METTRE A JOUR UNIQUEMENT SSI DIST(U,V) = -1

        # algo 1
        if not path.is_path(u, v):
            S, P = {}, {}
            S[v] = SlobbeAlgorithm.__find_affected_sources(path, graph, u, v)
            path.set_is_path(u, v, True)
            Q = deque()
            P[v] = v
            Q.append(v)
            graph.vis[v] = True
            while len(Q) > 0:
                y = Q.popleft()
                # update distances for source nodes
                for x in S.get(P[y], []):
                    if not path.is_path(x, y):
                        path.set_is_path(x, y, True)
                        if y != v:
                            if y not in S: S[y] = set()
                            S[y].add(x)

                # enqueue all neighbors that get closer to u
                for w in graph.adj_list[y]:
                    if not graph.vis[w] and not path.is_path(u, w):
                        Q.append(w)
                        graph.vis[w] = True
                        if w in P: print("error P should be a set")
                        P[w] = y

    @staticmethod
    def APSP_vertex(path : PathPresence, graph : Graph, z):
        #TODO contient potentiellement une erreur pour les boucle (ie si z possede une arête vers lui-meme)

        S, P = {}, {}                       # S : sources
        S[z] = set()
        Q = deque()
        # find sources
        Q.append(z)
        while len(Q) > 0:
            x = Q.popleft()
            for q in graph.reversed_adj_list[x]:
                if not path.is_path(q, z):
                    path.set_is_path(q, z, True)
                    Q.append(q)
                    S[z].add(q)

        Q.append(z)
        while len(Q) > 0:
            y = Q.popleft()
            if y != z:
                S[y] = set()
                for x in S[P[y]]:
                    if not path.is_path(x, y):
                        path.set_is_path(x, y, True)
                        S[y].add(x)

            for w in graph.adj_list[y]:
                if not path.is_path(z, w):
                    Q.append(w)
                    if w in P: print("\nerror2 P should be a set\n")
                    P[w] = y
                    path.set_is_path(z, w, True)

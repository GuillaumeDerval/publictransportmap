import json

from Program.dynamic_Inc_APSP.Slobbe import SlobbeAlgorithm
from Program.dynamic_Inc_APSP.Graph import Graph
from Program.dynamic_Inc_APSP.PathPresence import PathPresence
from Program.dynamic_Inc_APSP.MinimumTime import MinimumTime

from Program.Data_manager.path import Parameters
from Program.Map import MyMapStop
from Program.DistanceAndConversion import distance_Eucli


class Dynamic_APSP:
    def __init__(self, param: Parameters, path=None):
        if path is None:
            path = param.PATH.GRAPH_TC_WALK
        with open(path) as file:
            out = json.loads(file.read())
        self.param = param
        self.graph = Graph(out)
        self.idx_to_name = out["idx_to_name"]
        self.name_to_idx = {x: i for i, x in enumerate(self.idx_to_name)}
        self.max_time = out["max_time"]
        self.used_time = out["used_times"]
        assert len(self.used_time) == len(self.idx_to_name) == len(self.name_to_idx)
        # sort used_time by time
        for used in self.used_time:
            used.sort()

        self.path = PathPresence(self.graph, self.max_time)
        self.distance = MinimumTime(self.name_to_idx, self.idx_to_name, self.max_time, self.used_time, self.path)

        self.map: MyMapStop = param.MAP()

        # reversible state -> record change
        self.__change_log = []
        self.__stack_log = []

    def add_vertex(self, z_name, z_time, z_position, z_stop_in=None, z_stop_out=None, z_stop_except = None):

        """

        :param z_name:
        :param z_time:
        :param z_position: en lambert , peut etre None si le stop_time etait deja cree
        :param z_stop_in:  [(name_in1, time_in1),...] name_in should be a already generated stop
        :param z_stop_out: [(name_out1, time_out1),...] name_out should be a already generated stop
        :return:
        """
        if z_stop_in is None : z_stop_in = []
        if z_stop_out is None: z_stop_out = []
        if z_stop_except is None: z_stop_except = []

        self.distance.up_to_date = False


        # if the node is alreaddy created, simply add edge
        if z_name in self.name_to_idx and z_time in self.used_time[self.name_to_idx[z_name]]:
            # algo don't work, add edge one after the other
            z_idx = self.name_to_idx[z_name]
            for name_in, time_in in z_stop_in:
                self.add_edge(name_in, time_in, z_name, z_time)
            for name_out, time_out in z_stop_out:
                self.add_edge(z_name, z_time, name_out, time_out)
            return z_idx

        else:
            z_idx = self.__add_vertex_in_structure(z_name, z_time, z_position)
            z = z_idx * self.max_time + z_time
            #print("id ", z_idx)

            # add vertex for the nodes in Z_in/Z_out if they don't exist
            for s_name, s_time in z_stop_in:
                assert s_time <= z_time
                assert s_name in self.name_to_idx
                self.add_vertex(s_name, s_time, None, z_stop_except = z_stop_except + [(z_name,z_time)])

            for d_name, d_time in z_stop_out:
                assert d_time >= z_time
                assert d_name in self.name_to_idx
                self.add_vertex(d_name, d_time, None, z_stop_except = z_stop_except + [(z_name,z_time)])

            # Permettre a l'utilisateur de rester sur place et d'attendre le prochain TC
            if z_name in self.name_to_idx:
                i = 0
                while i < len(self.used_time[z_idx]) and self.used_time[z_idx][i] != z_time:
                    i += 1
                if i > 0:
                    z_time_inf = self.used_time[z_idx][i - 1]
                    z_stop_in.append((z_name, z_time_inf))
                if i + 1 < len(self.used_time[z_idx]):
                    z_time_supp = self.used_time[z_idx][i + 1]
                    z_stop_out.append((z_name, z_time_supp))

            # Allow the user to walk between stops
            walk_in, walk_out = self.__walking_edges(z_name, z_time, z_position)

            # conversion name, time, pos -> node
            z_in = [self.name_to_idx[n] * self.max_time + t for n, t in z_stop_in + walk_in]
            z_out = [self.name_to_idx[n] * self.max_time + t for n, t in z_stop_out + walk_out]

            #remove edge in z_except (they will be added later)
            for n,t in z_stop_except:
                expt = self.name_to_idx[n] * self.max_time + t
                if expt in z_in: z_in.remove(expt)
                if expt in z_out: z_out.remove(expt)

            #Add edge to the graph structure
            for i in z_in:
                self.graph.add_edge(i, z)
                #print("add edge,", i, " to ",z)
            for o in z_out:
                self.graph.add_edge(z, o)
                #print("add edge,", z, " to ", o)

            # computations

            SlobbeAlgorithm.APSP_vertex(self.path, self.graph, z)
        return z_idx

    def add_edge(self, u_stop_name, u_time,  v_stop_name, v_time, u_position=None, v_position=None):  #todo tester l'efficacité de separer en plusieur cas
        assert v_time >= u_time
        self.distance.up_to_date = False


        u_id = self.add_vertex(u_stop_name, u_time, u_position)
        v_id = self.add_vertex(v_stop_name, v_time, v_position)
        u = u_id * self.max_time + u_time
        v = v_id * self.max_time + v_time
        #print("add edge fonction ", u, " to ", v)

        # w = v % self.__max_time - u % self.__max_time
        self.graph.add_edge(u, v)
        # 4 cas sont possibles lors de l'ajout d'aret :

        # cas 1 : u->v doesn't impact the rest of the graph
        if self.graph.in_degree(u) == 0 and self.graph.out_degree(v) == 0:
            self.path.set_is_path(u, v, True)

        # cas 2 : no path to u
        elif self.graph.in_degree(u) == 0:
            # if path v-> . then dist(u, . ) = dist(v,.) + dist(u,v)
            self.path.or_in_place(u, v)

        # cas 3 : no path continue from v
        elif self.graph.out_degree(v) == 0:
            # for node x :compute dist v a partir de dist(.,u)
            for x in self.graph.vertex:
                is_path_u = self.path.is_path(x, u)
                if is_path_u:
                    self.path.set_is_path(x, v, True)

        # cas 4 : neither u neither v is a leaf
        else:
            SlobbeAlgorithm.APSP_edge(self.path, self.graph, u, v)

    def dist(self, s_name: str, d_name: str) -> float:
        """
        Return the minimal distance between u_name and v_name
        """
        return self.distance.dist(s_name, d_name)

    def dist_from(self, s_name: str) -> list:
        """
        Return the list of the minimal distance from source  s (id)
        """
        return self.distance.dist_from(s_name)

    def hard_save_distance(self, out_directory_path=None):
        if out_directory_path is None: out_directory_path=self.param.PATH.MINIMAL_TRAVEL_TIME_TC
        self.distance.hard_save(out_directory_path)

    def hard_save_is_reachable(self, out_directory_path=None):
        if out_directory_path is None: out_directory_path = self.param.PATH.MINIMAL_TRAVEL_TIME_TC
        self.path.hard_save(out_directory_path)

    def hard_save_graph(self, out_path=None):
        if out_path is None: out_path = self.param.PATH.GRAPH_TC_WALK
        with open(out_path, 'w') as out_file:
            graph = {}
            for key, value in self.graph.adj_list.items():
                l = []
                for i in value:
                    if i != int(key):
                        l.append(i)
                graph[key] = l
            json.dump({"idx_to_name": self.idx_to_name, "max_time": self.max_time,
                       "graph": graph, "used_times": self.used_time
                       }, out_file)

    def save(self):
        self.graph.save()
        self.path.save()
        self.distance.save()
        self.map.save()
        #todo save new positions

        self.__stack_log.append(self.__change_log)
        self.__change_log = []

    def restore(self):
        self.graph.restore()
        self.path.restore()
        self.distance.restore()
        self.map.restore()

        self.__change_log.reverse()
        for log in self.__change_log:
            if log[0] == "add_name":
                self.name_to_idx.pop(log[1])
                self.idx_to_name.pop()
                self.used_time.pop()
            elif log[0] == "add_time":
                idx = self.name_to_idx[log[1]]
                self.used_time[idx].remove(log[2])
            else:
                raise Exception("Unhandeled log")

        self.__change_log = self.__stack_log.pop()

    def get_changes(self):
        """
        Return the change done from the last save
        retourne l'ensemble de nouvelle valeur de is_reach, leur stop_name est indique par les cle du dictionnaire
        (new_value, old_value)
        :return: A dictionnary : {"size": (new_number_of_stop, old_number of stop),
                                  "added_stop_name": [added_stop_name1 , ...]
                                  "change_distance": {org_name : {dest_name : (new_dist, old_dist)}}
        """
        changes = self.distance.get_changes()
        # old_size = changes["size"][1]
        return changes

    # ################################################################################################################

    def __add_vertex_in_structure(self, stop_name: str, time: int, position: (float, float)):
        if stop_name in self.name_to_idx:
            idx = self.name_to_idx[stop_name]
            z = idx * self.max_time + time
            if time in self.used_time[idx]:
                return idx
            else:
                self.used_time[idx].append(time)
                self.used_time[idx].sort()
                self.__change_log.append(("add_time", stop_name, time))
        else:
            assert position is not None
            idx = len(self.name_to_idx)
            self.idx_to_name.append(stop_name)
            self.map.add_stop(stop_name, position)
            self.name_to_idx[stop_name] = idx
            z = idx * self.max_time + time
            self.used_time.append([time])
            self.__change_log.append(("add_name", stop_name))
            self.__change_log.append(("add_time", stop_name, time))

        self.graph.add_vertex(z)
        self.path.add_vertex(z)
        self.distance.up_to_date = False

        return idx

    def __walking_edges(self, z_name, z_time, z_position=None):
        # get position of the node
        if z_name in self.name_to_idx:
            z_position = self.map.get_stop(z_name)[1]
        else:
            assert z_position is not None

        # walking : find each node reachable thanks to walk
        reachable_stop = self.map.get_reachable_stop_pt(z_position)
        walk_in = []
        walk_out = []
        for walk_name, walk_pos in reachable_stop:
            walk_idx = self.name_to_idx[walk_name]
            walking_time = distance_Eucli(z_position, walk_pos) / self.param.WALKING_SPEED()
            if walking_time <= self.param.MAX_WALKING_TIME():
                i = len(self.used_time[walk_idx]) - 1
                while i >= 0 and self.used_time[walk_idx][i] + walking_time > z_time:
                    i -= 1
                if i >= 0 and walk_name != z_name:
                    #print("used time ", self.used_time[walk_idx],"walk time", walking_time)
                    #print("dynamic in",walk_name, "time: ", self.used_time[walk_idx][i],  " to ",z_name, " time", z_time)
                    walk_in.append((walk_name, self.used_time[walk_idx][i]))

                i = 0
                while i < len(self.used_time[walk_idx]) and self.used_time[walk_idx][i] < z_time + walking_time:
                    i += 1
                if i < len(self.used_time[walk_idx]) and walk_name != z_name:
                    #print("dynamic out", z_name, z_time," to ", walk_name, self.used_time[walk_idx][i])
                    walk_out.append((walk_name, self.used_time[walk_idx][i]))
        return walk_in, walk_out

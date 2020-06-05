import numpy as np
from math import inf
import json
from Program.dynamic_Inc_APSP.PathPresence import PathPresence
import os

class MinimumTime:

    # !!! attention le distance sont mise à jour seulement après un appel a update()

    def __init__(self, name_to_idx, idx_to_name, max_time, used_time, path_presence, load_path = None):
        self.name_to_idx = name_to_idx
        self.idx_to_name = idx_to_name
        self.max_time = max_time
        self.used_time = used_time                          #used node are sorted by time
        self.is_reachable: PathPresence = path_presence
        self.size: int = len(name_to_idx)
        self.__true_size = self.size
        self.distance = [np.full((self.size,), -1, dtype=np.int) for _ in range(self.size)]
        if load_path is not None:
            self.up_to_date = True
            self.__load_data(load_path)
        else:
            self.up_to_date = True
            self.__compute_times()
        self.__backup = {"size": self.size, "change_distance": {}}
        self.__backup_stack = []  # permet de faire une recherche sur plusieur etage

    def __compute_times(self):
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
                            time = dtime - stime
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
        if not self.up_to_date:
            self.update()
        if s_name not in self.name_to_idx or d_name not in self.name_to_idx:
            return -1
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
        if not self.up_to_date: self.update()
        assert  s_name in self.name_to_idx
        s_idx = self.name_to_idx[s_name]
        return self.distance[s_idx][:self.size], self.name_to_idx

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
            return distance, self.name_to_idx
        else:
            s_idx = self.name_to_idx[s_name]
            return self.distance[s_idx], self.name_to_idx

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
            self.size = self.size + 1

    def update(self):
        if not self.up_to_date:
            self.up_to_date = True
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
        retourne l'ensemble de nouvelle valeur de is_reach, leur stop_name est indique par les cle du dictionnaire
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

        for f_rm in os.listdir(out_directory_path):
            os.remove(out_directory_path + f_rm)

        for idx in range(self.size):
            name = self.idx_to_name[idx]
            data = self.distance[idx]
            np.save(out_directory_path + name + ".npy", data.astype(np.int16))

        with open(out_directory_path + "__conversion.json", "w") as out:
            json.dump(self.name_to_idx, out)

    def __load_data(self, path):
        with open(path + "__conversion.json", "r") as f:
            self.name_to_idx = json.load(f)
            self.size = len(self.name_to_idx)
            self.idx_to_name = [0]* self.size
            for x, i in self.name_to_idx.items():
                self.idx_to_name[i] = x
        for name in self.idx_to_name:
            file = path + str(name) + ".npy"
            is_path_list = np.load(file)
            self.distance[self.name_to_idx[name]] = is_path_list


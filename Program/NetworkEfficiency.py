from Program.Data_manager.path import Parameters
from Program.dynamic_Inc_APSP.Dynamic_Incremental_All_Pair_Shortest_Path import Dynamic_APSP
from Program.metric.monte_carlo_dynamic import TravellersModelisation
from Program.Data_manager.main import time_str_to_int
from Program.DistanceAndConversion import distance_Eucli
import random as rdm



class NetworkEfficiency:
    """

    """

    def __init__(self, param: Parameters, c=1, load_data=False, seed = None):
        self.param: Parameters = param
        self.APSP: Dynamic_APSP = Dynamic_APSP(param, load=load_data)
        self.metric = TravellersModelisation(param, self.APSP, C=c, my_seed= seed)

    #def getMap(self):
    #    return self.param.MAP()
    def get_value(self):
        return self.metric.total_results.mean()

    def modify(self, modification):
        modification.run(APSP=self.APSP)
        self.metric.update(changes=self.APSP.get_changes())
        new_value = self.metric.total_results.mean()
        return new_value

    def save(self):
        self.APSP.save()
        self.metric.save()

    def restore(self):
        self.APSP.restore()
        self.metric.restore()

    def hard_save(self):
        self.APSP.hard_save()


class NetworkModification:
    """ template for modifications"""

    def run(self, APSP: Dynamic_APSP):
        """ execute the modification on the APSP given in argument"""
        pass


class AddConnexion(NetworkModification):
    """
    Object used by NetworkEffficiency to add a connexion between 2 stops : source -> destination
    """

    def __init__(self, source_name, source_time, destination_name, destination_time,
                 source_position=None, destination_position=None):
        """
        Generate an AddConnexions object
        :param source_name: name of the stop where the connexion start             ex: stib32,tecBaegm501, ...
        :param source_time: [int] time in minutes a which the  public transport leaves the source. Ex: 620 for 10:20 AM
        :param destination_name: name of the stop where connexion arrives             ex: stib32,tecBaegm501, ...
        :param destination_time: [int] time  in minutes a which the  public transport arrives in the destination  .
        :param source_position: position of the source in Lambert. Don't fill if the source already exist
        :param destination_position: position of the destination in Lambert. Don't fill if the source already exist
        """
        super()
        self.source_name = source_name
        self.source_time = source_time
        self.source_position = source_position
        self.destination_name = destination_name
        self.destination_time = destination_time
        self.destination_position = destination_position

    def run(self, APSP:Dynamic_APSP):
        """
        Execute the modification : adding an edge to the given network.
        :param APSP: a Dynamic_APSP object used to modified the network structure and compute shortest paths
        """
        super().run(APSP)
        APSP.add_edge(self.source_name, self.source_time, self.destination_name, self.destination_time,
                      self.source_position, self.destination_position)

    def __str__(self):
        return "{},{} -> {},{}".format(self.source_name, self.source_time, self.destination_name, self.destination_time)


class AddLine(NetworkModification):
    """
    Object used by NetworkEffficiency to add a line composed by multiple connexion between stops.
    """

    def __init__(self, station_list):
        """
        Generate an AddLine object
        :param station_list : ordered list of station into which a new public transport line will pass through.
                              it should have the form
                               [(name1, time_arr_1, time_departure_1, position1) ,  ...]
                              ordered by increasing time

                              where
                              - namei is name of a stop     ex: stib32,tecBaegm501, ...
                              - time_arr_i is an interger representing the time in mintues
                                         where the transport arrives at the stop   Ex: 620 for 10:20 AM
                              - time_departure_i idem for departure
                              - positioni is position of the stop in Lambert. None if the stop already exist

        """
        super()
        self.station_List = station_list
        for i in range(len(self.station_List)-1):
            _, s_arr, s_departure, _ = self.station_List[i]
            _, d_arr, d_departure, _ = self.station_List[i+1]
            assert s_arr <= s_departure <= d_arr <= d_departure

    def run(self, APSP: Dynamic_APSP):
        """
        Execute the modification : adding an edge to the given network.
        :param APSP: a Dynamic_APSP object used to modified the network structure and compute shortest paths
        """
        super().run(APSP)
        for i in range(len(self.station_List)-1):
            s_name, _, s_time, s_position = self.station_List[i]
            d_name, d_time, _, d_position = self.station_List[i+1]
            APSP.add_edge(s_name, s_time, d_name, d_time, s_position, d_position)

    def __str__(self):
        s = ""
        for i in range(len(self.station_List)-1):
            s_name, _, s_time, s_position = self.station_List[i]
            d_name, d_time, _, d_position = self.station_List[i+1]
            s = s + "{},{} ->  {},{}  ".format(s_name, s_time, d_name, d_time)

        return s


class AddRandomConnexion(NetworkModification):

    def __init__(self, new_node=True, do_print=False):
        self.new_node = new_node
        self.print = do_print

    def run(self,APSP):
        name1 = rdm.sample(APSP.idx_to_name, 1).pop()
        name2 = rdm.sample(APSP.idx_to_name, 1).pop()
        pos1 = APSP.map.stop_position_dico[name1]
        pos2 = APSP.map.stop_position_dico[name2]
        dist = distance_Eucli(pos1, pos2)
        speed = rdm.uniform(10, 20)
        travel_time = dist / speed

        if self.new_node:
            start, end = time_str_to_int("06:00:00") // 60, math.floor(
                (time_str_to_int("10:30:00") // 60) - travel_time)
            if end >= start:
                time1 = rdm.randint(start, end)
                time2 = time1 + round(travel_time)
            else:
                return self.run(APSP)

        else:
            # verifie qu'il est possible de crée un  nouvelle ligne respectant le condition avec des noeud preexistant
            if len(APSP.used_time[APSP.name_to_idx[name1]]) >= 1 and len(
                    APSP.used_time[APSP.name_to_idx[name2]]) >= 1 and APSP.used_time[APSP.name_to_idx[name1]][0] + travel_time <= APSP.used_time[APSP.name_to_idx[name2]][-1]:
                last_time1 = APSP.used_time[APSP.name_to_idx[name2]][-1] - travel_time
                possible_time = APSP.used_time[APSP.name_to_idx[name1]].copy()
                possible_time = [t for t in possible_time if t <= last_time1]
                assert len(possible_time) > 0
                time1 = rdm.sample(possible_time, 1).pop()
                # time2 = time1 + travel_time
                for t in APSP.used_time[APSP.name_to_idx[name2]]:
                    if t >= time1 + travel_time:
                        time2 = t
                        break
            else:
                return self.run(APSP)

        if self.print:
            print("add edge {} time {} to {} time {}".format(name1, time1, name2, time2))
        APSP.add_edge(name1, time1, name2, time2, u_position=None, v_position=None)

    def __str__(self):
        return "random connexion"



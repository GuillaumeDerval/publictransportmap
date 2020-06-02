from Program.Data_manager.path import Parameters
from Program.dynamic_Inc_APSP.Dynamic_Incremental_All_Pair_Shortest_Path import Dynamic_APSP
from Program.metric.monte_carlo_dynamic import TravellersModelisation


class NetworkEfficiency:
    """

    """

    def __init__(self, param: Parameters, c=1, load_data=False):
        self.param: Parameters = param
        self.APSP: Dynamic_APSP = Dynamic_APSP(param, load=load_data)
        self.metric = TravellersModelisation(param, self.APSP, C=c)

    #def getMap(self):
    #    return self.param.MAP()

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
        self.APSP.hard_save_graph()
        self.APSP.hard_save_is_reachable()
        self.APSP.hard_save_distance()


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



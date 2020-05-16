import time
import Program.metric.BuildMyMap as BMap
import Program.metric.monte_carlo_dynamic as MC
from Program.Data_manager.main import DataManager
from Program.Data_manager.path import Parameters
from Program.dynamic_Inc_APSP.Dynamic_Incremental_All_Pair_Shortest_Path import Dynamic_APSP



def produce_map(localisation_name, transport = "train_bus", C = 1, localisation_list =None, load = False):
    t = time.time()
    if localisation_list is not None:
        DataManager.reduce_data(data_path, localisation_list,localisation_name,transport)

    param: Parameters = DataManager.produce_data(data_path, localisation_name, "train_bus")
    print("comput dist ", time.time() - t)
    distance_oracle = Dynamic_APSP(param,load=load)
    print("compute metric ",time.time() - t)
    metric = MC.TravellersModelisation(param, distance_oracle, C=C, my_seed=1)

    # todo process map before ?
    print("build map ",time.time() - t)
    BMap.travel_time_shape_map(param, metric)
    BMap.munty_shape_map(param)
    BMap.map_stop(param)
    print("end ",time.time() - t)


if __name__ == '__main__':
    data_path = "/Users/DimiS/Documents/Gotta_go_fast/Project/Data"
    print("start")
    produce_map("Nivelles")
    print("end")




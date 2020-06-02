import time
import csv
import math
from statistics import mean, stdev
from Program.Data_manager.main import make_data_structure, time_str_to_int
from Program.Data_manager.path import PATH_BELGIUM
from Test.Test_dynamic_inc_APSP.my_utils import *
from Program.Map import MyMap
from Program.metric.monte_carlo_dynamic import TravellersModelisation
from Program.NetworkEfficiency import *


def TimeInterval():
    # Nombre d'arete en fonction de la tranche horaire partout en Belgique( Train , Bus, both)
    # On veut que le temps de départ soit dans l'interval.
    data_path = "/User s/DimiS/Documents/Gotta_go_fast/Project/Program/Performance"
    train = open(data_path + "/Result/TimeIntervalTrain.csv","w")
    bus = open(data_path + "/Result/TimeIntervalBus.csv", "w")
    trainbus = open(data_path + "/Result/TimeIntervalTrainBus.csv", "w")
    train.write("start;end;node;edge\n")
    bus.write("start;end;node;edge\n")
    trainbus.write("start;end;node;edge\n")
    for h in range(0, 25):
        for file_name in os.listdir(data_path +"/TemporalDir/intermediate/"):
            os.remove(data_path +"/TemporalDir/intermediate/"+ file_name)
        make_data_structure(data_path)
        start_time = time_str_to_int("{}:00:00".format(h))
        end_time = time_str_to_int("{}:00:00".format(h+1))
        DataManager.produce_data_belgium(data_path+ "/TemporalDir", start_time=start_time, end_time=end_time)

        res = open(data_path + "/TemporalDir/intermediate/train_only.json","r")
        dico = json.load(res)
        V = sum(len(dico[k]["nei"])>0 for k in dico.keys())
        E = sum([len(dico[k]["nei"]) for k in dico.keys()])
        train.write("{};{};{};{}\n".format(h,h+1,V, E))
        res.close()

        res = open(data_path + "/TemporalDir/intermediate/bus_only.json","r")
        dico = json.load(res)
        V = sum(len(dico[k]["nei"]) > 0 for k in dico.keys())
        E = sum([len(dico[k]["nei"]) for k in dico.keys()])
        bus.write("{};{};{};{}\n".format(h,h+1,V, E))
        res.close()

        res = open(data_path + "/TemporalDir/intermediate/train_bus.json","r")
        dico = json.load(res)
        V = sum(len(dico[k]["nei"]) > 0 for k in dico.keys())
        E = sum([len(dico[k]["nei"]) for k in dico.keys()])
        trainbus.write("{};{};{};{}\n".format(h,h+1, V, E))
        res.close()


def reduce_all():
    def list_arrodissement():
        arrodisement_set = set()
        with open(path_Belgium.RSD_WORK, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='|')
            for row in reader:
                arrodisement_set.add(row["TX_ADM_DSTR_RESIDENCE_DESCR_FR"])
                arrodisement_set.add(row["TX_ADM_DSTR_WORK_DESCR_FR"])
        return list(arrodisement_set)

    arrondissement_list = list_arrodissement()
    arrondissement_list.sort()
    print(arrondissement_list)
    names = []
    for arrondissement in arrondissement_list[39:40]:
        name = arrondissement.replace("’", "e ").replace("Arrondissement de ", "")
        print(name)
        DataManager.reduce_data(data_path, arrondissement, name, "train_bus")
        names.append(name)
    names = list(names)
    names.sort()
    return names


def edge_node_by_arrondissement(names,transports):
    # ne compte pas le arrete des trajet à pied ni rester sur place
    out = open(result_path + "/ArrondVertexEdgeAll.csv","w")
    out.write("transport;arrondissementName;node;edge\n")
    for arr in names:
        for tr in transports:
            file = open(data_path + "/intermediate/" + arr + "_"+ tr +"/transport.json")
            dico = json.load(file)
            V = len(dico.keys()) # sum(len(dico[k]["nei"]) > 0 for k in dico.keys())
            E = sum([len(dico[k]["nei"]) for k in dico.keys()])
            out.write("{};{};{};{}\n".format(tr,arr, V, E))
            file.close()


# ###################################################################################################################

def generate_realist_random_edge(APSP, new_node):
    name1 = rdm.sample(APSP.idx_to_name, 1).pop()
    name2 = rdm.sample(APSP.idx_to_name, 1).pop()
    pos1 = APSP.map.stop_position_dico[name1]
    pos2 = APSP.map.stop_position_dico[name2]
    dist = distance_Eucli(pos1, pos2)
    speed = rdm.uniform(10, 20)
    travel_time = dist / speed

    if new_node:
        time1 = rdm.randint(time_str_to_int("06:00:00") // 60, (time_str_to_int("10:30:00") // 60) - travel_time)
        time2 = time1 + travel_time
    else:
        # verifie qu'il est possible de crée un  nouvelle ligne respectant le condition avec des noeud preexistant
        if len(APSP.used_time[APSP.name_to_idx[name1]]) >= 1 and len(APSP.used_time[APSP.name_to_idx[name2]]) >= 1 and APSP.used_time[APSP.name_to_idx[name1]][0] + travel_time <=  APSP.used_time[APSP.name_to_idx[name2]][-1]:
            last_time1 = APSP.used_time[APSP.name_to_idx[name2]][-1] - travel_time
            possible_time = APSP.used_time[APSP.name_to_idx[name1]].copy()
            possible_time = [t for t in possible_time if t <= last_time1]
            assert len(possible_time) > 0
            time1 = rdm.sample(possible_time, 1).pop()
            #time2 = time1 + travel_time
            for t in APSP.used_time[APSP.name_to_idx[name2]]:
                if t >= time1 + travel_time:
                    time2 = t
                    break
        else:
            generate_realist_random_edge(APSP, new_node)
            return

    print("add edge {} time {} to {} time {}".format(name1, time1, name2, time2))
    APSP.add_edge(name1, time1, name2, time2, u_position=None, v_position=None)


def generate_random_edge(APSP):
    name1 = rdm.sample(APSP.idx_to_name, 1).pop()
    if len(APSP.used_time[APSP.name_to_idx[name1]]) > 0:
        time1 = rdm.sample(APSP.used_time[APSP.name_to_idx[name1]], 1).pop()
    else :
        time1 = rdm.randint(time_str_to_int("06:00:00") // 60, time_str_to_int("10:30:00") // 60)
    name2 = rdm.sample(APSP.idx_to_name, 1).pop()
    possible_time = []
    for t in APSP.used_time[APSP.name_to_idx[name2]]:
        if t >= time1:
            possible_time.append(t)
    if len(possible_time) > 0:
        time2 = rdm.sample(possible_time, 1).pop()
    else:
        time2 = rdm.randint(time1, time_str_to_int("10:30:00")//60)
    #print("add edge {} time {} to {} time {}".format(name1, time1, name2, time2))
    APSP.add_edge(name1, time1, name2, time2, u_position=None, v_position=None)


def generate_random_vertex_new_pos(APSP):
    # New position
    z_name = str(rdm.random())  # on pourrait avoir 2 fois le meme nom mais c'est improbable + pas grave
    time = rdm.randint(time_str_to_int("06:00:00")//60, time_str_to_int("10:30:00")//60)
    pos = rdm_point_shape(APSP.param)
    #print("add vertex {} time {} pos {} :  z_in {} , z_out {}".format(z_name, time, pos, [],[]))
    APSP.add_vertex(z_name, time, pos)


def generate_random_vertex_old_pos(APSP):
    #mmap = MyMap.get_map(APSP.param)
    # New position
    z_name = rdm.sample(APSP.idx_to_name, 1).pop()
    time = rdm.randint(time_str_to_int("06:00:00")//60, time_str_to_int("10:30:00")//60)
    #pos = mmap.stop_position_dico[z_name]
    #print("add vertex {} time {} pos {} :  z_in {} , z_out {}".format(z_name, time, pos, [],[]))
    APSP.add_vertex(z_name, time, None)

# #####################################################################################################################


def time_static_dynamic(names, transports):
    max_walking_time = 30
    walking_speed = 3.2
    MAX_TIME = 12 * 60

    out = open(result_path + "/TimeStaticDynamic2.csv", "w")
    out.write("transport;localisation;type;mean;stderr\n")

    for tr in transports:
        print("transport : ", tr)
        for n in names:
            print(n)
            times = {"static": [], "dynamic_edge_new": [], "dynamic_edge_old": [], "dynamic_vertex_new": [], "dynamic_vertex_old": []}


            # Add edge with old nodes
            time.sleep(20)
            param = DataManager.produce_data(data_path, n, tr, max_walking_time, walking_speed, MAX_TIME)
            start_time = time.time()
            APSP = Dynamic_APSP(param)
            times["static"].append(time.time() - start_time)
            time.sleep(40)
            for i in range(25):
                start_time = time.time()
                generate_realist_random_edge(APSP, new_node=False)
                times["dynamic_edge_old"].append(time.time() - start_time)
            MyMap.belgium_map = None
            print("{};{};{};{};{}\n".format(tr, n, "static", mean(times["static"]),-1))
            print("{};{};{};{};{}\n".format(tr, n, "dynamic_edge_old", mean(times["dynamic_edge_old"]),
                                                stdev(times["dynamic_edge_old"]) / 5))

            # Add edge with new nodes
            time.sleep(20)
            param = DataManager.load_data(data_path, n, tr)
            start_time = time.time()
            APSP = Dynamic_APSP(param)
            times["static"].append(time.time() - start_time)
            time.sleep(40)
            for i in range(25):
                start_time = time.time()
                generate_realist_random_edge(APSP, new_node=True)
                times["dynamic_edge_new"].append(time.time() - start_time)
            MyMap.belgium_map = None
            print("{};{};{};{};{}\n".format(tr, n, "dynamic_edge_new", mean(times["dynamic_edge_new"]),
                                            stdev(times["dynamic_edge_new"]) / 5))

            # Vertex old add
            time.sleep(20)
            param = DataManager.load_data(data_path, n, tr)
            start_time = time.time()
            APSP = Dynamic_APSP(param)
            times["static"].append(time.time() - start_time)
            time.sleep(40)
            for i in range(25):
                start_time = time.time()
                generate_random_vertex_old_pos(APSP)
                times["dynamic_vertex_old"].append(time.time() - start_time)
            MyMap.belgium_map = None
            print("{};{};{};{};{}\n".format(tr, n, "dynamic_vertex_old", mean(times["dynamic_vertex_old"]),
                                            stdev(times["dynamic_vertex_old"]) / 5))


            # Vertex new add
            time.sleep(20)
            param = DataManager.load_data(data_path, n, tr)
            start_time = time.time()
            APSP = Dynamic_APSP(param)
            times["static"].append(time.time() - start_time)
            time.sleep(40)
            for i in range(25):
                start_time = time.time()
                generate_random_vertex_new_pos(APSP)
                times["dynamic_vertex_new"].append(time.time() - start_time)
            MyMap.belgium_map = None
            print("{};{};{};{};{}\n".format(tr, n, "dynamic_vertex_new", mean(times["dynamic_vertex_new"]),
                                                stdev(times["dynamic_vertex_new"]) / 5))

            print("{};{};{};{};{}\n".format(tr, n, "static", mean(times["static"]),
                                            stdev(times["static"]) / math.sqrt(4)))


            out.write("{};{};{};{};{}\n".format(tr, n, "static", mean(times["static"]), stdev(times["static"])/math.sqrt(4)))
            out.write("{};{};{};{};{}\n".format(tr, n, "dynamic_edge_new", mean(times["dynamic_edge_new"]), stdev(times["dynamic_edge_new"])/5))
            out.write("{};{};{};{};{}\n".format(tr, n, "dynamic_edge_old", mean(times["dynamic_edge_old"]), stdev(times["dynamic_edge_old"]) / 5))
            out.write("{};{};{};{};{}\n".format(tr, n, "dynamic_vertex_new", mean(times["dynamic_vertex_new"]), stdev(times["dynamic_vertex_new"])/5))
            out.write("{};{};{};{};{}\n".format(tr, n, "dynamic_vertex_old", mean(times["dynamic_vertex_old"]), stdev(times["dynamic_vertex_old"])/5))


def max_walking_time_effect(names, transports):
    out1 = open(result_path + "/WalkingTimeEffectVertex.csv", "w")
    out1.write("transport;localisation;max_time;mean;all\n")
    out2 = open(result_path + "/WalkingTimeEffectInit.csv", "w")
    out2.write("transport;localisation;max_time;value\n")
    for n in names:
        for tr in transports:
            for max_walking_time in range(0, 61, 5):
                walking_speed = 3.2
                MAX_TIME = 12 * 60
                print(n,"  ",max_walking_time)

                param = DataManager.produce_data(data_path, n, tr, max_walking_time, walking_speed, MAX_TIME)

                # Vertex old add
                start_time = time.time()
                APSP = Dynamic_APSP(param)
                t = time.time() - start_time
                out2.write("{};{};{};{}\n".format(tr, n, max_walking_time, t))

                times = []
                for i in range(50):
                    start_time = time.time()
                    generate_random_vertex_old_pos(APSP)
                    times.append(time.time() - start_time)
                out1.write("{};{};{};{};{}\n".format(tr, n, max_walking_time, sum(times) / 50, times))


def time_metric_vs_APSP(names):
    c = 1

    out = open(result_path + "/metricVsAPSP.csv", "w")
    out.write("localisation;type;value\n")

    for n in names:
        param = DataManager.load_data(data_path, n, "train_bus")
        t_metric = time.time()
        t_map = time.time()
        param.MAP()
        t_map = time.time() - t_map
        t_APSP = time.time()
        APSP: Dynamic_APSP = Dynamic_APSP(param, load=False)
        t_APSP = time.time() - t_APSP
        metric = TravellersModelisation(param, APSP, C=c)
        t_metric = time.time() - t_metric
        APSP.hard_save_is_reachable()
        APSP.hard_save_distance()
        out.write("{};{};{}\n".format(n,"carte", t_map))
        out.write("{};{};{}\n".format(n, "APSP", t_APSP))
        out.write("{};{};{}\n".format(n, "métrique", t_metric))
        out.write("{};{};{}\n".format(n, "valeur_métrique", metric.total_results.mean()))

def MC_reducing_factor(name = 'Dixmude'):
    c_values = [pow(10,(i/4)) for i in range(-3*4, 3*4)]
    out = open(result_path + "/MC_reducing_factor.csv", "w")
    out.write("localisation;c;times;values\n")

    for c in c_values:
        times = []
        values = []
        for i in range(10):
            param = DataManager.load_data(data_path, name, "train_bus")
            t = time.time()
            net = NetworkEfficiency(param,c,load_data=True)
            t = time.time() - t
            times.append(t)
            values.append(net.get_value())
        out.write("{};{};{}\n".format(name, c,times,values))


if __name__ == '__main__':
    #TimeInterval()
    data_path = "/Users/DimiS/Documents/Gotta_go_fast/Project/Data"
    result_path = "/Users/DimiS/Documents/Gotta_go_fast/Project/Program/Performance/Result"
    path_Belgium = PATH_BELGIUM(data_path)
    #   reduce_all()
    names = ['Alost', 'Anvers', 'Arlon', 'Ath', 'Audenarde', 'Bastogne', 'Bruges', 'Bruxelles-Capitale', 'Charleroi',
             'Courtrai', 'Dinant', 'Dixmude', 'Eeklo', 'Furnes', 'Gand', 'Hal-Vilvorde', 'Hasselt', 'Huy', 'Liège',
             'Louvain', 'Maaseik', 'Malines', 'Marche-en-Famenne', 'Mons', 'Mouscron', 'Namur', 'Neufchâteau',
             'Nivelles', 'Ostende', 'Philippeville', 'Roulers', 'Saint-Nicolas', 'Soignies', 'Termonde', 'Thuin',
             'Tielt', 'Tongres', 'Tournai', 'Turnhout', 'Verviers', 'Virton', 'Waremme', 'Ypres']

    names2 = ['Dixmude','Ath']#,'Tournai','Mons','Nivelles','Charleroi']#]#', 'Liège', 'Bruxelles-Capitale']
    transports = ["train_bus"] #,"bus_only","train_bus"]
    #edge_node_by_arrondissement(names, transports)

    #time_static_dynamic(names2, transports)
    #max_walking_time_effect(names2, ["train_bus"])
    time_metric_vs_APSP(names2)



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
from Program.Optimization import find_best_modification


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

def generate_realist_random_edge(APSP, new_node = True):
    name1 = rdm.sample(APSP.idx_to_name, 1).pop()
    name2 = rdm.sample(APSP.idx_to_name, 1).pop()
    pos1 = APSP.map.stop_position_dico[name1]
    pos2 = APSP.map.stop_position_dico[name2]
    dist = distance_Eucli(pos1, pos2)
    speed = rdm.uniform(10, 20)
    travel_time = dist / speed

    if new_node:
        start, end = time_str_to_int("06:00:00") // 60, math.floor((time_str_to_int("10:30:00") // 60) - travel_time)
        if end >= start:
            time1 = rdm.randint(start, end)
            time2 = time1 + round(travel_time)
        else:
            return generate_realist_random_edge(APSP, new_node)

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
            return generate_realist_random_edge(APSP, new_node)

    #print("add edge {} time {} to {} time {}".format(name1, time1, name2, time2))
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

    out = open(result_path + "/TimeStaticDynamic4.csv", "w")
    out.write("transport;localisation;type;mean;stderr\n")
    out.close()

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
            time.sleep(30)
            for i in range(25):
                time.sleep(10)
                APSP.save()
                start_time = time.time()
                generate_realist_random_edge(APSP, new_node=False)
                APSP.distance.update()
                times["dynamic_edge_old"].append(time.time() - start_time)
                APSP.restore()
            MyMap.belgium_map = None
            #print("{};{};{};{};{}\n".format(tr, n, "static", mean(times["static"]),-1))
            print("{};{};{};{};{}\n".format(tr, n, "dynamic_edge_old", mean(times["dynamic_edge_old"]),
                                                stdev(times["dynamic_edge_old"]) / 5))

            # Add edge with new nodes
            time.sleep(20)
            param = DataManager.load_data(data_path, n, tr)
            start_time = time.time()
            APSP = Dynamic_APSP(param)
            times["static"].append(time.time() - start_time)
            time.sleep(30)
            for i in range(25):
                time.sleep(10)
                APSP.save()
                start_time = time.time()
                generate_realist_random_edge(APSP, new_node=True)
                APSP.distance.update()
                times["dynamic_edge_new"].append(time.time() - start_time)
                APSP.restore()
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
                APSP.save()
                start_time = time.time()
                generate_random_vertex_old_pos(APSP)
                APSP.distance.update()
                times["dynamic_vertex_old"].append(time.time() - start_time)
                APSP.restore()
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
                APSP.save()
                start_time = time.time()
                generate_random_vertex_new_pos(APSP)
                APSP.distance.update()
                times["dynamic_vertex_new"].append(time.time() - start_time)
                APSP.restore()
            MyMap.belgium_map = None
            print("{};{};{};{};{}\n".format(tr, n, "dynamic_vertex_new", mean(times["dynamic_vertex_new"]),
                                                stdev(times["dynamic_vertex_new"]) / 5))

            print("{};{};{};{};{}\n".format(tr, n, "static", mean(times["static"]),
                                            stdev(times["static"]) / math.sqrt(4)))

            out = open(result_path + "/TimeStaticDynamic3.csv", "a")
            out.write("{};{};{};{};{}\n".format(tr, n, "static", mean(times["static"]), stdev(times["static"])/math.sqrt(4)))
            out.write("{};{};{};{};{}\n".format(tr, n, "dynamic_edge_new", mean(times["dynamic_edge_new"]), stdev(times["dynamic_edge_new"])/5))
            out.write("{};{};{};{};{}\n".format(tr, n, "dynamic_edge_old", mean(times["dynamic_edge_old"]), stdev(times["dynamic_edge_old"]) / 5))
            out.write("{};{};{};{};{}\n".format(tr, n, "dynamic_vertex_new", mean(times["dynamic_vertex_new"]), stdev(times["dynamic_vertex_new"])/5))
            out.write("{};{};{};{};{}\n".format(tr, n, "dynamic_vertex_old", mean(times["dynamic_vertex_old"]), stdev(times["dynamic_vertex_old"])/5))
            out.close()


def max_walking_time_effect_APSP(names, transports):
    #out1 = open(result_path + "/WalkingTimeEffectVertex.csv", "w")
    #out1.write("transport;localisation;max_time;mean;all\n")
    out2 = open(result_path + "/WalkingTimeEffectInit.csv", "w")
    out2.write("transport;localisation;max_time;value\n")
    out2.close()
    for n in names:
        for tr in transports:
            for max_walking_time in range(0, 61, 5):
                walking_speed = 3.2
                MAX_TIME = 12 * 60
                print(n,"  ",max_walking_time)

                param = DataManager.produce_data(data_path, n, tr,  max_walking_time, walking_speed, MAX_TIME)

                # Vertex old add
                t = time.time()
                APSP = Dynamic_APSP(param)
                t = time.time() - t
                out2 = open(result_path + "/WalkingTimeEffectInit.csv", "a")
                out2.write("{};{};{};{}\n".format(tr, n, max_walking_time, t))
                out2.close()

                #times = []
                #for i in range(50):
                #    start_time = time.time()
                #    generate_random_vertex_old_pos(APSP)
                #    times.append(time.time() - start_time)
                #out1.write("{};{};{};{};{}\n".format(tr, n, max_walking_time, sum(times) / 50, times))

def max_walking_time_effect_network(names):
    #out = open(result_path + "/WalkingTimeEffectInitNetwork.csv", "w")
    #out.write("localisation;max_time;time;value\n")
    #out.close()
    for n in names:
        for max_walking_time in range(55, 60, 5):
            walking_speed = 3.2
            MAX_TIME = 12 * 60
            print(n,"  ",max_walking_time)

            param = DataManager.produce_data(data_path, n, "train_bus", max_walking_time, walking_speed, MAX_TIME)

            # initialisation
            t = time.time()
            net = NetworkEfficiency(param, c=1, load_data=False)
            t = time.time() - t
            #out = open(result_path + "/WalkingTimeEffectInitNetwork.csv", "a")
            print("{};{};{};{}\n".format(n, max_walking_time, t, net.get_value()))
            #out.close()



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
        APSP.hard_save()
        out.write("{};{};{}\n".format(n,"carte", t_map))
        out.write("{};{};{}\n".format(n, "trajet dans le réseau de TC", t_APSP+t_map))
        out.write("{};{};{}\n".format(n, "métrique", t_metric))
        out.write("{};{};{}\n".format(n, "valeur_métrique", metric.total_results.mean()))


def MC_reducing_factor(name = 'Dixmude'):
    c_values = [pow(10,(i/4)) for i in range(-3*4, 1*4+1)]
    out1 = open(result_path + "/MC_reducing_factor_init.csv", "w")
    out1.write("localisation;c;time;value\n")
    out2 = open(result_path + "/MC_reducing_factor_modif.csv", "w")
    out2.write("localisation;modification;c;time;value\n")
    out3 = open(result_path + "/MC_reducing_factor_modif_delta.csv", "w")
    out3.write("localisation;modification;c;time;value\n")

    for c in c_values:
        print("c = ",c)
        for i in range(3):
            time.sleep(10)
            param = DataManager.load_data(data_path, name, "train_bus")
            t = time.time()
            net = NetworkEfficiency(param,c,load_data=True, seed = round(34536*c)+i)
            t2 = time.time() - t
            out1.write("{};{};{};{}\n".format(name, c, t2, net.get_value()))
            v = net.get_value()
            print("modif1")
            t = time.time()
            net.modify(AddConnexion("delijn42525", 438, "delijn90508", 440))
            t2 = time.time() - t
            out2.write("{};{};{};{};{}\n".format(name, "modif1", c, t2, net.get_value()))
            out3.write("{};{};{};{};{}\n".format(name,"modif1", c, t2, net.get_value()-v))
            v = net.get_value()
            print("modif2")
            t = time.time()
            net.modify(AddConnexion("delijn42296", 526, "delijn41729", 530))
            t2 = time.time() - t
            out2.write("{};{};{};{};{}\n".format(name, "modif2", c, t2, net.get_value()))
            out3.write("{};{};{};{};{}\n".format(name, "modif2", c, t2, net.get_value()-v))
            v = net.get_value()
            print("modif3")
            t = time.time()
            net.modify(AddConnexion("delijn87605", 404, "delijn42537", 418))
            t2 = time.time() - t
            out2.write("{};{};{};{};{}\n".format(name, "modif3", c, t2, net.get_value()))
            out3.write("{};{};{};{};{}\n".format(name, "modif3", c, t2, net.get_value()-v))

        #out2.write("{};{};{};{}\n".format(name, c, times, values))


def optimization_time(names):
    class modif_edge(NetworkModification):
        """ template for modifications"""

        def run(self, APSP: Dynamic_APSP):
            """ execute the modification on the APSP given in argument"""
            generate_realist_random_edge(APSP,True)


    c = 1
    out = open(result_path + "/optiTimeAbsolu.csv", "a")
    out.write("localisation;type;value\n")
    out.close()
    out2 = open(result_path + "/optiTimeRelative.csv", "a")
    out2.write("localisation;type;value\n")
    out2.close()

    for n in names:
        param = DataManager.load_data(data_path, n, "train_bus")

        #initialisation
        t_opti = time.time()
        t_metric_init = time.time()
        param.MAP()
        t_APSP_init = time.time()
        APSP: Dynamic_APSP = Dynamic_APSP(param, load=False)
        t_APSP_init = time.time() - t_APSP_init
        metric = TravellersModelisation(param, APSP, C=c)
        t_metric_init = time.time() - t_metric_init
        init = metric.total_results.mean()

        modifications =[modif_edge() for _ in range(15)]
        best = None
        min_value = math.inf
        t_metric_modif = 0
        t_APSP_modif = 0
        t_metric_revert = 0
        t_APSP_revert =0

        for modif in modifications:
            t = time.time()
            APSP.save()
            t_APSP_revert += (time.time() -t)
            metric.save()
            t_metric_revert += (time.time() - t)
            t = time.time()
            modif.run(APSP)
            changes = APSP.get_changes()
            t_APSP_modif += (time.time() - t)
            metric.update(changes=changes)
            t_metric_modif += (time.time() - t)
            value = metric.total_results.mean()
            if value < min_value:
                best = modif
                min_value = value
            t = time.time()
            APSP.restore()
            t_APSP_revert += (time.time() - t)
            metric.restore()
            t_metric_revert += (time.time() - t)
        t_opti = time.time() - t_opti
        out = open(result_path + "/optiTimeAbsolu.csv", "a")
        out.write("{};{};{}\n".format(n, "Initialisation : APSP", t_APSP_init))
        out.write("{};{};{}\n".format(n, "Initialisation : métrique", t_metric_init-t_APSP_init))
        out.write("{};{};{}\n".format(n, "Modification : APSP", t_APSP_modif))
        out.write("{};{};{}\n".format(n, "Modification : métrique", t_metric_init-t_APSP_modif))
        out.write("{};{};{}\n".format(n, "Annulation : APSP", t_APSP_modif))
        out.write("{};{};{}\n".format(n, "Annulation : métrique", t_metric_init - t_APSP_modif))
        out.write("{};{};{}\n".format(n, "Optimisation", t_opti))
        out.write("{};{};{}\n".format(n, "Meilleure valeur", best))
        out.write("{};{};{}\n".format(n, "Valeur initiale", init))
        out.close()

        out2 = open(result_path + "/optiTimeRelative.csv", "a")
        out2.write("{};{};{}\n".format(n, "Initialisation : APSP", t_APSP_init / t_opti))
        out2.write("{};{};{}\n".format(n, "Initialisation : métrique", t_metric_init / t_opti))
        out2.write("{};{};{}\n".format(n, "Modification : APSP", (t_APSP_modif + t_metric_init)/ t_opti))
        out2.write("{};{};{}\n".format(n, "Modification : métrique", (t_metric_modif + t_metric_init)/ t_opti))
        out2.write("{};{};{}\n".format(n, "Annulation : APSP", (t_APSP_revert + t_APSP_modif + t_metric_init)/ t_opti))
        out2.write("{};{};{}\n".format(n, "Annulation : métrique", (t_metric_revert + t_APSP_modif + t_metric_init) / t_opti))
        out2.write("{};{};{}\n".format(n, "Optimisation", 1))
        out2.close()


def optimization_values():
    class modif_edge(NetworkModification):
        """ template for modifications"""

        def run(self, APSP: Dynamic_APSP):
            """ execute the modification on the APSP given in argument"""
            generate_realist_random_edge(APSP,True)

    out = open(result_path + "/optiValues.csv", "w")
    out.write("localisation;number_modif;value;;deltatime\n")
    out.close()

    c = 1
    #for n in names:
    n = 'Dixmude'
    DataManager.produce_data(data_path, n, "train_bus")
    for i in range(3):
        for number_modif in range(0,51,5):
            print("number_modif = ",number_modif)
            time.sleep(10)
            t = time.time()
            param = DataManager.load_data(data_path, n, "train_bus")
            net = NetworkEfficiency(param, c, load_data=False, seed=round(345 * number_modif) +i)
            init_value = net.get_value()
            modifications = [modif_edge() for _ in range(number_modif)]
            _, best_value = find_best_modification(net, modifications)
            t = time.time() - t
            out = open(result_path + "/optiValues.csv", "a")
            out.write("{};{};{};{};{}\n".format(n, number_modif, best_value,best_value-init_value,t))
            out.close()


if __name__ == '__main__':
    # TimeInterval()
    data_path = "/Users/DimiS/Documents/Gotta_go_fast/Project/Data"
    result_path = "/Users/DimiS/Documents/Gotta_go_fast/Project/Program/Performance/Result"
    path_Belgium = PATH_BELGIUM(data_path)
    #   reduce_all()
    names = ['Alost', 'Anvers', 'Arlon', 'Ath', 'Audenarde', 'Bastogne', 'Bruges', 'Bruxelles-Capitale', 'Charleroi',
             'Courtrai', 'Dinant', 'Dixmude', 'Eeklo', 'Furnes', 'Gand', 'Hal-Vilvorde', 'Hasselt', 'Huy', 'Liège',
             'Louvain', 'Maaseik', 'Malines', 'Marche-en-Famenne', 'Mons', 'Mouscron', 'Namur', 'Neufchâteau',
             'Nivelles', 'Ostende', 'Philippeville', 'Roulers', 'Saint-Nicolas', 'Soignies', 'Termonde', 'Thuin',
             'Tielt', 'Tongres', 'Tournai', 'Turnhout', 'Verviers', 'Virton', 'Waremme', 'Ypres']

    names2 = ['Mons']#]#'Dixmude','Ath','Tournai','Mons','Nivelles','Charleroi', 'Liège', 'Bruxelles-Capitale']
    transports = ["train_bus"] #,"bus_only","train_bus"]
    #edge_node_by_arrondissement(names, transports)

    #time_static_dynamic(names2, transports)
    #max_walking_time_effect_APSP(names2, ["train_bus"])
    #time_metric_vs_APSP(names2)
    #MC_reducing_factor()
    #optimization_time(names2)
    #optimization_values()
    max_walking_time_effect_network(names2)




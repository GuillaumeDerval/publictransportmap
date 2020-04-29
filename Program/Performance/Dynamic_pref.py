import time
from Program.Data_manager.main import make_data_structure, time_str_to_int
from Program.Data_manager.path import PATH,PATH_BELGIUM
from Test.Test_dynamic_inc_APSP.my_utils import *
from Program.map import my_map


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
    #ne compte pas le arrete des trajet à pied ni rester sur place
    out = open(result_path + "/ArrondVertexEdge.csv","w")
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

def generate_random_edge(APSP):
    name1 = rdm.sample(APSP.idx_to_name, 1).pop()
    time1 = rdm.sample(APSP.used_time[APSP.name_to_idx[name1]], 1).pop()
    name2 = rdm.sample(APSP.idx_to_name, 1).pop()
    possible_time = []
    for t in APSP.used_time[APSP.name_to_idx[name2]]:
        if t >= time1:
            possible_time.append(t)
    if len(possible_time) > 0:
        time2 = rdm.sample(possible_time, 1).pop()
    else:
        time2 = rdm.randint(time1, APSP.max_time - 1)
    #print("add edge {} time {} to {} time {}".format(name1, time1, name2, time2))
    APSP.add_edge(name1, time1, name2, time2, u_position=None, v_position=None)


def generate_random_vertex_new_pos(APSP):
    mmap = my_map.get_map(APSP.param)
    # New position
    z_name = str(rdm.random())  # on pourrait avoir 2 fois le meme nom mais c'est improbable + pas grave
    time = rdm.randint(time_str_to_int("06:00:00")//60, time_str_to_int("10:30:00")//60)
    pos = rdm_point_shape(APSP.param)
    #print("add vertex {} time {} pos {} :  z_in {} , z_out {}".format(z_name, time, pos, [],[]))
    APSP.add_vertex(z_name, time, pos)


def generate_random_vertex_old_pos(APSP):
    mmap = my_map.get_map(APSP.param)
    # New position
    z_name = rdm.sample(APSP.idx_to_name, 1).pop()
    time = rdm.randint(time_str_to_int("06:00:00")//60, time_str_to_int("10:30:00")//60)
    pos = mmap.stop_position_dico[z_name]
    #print("add vertex {} time {} pos {} :  z_in {} , z_out {}".format(z_name, time, pos, [],[]))
    APSP.add_vertex(z_name, time, pos)

# #####################################################################################################################

def time_static_dynamic(names, transports):
    max_walking_time = 30
    walking_speed = 3.2
    MAX_TIME = 12 * 60

    out = open(result_path + "time_static_dynamic.csv", "w")
    out.write("transport;localisation;type;mean;all\n")

    for tr in transports:
        print("transport : ", tr)
        for n in names:
            print(n)
            times = {"static": [], "dynamic_edge": [], "dynamic_vertex_new": [], "dynamic_vertex_old": []}
            param = DataManager.produce_data(data_path,n, tr,max_walking_time, walking_speed, MAX_TIME)

            #Edge add
            start_time = time.time()
            APSP = Dynamic_APSP(param)
            times["static"].append(time.time() - start_time)
            for i in range(50):
                start_time = time.time()
                generate_random_edge(APSP)
                times["dynamic_edge"].append(time.time() - start_time)
            my_map.belgium_map = None

            # Vertex new add
            start_time = time.time()
            APSP = Dynamic_APSP(param)
            times["static"].append(time.time() - start_time)
            for i in range(50):
                start_time = time.time()
                generate_random_vertex_new_pos(APSP)
                times["dynamic_vertex_new"].append(time.time() - start_time)
            my_map.belgium_map = None

            # Vertex old add
            start_time = time.time()
            APSP = Dynamic_APSP(param)
            times["static"].append(time.time() - start_time)
            for i in range(50):
                start_time = time.time()
                generate_random_vertex_old_pos(APSP)
                times["dynamic_vertex_old"].append(time.time() - start_time)
            my_map.belgium_map = None

            out.write("{};{};{};{};{}".format(tr, n, "static", sum(times["static"])/3, times["static"]))
            out.write("{};{};{};{};{}".format(tr, n, "dynamic_edge", sum(times["dynamic_edge"]) / 50, times["dynamic_edge"]))
            out.write("{};{};{};{};{}".format(tr, n, "dynamic_vertex_new", sum(times["dynamic_vertex_new"]) / 50, times["dynamic_vertex_new"]))
            out.write("{};{};{};{};{}".format(tr, n, "dynamic_vertex_old", sum(times["dynamic_vertex_old"]) / 50, times["dynamic_vertex_old"]))


def max_walking_time_effect(names, transports):
    out = open(result_path + "time_static_dynamic.csv", "w")
    out.write("transport;localisation;max_time;mean;all\n")
    for max_walking_time in range(0, 60, 5):
        walking_speed = 3.2
        MAX_TIME = 12 * 60

        for tr in transports:
            for n in names:
                print(n)
                times = []
                param = DataManager.produce_data(data_path, n, tr, max_walking_time, walking_speed, MAX_TIME)

                # Vertex old add
                APSP = Dynamic_APSP(param)
                for i in range(50):
                    start_time = time.time()
                    generate_random_vertex_old_pos(APSP)
                    times.append(time.time() - start_time)
                out.write("{};{};{};{};{}".format(tr, n, max_walking_time, sum(times) / 50, times))


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

    names2 = ['Ath','Bruxelles-Capitale', 'Charleroi','Dixmude','Nivelles','Mons', 'Liège', 'Tournai']
    transports = ["train_only"] #,"bus_only","train_bus"]
    edge_node_by_arrondissement(names, transports)

    time_static_dynamic(names2, transports)
    max_walking_time_effect(names2, ["train_bus"])



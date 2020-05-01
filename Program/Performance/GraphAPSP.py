import csv
import numpy as np
import matplotlib.pyplot as plt

def graph_TimeInterval():
    data_path = "/Users/DimiS/Documents/Gotta_go_fast/Project/Program/Performance/Result"
    with open(data_path+"/TimeIntervalTrain.csv", newline='') as csvfile:
        train = csv.DictReader(csvfile, delimiter=';') #start;end;node;edge
        print(train.fieldnames)
        # Make a fake dataset
        starts,train_edges, train_nodes = [],[], []
        for row in train:
            starts.append(row["start"])
            train_edges.append(int(row["edge"]))
            train_nodes.append(int(row["node"]))

    with open(data_path+"/TimeIntervalBus.csv", newline='') as csvfile:
        train = csv.DictReader(csvfile, delimiter=';') #start;end;node;edge
        print(train.fieldnames)
        # Make a fake dataset
        bus_edges,bus_nodes = [], []
        for row in train:
            bus_edges.append(int(row["edge"]))
            bus_nodes.append(int(row["node"]))

    barWidth = 1
    plt.bar(starts, train_edges, color='#2d7f5e', edgecolor='white', width=barWidth)
    plt.show()
    plt.bar(starts, bus_edges,color='#2d7f5e', edgecolor='white', width=barWidth)
    #plt.xticks(y_pos, bars)
    plt.show()

    #plt.bar(starts, train_nodes, color='#557f2d', edgecolor='white', width=barWidth)
    #plt.show()
    #plt.bar(starts, bus_nodes, color='#2d7f5e', edgecolor='white', width=barWidth)
    # plt.xticks(y_pos, bars)
    #plt.show()

def graph_Node_by_Arrondi(tr):
    data_path = "/Users/DimiS/Documents/Gotta_go_fast/Project/Program/Performance/Result"


    with open(data_path+"/ArrondVertexEdge.csv", newline='') as csvfile:
        file = csv.DictReader(csvfile, delimiter=';')
        print(file.fieldnames)
        # Make a fake dataset
        arrond, edges, nodes = [],[], []
        for row in file:
            if row["transport"] == tr:
                arrond.append(row["arrondissementName"])
                edges.append(int(row["edge"]))
                nodes.append(int(row["node"]))

        arrNode = list(zip(arrond, nodes))
        arrNode.sort(key = lambda x : x[1])
        arrEdge = list(zip(arrond, edges))
        arrEdge.sort(key = lambda x : x[1])

        barWidth = 1
        plt.bar([x[0] for x in arrNode], [x[1] for x in arrNode], color='#2d7f5e', edgecolor='white', width=barWidth)
        plt.title("Nombre de stations de train par arrondissement")
        plt.xlabel("Arrondissement")
        plt.xticks(rotation=90)
        plt.ylabel("Nombre de stations")
        plt.yscale('log')
        plt.show()


        barWidth = 1
        plt.bar([x[0] for x in arrEdge], [x[1] for x in arrEdge], color='#2d7f5e', edgecolor='white', width=barWidth)
        plt.title("Nombre de connexion de train par arrondissement")
        plt.xlabel("Arrondissement")
        plt.xticks(rotation=90)
        plt.ylabel("Nombre de connexions")
        plt.yscale('log')
        plt.show()



def perf_graph():
    data_path = "/Users/DimiS/Documents/Gotta_go_fast/Project/Program/Performance/Result"

    with open(data_path + "/TimeStaticDynamic.csv", newline='') as csvfile:
        file = csv.DictReader(csvfile, delimiter=';')
        print(file.fieldnames)
        # Make a fake dataset
        arrond = {"train_only":[], "bus_only":[], "train_bus": []}
        static_mean, static_std =  {"train_only":[], "bus_only":[], "train_bus": []}, {"train_only":[], "bus_only":[], "train_bus": []}
        edge_mean, edge_std = {"train_only":[], "bus_only":[], "train_bus": []}, {"train_only":[], "bus_only":[], "train_bus": []}
        new_vertex_mean, new_vertex_std = {"train_only":[], "bus_only":[], "train_bus": []}, {"train_only":[], "bus_only":[], "train_bus": []}
        old_vertex_mean, old_vertex_std = {"train_only":[], "bus_only":[], "train_bus": []}, {"train_only":[], "bus_only":[], "train_bus": []}
        for row in file:
            tr = row["transport"]
            if row["type"] == "static":
                arrond[tr].append(row["localisation"])
                static_mean[tr].append(float(row["mean"]))
                static_std[tr].append(float(row["stderr"]))
            elif row["type"] == "dynamic_edge":
                edge_mean[tr].append(float(row["mean"]))
                edge_std[tr].append(float(row["stderr"]))
            elif row["type"] == "dynamic_vertex_new":
                new_vertex_mean[tr].append(float(row["mean"]))
                new_vertex_std[tr].append(float(row["stderr"]))
            else:
                old_vertex_mean[tr].append(float(row["mean"]))
                old_vertex_std[tr].append(float(row["stderr"]))



        tr = "train_bus"

        with open(data_path + "/ArrondVertexEdge.csv", newline='') as csvfile:
            file = csv.DictReader(csvfile, delimiter=';')
            print(file.fieldnames)
            # Make a fake dataset
            edges, nodes = [], []
            for row in file:
                if row["transport"] == tr:
                    edges.append(int(row["edge"]))
                    nodes.append(int(row["node"]))


        barWidth = 2000

        #r1 = np.arange(len(arrond[tr]))
        r1 = np.array(edges)
        r2 = [x + barWidth for x in r1]
        r3 = [x + 2*barWidth for x in r1]
        r4 = [x + 3*barWidth for x in r1]
        r5 = [x + 4 * barWidth for x in r1]
        r6 = [x + 5 * barWidth for x in r1]

        # Create blue bars
        plt.bar(r1, edge_mean[tr], width=barWidth, color='green', edgecolor='black',
                 label='Ajout d\'une arête')

        # Create cyan bars
        plt.bar(r2, new_vertex_mean[tr], width=barWidth, color='cyan', edgecolor='black',
                 label='Ajout d\'un noeud (nouvelle station)')

        plt.bar(r3, old_vertex_mean[tr], width=barWidth, color='blue', edgecolor='black',
                  label='Ajout d\'un noeud (ancienne station)')

        #plt.bar(r4, static_mean[tr], width=barWidth, color='red', edgecolor='black',
        #        yerr=static_std[tr], label='sorgho')

        #plt.bar(r5, nodes, width=barWidth, color='pink', edgecolor='black',
         #        label='sorgho')

        #plt.bar(r6, edges, width=barWidth, color='yellow', edgecolor='black',
        #         label='sorgho')
        plt.title("Durée d'execution d'un ajout en fonction de l'arrondissement")
        plt.xlabel("Arrondissement/ nombre d'arêtes")
        #plt.ylim()
        plt.ylabel("Temps (s)")
        plt.xticks(r2, [arrond[tr][i] + "\n arêtes: " + str(edges[i]) for i in range(len(arrond[tr]))], rotation=45)
        plt.legend()
        plt.show()

        plt.savefig("./Result/timeAdding.png")

    #plt.bar(starts, train_nodes, color='#557f2d', edgecolor='white', width=barWidth)
    #plt.show()
    #plt.bar(starts, bus_nodes, color='#2d7f5e', edgecolor='white', width=barWidth)
    # plt.xticks(y_pos, bars)
    #plt.show()



def perf_graph2():
    data_path = "/Users/DimiS/Documents/Gotta_go_fast/Project/Program/Performance/Result"

    with open(data_path + "/TimeStaticDynamic.csv", newline='') as csvfile:
        file = csv.DictReader(csvfile, delimiter=';')
        print(file.fieldnames)
        # Make a fake dataset
        arrond = {"train_only":[], "bus_only":[], "train_bus": []}
        static_mean, static_std =  {"train_only":[], "bus_only":[], "train_bus": []}, {"train_only":[], "bus_only":[], "train_bus": []}
        edge_mean, edge_std = {"train_only":[], "bus_only":[], "train_bus": []}, {"train_only":[], "bus_only":[], "train_bus": []}
        new_vertex_mean, new_vertex_std = {"train_only":[], "bus_only":[], "train_bus": []}, {"train_only":[], "bus_only":[], "train_bus": []}
        old_vertex_mean, old_vertex_std = {"train_only":[], "bus_only":[], "train_bus": []}, {"train_only":[], "bus_only":[], "train_bus": []}
        for row in file:
            tr = row["transport"]
            if row["type"] == "static":
                arrond[tr].append(row["localisation"])
                static_mean[tr].append(float(row["mean"]))
                static_std[tr].append(float(row["stderr"]))
            elif row["type"] == "dynamic_edge":
                edge_mean[tr].append(float(row["mean"]))
                edge_std[tr].append(float(row["stderr"]))
            elif row["type"] == "dynamic_vertex_new":
                new_vertex_mean[tr].append(float(row["mean"]))
                new_vertex_std[tr].append(float(row["stderr"]))
            else:
                old_vertex_mean[tr].append(float(row["mean"]))
                old_vertex_std[tr].append(float(row["stderr"]))



        tr = "train_bus"

        with open(data_path + "/ArrondVertexEdge.csv", newline='') as csvfile:
            file = csv.DictReader(csvfile, delimiter=';')
            print(file.fieldnames)
            # Make a fake dataset
            edges, nodes = [], []
            for row in file:
                if row["transport"] == tr:
                    edges.append(int(row["edge"]))
                    nodes.append(int(row["node"]))


        barWidth = 12
        r0 = np.array(edges)
        r1 = [x -2*x / barWidth for x in r0]
        r2 = [x - x/barWidth for x in r0]
        r3 = r0
        r4 = [x + x/barWidth for x in r0]
        r5 = [x +2*x / barWidth for x in r0]
        r6 = [x + 5 * barWidth for x in r1]

        plt.bar(r1, static_mean[tr], width=[e / barWidth for e in edges], color='red', edgecolor='black',
                label='Initialisation')
        plt.bar(r2, edge_mean[tr], width=[e/barWidth for e in edges], color='green', edgecolor='black',
                 label='Ajout d\'une arête')
        plt.bar(r3, new_vertex_mean[tr], width=[e/barWidth for e in edges], color='cyan', edgecolor='black',
                 label='Ajout d\'un noeud (nouvelle station)')

        plt.bar(r4, old_vertex_mean[tr], width=[e/barWidth for e in edges], color='blue', edgecolor='black',
                 label='Ajout d\'un noeud (ancienne station)')



        #plt.bar(r5, nodes, width=barWidth, color='pink', edgecolor='black',
         #       label='sorgho')

        #plt.bar(r6, edges, width=barWidth, color='yellow', edgecolor='black',
         #       label='sorgho')



        plt.xticks(r3, arrond[tr], rotation=60)

        plt.title("Durée d'execution en fonction de l'arrondissement \n échelle log-log ")
        plt.xlabel("Arrondissement / nombre d'arêtes")
        plt.xticks()
        #plt.ylim()
        plt.ylabel("Temps [s]")
        plt.xscale('log')
        plt.xticks(r3, [arrond[tr][i] + "\n arêtes: " + str(edges[i]) for i in range(len(arrond[tr]))], rotation=45)
        plt.yscale('log')
        plt.legend()
        #plt.show()

        plt.savefig("./Result/timeAllLogLog.png")

    #plt.bar(starts, train_nodes, color='#557f2d', edgecolor='white', width=barWidth)
    #plt.show()
    #plt.bar(starts, bus_nodes, color='#2d7f5e', edgecolor='white', width=barWidth)
    # plt.xticks(y_pos, bars)
    #plt.show()



if __name__ == '__main__':
    #graph_TimeInterval()
    #graph_Node_by_Arrondi(tr = "train_only")
    #graph_Node_by_Arrondi(tr="train_bus")
    #perf_graph()
    #perf_graph2()
    pass
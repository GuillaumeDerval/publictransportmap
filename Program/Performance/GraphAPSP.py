import csv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns
import math





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

    barWidth = 0.9

    #plt.show()
    plt.bar(starts, bus_edges,color='dodgerblue',  width=barWidth)
    #plt.title('Variation du nombre de connexions durant la journée')
    plt.xlabel('Temps   [ heure ]')
    plt.ylabel('Nombre de connexions')
    #plt.bar(starts, train_edges, color='darkorange', edgecolor='darkorange', width=barWidth)

    #plt.xticks(y_pos, bars)

    plt.savefig("./Result/edgeTime.png")
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

    with open(data_path + "/ArrondVertexEdgeAll.csv", newline='') as csvfile:
        file = csv.DictReader(csvfile, delimiter=';')
        print(file.fieldnames)
        # Make a fake dataset
        arrond, edges, nodes = [], [], []
        for row in file:
            if row["transport"] == tr:
                arrond.append(row["arrondissementName"])
                edges.append(int(row["edge"]))
                nodes.append(int(row["node"]))

        allArrNode = list(zip(arrond, nodes))
        allArrNode.sort(key=lambda x: x[1])
        allArrEdge = list(zip(arrond, edges))
        allArrEdge.sort(key=lambda x: x[1])

        barWidth = 1
        plt.bar([x[0] for x in allArrNode], [x[1] for x in allArrNode], color='dodgerblue', edgecolor='white', width=barWidth, label= 'non-sélectionné')
        plt.bar([x[0] for x in arrNode], [x[1] for x in arrNode], color='darkorange', edgecolor='white', width=barWidth,
                label='sélectionné')
        plt.title("Nombre de stations de transport en commun par arrondissement")
        plt.xlabel("Arrondissement")
        plt.xticks(rotation=90)
        plt.ylabel("Nombre de stations")
        #plt.yscale('log')
        plt.legend()
        plt.gcf().subplots_adjust(bottom=0.40)
        plt.savefig('./Result/sationsArrond.png', format='png')
        plt.show()


        barWidth = 1
        plt.bar([x[0] for x in allArrEdge], [x[1] for x in allArrEdge], color='dodgerblue', edgecolor='white', width=barWidth, label= 'non-sélectionné')
        plt.bar([x[0] for x in arrEdge], [x[1] for x in arrEdge], color='darkorange', edgecolor='white', width=barWidth,
                label='sélectionné')
        plt.title("Nombre de connexion de transport en commun par arrondissement")
        plt.xlabel("Arrondissement")
        plt.xticks(rotation=90)
        plt.ylim([0,200000])

        plt.ylabel("Nombre de connexions")
        #plt.yscale('log')
        plt.legend()
        plt.gcf().subplots_adjust(bottom=0.40)
        plt.savefig('./Result/connexArrond.png', format='png')
        plt.show()



        plt.scatter([x[1] for x in allArrNode],[x[1] for x in allArrEdge], edgecolors='dodgerblue', label= 'non-sélectionné')
        plt.scatter([x[1] for x in arrNode], [x[1] for x in arrEdge], edgecolors='darkorange', label='sélectionné')
        plt.title('Relation entre le nombre de station et de connexions')
        plt.xlabel("Nombre de stations")
        plt.ylabel("Nombre de connexions")
        plt.legend()
        plt.savefig('./Result/sationsConnex.png')
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
        plt.bar(r1, edge_mean[tr], width=barWidth, color='dodgerblue', edgecolor='white',
                 label='Ajout d\'une arête')

        # Create cyan bars
        plt.bar(r2, new_vertex_mean[tr], width=barWidth, color='yellowgreen', edgecolor='white',
                 label='Ajout d\'un noeud (nouvelle station)')

        plt.bar(r3, old_vertex_mean[tr], width=barWidth, color='green', edgecolor='white',
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
        plt.gcf().subplots_adjust(bottom=0.27)


        plt.savefig("./Result/timeAdding.png")
        plt.show()

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

        plt.bar(r1, static_mean[tr], width=[e / barWidth for e in edges], color='darkorange', edgecolor='white',
                label='Initialisation')
        plt.bar(r2, edge_mean[tr], width=[e/barWidth for e in edges], color='dodgerblue', edgecolor='white',
                 label='Ajout d\'une arête')
        plt.bar(r3, new_vertex_mean[tr], width=[e/barWidth for e in edges], color='yellowgreen', edgecolor='white',
                 label='Ajout d\'un noeud (nouvelle station)')

        plt.bar(r4, old_vertex_mean[tr], width=[e/barWidth for e in edges], color='green', edgecolor='white',
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
        plt.gcf().subplots_adjust(bottom=0.27)

        plt.savefig("./Result/timeAllLogLog.png")
        plt.show()

    #plt.bar(starts, train_nodes, color='#557f2d', edgecolor='white', width=barWidth)
    #plt.show()
    #plt.bar(starts, bus_nodes, color='#2d7f5e', edgecolor='white', width=barWidth)
    # plt.xticks(y_pos, bars)
    #plt.show()



def time_effectInit():
    data = pd.read_csv("./Result/WalkingTimeEffectInit2.csv",delimiter=';')
    #data.plot(kind='bar')

    sns.lmplot("max_time", "value", data=data,hue='localisation',legend=False, ci=None) #, fit_reg=False,  col_wrap=2
    plt.legend(loc='upper left')
    plt.ylabel("Temps [seconds]")
    plt.xlabel("Temps maximum de marche [minutes]")

    plt.savefig("./Result/WalkingTimeEffectInit.png")
    plt.show()
    #fig = plt.scatter(data, x="max_time", y="value")
    #fig.show()

def time_effectVertex():
    data = pd.read_csv("./Result/WalkingTimeEffectVertex2.csv",delimiter=';')
    #data.plot(kind='bar')

    sns.lmplot("max_time", "mean", data=data,hue='localisation',legend=False, ci=None) #, fit_reg=False,  col_wrap=2
    plt.legend(loc='upper left')
    plt.ylabel("Temps [seconds]")
    plt.xlabel("Temps maximum de marche [minutes]")

    plt.savefig("./Result/WalkingTimeEffectVertex.png")
    plt.show()
    #fig = plt.scatter(data, x="max_time", y="value")
    #fig.show()


def time_effectInitRatio():
    data = pd.read_csv("./Result/WalkingTimeEffectInit2.csv",delimiter=';')
    #data.plot(kind='bar')
    means = [sum(data["value"][i*13:i*13+13])/13 for i in range(4)]
    data["ratio"] = [v/means[i] for i in range(4) for v in data["value"][i*13:i*13+13]]
    sns.lmplot("max_time", "ratio", data=data,hue='localisation',legend=False,ci = None) #, fit_reg=False,  col_wrap=2
    plt.legend(loc='upper left')
    plt.ylabel("Ratio : temps/temps moyen")
    plt.xlabel("Temps maximum de marche [minutes]")

    plt.savefig("./Result/WalkingTimeEffectInitRatio.png")
    plt.show()


def time_effectVertexRatio():
    data = pd.read_csv("./Result/WalkingTimeEffectVertex2.csv",delimiter=';')
    #data.plot(kind='bar')
    means = [sum(data["mean"][i*13:i*13+13])/13 for i in range(4)]
    data["ratio"] = [v/means[i] for i in range(4) for v in data["mean"][i*13:i*13+13]]
    sns.lmplot("max_time", "ratio", data=data,hue='localisation',legend=False, ci = None) #, fit_reg=False,  col_wrap=2
    plt.legend(loc='upper left')
    plt.ylabel("Ratio : temps/temps moyen")
    plt.xlabel("Temps maximum de marche [minutes]")

    plt.savefig("./Result/WalkingTimeEffectEdgeRatio.png")
    plt.show()

if __name__ == '__main__':
    #graph_TimeInterval()
    #graph_Node_by_Arrondi(tr="train_only")
    #graph_Node_by_Arrondi(tr="train_bus")
    #perf_graph()
    #perf_graph2()
    time_effectInit()
    time_effectVertex()
    time_effectInitRatio()
    time_effectVertexRatio()
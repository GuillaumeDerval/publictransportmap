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

def graph_Node_by_Arrondi():
    data_path = "/Users/DimiS/Documents/Gotta_go_fast/Project/Program/Performance/Result"
    tr = "train_only"


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

        barWidth = 1
        plt.bar(arrond, nodes, color='#2d7f5e', edgecolor='white', width=barWidth)
        plt.title("Nombre de stations de train par arrondissement")
        plt.xlabel("Arrondissement")
        plt.ylabel("Nombre de stations")
        plt.show()

        barWidth = 1
        plt.bar(arrond, edges, color='#2d7f5e', edgecolor='white', width=barWidth)
        plt.title("Nombre de connexion de train par arrondissement")
        plt.xlabel("Arrondissement")
        plt.ylabel("Nombre de connexions")
        plt.show()

    #plt.bar(starts, train_nodes, color='#557f2d', edgecolor='white', width=barWidth)
    #plt.show()
    #plt.bar(starts, bus_nodes, color='#2d7f5e', edgecolor='white', width=barWidth)
    # plt.xticks(y_pos, bars)
    #plt.show()


if __name__ == '__main__':
    graph_TimeInterval()
    graph_Node_by_Arrondi()

"""
Ce fichier contient un example d'utilisation du projet
"""


# 0) Initialisation des dossier + localisation des donnée : fichier GTFS, census, ...
# A ne faire qu'une seule fois
main.initialisation(destination_path, gtfs_path, census_path, pop_path)


if __name__ == '__main__':
    data_path = "/Users/DimiS/Documents/Gotta_go_fast/Project/Data"
    #make_data_structure(data_path)
    #DataManager.produce_data_belgium(data_path)
    DataManager.reduce_data(data_path, "Arrondissement de Malines","Malines", "bus_only")
    #DataManager.produce_data(data_path,"Malines", "train_only", 15, 5)
#1)
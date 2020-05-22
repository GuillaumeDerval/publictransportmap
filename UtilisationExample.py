from Program.Data_manager.main import DataManager
from Program.NetworkEfficiency import NetworkEfficiency, NetworkModification, AddConnexion, AddLine

"""
Ce fichier contient un example d'utilisation du projet
"""


# 0) Etapes à faire une seule fois , lors du téléchargement du projet

#Initialiser la structure de dossier contenant les données
import os
os.makedirs("./Data/")
DataManager.make_data_structure("./Data/")

# Déplacer les fichier ...



if __name__ == '__main__':
    data_path = "/Users/DimiS/Documents/Gotta_go_fast/Project/Data"
    #make_data_structure(data_path)
    #DataManager.produce_data_belgium(data_path)
    DataManager.reduce_data(data_path, "Arrondissement de Malines","Malines", "bus_only")
    #DataManager.produce_data(data_path,"Malines", "train_only", 15, 5)
#1)
"""
Ce fichier contient un example d'utilisation du projet
"""

##### 0) Effectuer le import suivants
from Program.Data_manager.main import DataManager
from Program.NetworkEfficiency import NetworkEfficiency, AddConnexion, AddLine,AddRandomConnexion
from Program.Optimization import find_best_modification, find_best_Duo_modification


##### 0b) Etapes à faire une seule fois , lors du téléchargement du projet
##### Initialiser la structure de dossier contenant les données
DataManager.make_data_structure("./Data")

##### Telecharger les fichiers GTFS du TEC : https://data.gov.be/en/dataset/tec
#####                               de la STIB : https://opendata.stib-mivb.be/store/data
#####                               de Lijn : https://data.gov.be/en/dataset/delijn
#####                               de la SNCB/NMBS : https://www.belgiantrain.be/fr/3rd-party-services/mobility-service-providers/public-data
##### Déplacer les dossier fichier : delijn, sncb, stib, tec dans le dossier nouvellement créé : "./Data/initial/gtfs"


##### Telecharger le recensement Belge de 2011:
#####               https://data.gov.be/fr/dataset/0782121ea73e0ef80711b358645f74b06ebd3ac8
##### Telecharger le fichier geojson contenant la carte de la Belgique :
#####               https://statbel.fgov.be/fr/open-data/secteurs-statistiques
##### Telecharger le fichier contenant la population belge par secteur en 2011 :
#####               https://statbel.fgov.be/fr/open-data?category=209&page=0
##### Deplacer les fichiers TU_CENSUS_2011_COMMUTERS_MUNTY.txt,
#####                       sh_statbel_statsitcal_sectors.geojson,
#####                       OPEN_DATA_SECTOREN_2011.csv
#####  ainsi obtenu dans "./Data/initial"


##### Deplacer le fichier stop_lambert_train_bus.json dans le dossier "./Data/intermediate"
##### Si la position de certaines position d'arrêts sont manquantes, 
##### vous devez les calculer en vous inspirant BuildBelgiumMap.py 


raise (Exception, "commenter cette ligne apres avoir telecharger le données ")

##### Transformer regrouper et changer le format des données GTFS
##### 0) Créer les donner pour la belgique et choisir la tranche horaire
#####- la tranche horaire observée  (défaut :  6h à 10h30)
DataManager.produce_data_belgium("./Data", start_time=DataManager.time_transformation("06:00:00"),
                        end_time=DataManager.time_transformation("10:30:00"))






##### 1) Reduire le nombre de données traitées en selectionnant:
#####            - un ou plusieur arrondissement + donner leur un nom
#####            - le moyen de transport : "train_only", "bus_only",  "train_bus"
#####
DataManager.reduce_data("./Data",
                        ["Arrondissement de Dixmude"],
                        "Example",
                        "train_bus")






##### 2a) Produire les données utilisé par la métrique et l'incrementale All Pairs Shortest Paths
#####    Pour cela,  il faut definir :
#####           - le temps de trajet maximale en une traite   (défaut :  30 min)
#####           - la vitesse de marche à pied à vol d'oiseau  (défaut :  3.6 km/h)
#####           - le temps maximal atteignable               (défaut :  28*60 min)
parameter = DataManager.produce_data("./Data", "Example", "train_bus", 30, 3.6)


##### 2b) OU charger des données déjà produites
parameter =DataManager.load_data("./Data", "Dixmude", "train_bus")





print("compute")

##### 3) Utiliser la class calculant l'efficacité d'un réseau

#####Intitialisation
##### NetworkEfficency va initialiser la metrique et l'APSP, à l'aide des parametre suivant:
#####            - param, produit/charger par le Datamanager. Il s'agit d'un ensemble de données sur les constante utilisé et la localisation des fichier
#####            - c : int
#####            - load_data = True , pour charger les résultat d'un initialisation précedante
#####            (Attention à n'utilisé que si une unique sauvegarde effectué après l'initialisation et avant toute modifications)
network_efficiency = NetworkEfficiency(param=parameter, c=0.01, load_data=False)
print("save")
#####Sauvegarder les résultat
network_efficiency.hard_save()
print("end")

#####Effectuer une modification
##### Ajouter une connexion entre 2 arrêts
modif1 = AddConnexion("delijn87605", 404, "delijn42537", 418)
network_efficiency.modify(modif1)

#####Ajouter une ligne de TC
##### Ajouter une connexion entre 2 arrêts
modif2 = AddLine([("delijn42525", 500, 500, None),("delijn42296",505,506,None),("delijn87605",512,512,None)])
network_efficiency.modify(modif2)

modif3 = AddRandomConnexion()
network_efficiency.modify(modif3)


##### Il est aussi possible de créer ces propre modification en implementant l'interface
class NetworkModification:
    """ template for modifications"""

    def run(self, APSP):
        """ execute the modification on the APSP given in argument"""
        pass


##### Pour pouvoir revenir en arrière lors de la recherche de la meilleur ligne de transport 2 fonctions sont utilisées
##### Save,    pour sauvegarder momentanément l'état du réseau et de la mesure
network_efficiency.save()
##### Restore,   pour annuler toutes les modification effectuer depuis le dernier save() ainsi que le save() en question
##### Il est possible d'effectuer plusieur save et modifications de suite puis de les annuler avec plusieur restore
network_efficiency.restore()




##### 4) Utiliser le fonction d'optimisation conçue
print("\n Optimisation")
network = NetworkEfficiency(param=parameter, c=0.1, load_data=False, seed=42)
print("initial value : ", network.get_value())

best, best_value = find_best_modification(network=network, modifications=[modif1, modif2, modif3])
print(best, " with value : ", best_value)

best, best_value = find_best_Duo_modification(network=network, modifications=[modif1, modif2, modif3])
print("(",best[0],", ",best[1], " with value : ", best_value)



